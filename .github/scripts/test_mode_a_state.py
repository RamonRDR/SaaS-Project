#!/usr/bin/env python3
"""Testes unitários sem dependências externas para mode_a_state.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("mode_a_state.py")
SPEC = importlib.util.spec_from_file_location("mode_a_state", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def expect_error(callable_, message: str) -> None:
    try:
        callable_()
    except ValueError:
        return
    raise AssertionError(message)


def main() -> None:
    control = MODULE.parse_control(
        "ORCHESTRATOR_MODE: A\n"
        "PHASE: PHASE-0-G\n"
        "OBJECTIVE: Bootstrap tecnológico da fundação\n"
    )
    assert control.mode == "A"
    assert control.phase == "PHASE-0-G"
    assert MODULE.branch_for_phase(control.phase) == "orchestrator/phase-0-g"

    MODULE.validate_transition("INIT", "SDD_DRAFTING")
    MODULE.validate_transition("REVIEWING", "REVIEWING")
    MODULE.validate_transition("REVIEWING", "READY_FOR_HUMAN_MERGE")
    MODULE.validate_transition("MERGING", "FINALIZING")
    MODULE.validate_transition("FINALIZING", "DONE")

    expect_error(
        lambda: MODULE.validate_transition("INIT", "DONE"),
        "INIT -> DONE deveria falhar",
    )
    expect_error(
        lambda: MODULE.validate_transition("DONE", "REVIEWING"),
        "DONE não pode reabrir",
    )
    expect_error(
        lambda: MODULE.parse_control(
            "ORCHESTRATOR_MODE: B\nPHASE: PHASE-0-G\nOBJECTIVE: x"
        ),
        "modo diferente de A deveria falhar",
    )
    expect_error(
        lambda: MODULE.parse_control(
            "ORCHESTRATOR_MODE: A\nPHASE: 0G\nOBJECTIVE: x"
        ),
        "fase inválida deveria falhar",
    )

    print("mode_a_state: OK")


if __name__ == "__main__":
    main()
