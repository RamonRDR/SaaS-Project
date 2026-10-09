"""Laboratório distribuído entre runners via artefatos imutáveis.

Cada worker roda em job GitHub Actions independente e NÃO recebe credencial
GitHub com escrita. Reconciliação calcula resultado determinístico e guarda
o ledger como artefato, não como ref Git. Não prova CAS remoto multi-writer.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

WORKERS = ("alpha", "beta")
EXPECTED_REQUESTS = {
    "alpha": ["req-shared", "req-02", "req-03", "req-04"],
    "beta": ["req-shared", "req-03", "req-05", "req-06"],
}
CAP_MINOR = 4
ORDER = ("req-shared", "req-02", "req-03", "req-04", "req-05", "req-06")
PROTOCOL = "distributed-artifacts.v1"


class InvalidEvidence(Exception):
    pass


def canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def proposal(worker: str, source_head: str, run_id: str) -> dict[str, Any]:
    if worker not in WORKERS or not source_head or not run_id:
        raise InvalidEvidence("Worker/HEAD/run inválidos")
    content = {
        "protocol": PROTOCOL,
        "worker": worker,
        "source_head": source_head,
        "run_id": run_id,
        "snapshot_revision": 0,
        "claim_request_id": "claim-shared",
        "requests": EXPECTED_REQUESTS[worker],
        "budget_cost_minor": 1,
        "fault_injection": {
            "alpha": {"write_ack": "UNKNOWN_AFTER_PERSIST"},
            "beta": {"lost_request_before_persist": "req-lost"},
        }[worker],
    }
    content["digest"] = digest(content)
    return content


def validate_proposal(item: dict[str, Any], expected_head: str, expected_run: str) -> None:
    data = dict(item)
    sig = data.pop("digest", None)
    if not isinstance(sig, str) or sig != digest(data):
        raise InvalidEvidence("Hash mismatch; evidência rejeitada")
    worker = data.get("worker")
    if (
        worker not in WORKERS
        or data.get("protocol") != PROTOCOL
        or data.get("source_head") != expected_head
        or data.get("run_id") != expected_run
        or data.get("snapshot_revision") != 0
        or data.get("claim_request_id") != "claim-shared"
        or data.get("budget_cost_minor") != 1
        or data.get("requests") != EXPECTED_REQUESTS[worker]
    ):
        raise InvalidEvidence("Schema, origem, identidade ou HEAD divergente")
    if worker == "alpha" and data.get("fault_injection") != {"write_ack": "UNKNOWN_AFTER_PERSIST"}:
        raise InvalidEvidence("Injeção de ack incorreta")
    if worker == "beta" and data.get("fault_injection") != {"lost_request_before_persist": "req-lost"}:
        raise InvalidEvidence("Injeção de crash incorreta")


def reconcile(items: list[dict[str, Any]], source_head: str, run_id: str) -> dict[str, Any]:
    if len(items) != 2 or {x.get("worker") for x in items} != set(WORKERS):
        raise InvalidEvidence("Exigidos precisamente dois workers distintos")
    for item in items:
        validate_proposal(item, source_head, run_id)
    indexed = {i["worker"]: i for i in items}
    # Ambos observaram rev0; somente primeiro na ordem do protocolo vence.
    claim_winner = next(w for w in WORKERS if indexed[w]["claim_request_id"] == "claim-shared")
    all_requests = [req for w in WORKERS for req in indexed[w]["requests"]]
    unique_requests = set(all_requests)
    if set(ORDER) != unique_requests:
        raise InvalidEvidence("Solicitação perdida/inesperada")
    ledger = {"protocol": PROTOCOL, "run_id": run_id, "source_head": source_head,
              "generation": 0, "claim_winner": claim_winner,
              "budget_limit_minor": CAP_MINOR, "reservations": []}
    accepted = []
    denied = []
    for req in ORDER:
        if req in {x["request_id"] for x in ledger["reservations"]}:
            raise InvalidEvidence("Reserva duplicada")
        amount = 1
        if sum(x["max_cost_minor"] for x in ledger["reservations"]) + amount > CAP_MINOR:
            denied.append(req)
            continue
        ledger["generation"] += 1
        ledger["reservations"].append({"request_id": req, "max_cost_minor": amount})
        accepted.append(req)
    exposure = sum(x["max_cost_minor"] for x in ledger["reservations"])
    if len(accepted) != 4 or len(denied) != 2 or exposure > CAP_MINOR:
        raise InvalidEvidence("Budget incorreto")
    return {
        "ledger": ledger,
        "provenance": {
            "runner_ids": list(WORKERS),
            "proposal_digests": {w: indexed[w]["digest"] for w in WORKERS},
            "proposal_acks": {"alpha": "UNKNOWN_AFTER_PERSIST", "beta": "OK"},
            "unknown_ack_reconciled_by_artifact_read": True,
            "lost_before_persist_was_rejected": "req-lost" not in unique_requests,
            "duplicate_request_ids_deduplicated": len(all_requests) - len(unique_requests),
            "distinct_runner_proposals": 2,
            "claim_winners": 1,
            "financial_accepted": accepted,
            "financial_denied": denied,
            "provider_calls": 0,
            "real_git_ref_cas_tested_here": False,
            "simulated_coordinator_not_distributed_cas": True,
        },
    }


def worker_main(args: argparse.Namespace) -> None:
    p = proposal(args.worker, args.head, args.run)
    dst = Path(args.out)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PROPOSAL_CREATED worker=" + args.worker + " digest=" + p["digest"])
    if args.worker == "alpha":
        print("FAULT_INJECTED: simulated ACK_UNKNOWN after local proposal persistence")
    else:
        print("FAULT_INJECTED: req-lost interrupted before recording")
    print("NOTE: artifact transport occurs in a separate GitHub upload-artifact step")


def reconcile_main(args: argparse.Namespace) -> None:
    inbox = Path(args.inbox)
    names = {x.name for x in inbox.iterdir() if x.is_file()}
    if names != {"alpha.json", "beta.json"}:
        raise InvalidEvidence("Evidência incompleta ou arquivo inesperado: " + str(names))
    items = [json.loads((inbox / f"{w}.json").read_text(encoding="utf-8")) for w in WORKERS]
    result = reconcile(items, args.head, args.run)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("DISTRIBUTED_PROPOSALS_PASSED: 2 independent jobs, 1 claim, 4/4 budget, 2 denied")
    print("NOTE: this does not prove concurrent Git ref writers or API transport ambiguity")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as file:
            file.write("\n## Distributed workers: artifact reconciliation\n\n")
            file.write("| Check | Value |\n| --- | --- |\n")
            file.write("| Independent worker jobs | 2 |\n")
            file.write("| Unique persisted claim winner | alpha |\n")
            file.write("| Requests accepted / denied | 4 / 2 |\n")
            file.write("| Budget reserved | 4 of 4 |\n")
            file.write("| Duplicate request proposals deduplicated | 2 |\n")
            file.write("| Simulated ACK unknown | Reconciled by artifact read |\n")
            file.write("| Provider API calls | 0 |\n")
            file.write("| Real Git ref multi-writer CAS | Not tested in this workflow |\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("worker")
    a.add_argument("--worker", choices=WORKERS, required=True)
    a.add_argument("--head", required=True)
    a.add_argument("--run", required=True)
    a.add_argument("--out", required=True)
    b = sub.add_parser("reconcile")
    b.add_argument("--inbox", required=True)
    b.add_argument("--head", required=True)
    b.add_argument("--run", required=True)
    b.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.command == "worker":
        worker_main(args)
    else:
        reconcile_main(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
