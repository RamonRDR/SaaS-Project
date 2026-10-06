#!/usr/bin/env python3
"""Contrato determinístico de estados do runtime Mode A."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass


NORMAL_STATES = {
    "INIT",
    "SDD_DRAFTING",
    "SDD_READY_FOR_HUMAN_APPROVAL",
    "IMPLEMENTING",
    "REVIEWING",
    "READY_FOR_HUMAN_MERGE",
    "MERGING",
    "FINALIZING",
    "DONE",
}

INTERRUPTION_STATES = {
    "HUMAN_DECISION_REQUIRED",
    "BLOCKED_EXTERNAL",
    "LOOP_ESCALATION_REQUIRED",
}

ALL_STATES = NORMAL_STATES | INTERRUPTION_STATES

ALLOWED_TRANSITIONS = {
    "INIT": {"SDD_DRAFTING", "HUMAN_DECISION_REQUIRED", "BLOCKED_EXTERNAL"},
    "SDD_DRAFTING": {
        "SDD_READY_FOR_HUMAN_APPROVAL",
        "HUMAN_DECISION_REQUIRED",
        "BLOCKED_EXTERNAL",
        "LOOP_ESCALATION_REQUIRED",
    },
    "SDD_READY_FOR_HUMAN_APPROVAL": {
        "IMPLEMENTING",
        "HUMAN_DECISION_REQUIRED",
        "BLOCKED_EXTERNAL",
    },
    "IMPLEMENTING": {
        "REVIEWING",
        "HUMAN_DECISION_REQUIRED",
        "BLOCKED_EXTERNAL",
        "LOOP_ESCALATION_REQUIRED",
    },
    "REVIEWING": {
        "REVIEWING",
        "READY_FOR_HUMAN_MERGE",
        "HUMAN_DECISION_REQUIRED",
        "BLOCKED_EXTERNAL",
        "LOOP_ESCALATION_REQUIRED",
    },
    "READY_FOR_HUMAN_MERGE": {
        "MERGING",
        "HUMAN_DECISION_REQUIRED",
        "BLOCKED_EXTERNAL",
    },
    "MERGING": {"FINALIZING", "BLOCKED_EXTERNAL"},
    "FINALIZING": {
        "FINALIZING",
        "DONE",
        "HUMAN_DECISION_REQUIRED",
        "BLOCKED_EXTERNAL",
        "LOOP_ESCALATION_REQUIRED",
    },
    "DONE": set(),
    "HUMAN_DECISION_REQUIRED": set(),
    "BLOCKED_EXTERNAL": set(),
    "LOOP_ESCALATION_REQUIRED": set(),
}


@dataclass(frozen=True)
class Control:
    mode: str
    phase: str
    objective: str


def parse_control(text: str) -> Control:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^([A-Z_]+):\s*(.+?)\s*$", line)
        if match:
            fields[match.group(1)] = match.group(2)

    mode = fields.get("ORCHESTRATOR_MODE", "")
    phase = fields.get("PHASE", "")
    objective = fields.get("OBJECTIVE", "")

    if mode != "A":
        raise ValueError("ORCHESTRATOR_MODE deve ser A")
    if not re.fullmatch(r"PHASE-[A-Z0-9-]+", phase):
        raise ValueError("PHASE inválida")
    if not objective:
        raise ValueError("OBJECTIVE é obrigatório")

    return Control(mode=mode, phase=phase, objective=objective)


def branch_for_phase(phase: str) -> str:
    normalized = phase.lower()
    return f"orchestrator/{normalized}"


def validate_transition(current: str, target: str) -> None:
    if current not in ALL_STATES:
        raise ValueError(f"estado atual inválido: {current}")
    if target not in ALL_STATES:
        raise ValueError(f"estado alvo inválido: {target}")
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"transição inválida: {current} -> {target}")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    parse_cmd = sub.add_parser("parse-control")
    parse_cmd.add_argument("--text", required=True)

    branch_cmd = sub.add_parser("branch")
    branch_cmd.add_argument("--phase", required=True)

    transition_cmd = sub.add_parser("validate-transition")
    transition_cmd.add_argument("--current", required=True)
    transition_cmd.add_argument("--target", required=True)

    args = parser.parse_args()

    if args.command == "parse-control":
        control = parse_control(args.text)
        print(json.dumps(control.__dict__, ensure_ascii=False))
        return 0

    if args.command == "branch":
        print(branch_for_phase(args.phase))
        return 0

    validate_transition(args.current, args.target)
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
