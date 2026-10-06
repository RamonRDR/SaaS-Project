## Resumo

<!-- O que este PR entrega e por quê? -->

## Escopo e rastreabilidade

- SDD / issue / marco:
- ADRs aplicáveis:
- Branch:
- Fora de escopo:

## Gates

Preencha com `PASS`, `FAIL` ou `N/A` + justificativa.

| Gate | Status | Evidência / justificativa |
| --- | --- | --- |
| GOV-01 |  |  |
| GOV-02 |  |  |
| DOC-01 |  |  |
| SCOPE-01 |  |  |
| CODE-01 |  |  |
| CODE-02 |  |  |
| TEST-01 |  |  |
| TEST-02 |  |  |
| TEST-03 |  |  |
| TENANT-01 |  |  |
| AUTH-01 |  |  |
| DATA-01 |  |  |
| SEC-01 |  |  |
| SEC-02 |  |  |
| OBS-01 |  |  |
| BUILD-01 |  |  |
| BUILD-02 |  |  |
| CODEX-01 |  |  |
| STAGE-01 |  |  |
| HUMAN-01 |  |  |

## Testes e validações

<!-- Comandos, suites, cenários e resultados. -->

## Segurança e multi-tenancy

<!-- Impacto, testes negativos e evidências. Use N/A com justificativa quando realmente não aplicável. -->

## Observabilidade

<!-- Logs, correlation IDs, health, captura de erros e novos failure modes. -->

## Gates humanos

<!-- Registre links/comentários/aprovações verificáveis quando aplicável. -->

### Autorização de merge

- Evidência `ORCHESTRATOR_READY`:
- PR / HEAD:
- Tipo de autorização: `HUMAN_MERGE_AUTHORIZATION` | `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` | `MODE_A_ADMIN_ENVELOPE`
- Evidência da autorização:
- Para PR principal ou autorização específica: ordem temporal validada `ready.created_at < authorization_record.created_at < merged_at`
- Para `MODE_A_ADMIN_ENVELOPE`: referência à autorização final do PR principal + confirmação de escopo exclusivo `docs/PROJECT_STATUS.md` + GOV-01/GOV-02/SEC-01/CODEX-01 verdes

## Contrato congelado de revisão

- REVIEW_CONTRACT_FROZEN:
- HEAD:
- Escopo / SDD / ADRs:
- Riscos residuais aceitos:
- FOLLOW_UPs não bloqueantes:

## Codex Review

O CODEX-01 só pode ser marcado como PASS depois do último commit mutável.

- HEAD final:
- SHA revisado pelo Codex:
- Findings:
- Tratamento:

## Checklist de fechamento

- [ ] Nenhum gate obrigatório aplicável está em FAIL.
- [ ] Todo N/A possui justificativa.
- [ ] Documentação final pré-merge está atualizada.
- [ ] Codex Review corresponde ao HEAD final.
- [ ] PR está apto para validação PRE_MERGE.

> O estado final de conclusão em `docs/PROJECT_STATUS.md` só é persistido depois do merge principal, em PR administrativo exclusivo.
