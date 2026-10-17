#!/usr/bin/env python3
"""Reconciliação consultiva de PR do Mode A, sem escrita no GitHub."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOSITORY = "RamonRDR/SaaS-Project"
API_ROOT = f"https://api.github.com/repos/{REPOSITORY}"
REQUIRED_CHECKS = ("governance", "secret-scan", "mode-a-reconciler")
MAX_RESPONSE_BYTES = 1_048_576
MAX_CHECKPOINT_BYTES = 16_384
SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")


class ReconcileError(Exception):
    """Representa um bloqueio conservador, sem expor resposta remota."""


EXTERNAL_BLOCKERS = frozenset({"GITHUB_UNAVAILABLE", "GITHUB_RESPONSE_TOO_LARGE"})


def failure_state(reason: str) -> str:
    """Distingue indisponibilidade externa de falha local/de confiança.

    Motivos desconhecidos exigem decisão humana e nunca falham de forma aberta.
    """
    return "BLOCKED_EXTERNAL" if reason in EXTERNAL_BLOCKERS else "HUMAN_DECISION_REQUIRED"


def canonical_digest(value: object) -> str:
    """Gera identidade reproduzível, independente da ordem de chaves JSON."""
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_sha(value: object) -> str:
    if not isinstance(value, str) or not SHA_PATTERN.fullmatch(value):
        raise ReconcileError("INVALID_SHA")
    return value


def validate_pr_number(value: object) -> int:
    if type(value) is not int or not 1 <= value <= 999_999_999:
        raise ReconcileError("INVALID_PR_NUMBER")
    return value


def read_json(path: Path) -> dict[str, Any]:
    """Aceita checkpoint local limitado, nunca autorização de operação."""
    try:
        if not path.is_file() or path.stat().st_size > MAX_CHECKPOINT_BYTES:
            raise ReconcileError("INVALID_CHECKPOINT")
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReconcileError("INVALID_CHECKPOINT") from exc
    if not isinstance(value, dict):
        raise ReconcileError("INVALID_CHECKPOINT")
    return value


def get_json(path: str) -> dict[str, Any]:
    """Consulta somente endpoints predefinidos de um repositório público."""
    if not re.fullmatch(
        r"(?:/pulls/[1-9][0-9]{0,8}|/commits/[0-9a-f]{40}/check-runs\?per_page=100)",
        path,
    ):
        raise ReconcileError("INVALID_API_PATH")
    request = Request(
        API_ROOT + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "saas-mode-a-readonly-reconciler/1",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urlopen(request, timeout=12) as response:
            if response.status != 200:
                raise ReconcileError("GITHUB_UNAVAILABLE")
            data = response.read(MAX_RESPONSE_BYTES + 1)
        if len(data) > MAX_RESPONSE_BYTES:
            raise ReconcileError("GITHUB_RESPONSE_TOO_LARGE")
        result = json.loads(data)
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReconcileError("GITHUB_UNAVAILABLE") from exc
    if not isinstance(result, dict):
        raise ReconcileError("INVALID_GITHUB_RESPONSE")
    return result


def check_summary(payload: dict[str, Any], head_sha: str) -> dict[str, str]:
    """Nunca trata checks ausentes, incompletos ou ambíguos como sucesso."""
    checks = payload.get("check_runs")
    if not isinstance(checks, list) or type(payload.get("total_count")) is not int:
        raise ReconcileError("INVALID_CHECKS_RESPONSE")
    if payload["total_count"] != len(checks):
        raise ReconcileError("INCOMPLETE_CHECKS_RESPONSE")
    results: dict[str, str] = {}
    for name in REQUIRED_CHECKS:
        matched = [check for check in checks if isinstance(check, dict) and check.get("name") == name]
        if len(matched) > 1:
            raise ReconcileError("AMBIGUOUS_CHECK")
        if not matched:
            results[name] = "missing"
            continue
        check = matched[0]
        app = check.get("app")
        if (
            check.get("head_sha") != head_sha
            or not isinstance(app, dict)
            or app.get("slug") != "github-actions"
        ):
            raise ReconcileError("UNTRUSTED_CHECK")
        if check.get("status") != "completed":
            results[name] = "pending"
        elif check.get("conclusion") == "success":
            results[name] = "success"
        else:
            results[name] = "failed"
    return results


def reconcile(
    pr_number: int,
    expected_head: str,
    fetch: Callable[[str], dict[str, Any]] = get_json,
    checkpoint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Produz decisão consultiva sem chamar endpoints de escrita."""
    validate_pr_number(pr_number)
    validate_sha(expected_head)
    pr = fetch(f"/pulls/{pr_number}")
    head = pr.get("head")
    base = pr.get("base")
    if not isinstance(head, dict) or not isinstance(base, dict):
        raise ReconcileError("INVALID_PR_RESPONSE")
    actual_head = validate_sha(head.get("sha"))
    head_repo = head.get("repo")
    base_repo = base.get("repo")
    if (
        not isinstance(head_repo, dict)
        or head_repo.get("full_name") != REPOSITORY
        or not isinstance(base_repo, dict)
        or base_repo.get("full_name") != REPOSITORY
        or base.get("ref") != "main"
        or pr.get("number") != pr_number
    ):
        raise ReconcileError("PR_OUTSIDE_TRUSTED_SCOPE")

    checks: dict[str, str] = {}
    if actual_head != expected_head:
        state, reason = "HUMAN_DECISION_REQUIRED", "HEAD_DIVERGED"
    elif pr.get("state") != "open" or pr.get("merged_at") is not None:
        state, reason = "HUMAN_DECISION_REQUIRED", "PR_NOT_OPEN"
    elif pr.get("draft") is True:
        state, reason = "IMPLEMENTING", "PR_DRAFT_NO_AUTOMATIC_WRITE"
    elif pr.get("draft") is False:
        payload = fetch(f"/commits/{actual_head}/check-runs?per_page=100")
        checks = check_summary(payload, actual_head)
        if all(value == "success" for value in checks.values()):
            state, reason = "REVIEWING", "WAITING_CODEX_INDEPENDENT_REVIEW"
        else:
            state, reason = "REVIEWING", "CI_VALIDATION_REQUIRED"
    else:
        raise ReconcileError("INVALID_PR_RESPONSE")

    evidence = {
        "repository": REPOSITORY,
        "pr_number": pr_number,
        "head_sha": actual_head,
        "expected_head": expected_head,
        "state": state,
        "reason": reason,
        "checks": checks,
    }
    decision_id = canonical_digest({"schema": "MODE_A_V2_DECISION_1", **evidence})
    replay = False
    if checkpoint is not None:
        if (
            checkpoint.get("repository") != REPOSITORY
            or checkpoint.get("pr_number") != pr_number
            or checkpoint.get("head_sha") != actual_head
        ):
            raise ReconcileError("CHECKPOINT_SCOPE_MISMATCH")
        replay = checkpoint.get("decision_id") == decision_id

    return {
        **evidence,
        "decision_id": decision_id,
        "replayed_decision": replay,
        "writes_enabled": False,
        "paid_inference_enabled": False,
        "ready_for_merge": False,
        "checkpoint_persisted": False,
        "note": "Saída consultiva; CODEX-01, autorização humana e persistência permanecem externos.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reconciliar PR sem escrita ou API paga")
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args(argv)
    try:
        previous = read_json(args.checkpoint) if args.checkpoint else None
        decision = reconcile(args.pr_number, args.expected_head, checkpoint=previous)
    except ReconcileError as exc:
        reason = str(exc)
        print(json.dumps({"state": failure_state(reason), "reason": reason, "writes_enabled": False,
                          "paid_inference_enabled": False, "ready_for_merge": False}, sort_keys=True))
        return 2
    print(json.dumps(decision, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
