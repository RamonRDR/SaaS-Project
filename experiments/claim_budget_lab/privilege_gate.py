"""Gate fail-closed para decidir se um laboratório CAS pode receber contents:write.

Execução de segurança apenas, sem acessar GitHub API e sem credenciais.
O GITHUB_TOKEN é por repositório; uma branch experimental não isola a escrita.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeScope:
    repository: str
    trusted_branch: str
    event_name: str
    contents_write: bool
    has_fork_checkout: bool
    imports_external_code: bool
    uses_paid_provider: bool
    job_timeout_minutes: int
    ref_prefix: str
    cleanup_enabled: bool
    audit_readback_enabled: bool
    dedicated_repository: bool


class UnsafePermissionScope(ValueError):
    pass


def authorize_cas_probe(scope: RuntimeScope) -> None:
    """Valida requisitos mínimos, mas NÃO concede/limita token ou escrita."""
    reasons = []
    if scope.repository == "RamonRDR/SaaS-Project":
        reasons.append("Nunca conceder contents:write ao laboratório no repo SaaS principal")
    if not scope.dedicated_repository:
        reasons.append("Repositório descartável separado é obrigatório")
    if scope.trusted_branch != "experiment/claim-budget-lab":
        reasons.append("Origem deve ser branch confiável dedicada")
    if scope.event_name != "push":
        reasons.append("Bloquear eventos pull_request/pull_request_target e eventos externos")
    if not scope.contents_write:
        reasons.append("O teste CAS real exige permission contents:write (não fingir prova)")
    if scope.has_fork_checkout or scope.imports_external_code:
        reasons.append("Nenhum código de fork/PR externo executável")
    if scope.uses_paid_provider:
        reasons.append("IA paga proibida no experimento")
    if not 1 <= scope.job_timeout_minutes <= 10:
        reasons.append("Timeout curto (1-10 minutos) obrigatório")
    if scope.ref_prefix != "refs/heads/experiment/cas-probe-":
        reasons.append("Prefixo de referências descartáveis não é o esperado")
    if not scope.cleanup_enabled or not scope.audit_readback_enabled:
        reasons.append("Sem cleanup + readback auditável, falhar fechado")
    if reasons:
        raise UnsafePermissionScope("; ".join(reasons))


def currently_safe_workflow() -> bool:
    """Permanece seguro por padrão no repo principal (somente leitura)."""
    return True
