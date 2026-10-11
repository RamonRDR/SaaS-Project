#!/usr/bin/env python3
"""Testes de ingressos idempotentes e reconstrução de eventos sem API real."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "mode_a_inbox", Path(__file__).with_name("mode_a_inbox.py")
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

SHA_A = "a" * 40
SHA_B = "b" * 40
MAIN_SHA = "c" * 40
BOT = {"login": "github-actions[bot]", "id": 41898282}


def pr(number: int = 17, sha: str = SHA_A, body: str | None = None) -> dict:
    return {
        "number": number,
        "state": "open",
        "body": body
        if body is not None
        else ("ORCHESTRATOR_MODE: A\nCONTROL_ISSUE: 1\n"),
        "base": {
            "ref": "main",
            "repo": {"full_name": MODULE.REPOSITORY},
        },
        "head": {"sha": sha},
    }


def comment(intent: dict, author: dict | None = None) -> dict:
    return {
        "body": MODULE.serialize_intent(intent),
        "user": author or BOT,
    }


class FakeAPI:
    """Emula fonte GitHub com comentários duráveis e eventos não confiáveis."""

    def __init__(self, prs: list[dict] | None = None):
        self.prs = {p["number"]: p for p in (prs if prs is not None else [pr()])}
        self.comments: list[dict] = []
        self.posts = 0
        self.write_then_timeout = False
        self.control_open = True
        self.page_limit = False
        self.inbox_scans = 0
        self.direct_readbacks = 0
        self.control_reads = 0
        self.close_on_control_read = None

    def request(self, method: str, endpoint: str, data: dict | None = None):
        if method == "POST" and endpoint == "/issues/99/comments":
            assert data and "body" in data
            self.posts += 1
            self.comments.append(
                {
                    "id": 6_100_000_000 + self.posts,
                    "body": data["body"],
                    "user": BOT,
                }
            )
            if self.write_then_timeout:
                self.write_then_timeout = False
                raise MODULE.ClosedGate("GITHUB_API_UNCERTAIN")
            return self.comments[-1]
        if method == "GET" and endpoint == "/issues/99":
            return {"state": "open", "body": "MODE_A_INBOX_V1\nsomente intents"}
        if method == "GET" and endpoint.startswith("/issues/comments/"):
            self.direct_readbacks += 1
            number = int(endpoint.rsplit("/", 1)[1])
            matches = [row for row in self.comments if row.get("id") == number]
            if len(matches) != 1:
                raise MODULE.ClosedGate("GITHUB_API_UNCERTAIN")
            return matches[0]
        if method == "GET" and endpoint in {"/issues/1", "/issues/2"}:
            self.control_reads += 1
            if self.close_on_control_read == self.control_reads:
                self.control_open = False
            return {
                "state": "open" if self.control_open else "closed",
                "body": (
                    "ORCHESTRATOR_MODE: A\n"
                    "PHASE: PHASE-0-G\n"
                    "OBJECTIVE: Runtime unattended\n"
                ),
                "user": {"login": "RamonRDR"},
            }
        if method == "GET" and endpoint.startswith("/pulls/"):
            return self.prs[int(endpoint.rsplit("/", 1)[1])]
        raise AssertionError(f"unexpected API path: {method} {endpoint}")

    def pages(self, path: str):
        if path.startswith("/issues/99/comments"):
            self.inbox_scans += 1
            if self.page_limit:
                raise MODULE.ClosedGate("PAGINATION_LIMIT")
            return list(self.comments)
        if path.startswith("/pulls?state=open"):
            return list(self.prs.values())
        raise AssertionError(f"unexpected listing: {path}")


class InboxTests(unittest.TestCase):
    def test_request_identity_does_not_depend_on_main_or_run(self):
        first = MODULE.make_intent(pr(), MAIN_SHA)
        second = MODULE.make_intent(pr(), SHA_B)
        assert first and second
        self.assertEqual(first["request_id"], second["request_id"])
        self.assertEqual(first["operation_key"], second["operation_key"])
        self.assertNotEqual(first["main_source_sha"], second["main_source_sha"])
        self.assertEqual(first["state"], "PENDING")
        self.assertEqual(first["operation_kind"], "CODEX_01")
        self.assertEqual(first["authorized_attempt"], 0)

    def test_write_and_readback_and_repeat_are_idempotent(self):
        api = FakeAPI()
        first = MODULE.ingest(api, 99, MAIN_SHA, 17)
        self.assertEqual(first["new_intents_verified"], 1)
        self.assertEqual(api.posts, 1)
        second = MODULE.ingest(api, 99, MAIN_SHA, 17)
        self.assertEqual(second["new_intents_verified"], 0)
        self.assertEqual(api.posts, 1)
        report = MODULE.reconcile(api, 99, MAIN_SHA)
        self.assertEqual(report["inbox_records"], 1)
        self.assertEqual(report["missing_requests"], [])
        self.assertFalse(report["paid_inference_enabled"])

    def test_lost_event_is_reconstructed_from_current_prs(self):
        api = FakeAPI([pr(17), pr(18, SHA_B)])
        report = MODULE.reconcile(api, 99, MAIN_SHA)
        self.assertEqual(len(report["missing_requests"]), 2)
        result = MODULE.ingest(api, 99, MAIN_SHA, None)
        self.assertEqual(result["new_intents_verified"], 2)
        self.assertEqual(MODULE.reconcile(api, 99, MAIN_SHA)["missing_requests"], [])

    def test_batch_readback_uses_comment_id_without_n_squared_scans(self):
        api = FakeAPI([pr(17), pr(18, SHA_B), pr(19, "d" * 40)])
        outcome = MODULE.ingest(api, 99, MAIN_SHA, None)
        self.assertEqual(outcome["new_intents_verified"], 3)
        self.assertEqual(api.posts, 3)
        self.assertEqual(api.inbox_scans, 1)
        self.assertEqual(api.direct_readbacks, 3)
        self.assertEqual(api.control_reads, 6)

    def test_control_is_rechecked_before_post(self):
        api = FakeAPI()
        api.close_on_control_read = 2
        with self.assertRaisesRegex(MODULE.ClosedGate, "INVALID_CONTROL_ISSUE"):
            MODULE.ingest(api, 99, MAIN_SHA, 17)
        self.assertEqual(api.posts, 0)
        self.assertEqual(api.control_reads, 2)

    def test_invalid_open_pr_does_not_block_other_candidates(self):
        api = FakeAPI(
            [
                pr(17, body="ORCHESTRATOR_MODE: A\nCONTROL_ISSUE: broken"),
                pr(18, SHA_B),
            ]
        )
        result = MODULE.ingest(api, 99, MAIN_SHA, None)
        self.assertEqual(result["new_intents_verified"], 1)
        self.assertEqual(api.posts, 1)
        self.assertEqual(api.comments[0]["user"], BOT)

    def test_inbox_cannot_be_control_issue(self):
        api = FakeAPI([pr(body="ORCHESTRATOR_MODE: A\nCONTROL_ISSUE: 99")])
        with self.assertRaisesRegex(MODULE.ClosedGate, "CONTROL_EQUALS_INBOX"):
            MODULE.ingest(api, 99, MAIN_SHA, 17)

    def test_untrusted_comment_cannot_forge_pending(self):
        api = FakeAPI()
        intent = MODULE.make_intent(pr(), MAIN_SHA)
        assert intent
        api.comments.append(comment(intent, {"login": "malicious", "id": 7}))
        report = MODULE.reconcile(api, 99, MAIN_SHA)
        self.assertEqual(len(report["missing_requests"]), 1)
        self.assertEqual(report["inbox_records"], 0)

    def test_mutated_bot_comment_blocks(self):
        api = FakeAPI()
        item = MODULE.make_intent(pr(), MAIN_SHA)
        assert item
        forged = comment(item)
        forged["body"] += "\nchanged"
        api.comments.append(forged)
        with self.assertRaisesRegex(
            MODULE.ClosedGate, "INVALID_INBOX_JSON|MODIFIED_INBOX_RECORD"
        ):
            MODULE.reconcile(api, 99, MAIN_SHA)

    def test_wrong_operation_key_blocks(self):
        item = MODULE.make_intent(pr(), MAIN_SHA)
        assert item
        item["operation_key"] = "overridden"
        with self.assertRaisesRegex(MODULE.ClosedGate, "INVALID_INBOX_IDENTITY"):
            MODULE.parse_comment(comment(item))

    def test_ambiguous_post_uses_authoritative_readback(self):
        api = FakeAPI()
        api.write_then_timeout = True
        result = MODULE.ingest(api, 99, MAIN_SHA, 17)
        self.assertEqual(result["new_intents_verified"], 1)
        self.assertEqual(api.posts, 1)
        MODULE.ingest(api, 99, MAIN_SHA, 17)
        self.assertEqual(api.posts, 1)

    def test_stale_head_does_not_pass_reconciliation(self):
        api = FakeAPI()
        MODULE.ingest(api, 99, MAIN_SHA, 17)
        api.prs[17] = pr(17, SHA_B)
        report = MODULE.reconcile(api, 99, MAIN_SHA)
        self.assertEqual(len(report["missing_requests"]), 1)
        self.assertEqual(report["stale_records"], 1)

    def test_changed_control_on_same_head_blocks_reuse(self):
        api = FakeAPI()
        MODULE.ingest(api, 99, MAIN_SHA, 17)
        api.prs[17] = pr(body="ORCHESTRATOR_MODE: A\nCONTROL_ISSUE: 2\n")
        with self.assertRaisesRegex(MODULE.ClosedGate, "REQUEST_CONTEXT_CHANGED"):
            MODULE.reconcile(api, 99, MAIN_SHA)
        with self.assertRaisesRegex(MODULE.ClosedGate, "REQUEST_CONTEXT_CHANGED"):
            MODULE.ingest(api, 99, MAIN_SHA, 17)
        self.assertEqual(api.posts, 1)

    def test_duplicate_records_are_not_financial_claims(self):
        api = FakeAPI()
        item = MODULE.make_intent(pr(), MAIN_SHA)
        assert item
        api.comments.extend([comment(item), comment(item)])
        report = MODULE.reconcile(api, 99, MAIN_SHA)
        self.assertEqual(report["duplicate_records"], 1)
        self.assertFalse(report["ledger_mutations"])
        self.assertFalse(report["ready_enabled"])

    def test_closed_control_issue_blocks_intake(self):
        api = FakeAPI()
        api.control_open = False
        with self.assertRaisesRegex(MODULE.ClosedGate, "INVALID_CONTROL_ISSUE"):
            MODULE.ingest(api, 99, MAIN_SHA, 17)

    def test_invalid_or_duplicate_control_fields_block(self):
        for body in [
            "ORCHESTRATOR_MODE: A\n",
            "ORCHESTRATOR_MODE: A\nCONTROL_ISSUE: 1\nCONTROL_ISSUE: 2",
            "ORCHESTRATOR_MODE: A\nCONTROL_ISSUE: 0",
            "ORCHESTRATOR_MODE: B\nCONTROL_ISSUE: 1",
            "ORCHESTRATOR_MODE: A\nCONTROL_ISSUE: 1; rm -rf .",
        ]:
            with self.subTest(body=body):
                with self.assertRaises(MODULE.ClosedGate):
                    MODULE.make_intent(pr(body=body), MAIN_SHA)

    def test_non_mode_a_pr_is_ineligible(self):
        self.assertIsNone(
            MODULE.make_intent(pr(body="ORCHESTRATOR_MODE: NONE"), MAIN_SHA)
        )

    def test_missing_or_misconfigured_inbox_blocks(self):
        api = FakeAPI()
        with self.assertRaisesRegex(MODULE.ClosedGate, "INVALID_INBOX_ISSUE"):
            MODULE.validate_inbox(api, 1)

    def test_pagination_error_blocks(self):
        api = FakeAPI()
        api.page_limit = True
        with self.assertRaisesRegex(MODULE.ClosedGate, "PAGINATION_LIMIT"):
            MODULE.reconcile(api, 99, MAIN_SHA)

    def test_complete_api_response_beyond_old_two_mb_limit(self):
        api = MODULE.GitHubAPI("test-token-not-real")
        raw = b'{"data":"' + b"a" * 2_200_000 + b'"}'
        with patch.object(
            MODULE.urllib.request, "urlopen", return_value=io.BytesIO(raw)
        ):
            result = api.request("GET", "/issues/99")
        self.assertEqual(len(result["data"]), 2_200_000)

    def test_invalid_or_oversize_response_fails_closed(self):
        api = MODULE.GitHubAPI("test-token-not-real")
        for raw, reason in [
            (b'{"data":', "INVALID_API_RESPONSE"),
            (b"x" * (MODULE.MAX_RESPONSE_BYTES + 100), "API_RESPONSE_TOO_LARGE"),
        ]:
            with self.subTest(reason=reason):
                with patch.object(
                    MODULE.urllib.request, "urlopen", return_value=io.BytesIO(raw)
                ):
                    with self.assertRaisesRegex(MODULE.ClosedGate, reason):
                        api.request("GET", "/issues/99")

    def test_pagination_complete_after_2000_records(self):
        api = MODULE.GitHubAPI("test-token-not-real")
        total = 2_017

        def fake_request(method, endpoint, data=None):
            self.assertEqual(method, "GET")
            page = int(endpoint.rsplit("page=", 1)[1])
            start = (page - 1) * MODULE.PAGE_SIZE
            return [
                {"id": index}
                for index in range(start, min(start + MODULE.PAGE_SIZE, total))
            ]

        api.request = fake_request
        records = api.pages("/issues/99/comments")
        self.assertEqual(len(records), total)
        self.assertEqual(records[-1]["id"], total - 1)

    def test_inbox_page_budget_is_strictly_bounded(self):
        api = MODULE.GitHubAPI("test-token-not-real")
        total = MODULE.MAX_LIST_ITEMS + MODULE.PAGE_SIZE
        pages_seen = []

        def fake_request(method, endpoint, data=None):
            self.assertEqual(method, "GET")
            page = int(endpoint.rsplit("page=", 1)[1])
            pages_seen.append(page)
            start = (page - 1) * MODULE.PAGE_SIZE
            return [
                {"id": index}
                for index in range(start, min(start + MODULE.PAGE_SIZE, total))
            ]

        api.request = fake_request
        with self.assertRaisesRegex(
            MODULE.ClosedGate, "INBOX_CAPACITY_SAFETY_GATE"
        ):
            api.pages("/issues/99/comments")
        self.assertEqual(MODULE.PAGE_SIZE, 100)
        self.assertLessEqual(len(pages_seen), 51)

    def test_exact_multiple_page_size_requires_empty_final_page(self):
        api = MODULE.GitHubAPI("test-token-not-real")
        total = MODULE.PAGE_SIZE * 3
        requested = []

        def fake_request(method, endpoint, data=None):
            page = int(endpoint.rsplit("page=", 1)[1])
            requested.append(page)
            start = (page - 1) * MODULE.PAGE_SIZE
            return [
                {"id": index}
                for index in range(start, min(start + MODULE.PAGE_SIZE, total))
            ]

        api.request = fake_request
        self.assertEqual(len(api.pages("/issues/99/comments")), total)
        self.assertEqual(requested[-1], 4)

    def test_ingest_uses_actual_main_source_sha_not_event_sha(self):
        fake = FakeAPI()
        env = {
            "GITHUB_REPOSITORY": MODULE.REPOSITORY,
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_SHA": SHA_A,  # Event snapshot, potentially stale.
            "MODE_A_SOURCE_SHA": MAIN_SHA,  # Commit actually checked out.
            "GITHUB_EVENT_NAME": "schedule",
            "MODE_A_INBOX_ISSUE": "99",
            "MODE_A_INTAKE_ENABLED": "true",
            "GH_TOKEN": "fake",
        }
        with (
            patch.dict(MODULE.os.environ, env, clear=True),
            patch.object(sys, "argv", ["mode_a_inbox.py", "intake"]),
            patch.object(MODULE, "GitHubAPI", return_value=fake),
            patch("builtins.print"),
        ):
            self.assertEqual(MODULE.main(), 0)
        self.assertEqual(fake.posts, 1)
        stored = MODULE.parse_comment(fake.comments[0])
        self.assertEqual(stored["main_source_sha"], MAIN_SHA)

    def test_real_json_roundtrip(self):
        item = MODULE.make_intent(pr(), MAIN_SHA)
        assert item
        raw = MODULE.serialize_intent(item)
        self.assertEqual(MODULE.parse_comment({"body": raw, "user": BOT}), item)
        self.assertEqual(json.loads(raw.split("\n", 1)[1])["state"], "PENDING")


if __name__ == "__main__":
    unittest.main()
