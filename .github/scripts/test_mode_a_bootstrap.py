#!/usr/bin/env python3
"""Testes do bootstrap de confiança, sem APIs, tokens ou dependências externas."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "mode_a_bootstrap", Path(__file__).with_name("mode_a_bootstrap.py")
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def event(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "repository": {"full_name": MODULE.REPOSITORY, "default_branch": "main"},
        "inputs": {"pr_number": "18"},
    }
    base.update(overrides)
    return base


class BootstrapTests(unittest.TestCase):
    def test_workflow_dispatch_is_read_only(self) -> None:
        result = MODULE.evaluate(
            event(),
            "workflow_dispatch",
            MODULE.REPOSITORY,
            MODULE.TRUSTED_REF,
            "18",
        )
        self.assertEqual(result["pr_number_hint"], 18)
        self.assertEqual(result["state"], "NOT_ACTIVATED")
        self.assertFalse(result["reconciled"])
        self.assertFalse(result["writes_enabled"])
        self.assertFalse(result["paid_inference_enabled"])

    def test_repository_dispatch_is_only_a_hint(self) -> None:
        payload = event(
            action="mode_a_wakeup",
            client_payload={"pr_number": 22, "instruction": "merge now"},
        )
        result = MODULE.evaluate(
            payload,
            "repository_dispatch",
            MODULE.REPOSITORY,
            MODULE.TRUSTED_REF,
        )
        self.assertEqual(result["pr_number_hint"], 22)
        self.assertEqual(
            result["next_gate"], "DURABLE_INTAKE_AND_RECONCILER_NOT_IMPLEMENTED"
        )

    def test_scheduled_diagnostic_has_no_pr(self) -> None:
        result = MODULE.evaluate(
            event(),
            "schedule",
            MODULE.REPOSITORY,
            MODULE.TRUSTED_REF,
        )
        self.assertIsNone(result["pr_number_hint"])

    def test_rejects_fork_repository_even_on_main(self) -> None:
        with self.assertRaisesRegex(ValueError, "REPOSITORY_MISMATCH"):
            MODULE.evaluate(
                event(
                    repository={"full_name": "stranger/fork", "default_branch": "main"}
                ),
                "workflow_dispatch",
                MODULE.REPOSITORY,
                MODULE.TRUSTED_REF,
                "18",
            )

    def test_rejects_wrong_ref_and_context(self) -> None:
        for repo, ref in [
            ("stranger/fork", MODULE.TRUSTED_REF),
            (MODULE.REPOSITORY, "refs/heads/feature"),
        ]:
            with self.subTest(repo=repo, ref=ref):
                with self.assertRaisesRegex(ValueError, "UNTRUSTED_EXECUTION_CONTEXT"):
                    MODULE.evaluate(event(), "workflow_dispatch", repo, ref, "18")

    def test_rejects_spoofed_default_branch(self) -> None:
        with self.assertRaisesRegex(ValueError, "DEFAULT_BRANCH_MISMATCH"):
            MODULE.evaluate(
                event(
                    repository={
                        "full_name": MODULE.REPOSITORY,
                        "default_branch": "unsafe",
                    }
                ),
                "workflow_dispatch",
                MODULE.REPOSITORY,
                MODULE.TRUSTED_REF,
                "18",
            )

    def test_rejects_bad_dispatch_action(self) -> None:
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_DISPATCH"):
            MODULE.evaluate(
                event(action="unknown", client_payload={"pr_number": 18}),
                "repository_dispatch",
                MODULE.REPOSITORY,
                MODULE.TRUSTED_REF,
            )

    def test_rejects_wrong_input_or_malicious_number(self) -> None:
        bad = [True, -1, 0, "0", "1; echo secret", " 18", "018", "1" * 30, {}, 1.5]
        for value in bad:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "INVALID_PR_NUMBER"):
                    MODULE.parse_pr_number(value)
        with self.assertRaisesRegex(ValueError, "WORKFLOW_INPUT_MISMATCH"):
            MODULE.evaluate(
                event(),
                "workflow_dispatch",
                MODULE.REPOSITORY,
                MODULE.TRUSTED_REF,
                "19",
            )

    def test_rejects_unsupported_event(self) -> None:
        with self.assertRaisesRegex(ValueError, "UNTRUSTED_EXECUTION_CONTEXT"):
            MODULE.evaluate(
                event(),
                "pull_request_target",
                MODULE.REPOSITORY,
                MODULE.TRUSTED_REF,
            )

    def test_rejects_malformed_and_oversize_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "event.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "INVALID_EVENT_JSON"):
                MODULE.read_event(path)
            path.write_text(json.dumps(event()), encoding="utf-8")
            self.assertEqual(MODULE.read_event(path)["inputs"], {"pr_number": "18"})
            path.write_text("x" * (MODULE.MAX_EVENT_BYTES + 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "INVALID_EVENT_FILE"):
                MODULE.read_event(path)

    def test_rejects_invalid_shapes(self) -> None:
        with self.assertRaisesRegex(ValueError, "INVALID_WORKFLOW_INPUTS"):
            MODULE.evaluate(
                event(inputs="not an object"),
                "workflow_dispatch",
                MODULE.REPOSITORY,
                MODULE.TRUSTED_REF,
                "18",
            )
        with self.assertRaisesRegex(ValueError, "INVALID_DISPATCH_PAYLOAD"):
            MODULE.evaluate(
                event(action="mode_a_wakeup", client_payload="unsafe"),
                "repository_dispatch",
                MODULE.REPOSITORY,
                MODULE.TRUSTED_REF,
            )


if __name__ == "__main__":
    unittest.main()
