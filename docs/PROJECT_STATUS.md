# Status do Projeto

## Projeto

SaaS Project — nome técnico temporário de uma plataforma SaaS multi-tenant para negócios de serviços.

## Fase atual

**Fase 0 — Fundação de Engenharia**

## Estado de governança automatizada

O bloco abaixo é reservado ao enforcement de CI.

<!-- GOV:PROJECT_STATUS:BEGIN -->
<!-- GOV:PHASE-0-F:completed -->
<!-- GOV:PHASE-0-G:planned -->
<!-- GOV:PROJECT_STATUS:END -->

## Estado atual

- repositório público iniciado a partir de snapshot de engenharia sanitizado;
- histórico operacional privado e experimentos descartados não fazem parte deste Git público;
- branch padrão: `main`;
- Phase 0A — fundação do repositório: concluída;
- Phase 0B — Agent System V1: concluída;
- Phase 0C — Skill System V1: concluída;
- Phase 0D — templates e lifecycle de SDD/ADR: concluída;
- Phase 0E — baseline arquitetural ADR-0001 a ADR-0010: concluída;
- Phase 0F — Definition of Done e gates de CI: concluída;
- Mode A interativo: operacional;
- runtime unattended anterior: experimento encerrado e não importado para o repositório público;
- novo runtime unattended: piloto A com arquitetura documentada e aprovada (ADR-0015 rev.6 / SDD-0002 v0.6, PR #11 integrado); **ainda não implementado nem ativado**;
- backend de produto: não iniciado;
- frontend de produto: não iniciado;
- PHASE-0-G permanece planejada até a conclusão do novo runtime unattended.

## Baseline arquitetural vigente

- monólito modular em Django;
- Django REST Framework para API;
- Flutter como frontend multiplataforma;
- PostgreSQL como banco transacional;
- Docker para ambientes;
- n8n restrito a automações e integrações, fora das regras centrais de domínio;
- estratégia multi-tenant com isolamento explícito;
- autenticação e sessão definidas por ADR;
- observabilidade desde a fundação;
- CI/CD e política de merge definidas por ADR-0010;
- desenvolvimento orientado por SDD e ADR;
- revisão técnica e gates humanos para decisões materiais.

## Próximo marco

**Piloto A do Mode A, etapas M1–M4 (ainda não executadas):**

1. **M1: isolamento**. Escolher e autorizar sandbox separado, auditar a conexão GitHub efetivamente usada pelo Work e comprovar ausência de escrita, comentários e administração no repositório principal. A conexão ampla existente não é evidência de isolamento.
2. **M2: canary Work somente no sandbox**. Após M1 e autorização de ativação específica, testar wake-up legítimo/duplicado, escopo pequeno e reversível, PR draft e CI sem secrets do principal.
3. **M3: promoção humana**. O responsável inspeciona diff e manifesto completos, rejeita candidato que toque control plane e reproduz manualmente patch pequeno permitido pelo GitHub web em novo PR principal, com HEAD, CI e Codex próprios.
4. **M4: validação**. Reconciliar gates, `REVIEW_CONTRACT_FROZEN`, `CODEX-01` no HEAD exato, READY e MERGE-01 somente mediante autorização humana posterior.
5. **Retomada por evento**. O observador horário `SaaS Project — Codex Review Watch` é read-only e não ativa Work; o novo contrato de wake-up deve ser implementado e testado em PR próprio. O contrato legado `.ai/runtime/prompts/work-unattended.md` está ausente da `main`, portanto tarefas que dependam dele devem falhar fechado, sem improvisação.

A arquitetura do piloto A foi integrada documentalmente pelo [PR #11](https://github.com/RamonRDR/SaaS-Project/pull/11), com [`POST_MERGE / STATUS_FINALIZATION_ALLOWED`](https://github.com/RamonRDR/SaaS-Project/pull/11#issuecomment-6180238057). A execução/segregação está rastreada na [issue #13](https://github.com/RamonRDR/SaaS-Project/issues/13). Publicador autônomo, Budget Broker pago, credenciais de escrita principal no Work e APIs pagas continuam fora do escopo do piloto A.

**PHASE-0-G continua `planned`** e seus gates próprios não foram comprovados. O encerramento documental M0 não autoriza ativação, gasto, merge de PR subsequente ou `DONE_ALLOWED` de PHASE-0-G.

## Política pública

Este repositório é uma vitrine técnica e, ao mesmo tempo, o repositório de engenharia do projeto.

Não devem ser versionados:

- credenciais, tokens, chaves ou arquivos `.env`;
- dados pessoais ou dados de clientes;
- URLs de sessão privadas;
- logs operacionais sensíveis;
- artefatos locais;
- conteúdo copiado de fontes privadas sem autorização.

Consulte `SECURITY.md` e `CONTRIBUTING.md`.
