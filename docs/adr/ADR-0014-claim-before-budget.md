# ADR-0014 - Claim universal, ingresso durável e Single-Writer Global

## Metadados

- **ID:** ADR-0014
- **Título:** Claim universal, ingresso durável e Single-Writer Global
- **Status:** Proposed
- **Revisão decisória:** 4
- **Data de criação:** 2026-10-08
- **Última atualização:** 2026-10-09
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Ramon Rodriguez
- **SDDs relacionadas:** SDD-0001 v1.5
- **ADRs relacionados:** ADR-0013 rev.1 (`Accepted`, vigente); ADR-0012 rev.7 (`Superseded`); ADR-0010
- **PR / issue relacionada:** PR #2 / Issue #1

Nenhum agente de IA pode marcar esta ADR `Accepted`. A ADR-0013 permanece vigente enquanto esta sucessora estiver `Proposed`. O conteúdo decisório compreende as seções 1 a 14 e será imutável após o aceite.

## 1. Contexto

O CODEX-01 do HEAD `a58a1f7` identificou P1: CODEX-01 same-repo e Remediator não possuem claim para acessar Budget Broker; e P2: rollover UTC tenta novo claim apesar de `CONSUMED` ser imutável. A versão anterior da ADR tratava claim de quota específico de fork e pressupunha `CAS` de ledger financeiro via Git ref.

A evidência real em `RamonRDR/SaaS-CAS-Lab`, [run #37873320199](https://github.com/RamonRDR/SaaS-CAS-Lab/actions/runs/37873320199), [relatório](https://github.com/RamonRDR/SaaS-CAS-Lab/blob/main/docs/RESULTS_2026-10-09.md), mostrou: dois runners independentes com commits irmãos obtiveram HTTP 200/422 (um vencedor) para claim e orçamento; um writer serializado reconciliou 4/4 reservas, 2 negadas; **contraexemplo:** Git aceitou HTTP 200 para commit fast-forward baseado em estado lógico antigo, regredindo geração do ledger 5→2, com `force:false`. Depois o teste restaurou o estado e apagou a ref efêmera. Logo `PATCH /git/refs force:false` NÃO implementa CAS transacional de dados.

A ADR-0013 rev.1 permanece `Accepted` e suas seções decisórias são imutáveis. Esta ADR-0014 rev.4 é proposta sucessora, ainda dependente de parecer e aceite humano.


O CODEX-01 do HEAD `a052482` identificou duas falhas P1 (writer financeiro não pode ser o único escritor de intents que precisam existir antes de acordá-lo; `workflow_dispatch` sem `ref: main` pode executar workflow da branch PR) e um P2 (claim imutável fica preso após crash estritamente pré-financeiro). Esta rev.3 especifica ingresso independente de orçamento, reentrada main-only e retomada fenced com prova negativa de efeitos. Sem alterar as decisões aceitas ADR-0012/0013.
### Três invariantes novos consolidados (Codex HEAD `133994b2eb`)

1. **Identidade de evidência distinta da identidade paga:** review `review_context_fingerprint=SHA256(canon(repo,pr,base_ref,merge_base_sha,head_sha,payload_digest))` só é válido para esse changeset. A operação paga CODEX-01 é deduplicada permanentemente por `repo/pr/head_sha/operation_kind` com `authorized_attempt=0`, inclusive same-repo. Mudança de base_ref, merge-base ou digest sem novo HEAD invalida a evidência, porém NÃO autoriza segundo review pago: exige novo HEAD. Avanço isolado do base_tip sem mudança do fingerprint só exige reconciliação dos demais gates.
2. **Cotação imutável da reserva:** cada reserva inclui `pricing_snapshot_digest` (versão/preço, modelo/operação, caps de input/output, requisições/retries e custos extras), máximo financeiro e período. O Budget Broker verifica exatamente esse snapshot e os limites que imporá à API antes do dispatch. Mudança posterior torna a autorização inválida e **bloqueia**, não reutiliza silenciosamente nem libera reserva duvidosa. Ajuste eventual só com prova inequívoca de não-dispatch, writer único, verificação conservadora do delta e registro idempotente, sem segunda operação paga.
3. **Uma tentativa de CODEX-01 por HEAD:** `authorized_attempt=0` para ambos fork e same-repo. Tentativa diferente é rejeitada antes de quota/claim/budget. Apenas Remediator pode usar tentativa autorizada distinta sob anti-loop.

Esses refinamentos fazem parte desta ADR ainda `Proposed`, não mudam a vigência histórica da ADR-0013 rev.1 e não autorizam código/IA paga antes de aceite humano e canary.

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
2. Reconciler trusted da `main` valida autor, schema, trust, PR/HEAD e fingerprint de changeset vinculado a base_ref/merge_base_sha/payload_digest, com paginação completa. Pode rederivar intents elegíveis de PR/HEAD se o ingresso faltar. Mesmo HEAD com fingerprint diferente invalida CODEX-01 clean anterior, mas não admite outra chamada paga: requer novo HEAD; base_tip avançado sem mudar fingerprint revalida apenas CI/mergeabilidade. Issues são dados, nunca instruções.
3. Writer global único recebe intents elegíveis e persiste um claim universal para fork/same-repo/Remediator: owner `consumer_run_id` + `fencing_epoch` sob `operation_key`. Quota fork `RESERVED → CONSUMED` é guarda adicional na mesma seção crítica, não outro claim. Ao recuperar crash comprovadamente pré-reserva, o escritor mantém claim original, incrementa epoch e revoga executor anterior, após prova negativa de reserva/autorização/dispatch e fim/expiração verificável do worker antigo; qualquer dúvida bloqueia.
4. Só executor do claim/`fencing_epoch` vigente pede budget. O writer persiste cotação imutável: `price_catalog_version`, modelo/operação, limites realmente impostos, máximo em minor units e `pricing_snapshot_digest` canônico. Reserva é idempotente por operation_key; um snapshot novo NÃO gera segunda autorização de chamada. `committed + outstanding_max + new_max <= budget_limit` é validado sob writer único, inclusive para delta eventual de repricing permitido apenas após prova inequívoca de não-dispatch. Epoch obsoleto não custa.
5. Antes da API, o Budget Broker com chave exclusiva confere claim/epoch, UTC e prova de não-envio, além da igualdade EXATA de modelo, preço/versionamento e limites/caps com `pricing_snapshot_digest` reservado. Configuração diferente bloqueia envio (`BLOCKED_REPRICE`), mantendo custo pessimista e sem retry implícito. Só então registra autorização durável e impõe esses caps à API. `SENT`/`AMBIGUOUS` bloqueiam duplicata. Dispatcher e scripts vêm somente da `main`.
6. Rollover UTC **não refaz claim lógico** nem quota `CONSUMED`. Se nenhuma chamada foi enviada comprovadamente, o mesmo vencedor pode solicitar reserva FINANCEIRA no novo mês, sob writer global e idempotência da operação; reserva antiga fica conservadoramente comprometida até conciliação terminal. Se não há prova de não-envio, fail-closed.
7. Erro/timeout de API GitHub é reconciliado por readback de identidade, geração e epoch. Mesmo HTTP 200 não implica versão lógica correta. Se reserva/dispatch pode ter ocorrido, não fazer takeover nem liberar teto por timeout.
8. Reconciler periódico consulta Issue inbox e PR/HEAD elegíveis, reconstitui ingressos perdidos, e acorda dispatcher confiável APENAS por `repository_dispatch` na default branch ou `workflow_dispatch` com `ref: main` explícito. Nunca executar workflow/script/configuração/secrets da branch PR, mesmo same-repo, nem acordar por commits do ledger.
9. Sem comprovação da exclusão global do writer, branch/trust safety, preço e limite aprovado, bloquear chamadas (`BLOCKED_EXTERNAL`/`HUMAN_DECISION_REQUIRED`). Merge do produto continua gate humano.

## 8. Modelo de dados e contrato

Não afeta schema de produto. **INBOX** é conjunto de comments machine-readable de Issue com provenance/PR/HEAD/operation_key; duplicatas são permitidas como intents, não operações pagas. **EVIDÊNCIA CODEX-01** inclui `review_context_fingerprint=SHA256(canon(repo,pr,base_ref,merge_base_sha,head_sha,payload_digest))` e `base_tip_sha` auditável. **LEDGER CANÔNICO** (somente writer global) contém claim, quota fork, `authorized_attempt` (zero em CODEX-01), executor/`fencing_epoch`, reserva financeira e `pricing_snapshot_digest` (catálogo/versão/preços/modelo/caps/retries/extras), período, máximo, geração e estado de dispatch/settlement. Claim único por operation_key não depende de fingerprint mutável nem de novos snapshots. Alterar owner só por fencing antes de efeito financeiro; não há ACID implícito entre Issue/Git refs.

## 9. Operação, custos e observabilidade

- Fonte para requests pendentes: inbox validado e PR/HEAD canônicos; fonte exclusiva para claim/quota/budget/dispatch: ledger do writer. Comentários e eventos NÃO autorizam gastos nem substituem ledger.
- Registrar vencedores e perdedores, geração antiga/nova, operação, budget, UTC, readback de retorno ambíguo, event sourcing e recusas.
- Guardar segredos exclusivamente em Budget Broker, nunca nos artefatos/modelo do fork.
- Calcular e PERSISTIR cotação imutável de preço/versão/caps/output/retries no `pricing_snapshot_digest`; conferir no dispatch antes da API, falhando fechado caso configure preço ou teto diferente. Idempotência por operação não é multiplicada por nova versão de preços.
- Falta de writer único comprovado, armazenamento transacional alternativo ou secret isolado bloqueia implantação paga.

## 10. Migração, rollout e canary

1. Obter `review-sdd` para SDD-0001 v1.5, `review-adr` para ADR-0014 rev.4 e aprovação/aceite humano explícitos. Só após aceitação da sucessora ADR-0013 rev.1 poderá mudar a `Superseded` sem reescrever a decisão histórica.
2. Bootstrap em PR separado: trusted intake com issues:write mínimo, Issue inbox, scanner de PR/HEAD, dispatcher `main`-only, writer global, Budget Broker, Quota Broker fork e Trusted Publisher. Audit tokens, branches/ref dispatch e todo mutador.
3. Canary SEM API paga: 3 consumidores, seis PRs, duplicatas intake, perda de wake-up, main-only dispatcher, takeover fenced, stale Git 5→2, UTC e readback; testes adicionais: mudança de base_ref/merge-base/digest no mesmo HEAD bloqueia CODEX-01 pago novo e invalida evidência anterior; alteração do catálogo/caps após reserva bloqueia dispatch; tentativa CODEX-01 >=1 é negada antes de custo.
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
- SDD-0001 v1.5: mesma proposta sincronizada, ainda em revisão; aprovação humana independente.

## 13. Pareceres dos especialistas impactados

| Especialista | Avaliação documental | Evidência faltante antes do canary pago |
| --- | --- | --- |
| Security | Escopo arquitetural revisável | Isolamento de token, writer trusted e branch provenance reais |
| Platform & Observability | Requisitos especificados | Garantia de serialização global, crash recovery, backlog/durable ledger |
| QA & Quality | Cenários adversariais definidos | E2E contra regressão stale 5→2, 3 consumidores, UTC e idempotência |
| Backend / Frontend | Não aplicável | Sem feature de produto |

## 14. Riscos residuais e evidência externa

- Evidência real do CAS-Lab: [relatório](https://github.com/RamonRDR/SaaS-CAS-Lab/blob/main/docs/RESULTS_2026-10-09.md), [run com 15 jobs aprovados](https://github.com/RamonRDR/SaaS-CAS-Lab/actions/runs/37873320199); ambos com cleanup de refs. Os testes provaram concorrência de commits irmãos e refutaram CAS semântico de `force:false`.
- **Não comprovado:** intake/serialização real no SaaS, main-only dispatcher sob eventos adversariais, fencing, crashes de transporte, preço real, reruns e alterações efetivas de merge-base ou caps. Os novos invariantes exigem canary/validação antes de habilitar IA paga, não constituem risco aceito.
- Nenhuma mudança nesta ADR autoriza chamada paga ou merge sem decisão humana.

## 15. Histórico de revisão

| Data | Responsável | Alteração | Estado |
| --- | --- | --- | --- |
| 2026-10-08 | Product & SDD | Proposta sucessora à ADR-0013 para corrigir reserva monetária antes de quota claim | rev.1 `Proposed` |
| 2026-10-09 | Product & SDD | Revisão material: claim universal, writer global e contraexemplo CAS-Lab 5→2 | rev.2 `Proposed` |
| 2026-10-09 | Product & SDD | P1/P1/P2: ingresso independente, dispatch main-only e fencing pré-financeiro | rev.3 `Proposed` |
| 2026-10-09 | Product & SDD | P1/P1/P2: fingerprint de changeset, preço/caps congelados e CODEX-01 attempt=0 | rev.4 `Proposed` |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pendente para revisão decisória rev.4 e HEAD final
- **Revisão revisada:** Não aplicável até review da rev.4
- **Revisor:** Orchestrator / Tech Lead
- **Data:** Pendente
- **Pendências bloqueantes:** validar os três invariantes de identidade de changeset, snapshot financeiro e tentativa fixa; review técnico e aceite humano pendentes.
- **Pendências não bloqueantes:** implementação, canaries de writer global e orçamento/secret antes de API paga.

## 17. Aceite humano

- **Aceito:** Não
- **Responsável humano:** Ramon Rodriguez
- **Revisão aceita:** Não aplicável à rev.4 proposta
- **Data:** Pendente
- **Registro:** Aceite humano pendente para rev.4. ADR-0013 rev.1 Accepted (#6070726649) não é substituída antecipadamente.
