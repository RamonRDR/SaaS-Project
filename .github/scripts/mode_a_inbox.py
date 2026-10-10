#!/usr/bin/env python3
"""Inbox de intenções do Mode A: persistência separada de orçamento e dispatch."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

REPOSITORY = "RamonRDR/SaaS-Project"
INBOX_MARKER = "MODE_A_INBOX_V1"
COMMENT_PREFIX = "MODE_A_INBOX_V1\n"
BOT_LOGIN = "github-actions[bot]"
MAX_PAGES = 20
PAGE_SIZE = 100
MAX_BODY_BYTES = 16384
SHA_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
INT_PATTERN = re.compile(r"[1-9][0-9]{0,8}\Z")


class ClosedGate(ValueError):
    """Uma condição não comprovada impede alteração e processamento."""


def positive_number(value: object) -> int:
    if type(value) is int and 1 <= value <= 999999999:
        return value
    if isinstance(value, str) and INT_PATTERN.fullmatch(value):
        return int(value)
    raise ClosedGate("INVALID_NUMBER")


def canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def parse_control(body: object) -> int | None:
    """Requer exatamente um Mode A e um CONTROL_ISSUE, sem inferir texto."""
    if not isinstance(body, str) or len(body.encode("utf-8")) > MAX_BODY_BYTES:
        raise ClosedGate("INVALID_PR_BODY")
    modes = re.findall(r"^ORCHESTRATOR_MODE: ([A-Z]+)$", body, re.MULTILINE)
    issues = re.findall(r"^CONTROL_ISSUE: ([^\r\n]+)$", body, re.MULTILINE)
    if not modes and not issues:
        return None
    if modes == ["NONE"] and len(issues) <= 1:
        return None
    if modes != ["A"] or len(issues) != 1:
        raise ClosedGate("INVALID_CONTROL_FIELDS")
    return positive_number(issues[0])


def make_intent(pr: dict[str, Any], main_sha: str) -> dict[str, Any] | None:
    if not isinstance(pr, dict):
        raise ClosedGate("INVALID_PR")
    base = pr.get("base")
    head = pr.get("head")
    if not isinstance(base, dict) or not isinstance(head, dict):
        raise ClosedGate("INVALID_PR_REFS")
    if pr.get("state") != "open" or base.get("ref") != "main":
        return None
    base_repo = base.get("repo")
    if not isinstance(base_repo, dict) or base_repo.get("full_name") != REPOSITORY:
        raise ClosedGate("INVALID_PR_BASE")
    control_issue = parse_control(pr.get("body") or "")
    if control_issue is None:
        return None
    number = positive_number(pr.get("number"))
    head_sha = head.get("sha")
    if (
        not isinstance(head_sha, str)
        or not SHA_PATTERN.fullmatch(head_sha)
        or not SHA_PATTERN.fullmatch(main_sha)
    ):
        raise ClosedGate("INVALID_SHA")
    operation_key = f"{REPOSITORY}/PR/{number}/HEAD/{head_sha}/CODEX_01/0"
    request_id = hashlib.sha256(operation_key.encode("ascii")).hexdigest()
    return {
        "schema": "mode_a_inbox_v1",
        "state": "PENDING",
        "repository": REPOSITORY,
        "pr_number": number,
        "head_sha": head_sha,
        "base_ref": "main",
        "control_issue": control_issue,
        "operation_kind": "CODEX_01",
        "authorized_attempt": 0,
        "operation_key": operation_key,
        "request_id": request_id,
        "main_source_sha": main_sha,
    }


def verify_request_context(saved: dict[str, Any], current: dict[str, Any]) -> None:
    """Uma operation key não pode ser reutilizada com outro contexto."""
    material = (
        "repository",
        "pr_number",
        "head_sha",
        "base_ref",
        "control_issue",
        "operation_kind",
        "authorized_attempt",
        "operation_key",
        "request_id",
    )
    if any(saved[key] != current[key] for key in material):
        raise ClosedGate("REQUEST_CONTEXT_CHANGED")


def serialize_intent(intent: dict[str, Any]) -> str:
    return COMMENT_PREFIX + canonical(intent)


def parse_comment(comment: dict[str, Any]) -> dict[str, Any] | None:
    author = comment.get("user")
    if not isinstance(author, dict):
        raise ClosedGate("INVALID_COMMENT_AUTHOR")
    if author.get("login") != BOT_LOGIN or author.get("id") != 41898282:
        # Comentários de terceiros não são autoridade; nunca incorporá-los ao inbox.
        return None
    body = comment.get("body")
    if not isinstance(body, str) or not body.startswith(COMMENT_PREFIX):
        return None
    if len(body.encode("utf-8")) > 4096:
        raise ClosedGate("OVERSIZE_INBOX_RECORD")
    try:
        intent = json.loads(body[len(COMMENT_PREFIX) :])
    except json.JSONDecodeError as exc:
        raise ClosedGate("INVALID_INBOX_JSON") from exc
    if not isinstance(intent, dict) or serialize_intent(intent) != body:
        raise ClosedGate("MODIFIED_INBOX_RECORD")
    required = {
        "schema",
        "state",
        "repository",
        "pr_number",
        "head_sha",
        "base_ref",
        "control_issue",
        "operation_kind",
        "authorized_attempt",
        "operation_key",
        "request_id",
        "main_source_sha",
    }
    if set(intent) != required:
        raise ClosedGate("INVALID_INBOX_SCHEMA")
    try:
        reconstructed = make_intent(
            {
                "state": "open",
                "number": intent["pr_number"],
                "body": (
                    f"ORCHESTRATOR_MODE: A\nCONTROL_ISSUE: {intent['control_issue']}"
                ),
                "base": {"ref": "main", "repo": {"full_name": REPOSITORY}},
                "head": {"sha": intent["head_sha"]},
            },
            intent["main_source_sha"],
        )
    except (TypeError, ValueError) as exc:
        raise ClosedGate("INVALID_INBOX_FIELDS") from exc
    if reconstructed != intent:
        raise ClosedGate("INVALID_INBOX_IDENTITY")
    return intent


class GitHubAPI:
    def __init__(self, token: str):
        if not token:
            raise ClosedGate("MISSING_GITHUB_TOKEN")
        self.token = token

    def request(self, method: str, endpoint: str, data: dict | None = None) -> Any:
        if not endpoint.startswith("/") or "//" in endpoint:
            raise ClosedGate("INVALID_API_PATH")
        url = "https://api.github.com/repos/" + REPOSITORY + endpoint
        payload = canonical(data).encode("utf-8") if data is not None else None
        request = urllib.request.Request(
            url,
            data=payload,
            method=method,
            headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "mode-a-inbox-v1",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.loads(response.read(2_000_000))
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and method == "GET" and endpoint.startswith("/issues/"):
                raise ClosedGate("ISSUE_NOT_FOUND") from exc
            raise ClosedGate("GITHUB_API_UNCERTAIN") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            # Nunca inserir URL, headers, token ou payload externo em logs.
            raise ClosedGate("GITHUB_API_UNCERTAIN") from exc

    def pages(self, path: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for page in range(1, MAX_PAGES + 1):
            separator = "&" if "?" in path else "?"
            batch = self.request(
                "GET", f"{path}{separator}per_page={PAGE_SIZE}&page={page}"
            )
            if not isinstance(batch, list) or len(batch) > PAGE_SIZE:
                raise ClosedGate("INVALID_API_PAGE")
            items.extend(batch)
            if len(batch) < PAGE_SIZE:
                return items
        raise ClosedGate("PAGINATION_LIMIT")


def validate_inbox(api: GitHubAPI, inbox_number: int) -> None:
    issue = api.request("GET", f"/issues/{inbox_number}")
    if (
        not isinstance(issue, dict)
        or issue.get("state") != "open"
        or not isinstance(issue.get("body"), str)
        or issue["body"].splitlines()[0:1] != [INBOX_MARKER]
        or "pull_request" in issue
    ):
        raise ClosedGate("INVALID_INBOX_ISSUE")


def records(api: GitHubAPI, inbox_number: int) -> list[dict[str, Any]]:
    comments = api.pages(f"/issues/{inbox_number}/comments")
    valid: list[dict[str, Any]] = []
    for comment in comments:
        item = parse_comment(comment)
        if item is not None:
            valid.append(item)
    return valid


def validate_control_issue(
    api: GitHubAPI, control_number: int, inbox_number: int
) -> None:
    """Somente issue autorada pelo dono e marcada como controle Mode A."""
    if control_number == inbox_number:
        raise ClosedGate("CONTROL_EQUALS_INBOX")
    try:
        issue = api.request("GET", f"/issues/{control_number}")
    except ClosedGate as exc:
        if str(exc) == "ISSUE_NOT_FOUND":
            raise ClosedGate("INVALID_CONTROL_ISSUE") from exc
        raise
    if not isinstance(issue, dict):
        raise ClosedGate("INVALID_CONTROL_ISSUE")
    body = issue.get("body")
    author = issue.get("user")
    if (
        issue.get("state") != "open"
        or "pull_request" in issue
        or not isinstance(body, str)
        or not isinstance(author, dict)
        or author.get("login") != "RamonRDR"
        or len(body.encode("utf-8")) > MAX_BODY_BYTES
    ):
        raise ClosedGate("INVALID_CONTROL_ISSUE")
    lines = body.splitlines()
    modes = [line for line in lines if line.startswith("ORCHESTRATOR_MODE:")]
    phases = [line for line in lines if line.startswith("PHASE:")]
    objectives = [line for line in lines if line.startswith("OBJECTIVE:")]
    if (
        modes != ["ORCHESTRATOR_MODE: A"]
        or len(phases) != 1
        or not re.fullmatch(r"PHASE: PHASE-[A-Z0-9-]+", phases[0])
        or len(objectives) != 1
        or not objectives[0].partition(":")[2].strip()
    ):
        raise ClosedGate("INVALID_CONTROL_SCHEMA")


def current_intents(
    api: GitHubAPI,
    main_sha: str,
    only: int | None = None,
    inbox_number: int = 0,
) -> list[dict]:
    if only is not None:
        candidates = [api.request("GET", f"/pulls/{only}")]
    else:
        candidates = api.pages("/pulls?state=open")
    intents: list[dict] = []
    for item in candidates:
        if not isinstance(item, dict):
            raise ClosedGate("INVALID_PR_ITEM")
        number = positive_number(item.get("number"))
        pr = api.request("GET", f"/pulls/{number}")
        try:
            intent = make_intent(pr, main_sha)
        except ClosedGate:
            # Um PR malformado não pode impedir recuperação dos demais.
            if only is not None:
                raise
            continue
        if intent is None:
            continue
        try:
            validate_control_issue(api, intent["control_issue"], inbox_number)
        except ClosedGate as exc:
            if only is not None or str(exc) == "GITHUB_API_UNCERTAIN":
                raise
            continue
        intents.append(intent)
    return intents


def reconcile(api: GitHubAPI, inbox: int, main_sha: str) -> dict[str, Any]:
    validate_inbox(api, inbox)
    entries = records(api, inbox)
    by_id: dict[str, list[dict]] = {}
    for entry in entries:
        by_id.setdefault(entry["request_id"], []).append(entry)
    live = current_intents(api, main_sha, inbox_number=inbox)
    for intent in live:
        for existing in by_id.get(intent["request_id"], []):
            verify_request_context(existing, intent)
    missing = sorted(x["request_id"] for x in live if x["request_id"] not in by_id)
    stale = sum(
        1
        for record in entries
        if record["request_id"] not in {i["request_id"] for i in live}
    )
    return {
        "state": "RECONCILED_READ_ONLY",
        "inbox_records": len(entries),
        "distinct_requests": len(by_id),
        "duplicate_records": sum(len(v) - 1 for v in by_id.values()),
        "missing_requests": missing,
        "stale_records": stale,
        "paid_inference_enabled": False,
        "ledger_mutations": False,
        "ready_enabled": False,
    }


def ingest(api: GitHubAPI, inbox: int, main_sha: str, only: int | None) -> dict:
    validate_inbox(api, inbox)
    before = records(api, inbox)
    known = {item["request_id"] for item in before}
    by_id: dict[str, list[dict]] = {}
    for item in before:
        by_id.setdefault(item["request_id"], []).append(item)
    intents = current_intents(api, main_sha, only, inbox)
    new = 0
    for intent in intents:
        key = intent["request_id"]
        if key in known:
            for existing in by_id[key]:
                verify_request_context(existing, intent)
            continue
        # Novo readback do PR evita gravar HEAD obsoleto por corrida óbvia.
        fresh = api.request("GET", f"/pulls/{intent['pr_number']}")
        if make_intent(fresh, main_sha) != intent:
            raise ClosedGate("STALE_PR_BEFORE_WRITE")
        body = serialize_intent(intent)
        try:
            api.request("POST", f"/issues/{inbox}/comments", {"body": body})
        except ClosedGate:
            # ACK incerto nunca implica que o registro não foi gravado.
            pass
        after = records(api, inbox)
        matches = [x for x in after if x["request_id"] == key]
        if not matches:
            raise ClosedGate("INBOX_READBACK_UNCERTAIN")
        for recorded in matches:
            verify_request_context(recorded, intent)
        known.add(key)
        new += 1
    return {
        "state": "INTAKE_ONLY",
        "new_intents_verified": new,
        "eligible_prs": len(intents),
        "paid_inference_enabled": False,
        "ledger_mutations": False,
        "dispatch_enabled": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["intake", "reconcile"])
    args = parser.parse_args()
    try:
        if (
            os.getenv("GITHUB_REPOSITORY") != REPOSITORY
            or os.getenv("GITHUB_REF") != "refs/heads/main"
            or not SHA_PATTERN.fullmatch(os.getenv("GITHUB_SHA", ""))
        ):
            raise ClosedGate("UNTRUSTED_RUN_CONTEXT")
        if args.mode == "intake":
            if os.getenv("MODE_A_INTAKE_ENABLED") != "true":
                raise ClosedGate("INTAKE_NOT_ENABLED")
            if os.getenv("GITHUB_EVENT_NAME") not in {
                "pull_request_target",
                "schedule",
                "workflow_dispatch",
            }:
                raise ClosedGate("UNTRUSTED_EVENT")
        else:
            if os.getenv("GITHUB_EVENT_NAME") not in {
                "schedule",
                "workflow_dispatch",
                "repository_dispatch",
            }:
                raise ClosedGate("UNTRUSTED_EVENT")
        inbox = positive_number(os.getenv("MODE_A_INBOX_ISSUE"))
        api = GitHubAPI(os.getenv("GH_TOKEN", ""))
        if args.mode == "intake":
            only = None
            if os.getenv("GITHUB_EVENT_NAME") == "pull_request_target":
                with open(os.environ["GITHUB_EVENT_PATH"], "rb") as fp:
                    payload = fp.read(262145)
                if len(payload) > 262144:
                    raise ClosedGate("EVENT_TOO_LARGE")
                event = json.loads(payload)
                only = positive_number(event["pull_request"]["number"])
            result = ingest(api, inbox, os.environ["GITHUB_SHA"], only)
        else:
            result = reconcile(api, inbox, os.environ["GITHUB_SHA"])
        print(canonical(result))
        return 0
    except (ClosedGate, KeyError, OSError, TypeError, ValueError) as exc:
        code = str(exc) if isinstance(exc, ClosedGate) else "UNTRUSTED_INPUT"
        # Código de erro sem eco de conteúdo externo.
        print(canonical({"state": "BLOCKED", "reason": code[:60]}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
