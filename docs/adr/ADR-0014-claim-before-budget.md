# ADR-0014 - Claim universal, ingresso durável e Single-Writer Global

## Metadados

- **ID:** ADR-0014
- **Título:** Claim universal, ingresso durável e Single-Writer Global
- **Status:** Proposed
- **Revisão decisória:** 3
- **Data de criação:** 2026-10-08
- **Última atualização:** 2026-10-09
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Ramon Rodriguez
- **SDDs relacionadas:** SDD-0001 v1.4
- **ADRs relacionados:** ADR-0013 rev.1 (`Accepted`, vigente); ADR-0012 rev.7 (`Superseded`); ADR-0010
- **PR / issue relacionada:** PR #2 / Issue #1

Nenhum agente de IA pode marcar esta ADR `Accepted`. A ADR-0013 permanece vigente enquanto esta sucessora estiver `Proposed`. O conteúdo decisório compreende as seções 1 a 14 e será imutável após o aceite.

## 1. Contexto

O CODEX-01 do HEAD `a58a1f7` identificou P1: CODEX-01 same-repo e Remediator não possuem claim para acessar Budget Broker; e P2: rollover UTC tenta novo claim apesar de `CONSUMED` ser imutável. A versão anterior da ADR tratava claim de quota específico de fork e pressupunha `CAS` de ledger financeiro via Git ref.

A evidência real em `RamonRDR/SaaS-CAS-Lab`, [run #37873320199](https://github.com/RamonRDR/SaaS-CAS-Lab/actions/runs/37873320199), [relatório](https://github.com/RamonRDR/SaaS-CAS-Lab/blob/main/docs/RESULTS_2026-10-09.md), mostrou: dois runners independentes com commits irmãos obtiveram HTTP 200/422 (um vencedor) para claim e orçamento; um writer serializado reconciliou 4/4 reservas, 2 negadas; **contraexemplo:** Git aceitou HTTP 200 para commit fast-forward baseado em estado lógico antigo, regredindo geração do ledger 5→2, com `force:false`. Depois o teste restaurou o estado e apagou a ref efêmera. Logo `PATCH /git/refs force:false` NÃO implementa CAS transacional de dados.

A ADR-0013 rev.1 permanece `Accepted` e suas seções decisórias são imutáveis. Esta ADR-0014 rev.3 é proposta sucessora, ainda dependente de parecer e aceite humano.


O CODEX-01 do HEAD `a052482` identificou duas falhas P1 (writer financeiro não pode ser o único escritor de intents que precisam existir antes de acordá-lo; `workflow_dispatch` sem `ref: main` pode executar workflow da branch PR) e um P2 (claim imutável fica preso após crash estritamente pré-financeiro). Esta rev.3 especifica ingresso independente de orçamento, reentrada main-only e retomada fenced com prova negativa de efeitos. Sem alterar as decisões aceitas ADR-0012/0013.
## 2. Drivers da decisão

- Todos os consumidores de IA paga precisam de claim exclusivo e orçamento sem exceções same-repo.
- Um único ledger mensal global deve impedir dupla reserva e gasto acima do teto sob concorrência entre PRs/workflows.
- Crash, reentrada, falha de transporte e rollover UTC não podem converter incerteza em nova chamada paga.
- Repositório público: zero segredo em fork/reviewer/Remediator/Trusted Publisher; broker isolado trusted da `main`.
- Governança, provenance, human gates e anti-loop prevalecem; arquitetura ≠ prova de runtime operacional.

## 3. Restrições

- Sem mudança de domínio do SaaS, Flutter, banco de produto ou PHASE-0-G.
- Não confiar em `concurrency` por PR/grupo global, pending Actions, Git force:false ou comentários como storage financeiro transacional; Issue inbox guarda somente intents, não autorização de gasto.
- Não pressupor duas refs Git atômicas entre quota/claim/budget; o escritor global é o ÚNICO decisor de mutações financeiras e claims.
- O token privilegiado do **intake** possui `issues:write` e `contents:read`, sem `contents:write` nem chave OpenAI. Pode criar comentários no Issue dedicado de inbox e precisa ser trusted da `main`, sem executar nada de PR/fork. Writer de claim/budget tem identidade de escrita separada; permissão é por repositório, então proteger origem dos jobs.
- Sem prova de exclusão durável, ledger íntegro, preço, orçamento humano e despacho autorizado, NENHUMA API paga está habilitada.

## 4. Opções consideradas

### A - Budget antes do claim

Rejeitada: consumidores perdedores comprometem orçamento e podem consumir o teto sem chamada.

### B - Quota claim de fork e Git ref `force:false` como CAS financeiro

Rejeitada como solução global: deixa same-repo sem claim e a prova negativa do CAS-Lab demonstrou sobrescrita fast-forward de snapshot stale (geração 5→2).

### C - Dois ledgers independentes com suposta transação atômica

Rejeitada sem transação distribuída comprovada; crash entre refs cria ambiguidade e risco de inconsistência.

### D - Intake mínimo durable + Writer Global Único + claim universal (escolhida)

Todos os consumidores fazem ingresso via workflow trusted da `main`, com permissão mínima de comentar Issue de inbox, **antes** do wake-up. Esse ingresso NÃO altera ledger de claim/finanças e um scanner periódico recupera intents ausentes enumerando PR/HEAD atuais. Apenas o writer global trusted, efetivamente serializado, aplica trust/quota extra de fork, claim lógico e budget; revalida valores sob exclusão e relê após resposta ambígua. A reentrada é sempre `repository_dispatch` no default branch ou `workflow_dispatch` explicitamente com `ref: main`. Após crash comprovadamente anterior a toda reserva, autorização e envio, pode transferir executor do MESMO claim por epoch/fencing. Sem prova, bloquear.

## 5. Decisão proposta

- **Opção:** D. Intake mínimo com inbox persistido antes do wake-up; claim universal e escritor financeiro global único; dispatch main-only; takeover pré-financeiro com fencing e Budget Broker exclusivo.
- **Motivo:** corrige P1/P1/P2 da última revisão sem relaxar o controle de custo nem confiar em atomicidade Git não demonstrada; separa persistência da solicitação, exclusividade financeira e execução do consumidor.
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
- O job pending do Actions pode ser substituído, por isso o ingresso em inbox GitHub é independente do writer e precede o wake-up; scanner periódico também rederiva intents elegíveis se o próprio evento/ingresso falhar.
- Crash entre claim e gasto requer distinguir pré-reserva comprovado (takeover fenced seguro sem segundo claim) de qualquer estado financeiro/dispatch ambíguo (bloqueio conservador).
- Storage Git é permitido SOMENTE se o canary demonstrar exclusão efetiva, monotonicidade lógica, recuperação e ausência de concorrente alternativo; caso contrário requer backend transacional.

## 7. Segurança e protocolo de execução

1. O trusted intake da `main` persiste comentário JSON machine-readable em Issue de inbox dedicado, com `issues:write` e `contents:read` SOMENTE, sem secret de IA/checkout/execução de código PR. Identidade `operation_key=repo/pr/head_sha/operation_kind/authorized_attempt` é estável e não inclui run ID; readback confirma persistência ANTES do wake-up. Retry pode duplicar comentário, nunca operação.
2. Reconciler trusted da `main` valida autor do ingresso, schema, PR, HEAD, estado, trust gate e quota extra para fork, com paginação completa. Também varre PRs elegíveis para reconstruir solicitações que não chegaram ao inbox. Conteúdo do Issue é dado não confiável, não instrução; comentários inválidos/truncados falham fechados.
3. Writer global único recebe intents elegíveis e persiste um claim universal para fork/same-repo/Remediator: owner `consumer_run_id` + `fencing_epoch` sob `operation_key`. Quota fork `RESERVED → CONSUMED` é guarda adicional na mesma seção crítica, não outro claim. Ao recuperar crash comprovadamente pré-reserva, o escritor mantém claim original, incrementa epoch e revoga executor anterior, após prova negativa de reserva/autorização/dispatch e fim/expiração verificável do worker antigo; qualquer dúvida bloqueia.
4. Só o executor atual do mesmo claim com `fencing_epoch` vigente pode pedir budget. O writer financeiro revalida epoch e ledger antes de gravar, e Budget Broker verifica novamente epoch antes de dispatch. Reservas idempotentes respeitam `committed + outstanding_max + new_max <= budget_limit`, sem recontagem por rerun. Epoch antigo nunca gera custo.
5. Antes da API, Budget Broker trusted com chave exclusiva valida claim/epoch, grava autorização durável de dispatch, confere UTC e prova de não-envio. `SENT`/`AMBIGUOUS` ou evidência insuficiente bloqueiam retry. Toda reentrada do dispatcher passa pela `main` confiável, jamais por workflow alterado em branch PR.
6. Rollover UTC **não refaz claim lógico** nem quota `CONSUMED`. Se nenhuma chamada foi enviada comprovadamente, o mesmo vencedor pode solicitar reserva FINANCEIRA no novo mês, sob writer global e idempotência da operação; reserva antiga fica conservadoramente comprometida até conciliação terminal. Se não há prova de não-envio, fail-closed.
7. Erro/timeout de API GitHub é reconciliado por readback de identidade, geração e epoch. Mesmo HTTP 200 não implica versão lógica correta. Se reserva/dispatch pode ter ocorrido, não fazer takeover nem liberar teto por timeout.
8. Reconciler periódico consulta Issue inbox e PR/HEAD elegíveis, reconstitui ingressos perdidos, e acorda dispatcher confiável APENAS por `repository_dispatch` na default branch ou `workflow_dispatch` com `ref: main` explícito. Nunca executar workflow/script/configuração/secrets da branch PR, mesmo same-repo, nem acordar por commits do ledger.
9. Sem comprovação da exclusão global do writer, branch/trust safety, preço e limite aprovado, bloquear chamadas (`BLOCKED_EXTERNAL`/`HUMAN_DECISION_REQUIRED`). Merge do produto continua gate humano.

## 8. Modelo de dados e contrato

Não afeta schema de domínio do SaaS. **INBOX** são comentários GitHub de Issue exclusivo de controle com provenance, schema, operation_key e metadados PR/HEAD, podendo haver duplicatas lógicas. **LEDGER CANÔNICO**, gravado só pelo writer global, contém claim, quota fork, `consumer_run_id`, `fencing_epoch`, reservas, período, geração, custo e estado de envio. Alterar owner de execução apenas com epoch incrementado antes de efeitos financeiros. Nenhuma atomicidade ACID entre Issue comments e Git ref é assumida; reconciler deduplica e recuperação é fail-closed.

## 9. Operação, custos e observabilidade

- Fonte para requests pendentes: inbox validado e PR/HEAD canônicos; fonte exclusiva para claim/quota/budget/dispatch: ledger do writer. Comentários e eventos NÃO autorizam gastos nem substituem ledger.
- Registrar vencedores e perdedores, geração antiga/nova, operação, budget, UTC, readback de retorno ambíguo, event sourcing e recusas.
- Guardar segredos exclusivamente em Budget Broker, nunca nos artefatos/modelo do fork.
- Limitar custo por input/output tokens, preço versionado, modelo, tamanho, retries e custos adicionais com teto mensal humano positivo.
- Falta de writer único comprovado, armazenamento transacional alternativo ou secret isolado bloqueia implantação paga.

## 10. Migração, rollout e canary

1. Obter `review-sdd` e aprovação humana da SDD-0001 v1.4, `review-adr` e aceite humano desta ADR-0014 rev.3. Somente então a ADR-0013 rev.1 poderá mudar para `Superseded`, sem reescrever decisões originais.
2. Bootstrap em PR separado: trusted intake com issues:write mínimo, Issue inbox, scanner de PR/HEAD, dispatcher `main`-only, writer global, Budget Broker, Quota Broker fork e Trusted Publisher. Audit tokens, branches/ref dispatch e todo mutador.
3. Canary SEM API paga: 3 consumidores, seis PRs, dois ingressos duplicados, perda de evento antes do ingresso, pending substituído, `workflow_dispatch` ref de PR negado, provenance de comentário malicioso, takeover pré-financeiro com fencing stale worker, timeout ambíguo sem takeover, CAS-Lab stale 5→2, UTC e readback.
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
- SDD-0001 v1.4: mesma versão/contrato proposta para aprovação humana independente.

## 13. Pareceres dos especialistas impactados

| Especialista | Avaliação documental | Evidência faltante antes do canary pago |
| --- | --- | --- |
| Security | Escopo arquitetural revisável | Isolamento de token, writer trusted e branch provenance reais |
| Platform & Observability | Requisitos especificados | Garantia de serialização global, crash recovery, backlog/durable ledger |
| QA & Quality | Cenários adversariais definidos | E2E contra regressão stale 5→2, 3 consumidores, UTC e idempotência |
| Backend / Frontend | Não aplicável | Sem feature de produto |

## 14. Riscos residuais e evidência externa

- Evidência real do CAS-Lab: [relatório](https://github.com/RamonRDR/SaaS-CAS-Lab/blob/main/docs/RESULTS_2026-10-09.md), [run com 15 jobs aprovados](https://github.com/RamonRDR/SaaS-CAS-Lab/actions/runs/37873320199); ambos com cleanup de refs. Os testes provaram concorrência de commits irmãos e refutaram CAS semântico de `force:false`.
- **Não comprovado:** garantia operacional de intake `issues:write` seguro, scanner de PR/HEAD, main-only dispatcher sob eventos adversariais, fencing entre workers e writer real do SaaS, crashes/transporte real e custo API. Todos exigem canary/validação antes da execução paga, não são risco já aceito.
- Nenhuma mudança nesta ADR autoriza chamada paga ou merge sem decisão humana.

## 15. Histórico de revisão

| Data | Responsável | Alteração | Estado |
| --- | --- | --- | --- |
| 2026-10-08 | Product & SDD | Proposta sucessora à ADR-0013 para corrigir reserva monetária antes de quota claim | rev.1 `Proposed` |
| 2026-10-09 | Product & SDD | Revisão material: claim universal, writer global e contraexemplo CAS-Lab 5→2 | rev.2 `Proposed` |
| 2026-10-09 | Product & SDD | P1/P1/P2: intake independente, dispatch main-only e takeover pré-financeiro fenced | rev.3 `Proposed` |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pendente, revisão decisória rev.3
- **Revisão revisada:** Ainda não revisada, rev.3 proposta
- **Revisor:** Orchestrator / Tech Lead
- **Data:** Pendente
- **Pendências bloqueantes:** validar segurança/provenance do ingresso, main-only dispatch e prova de no-send com epoch/fencing, além de revisão/aceite humano.
- **Pendências não bloqueantes:** implementação, canaries de writer global e orçamento/secret antes de API paga.

## 17. Aceite humano

- **Aceito:** Não
- **Responsável humano:** Ramon Rodriguez
- **Revisão aceita:** Não aplicável à rev.3 proposta
- **Data:** Pendente
- **Registro:** Aceite pendente para rev.3. ADR-0013 rev.1 (#6070726649) não autoriza esta decisão.
