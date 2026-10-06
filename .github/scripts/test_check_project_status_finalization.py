#!/usr/bin/env python3
"""Testes unitários do contrato determinístico GOV-02."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from check_project_status_finalization import (  # noqa: E402
    BLOCK_BEGIN,
    BLOCK_END,
    GovernanceError,
    STATUS_PATH,
    evaluate,
    parse_markers,
)


def gov_block(*markers: str) -> str:
    return "\n".join((BLOCK_BEGIN, *markers, BLOCK_END))


class Gov02Tests(unittest.TestCase):
    def test_legacy_base_without_block_is_allowed(self) -> None:
        head = gov_block(
            "<!-- GOV:PHASE-0-F:active -->",
            "<!-- GOV:PHASE-0-G:planned -->",
        )
        result = evaluate("# legado", head, [STATUS_PATH, "AGENTS.md"])
        self.assertFalse(result.applicable)

    def test_head_requires_machine_block(self) -> None:
        with self.assertRaises(GovernanceError):
            parse_markers("# sem bloco")

    def test_duplicate_phase_fails(self) -> None:
        content = gov_block(
            "<!-- GOV:PHASE-0-F:active -->",
            "<!-- GOV:PHASE-0-F:completed -->",
        )
        with self.assertRaises(GovernanceError):
            parse_markers(content)

    def test_invalid_marker_fails(self) -> None:
        content = gov_block("<!-- GOV:PHASE-0-F:done -->")
        with self.assertRaises(GovernanceError):
            parse_markers(content)

    def test_marker_outside_reserved_block_fails(self) -> None:
        content = "\n".join(
            (
                gov_block("<!-- GOV:PHASE-0-F:active -->"),
                "<!-- GOV:PHASE-0-G:planned -->",
            )
        )
        with self.assertRaises(GovernanceError):
            parse_markers(content)

    def test_active_to_completed_requires_exclusive_status_file(self) -> None:
        base = gov_block("<!-- GOV:PHASE-0-F:active -->")
        head = gov_block("<!-- GOV:PHASE-0-F:completed -->")

        result = evaluate(base, head, [STATUS_PATH])
        self.assertTrue(result.applicable)
        self.assertEqual(("PHASE-0-F",), result.newly_completed)

        with self.assertRaises(GovernanceError):
            evaluate(base, head, [STATUS_PATH, "AGENTS.md"])

    def test_completed_state_cannot_regress(self) -> None:
        base = gov_block("<!-- GOV:PHASE-0-E:completed -->")
        head = gov_block("<!-- GOV:PHASE-0-E:active -->")
        with self.assertRaises(GovernanceError):
            evaluate(base, head, [STATUS_PATH])

    def test_existing_marker_cannot_be_removed(self) -> None:
        base = gov_block(
            "<!-- GOV:PHASE-0-F:active -->",
            "<!-- GOV:PHASE-0-G:planned -->",
        )
        head = gov_block("<!-- GOV:PHASE-0-G:planned -->")
        with self.assertRaises(GovernanceError):
            evaluate(base, head, [STATUS_PATH])

    def test_remove_old_completion_cannot_compensate_new_completion(self) -> None:
        base = gov_block(
            "<!-- GOV:PHASE-0-E:completed -->",
            "<!-- GOV:PHASE-0-F:active -->",
        )
        head = gov_block(
            "<!-- GOV:PHASE-0-E:active -->",
            "<!-- GOV:PHASE-0-F:completed -->",
        )
        with self.assertRaises(GovernanceError):
            evaluate(base, head, [STATUS_PATH, "AGENTS.md"])

    def test_non_completion_transition_is_not_gov02_finalization(self) -> None:
        base = gov_block("<!-- GOV:PHASE-0-G:planned -->")
        head = gov_block("<!-- GOV:PHASE-0-G:active -->")
        result = evaluate(base, head, [STATUS_PATH, "AGENTS.md"])
        self.assertFalse(result.applicable)

    def test_markdown_content_does_not_change_machine_state(self) -> None:
        base = "\n".join(
            (
                "# Status",
                "```md",
                "### PHASE-FAKE",
                "Concluída.",
                "```",
                gov_block("<!-- GOV:PHASE-0-F:active -->"),
            )
        )
        head = base.replace("### PHASE-FAKE", "   ### OUTRA-FASE")
        result = evaluate(base, head, [STATUS_PATH, "AGENTS.md"])
        self.assertFalse(result.applicable)


if __name__ == "__main__":
    unittest.main()
