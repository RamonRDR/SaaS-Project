#!/usr/bin/env python3
"""Diagnóstico fail-closed do primeiro bootstrap unattended, sem mutações."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Mapping


REPOSITORY = "RamonRDR/SaaS-Project"
TRUSTED_REF = "refs/heads/main"
MAX_EVENT_BYTES = 262_144
SUPPORTED_EVENTS = {"workflow_dispatch", "repository_dispatch", "schedule"}


def parse_pr_number(value: object) -> int | None:
    """Aceita somente números de PR positivos e com tamanho controlado."""
    if value is None or value == "":
        return None
    if type(value) is int and 1 <= value <= 999_999_999:
        return value
    if isinstance(value, str) and re.fullmatch(r"[1-9][0-9]{0,8}", value):
        return int(value)
    raise ValueError("INVALID_PR_NUMBER")


def read_event(path: Path) -> dict[str, Any]:
    """Lê o payload apenas como dado, impondo limite e formato estritos."""
    if not path.is_file() or path.stat().st_size > MAX_EVENT_BYTES:
        raise ValueError("INVALID_EVENT_FILE")
    try:
        event = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("INVALID_EVENT_JSON") from exc
    if not isinstance(event, dict):
        raise ValueError("INVALID_EVENT_FORMAT")
    return event


def evaluate(
    event: Mapping[str, Any],
    event_name: str,
    repository: str,
    ref: str,
    input_pr_number: object = None,
) -> dict[str, Any]:
    """Valida contexto confiável, mas não reconcilia estado do GitHub."""
    if (
        event_name not in SUPPORTED_EVENTS
        or repository != REPOSITORY
        or ref != TRUSTED_REF
    ):
        raise ValueError("UNTRUSTED_EXECUTION_CONTEXT")
    repo_data = event.get("repository")
    if not isinstance(repo_data, dict) or repo_data.get("full_name") != REPOSITORY:
        raise ValueError("REPOSITORY_MISMATCH")
    if repo_data.get("default_branch") != "main":
        raise ValueError("DEFAULT_BRANCH_MISMATCH")

    if event_name == "repository_dispatch":
        if event.get("action") != "mode_a_wakeup":
            raise ValueError("UNSUPPORTED_DISPATCH")
        payload = event.get("client_payload", {})
        if not isinstance(payload, dict):
            raise ValueError("INVALID_DISPATCH_PAYLOAD")
        pr_number = parse_pr_number(payload.get("pr_number"))
    elif event_name == "workflow_dispatch":
        inputs = event.get("inputs", {})
        if inputs is None:
            inputs = {}
        if not isinstance(inputs, dict):
            raise ValueError("INVALID_WORKFLOW_INPUTS")
        # O payload não é autoridade sobre o PR, mesmo quando o número coincide.
        pr_number = parse_pr_number(input_pr_number)
        payload_number = parse_pr_number(inputs.get("pr_number"))
        if pr_number != payload_number:
            raise ValueError("WORKFLOW_INPUT_MISMATCH")
    else:
        pr_number = None

    return {
        "diagnostic": "MODE_A_BOOTSTRAP_ONLY",
        "state": "NOT_ACTIVATED",
        "event": event_name,
        "repository": REPOSITORY,
        "ref": TRUSTED_REF,
        "pr_number_hint": pr_number,
        "reconciled": False,
        "writes_enabled": False,
        "paid_inference_enabled": False,
        "next_gate": "DURABLE_INTAKE_AND_RECONCILER_NOT_IMPLEMENTED",
    }


def main() -> int:
    """Produz telemetria segura; nenhuma falha habilita execução alternativa."""
    try:
        raw_path = os.environ.get("GITHUB_EVENT_PATH", "")
        if not raw_path:
            raise ValueError("MISSING_EVENT_PATH")
        event = read_event(Path(raw_path))
        result = evaluate(
            event=event,
            event_name=os.environ.get("GITHUB_EVENT_NAME", ""),
            repository=os.environ.get("GITHUB_REPOSITORY", ""),
            ref=os.environ.get("GITHUB_REF", ""),
            input_pr_number=os.environ.get("INPUT_PR_NUMBER", ""),
        )
    except ValueError as exc:
        # Somente códigos conhecidos, nunca imprime payload, token ou exceção bruta.
        allowed = {
            "INVALID_PR_NUMBER",
            "INVALID_EVENT_FILE",
            "INVALID_EVENT_JSON",
            "INVALID_EVENT_FORMAT",
            "UNTRUSTED_EXECUTION_CONTEXT",
            "REPOSITORY_MISMATCH",
            "DEFAULT_BRANCH_MISMATCH",
            "UNSUPPORTED_DISPATCH",
            "INVALID_DISPATCH_PAYLOAD",
            "INVALID_WORKFLOW_INPUTS",
            "WORKFLOW_INPUT_MISMATCH",
            "MISSING_EVENT_PATH",
        }
        reason = str(exc)
        print(
            json.dumps(
                {
                    "diagnostic": "MODE_A_BOOTSTRAP_REJECTED",
                    "reason": reason if reason in allowed else "INVALID_INPUT",
                    "writes_enabled": False,
                    "paid_inference_enabled": False,
                },
                sort_keys=True,
            )
        )
        return 2

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
