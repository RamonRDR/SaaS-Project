"""Simulador determinístico do protocolo de inferência paga. Sem SDK/API/segredos.

Isto NÃO implementa CAS real do GitHub ou transação distribuída. Serve para
testar invariantes de negócio antes de escolher infraestrutura de produção.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import threading


class Denied(Exception):
    """Transição negada conservadoramente."""


class CASConflict(Denied):
    """Snapshot perdeu corrida de optimistic concurrency."""


class AmbiguousDispatch(Denied):
    """Envio foi tentado; resultado sem confirmação: sem retry automático."""


@dataclass(frozen=True)
class Operation:
    repository: str
    pr: int
    head: str
    kind: str
    author: str
    association: str = "OWNER"
    attempt: int = 0

    @property
    def request_id(self) -> str:
        raw = json.dumps(
            [self.repository, self.pr, self.head, self.kind, self.attempt],
            separators=(",", ":"),
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


class FakeClock:
    def __init__(self, now: datetime):
        if now.tzinfo is None:
            raise ValueError("Relógio UTC precisa de timezone")
        self.now_value = now.astimezone(timezone.utc)
        self.lock = threading.Lock()

    def now(self) -> datetime:
        with self.lock:
            return self.now_value

    def set(self, new_value: datetime) -> None:
        if new_value.tzinfo is None:
            raise ValueError("Relógio confiável ausente")
        with self.lock:
            self.now_value = new_value.astimezone(timezone.utc)


class SimulatedCASLedger:
    """Célula simulada com revisão monotônica, não é GitHub Git-ref CAS real."""
    def __init__(self):
        self.lock = threading.RLock()
        self.version = 0

    def update(self, expected_version: int, action) -> object:
        with self.lock:
            if expected_version != self.version:
                raise CASConflict("Revision mismatch")
            value = action()
            self.version += 1
            return value

    def atomic(self, action) -> object:
        # Modelo: lê revisão e aplica CAS na mesma seção crítica simulada.
        # No GitHub real será necessário retry com lease/version e prova E2E.
        with self.lock:
            return self.update(self.version, action)


class MockProvider:
    """Nenhuma rede. Simula a entrada no provedor e seu custo final."""
    def __init__(self, cost_minor: int = 3):
        self.calls = []
        self.cost_minor = cost_minor
        self.lock = threading.Lock()

    def call(self, request_id: str, *, ambiguous: bool = False) -> int:
        with self.lock:
            self.calls.append(request_id)
        if ambiguous:
            raise AmbiguousDispatch("Envio ocorreu, confirmação ausente")
        return self.cost_minor


class PaidInferenceLab:
    VALID_KINDS = {"fork_review", "same_repo_review", "remediator"}
    TRUSTED_ROLES = {"OWNER", "MEMBER", "COLLABORATOR"}

    def __init__(
        self,
        *,
        clock: FakeClock,
        provider: MockProvider,
        monthly_limit_minor: int = 100,
        boundary_guard_seconds: int = 30,
    ):
        if monthly_limit_minor <= 0:
            raise ValueError("Orçamento deve ser positivo")
        self.clock = clock
        self.provider = provider
        self.monthly_limit_minor = monthly_limit_minor
        self.boundary_guard_seconds = boundary_guard_seconds
        self.quota = SimulatedCASLedger()
        self.budget = SimulatedCASLedger()
        self.requests = {}  # id -> {op, state, winner, created_at, sent}
        self.financial = {}  # (request_id, period) -> reserva financeira
        self.fork_quota = []  # (request_id, pr, author, timestamp)
        self.approved_external = set()

    @staticmethod
    def period(now: datetime) -> str:
        return now.astimezone(timezone.utc).strftime("%Y-%m")

    @staticmethod
    def in_window(now: datetime, then: datetime) -> bool:
        return timedelta(0) <= now - then < timedelta(hours=24)

    def approve_external(self, request_id: str) -> None:
        with self.quota.lock:
            self.approved_external.add(request_id)

    def enqueue(self, op: Operation) -> str:
        if op.kind not in self.VALID_KINDS or not op.head or not op.repository or op.pr < 1:
            raise Denied("Operação inválida")
        if op.kind == "fork_review" and op.attempt != 0:
            raise Denied("Fork review tem no máximo uma chamada por HEAD")
        key = op.request_id
        def apply():
            current = self.requests.get(key)
            if current:
                if current["op"] != op:
                    raise Denied("Identidade conflitante")
                return key
            self.requests[key] = {
                "op": op, "state": "PENDING", "winner": None,
                "created_at": self.clock.now(), "sent": False,
            }
            return key
        return self.quota.atomic(apply)

    def eligible(self, key: str) -> None:
        def apply():
            r = self.requests.get(key)
            if not r:
                raise Denied("Solicitação não persistida")
            if r["state"] == "RESERVED":
                return
            if r["state"] != "PENDING":
                raise Denied("Elegibilidade não pode voltar")
            op = r["op"]
            now = self.clock.now()
            if op.kind == "fork_review":
                if op.association not in self.TRUSTED_ROLES and key not in self.approved_external:
                    raise Denied("Trust gate humano pendente")
                recent = [x for x in self.fork_quota if self.in_window(now, x[3])]
                if sum(x[1] == op.pr for x in recent) >= 3:
                    raise Denied("Quota fork por PR excedida")
                if op.association not in self.TRUSTED_ROLES and sum(x[2] == op.author for x in recent) >= 5:
                    raise Denied("Quota autor externo excedida")
                self.fork_quota.append((key, op.pr, op.author, now))
            r["state"] = "RESERVED"
        self.quota.atomic(apply)

    def claim(self, key: str, consumer_run_id: str) -> bool:
        if not consumer_run_id:
            raise Denied("Consumer id vazio")
        def apply():
            r = self.requests.get(key)
            if not r or r["state"] != "RESERVED":
                return False
            r["state"] = "CLAIMED"
            r["winner"] = consumer_run_id
            return True
        return self.quota.atomic(apply)

    def _require_winner(self, key: str, winner: str):
        with self.quota.lock:
            r = self.requests.get(key)
            if not r or r["winner"] != winner or r["state"] != "CLAIMED":
                raise Denied("Consumer não venceu claim universal")
            if r["sent"]:
                raise Denied("Dispatch já tentado, sem segunda chamada")
            return r

    def _exposure(self, period: str) -> int:
        return sum(
            x["final_cost"] if x["final_cost"] is not None else x["max_cost"]
            for x in self.financial.values() if x["period"] == period
        )

    def reserve_budget(
        self, key: str, consumer: str, max_cost: int,
        *, prove_not_sent: bool = False,
    ) -> dict:
        if max_cost <= 0:
            raise Denied("Custo máximo indefinido")
        r = self._require_winner(key, consumer)
        if r["sent"]:
            raise Denied("Já houve envio")
        period = self.period(self.clock.now())
        def apply():
            self._require_winner(key, consumer)
            slot = (key, period)
            prior = self.financial.get(slot)
            if prior:
                if prior["consumer"] != consumer or prior["max_cost"] != max_cost:
                    raise Denied("Reserva conflitante")
                return dict(prior)
            previous_periods = [
                x for (rid, p), x in self.financial.items() if rid == key and p != period
            ]
            if previous_periods and not prove_not_sent:
                raise Denied("Virada UTC exige prova de não-envio")
            if self._exposure(period) + max_cost > self.monthly_limit_minor:
                raise Denied("Budget global insuficiente")
            reservation = {
                "request_id": key, "consumer": consumer, "period": period,
                "max_cost": max_cost, "final_cost": None, "sent": False,
            }
            self.financial[slot] = reservation
            return dict(reservation)
        return self.budget.atomic(apply)

    def dispatch(
        self, key: str, consumer: str, *, ambiguous: bool = False,
    ) -> int:
        self._require_winner(key, consumer)
        now = self.clock.now()
        month_end = (datetime(now.year + (now.month == 12), now.month % 12 + 1, 1, tzinfo=timezone.utc))
        if (month_end - now).total_seconds() <= self.boundary_guard_seconds:
            raise Denied("Janela insegura próxima à virada UTC")
        period = self.period(now)
        def mark_sent():
            r = self._require_winner(key, consumer)
            reservation = self.financial.get((key, period))
            if not reservation or reservation["consumer"] != consumer:
                raise Denied("Reserva financeira do mês UTC corrente ausente")
            if any(x["sent"] for (rid, _), x in self.financial.items() if rid == key):
                raise Denied("Envio anterior ou ambíguo")
            if self.period(self.clock.now()) != period:
                raise Denied("Virada UTC antes do dispatch")
            r["sent"] = True
            reservation["sent"] = True
        self.budget.atomic(mark_sent)
        # Não existe retry: marcar antes do envio conserva custo em erro ambíguo.
        cost = self.provider.call(key, ambiguous=ambiguous)
        with self.budget.lock:
            entry = self.financial[(key, period)]
            if cost > entry["max_cost"]:
                raise AmbiguousDispatch("Custo real excedeu máximo: bloquear reconciliação")
            entry["final_cost"] = cost
        return cost

    def snapshot(self) -> dict:
        # Consistente com reserva financeira: lock do budget antes do quota.
        with self.budget.lock, self.quota.lock:
            return {
                "requests": len(self.requests),
                "claimed": sum(r["state"] == "CLAIMED" for r in self.requests.values()),
                "reservations": len(self.financial),
                "provider_calls": len(self.provider.calls),
                "exposure_by_period": {
                    p: self._exposure(p) for p in sorted({v["period"] for v in self.financial.values()})
                },
            }
