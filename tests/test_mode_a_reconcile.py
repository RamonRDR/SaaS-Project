#!/usr/bin/env python3
"""Testes negativos e de estabilidade para o reconciliador consultivo."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "mode_a_reconcile.py"
SPEC = importlib.util.spec_from_file_location("mode_a_reconcile", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SHA = "a" * 40
NEW_SHA = "b" * 40


def pr(*, sha=SHA, draft=False, state="open", repo=MODULE.REPOSITORY):
    return {"number": 13, "state": state, "draft": draft, "merged_at": None,
            "head": {"sha": sha, "repo": {"full_name": repo}},
            "base": {"ref": "main", "repo": {"full_name": MODULE.REPOSITORY}}}


def checks(*, governance="success", secret="success", sha=SHA):
    def check(name, result):
        return {"name": name, "head_sha": sha,
                "app": {"slug": "github-actions"}, "status": "completed", "conclusion": result}
    return {"total_count": 2, "check_runs": [check("governance", governance), check("secret-scan", secret)]}


def transport(pr_payload=None, check_payload=None):
    responses = {"/pulls/13": pr_payload or pr(),
                 f"/commits/{SHA}/check-runs?per_page=100": check_payload or checks()}
    requested = []

    def fetch(path):
        requested.append(path)
        return responses[path]
    return fetch, requested


class ReconcilerTests(unittest.TestCase):
    def test_read_only_path_and_expected_checks(self):
        fetch, requested = transport()
        value = MODULE.reconcile(13, SHA, fetch)
        self.assertEqual(requested, ["/pulls/13", f"/commits/{SHA}/check-runs?per_page=100"])
        self.assertEqual(value["reason"], "WAITING_CODEX_INDEPENDENT_REVIEW")
        self.assertEqual(value["state"], "REVIEWING")
        self.assertFalse(value["ready_for_merge"])
        self.assertFalse(value["writes_enabled"])
        self.assertFalse(value["checkpoint_persisted"])

    def test_repeat_is_stable_and_checkpoint_is_not_authorization(self):
        fetch, _ = transport()
        first = MODULE.reconcile(13, SHA, fetch)
        again = MODULE.reconcile(13, SHA, fetch, first)
        self.assertEqual(first["decision_id"], again["decision_id"])
        self.assertTrue(again["replayed_decision"])
        self.assertFalse(again["ready_for_merge"])

    def test_head_divergence_fails_closed_without_check_call(self):
        fetch, requested = transport(pr_payload=pr(sha=NEW_SHA))
        value = MODULE.reconcile(13, SHA, fetch)
        self.assertEqual(value["reason"], "HEAD_DIVERGED")
        self.assertEqual(len(requested), 1)

    def test_fork_rejected(self):
        fetch, _ = transport(pr_payload=pr(repo="unknown/fork"))
        with self.assertRaisesRegex(MODULE.ReconcileError, "PR_OUTSIDE_TRUSTED_SCOPE"):
            MODULE.reconcile(13, SHA, fetch)

    def test_draft_does_not_claim_review(self):
        fetch, requested = transport(pr_payload=pr(draft=True))
        value = MODULE.reconcile(13, SHA, fetch)
        self.assertEqual(value["state"], "IMPLEMENTING")
        self.assertEqual(len(requested), 1)

    def test_closed_pr_does_not_progress(self):
        fetch, _ = transport(pr_payload=pr(state="closed"))
        self.assertEqual(MODULE.reconcile(13, SHA, fetch)["reason"], "PR_NOT_OPEN")

    def test_fail_and_pending_checks_do_not_progress(self):
        for status in ("failure", "cancelled", "timed_out"):
            with self.subTest(status=status):
                fetch, _ = transport(check_payload=checks(secret=status))
                self.assertEqual(MODULE.reconcile(13, SHA, fetch)["reason"], "CI_VALIDATION_REQUIRED")

    def test_missing_check_does_not_progress(self):
        payload = {"total_count": 1, "check_runs": checks()["check_runs"][:1]}
        fetch, _ = transport(check_payload=payload)
        self.assertEqual(MODULE.reconcile(13, SHA, fetch)["checks"]["secret-scan"], "missing")

    def test_partial_or_duplicate_checks_rejected(self):
        partial = {"total_count": 1000, "check_runs": checks()["check_runs"]}
        duplicate = {"total_count": 3, "check_runs": checks()["check_runs"] + checks()["check_runs"][:1]}
        for payload in (partial, duplicate):
            with self.subTest(payload=payload):
                fetch, _ = transport(check_payload=payload)
                with self.assertRaises(MODULE.ReconcileError):
                    MODULE.reconcile(13, SHA, fetch)

    def test_wrong_head_or_app_check_rejected(self):
        payload = checks(sha=NEW_SHA)
        fetch, _ = transport(check_payload=payload)
        with self.assertRaisesRegex(MODULE.ReconcileError, "UNTRUSTED_CHECK"):
            MODULE.reconcile(13, SHA, fetch)
        payload = checks()
        payload["check_runs"][0]["app"]["slug"] = "unknown"
        fetch, _ = transport(check_payload=payload)
        with self.assertRaisesRegex(MODULE.ReconcileError, "UNTRUSTED_CHECK"):
            MODULE.reconcile(13, SHA, fetch)

    def test_checkpoint_from_different_head_is_rejected(self):
        fetch, _ = transport()
        with self.assertRaisesRegex(MODULE.ReconcileError, "CHECKPOINT_SCOPE_MISMATCH"):
            MODULE.reconcile(13, SHA, fetch, {"repository": MODULE.REPOSITORY,
                                              "pr_number": 13, "head_sha": NEW_SHA})

    def test_invalid_input_fails_closed(self):
        fetch, _ = transport()
        for value in (0, True, 1_000_000_000, "13"):
            with self.subTest(value=value), self.assertRaises(MODULE.ReconcileError):
                MODULE.reconcile(value, SHA, fetch)
        with self.assertRaises(MODULE.ReconcileError):
            MODULE.reconcile(13, "HEAD", fetch)

    def test_only_two_endpoints_are_permitted(self):
        for value in ("/issues/13/comments", "/pulls/13/../secrets", "/pulls/13?x=1",
                      "/commits/" + SHA + "/check-runs?per_page=1000"):
            with self.subTest(value=value), self.assertRaisesRegex(
                MODULE.ReconcileError, "INVALID_API_PATH"
            ):
                MODULE.get_json(value)

    def test_event_instruction_is_not_an_input(self):
        fetch, requested = transport()
        value = MODULE.reconcile(13, SHA, fetch)
        self.assertEqual(value["reason"], "WAITING_CODEX_INDEPENDENT_REVIEW")
        self.assertTrue(all(path.startswith(("/pulls/", "/commits/")) for path in requested))


if __name__ == "__main__":
    unittest.main()
