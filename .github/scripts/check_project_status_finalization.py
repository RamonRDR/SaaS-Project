#!/usr/bin/env python3
"""Valida o contrato GOV-02 usando marcadores de máquina determinísticos."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Iterable

STATUS_PATH = "docs/PROJECT_STATUS.md"
BLOCK_BEGIN = "<!-- GOV:PROJECT_STATUS:BEGIN -->"
BLOCK_END = "<!-- GOV:PROJECT_STATUS:END -->"
MARKER_PREFIX = "<!-- GOV:"
MARKER_RE = re.compile(
    r"^<!-- GOV:(PHASE-\d+(?:-[A-Z0-9]+)+):(planned|active|completed) -->$"
)

ALLOWED_TRANSITIONS = {
    "planned": {"planned", "active", "completed"},
    "active": {"active", "completed"},
    "completed": {"completed"},
}


class GovernanceError(RuntimeError):
    """Representa falha de contrato no GOV-02."""


@dataclass(frozen=True)
class Evaluation:
    """Resultado determinístico da avaliação de finalização."""

    applicable: bool
    newly_completed: tuple[str, ...]


def parse_markers(content: str, *, allow_missing_block: bool = False) -> dict[str, str]:
    """Lê apenas o bloco reservado de estado de máquina, sem interpretar Markdown."""

    lines = content.splitlines()
    begin_indexes = [i for i, line in enumerate(lines) if line.strip() == BLOCK_BEGIN]
    end_indexes = [i for i, line in enumerate(lines) if line.strip() == BLOCK_END]

    if not begin_indexes and not end_indexes:
        if allow_missing_block:
            return {}
        raise GovernanceError("Bloco de governança ausente em PROJECT_STATUS.md.")

    if len(begin_indexes) != 1 or len(end_indexes) != 1:
        raise GovernanceError("PROJECT_STATUS.md deve conter exatamente um bloco GOV.")

    begin = begin_indexes[0]
    end = end_indexes[0]
    if begin >= end:
        raise GovernanceError("Bloco GOV possui delimitadores em ordem inválida.")

    for i, line in enumerate(lines):
        stripped = line.strip()
        if i in (begin, end):
            continue
        if stripped.startswith(MARKER_PREFIX) and not (begin < i < end):
            raise GovernanceError("Marcador GOV encontrado fora do bloco reservado.")

    markers: dict[str, str] = {}
    for raw_line in lines[begin + 1 : end]:
        line = raw_line.strip()
        if not line:
            continue
        match = MARKER_RE.fullmatch(line)
        if not match:
            raise GovernanceError(f"Linha inválida dentro do bloco GOV: {raw_line!r}")
        phase, state = match.groups()
        if phase in markers:
            raise GovernanceError(f"Marcador duplicado para {phase}.")
        markers[phase] = state

    if not markers:
        raise GovernanceError("Bloco GOV não pode ficar vazio.")

    return markers


def validate_transitions(base: dict[str, str], head: dict[str, str]) -> tuple[str, ...]:
    """Valida transições monotônicas e retorna fases que ficaram concluídas."""

    for phase, base_state in base.items():
        if phase not in head:
            raise GovernanceError(f"Marcador removido para {phase}.")
        head_state = head[phase]
        if head_state not in ALLOWED_TRANSITIONS[base_state]:
            raise GovernanceError(
                f"Transição inválida para {phase}: {base_state} -> {head_state}."
            )

    newly_completed = tuple(
        sorted(
            phase
            for phase, head_state in head.items()
            if head_state == "completed" and base.get(phase) != "completed"
        )
    )
    return newly_completed


def evaluate(
    base_content: str,
    head_content: str,
    changed_files: Iterable[str],
) -> Evaluation:
    """Avalia aplicabilidade e escopo do GOV-02."""

    base = parse_markers(base_content, allow_missing_block=True)
    head = parse_markers(head_content)
    newly_completed = validate_transitions(base, head)

    if not newly_completed:
        return Evaluation(applicable=False, newly_completed=())

    normalized_files = tuple(sorted(set(changed_files)))
    if normalized_files != (STATUS_PATH,):
        raise GovernanceError(
            "GOV-02 falhou: finalização exige PR exclusivo de "
            f"{STATUS_PATH}; arquivos alterados: {normalized_files!r}"
        )

    return Evaluation(applicable=True, newly_completed=newly_completed)


def run_git(*args: str) -> str:
    """Executa Git em modo fail-closed."""

    try:
        completed = subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip()
        raise GovernanceError(
            f"Falha ao executar git {' '.join(args)}: {stderr or exc.returncode}"
        ) from exc
    return completed.stdout


def load_snapshot(sha: str) -> str:
    """Lê PROJECT_STATUS.md de um commit específico."""

    return run_git("show", f"{sha}:{STATUS_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    args = parser.parse_args()

    try:
        merge_base = run_git("merge-base", args.base_sha, args.head_sha).strip()
        if not merge_base:
            raise GovernanceError("git merge-base não retornou SHA.")

        changed_output = run_git("diff", "--name-only", merge_base, args.head_sha)
        changed_files = [line for line in changed_output.splitlines() if line]

        base_content = load_snapshot(merge_base)
        head_content = load_snapshot(args.head_sha)

        result = evaluate(base_content, head_content, changed_files)
    except GovernanceError as exc:
        print(f"::error::GOV-02 falhou: {exc}", file=sys.stderr)
        return 1

    if not result.applicable:
        print("GOV-02 N/A: nenhuma fase transitou para completed.")
        return 0

    phases = ", ".join(result.newly_completed)
    print(
        "GOV-02 PASS: finalização determinística detectada "
        f"para {phases}; escopo exclusivo confirmado."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
