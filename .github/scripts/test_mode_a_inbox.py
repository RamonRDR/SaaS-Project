#!/usr/bin/env python3
"""Testes de ingressos idempotentes e reconstrução de eventos sem API real."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
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

    def request(self, method: str, endpoint: str, data: dict | None = None):
        if method == "POST" and endpoint == "/issues/99/comments":
            assert data and "body" in data
            self.posts += 1
            self.comments.append({"body": data["body"], "user": BOT})
            if self.write_then_timeout:
                self.write_then_timeout = False
                raise MODULE.ClosedGate("GITHUB_API_UNCERTAIN")
            return self.comments[-1]
        if method == "GET" and endpoint == "/issues/99":
            return {"state": "open", "body": "MODE_A_INBOX_V1\nsomente intents"}
        if method == "GET" and endpoint == "/issues/1":
            return {
                "state": "open" if self.control_open else "closed",
                "body": "Issue de controle",
            }
        if method == "GET" and endpoint.startswith("/pulls/"):
            return self.prs[int(endpoint.rsplit("/", 1)[1])]
        raise AssertionError(f"unexpected API path: {method} {endpoint}")

    def pages(self, path: str):
        if path.startswith("/issues/99/comments"):
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
        with self.assertRaisesRegex(MODULE.ClosedGate, "INVALID_INBOX_JSON|MODIFIED_INBOX_RECORD"):
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

    def test_real_json_roundtrip(self):
        item = MODULE.make_intent(pr(), MAIN_SHA)
        assert item
        raw = MODULE.serialize_intent(item)
        self.assertEqual(MODULE.parse_comment({"body": raw, "user": BOT}), item)
        self.assertEqual(json.loads(raw.split("\n", 1)[1])["state"], "PENDING")


if __name__ == "__main__":
    unittest.main()
