# ADR-0014 - Claim universal e Single-Writer Global para inferência paga

## Metadados

- **ID:** ADR-0014
- **Título:** Claim universal e Single-Writer Global para inferência paga
- **Status:** Proposed
- **Revisão decisória:** 2
- **Data de criação:** 2026-10-08
- **Última atualização:** 2026-10-09
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Ramon Rodriguez
- **SDDs relacionadas:** SDD-0001 v1.3
- **ADRs relacionados:** ADR-0013 rev.1 (`Accepted`, vigente); ADR-0012 rev.7 (`Superseded`); ADR-0010
- **PR / issue relacionada:** PR #2 / Issue #1

Nenhum agente de IA pode marcar esta ADR `Accepted`. A ADR-0013 permanece vigente enquanto esta sucessora estiver `Proposed`. O conteúdo decisório compreende as seções 1 a 14 e será imutável após o aceite.

## 1. Contexto

O CODEX-01 do HEAD `a58a1f7` identificou P1: CODEX-01 same-repo e Remediator não possuem claim para acessar Budget Broker; e P2: rollover UTC tenta novo claim apesar de `CONSUMED` ser imutável. A versão anterior da ADR tratava claim de quota específico de fork e pressupunha `CAS` de ledger financeiro via Git ref.

A evidência real em `RamonRDR/SaaS-CAS-Lab`, [run #37873320199](https://github.com/RamonRDR/SaaS-CAS-Lab/actions/runs/37873320199), [relatório](https://github.com/RamonRDR/SaaS-CAS-Lab/blob/main/docs/RESULTS_2026-10-09.md), mostrou: dois runners independentes com commits irmãos obtiveram HTTP 200/422 (um vencedor) para claim e orçamento; um writer serializado reconciliou 4/4 reservas, 2 negadas; **contraexemplo:** Git aceitou HTTP 200 para commit fast-forward baseado em estado lógico antigo, regredindo geração do ledger 5→2, com `force:false`. Depois o teste restaurou o estado e apagou a ref efêmera. Logo `PATCH /git/refs force:false` NÃO implementa CAS transacional de dados.

A ADR-0013 rev.1 permanece `Accepted` e suas seções decisórias são imutáveis. Esta ADR-0014 rev.2 é proposta sucessora, ainda dependente de parecer e aceite humano.

## 2. Drivers da decisão

- Todos os consumidores de IA paga precisam de claim exclusivo e orçamento sem exceções same-repo.
- Um único ledger mensal global deve impedir dupla reserva e gasto acima do teto sob concorrência entre PRs/workflows.
- Crash, reentrada, falha de transporte e rollover UTC não podem converter incerteza em nova chamada paga.
- Repositório público: zero segredo em fork/reviewer/Remediator/Trusted Publisher; broker isolado trusted da `main`.
- Governança, provenance, human gates e anti-loop prevalecem; arquitetura ≠ prova de runtime operacional.

## 3. Restrições

- Sem mudança de domínio do SaaS, Flutter, banco de produto ou PHASE-0-G.
- Não confiar em `concurrency` por PR, 1 pending workflow, Git ref fast-forward ou comentários como storage transacional.
- Não pressupor duas refs Git atômicas entre quota/claim/budget; o escritor global é o ÚNICO decisor de mutações financeiras e claims.
- O `GITHUB_TOKEN` com `contents:write` vale para o repositório, não um prefixo de branch. Escritor somente da `main` confiável, sem executar PR/fork e com isolamento de credenciais.
- Sem prova de exclusão durável, ledger íntegro, preço, orçamento humano e despacho autorizado, NENHUMA API paga está habilitada.

## 4. Opções consideradas

### A - Budget antes do claim

Rejeitada: consumidores perdedores comprometem orçamento e podem consumir o teto sem chamada.

### B - Quota claim de fork e Git ref `force:false` como CAS financeiro

Rejeitada como solução global: deixa same-repo sem claim e a prova negativa do CAS-Lab demonstrou sobrescrita fast-forward de snapshot stale (geração 5→2).

### C - Dois ledgers independentes com suposta transação atômica

Rejeitada sem transação distribuída comprovada; crash entre refs cria ambiguidade e risco de inconsistência.

### D - Writer Global Único + claim universal + ledger canônico (escolhida)

Todos os consumidores publicam intents duráveis; um escritor global trusted, serializado efetivamente para todo repositório, aplica elegibilidade, quota adicional de fork, claim lógico e orçamento idempotente. Dentro da exclusão, verifica estado lógico imediatamente antes de gravar e relê após erro ambíguo. Sem garantia real de exclusão ou recuperação, bloqueia gasto ou muda para storage de CAS server-side verificável.

## 5. Decisão proposta

- **Opção:** D. Claim universal anterior ao orçamento, Single-Writer Global para claim/quota/finanças e Budget Broker exclusivo.
- **Motivo:** corrige P1/P2, evita duas reservas antes de escolher vencedor, e não inventa transação Git que não existe.
- **Limite importante:** `concurrency.group` global, com `cancel-in-progress:false`, é controle operacional auxiliar de exclusão, mas **não é fila durável nem transação**. Ao habilitar execução paga, testar que TODO workflow mutador compartilha exclusivamente a mesma região crítica e que nenhuma execução paralela ou bypass existe. Se GitHub não comprovar, trocar backend antes de cobrar.

Esta seção é PROPOSTA, não aceite humano.

## 6. Consequências

### Positivas

- Quota de autor/PR é guarda ADICIONAL só para fork. CODEX-01 same-repo e Remediator recebem claim universal sem depender da quota de fork.
- Chave lógica estável impede múltiplos compromissos após troca do workflow_run_id.
- Writer único reduz superfícies concorrentes e permite orçamento global em um único limite conservador.
- Incerteza vira bloqueio auditável e não repetição automática de pagamento.

### Trade-offs

- Writer único limita throughput e exige drainer/reconciler e backpressure.
- Job pending do Actions pode ser substituído; toda solicitação deve persistir antes do wake-up.
- Crash entre claim e gasto pode deixar operação bloqueada sem chamada; isso é intencional fail-closed.
- Storage Git é permitido SOMENTE se o canary demonstrar exclusão efetiva, monotonicidade lógica, recuperação e ausência de concorrente alternativo; caso contrário requer backend transacional.

## 7. Segurança e protocolo de execução

1. Persistir `operation_key = repository/pr/head_sha/operation_kind/authorized_attempt` e `request_id` derivado antes de qualquer wake-up. Para fork CODEX-01, uma tentativa por HEAD; Remediator usa número de tentativa autorizada e anti-loop.
2. Reconciler trusted da `main` valida origem/HEAD, job/PR, risco, trust gate para autor externo e quotas de fork. Quem chega à inferência paga é fork CODEX-01, same-repo CODEX-01 ou Codex Remediator; ninguém chama provedor diretamente.
3. Writer global único verifica `PENDING → ELIGIBLE → CLAIMED` para qualquer tipo e grava vencedor `consumer_run_id`. `workflow_run_id` não entra na chave idempotente de operação. Para fork, quota `RESERVED → CONSUMED` é parte da mesma decisão serializada, não outro claim independente.
4. Somente vencedor pode pedir reserva financeira. Ledger canônico inclui `operation_key`, `financial_reservation_id`, `budget_period_utc`, `model`, `operation`, `max_cost_minor`, comprometido, outstanding, geração, provenance e estado de envio. Sob writer global, revalidar estado imediatamente antes da mutação e permitir apenas `committed + outstanding_max + new_max <= budget_limit`. Duplicate retorna reserva existente sem aumentar teto nem habilitar novo dispatch.
5. Antes da API, Budget Broker com única credencial e código trusted grava autorização de dispatch durável e verifica relógio UTC confiável, mês vigente, janela segura e ausência de envio anterior. Estado `SENT`/`AMBIGUOUS` bloqueia retry automático da mesma operação.
6. Rollover UTC **não refaz claim lógico** nem quota `CONSUMED`. Se nenhuma chamada foi enviada comprovadamente, o mesmo vencedor pode solicitar reserva FINANCEIRA no novo mês, sob writer global e idempotência da operação; reserva antiga fica conservadoramente comprometida até conciliação terminal. Se não há prova de não-envio, fail-closed.
7. Erro, timeout ou resposta desconhecida da GitHub API exige readback remoto por identidade/geração e estado de envio antes de decidir nova transição. Mesmo HTTP 200 não prova que os dados eram logicamente atuais: validar geração e invariantes sob exclusão.
8. Reconciler periódico lê journal canônico, não payload de evento; lida com pending Actions coalescido e nunca faz envio pago automático sob estado ambíguo. Commits do ledger não devem reativar o dispatcher por `push` recursivo.
9. Sem comprovação da exclusão global do writer, branch/trust safety, preço e limite aprovado, bloquear chamadas (`BLOCKED_EXTERNAL`/`HUMAN_DECISION_REQUIRED`). Merge do produto continua gate humano.

## 8. Modelo de dados e contrato

Não afeta schema de domínio do SaaS. O journal de execução persiste identidade da operação, request, consumer, PR/HEAD, kind, tentativa autorizada, quota fork (quando aplicável), reserva de custo, mês UTC, custo máximo e conciliado, geração monotônica, controle de envio e provenance. Separar `quota_reservation_id` de `financial_reservation_id`. O escritor deve tratar as transições como *uma decisão global serializada*, sem atribuir ACID a refs Git separadas.

## 9. Operação, custos e observabilidade

- Fonte de verdade: ledger confiável, não comentários, logs, nem payload de wake-up.
- Registrar vencedores e perdedores, geração antiga/nova, operação, budget, UTC, readback de retorno ambíguo, event sourcing e recusas.
- Guardar segredos exclusivamente em Budget Broker, nunca nos artefatos/modelo do fork.
- Limitar custo por input/output tokens, preço versionado, modelo, tamanho, retries e custos adicionais com teto mensal humano positivo.
- Falta de writer único comprovado, armazenamento transacional alternativo ou secret isolado bloqueia implantação paga.

## 10. Migração, rollout e canary

1. Obter `review-sdd` e aprovação humana da SDD-0001 v1.3, `review-adr` e aceite humano desta ADR-0014 rev.2. Somente então a ADR-0013 rev.1 poderá mudar para `Superseded`, sem reescrever decisões originais.
2. Bootstrap em PR separado do dispatcher confiável, fila durável, writer global, Budget Broker, quota extra de fork, Trusted Publisher e reconciler; incluir `concurrency` global e auditoria de todos os mutadores.
3. Canary SEM API paga: testar fork, same-repo e Remediator, dois workers por `operation_key`, seis PRs competindo por teto, duplicatas, reruns, crashes, perda de pending job, readback de erro de API, rollover UTC e proposta stale descendente.
4. Critério crítico: tentativa de fast-forward com dados obsoletos (regressão 5→2) deve falhar no guard do writer ou motivar adoção de storage CAS server-side. É insuficiente que commits irmãos resultem 200/422.
5. Verificar que escritor privilegiado da `main` não executa código de fork nem expõe secrets; `OPENAI_API_KEY` somente no Budget Broker. Sem guardas completos, canary pago não inicia.
6. Apenas depois de todos os gates, modelo/preços/tetos humanos e CODEX-01 final, permitir canary pago controlado em escopo restrito. `DONE_ALLOWED`/PHASE-0-G continuam bloqueados até validação real pós-merge.

## 11. Rollback

- Desabilitar chamadas pagas e retornar Mode A interativo se a exclusão de writer/ledger/segredo não puder ser demonstrada.
- Nunca liberar automaticamente reservas ambíguas nem sobrescrever ledger a partir de snapshot obsoleto.
- Preservar journal e auditoria para reconciliação humana; rollback de código não implica desfazer gasto.

## 12. Relação com decisões existentes

- ADR-0013 rev.1: `Accepted`, vigente enquanto esta ADR estiver `Proposed`. O conteúdo decisório aceito não foi editado; transição a `Superseded` só depois do aceite desta sucessora.
- ADR-0012 rev.7: `Superseded`, decisão histórica preservada.
- ADR-0010: mantém merge humano obrigatório, CI e gates.
- SDD-0001 v1.3: mesma versão/contrato proposta para aprovação humana independente.

## 13. Pareceres dos especialistas impactados

| Especialista | Avaliação documental | Evidência faltante antes do canary pago |
| --- | --- | --- |
| Security | Escopo arquitetural revisável | Isolamento de token, writer trusted e branch provenance reais |
| Platform & Observability | Requisitos especificados | Garantia de serialização global, crash recovery, backlog/durable ledger |
| QA & Quality | Cenários adversariais definidos | E2E contra regressão stale 5→2, 3 consumidores, UTC e idempotência |
| Backend / Frontend | Não aplicável | Sem feature de produto |

## 14. Riscos residuais e evidência externa

- Evidência real do CAS-Lab: [relatório](https://github.com/RamonRDR/SaaS-CAS-Lab/blob/main/docs/RESULTS_2026-10-09.md), [run com 15 jobs aprovados](https://github.com/RamonRDR/SaaS-CAS-Lab/actions/runs/37873320199); ambos com cleanup de refs. Os testes provaram concorrência de commits irmãos e refutaram CAS semântico de `force:false`.
- **Não comprovado:** exclusão global de writer de produção em todos os workflows/PRs do SaaS, durabilidade end-to-end da fila, recuperação real de falha de transporte, autorização sem duplicação e custo real da API. Esses são gates obrigatórios de bootstrap/canary, NÃO riscos implicitamente aceitos.
- Nenhuma mudança nesta ADR autoriza chamada paga ou merge sem decisão humana.

## 15. Histórico de revisão

| Data | Responsável | Alteração | Estado |
| --- | --- | --- | --- |
| 2026-10-08 | Product & SDD | Proposta sucessora à ADR-0013 para corrigir reserva monetária antes de quota claim | rev.1 `Proposed` |
| 2026-10-09 | Product & SDD | Revisão material: claim universal, writer global e contraexemplo real CAS-Lab 5→2 | rev.2 `Proposed` |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pendente para rev.2
- **Revisão revisada:** Não aplicável até parecer técnico sobre rev.2
- **Revisor:** Orchestrator / Tech Lead
- **Data:** Pendente
- **Pendências bloqueantes:** revisar consistência de claim universal, Single-Writer Global, idempotência, UTC e evidência CAS-Lab; aceite humano posterior ainda pendente.
- **Pendências não bloqueantes:** implementação, canaries de writer global e orçamento/secret antes de API paga.

## 17. Aceite humano

- **Aceito:** Não
- **Responsável humano:** Ramon Rodriguez
- **Revisão aceita:** Não aplicável à rev.2 ainda proposta
- **Data:** Pendente
- **Registro:** Pendente. Aceite humano anterior da ADR-0013 rev.1 (#6070726649) não se estende à ADR-0014 rev.2.
