# ADR-0014 - Claim universal, ingresso durável e Single-Writer Global

## Metadados

- **ID:** ADR-0014
- **Título:** Claim universal, ingresso durável e Single-Writer Global
- **Status:** Accepted
- **Revisão decisória:** 5
- **Data de criação:** 2026-10-08
- **Última atualização:** 2026-10-09
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Ramon Rodriguez
- **SDDs relacionadas:** SDD-0001 v1.6
- **ADRs relacionados:** ADR-0013 rev.1 (`Superseded`, histórica); ADR-0012 rev.7 (`Superseded`); ADR-0010
- **PR / issue relacionada:** PR #2 / Issue #1

Esta ADR chegou a `Accepted` por decisão humana expressa em ChatGPT, registrada no PR #2 comentário #6091567757. Nenhum agente aceitou a decisão por conta própria. A ADR-0013 rev.1 passa a `Superseded`. As seções decisórias 1 a 14 são imutáveis após o aceite.

## 1. Contexto

O CODEX-01 do HEAD `a58a1f7` identificou P1: CODEX-01 same-repo e Remediator não possuem claim para acessar Budget Broker; e P2: rollover UTC tenta novo claim apesar de `CONSUMED` ser imutável. A versão anterior da ADR tratava claim de quota específico de fork e pressupunha `CAS` de ledger financeiro via Git ref.

A evidência real em `RamonRDR/SaaS-CAS-Lab`, [run #37873320199](https://github.com/RamonRDR/SaaS-CAS-Lab/actions/runs/37873320199), [relatório](https://github.com/RamonRDR/SaaS-CAS-Lab/blob/main/docs/RESULTS_2026-10-09.md), mostrou: dois runners independentes com commits irmãos obtiveram HTTP 200/422 (um vencedor) para claim e orçamento; um writer serializado reconciliou 4/4 reservas, 2 negadas; **contraexemplo:** Git aceitou HTTP 200 para commit fast-forward baseado em estado lógico antigo, regredindo geração do ledger 5→2, com `force:false`. Depois o teste restaurou o estado e apagou a ref efêmera. Logo `PATCH /git/refs force:false` NÃO implementa CAS transacional de dados.

A ADR-0013 rev.1 foi `Accepted` historicamente, mas agora está `Superseded` pela sucessora ADR-0014 rev.5; suas seções decisórias seguem imutáveis. Esta ADR-0014 rev.5 foi aceita após parecer técnico e decisão humana registrada no PR #2; seu aceite não autoriza execução paga sem canary.


O CODEX-01 do HEAD `a052482` identificou duas falhas P1 (writer financeiro não pode ser o único escritor de intents que precisam existir antes de acordá-lo; `workflow_dispatch` sem `ref: main` pode executar workflow da branch PR) e um P2 (claim imutável fica preso após crash estritamente pré-financeiro). Esta rev.3 especifica ingresso independente de orçamento, reentrada main-only e retomada fenced com prova negativa de efeitos. Sem alterar as decisões aceitas ADR-0012/0013.
### Três invariantes novos consolidados (Codex HEAD `133994b2eb`)

1. **Identidade de evidência distinta da identidade paga:** review `review_context_fingerprint=SHA256(canon(repo,pr,base_ref,merge_base_sha,head_sha,payload_digest))` só é válido para esse changeset. A operação paga CODEX-01 é deduplicada permanentemente por `repo/pr/head_sha/operation_kind` com `authorized_attempt=0`, inclusive same-repo. Mudança de base_ref, merge-base ou digest sem novo HEAD invalida a evidência, porém NÃO autoriza segundo review pago: exige novo HEAD. Avanço isolado do base_tip sem mudança do fingerprint só exige reconciliação dos demais gates.
2. **Cotação imutável da reserva:** cada reserva inclui `pricing_snapshot_digest` (versão/preço, modelo/operação, caps de input/output, requisições/retries e custos extras), máximo financeiro e período. O Budget Broker verifica exatamente esse snapshot e os limites que imporá à API antes do dispatch. Mudança posterior torna a autorização inválida e **bloqueia**, não reutiliza silenciosamente nem libera reserva duvidosa. Ajuste eventual só com prova inequívoca de não-dispatch, writer único, verificação conservadora do delta e registro idempotente, sem segunda operação paga.
3. **Uma tentativa de CODEX-01 por HEAD:** `authorized_attempt=0` para ambos fork e same-repo. Tentativa diferente é rejeitada antes de quota/claim/budget. Apenas Remediator pode usar tentativa autorizada distinta sob anti-loop.

Esses refinamentos integram a ADR-0014 rev.5 aceita; a decisão anterior da ADR-0013 rev.1 é histórica, e nenhuma chamada paga pode ocorrer antes dos canaries.

### Dois invariantes adicionais identificados no CODEX-01 do HEAD `9ca3248`

- **Contrato confiável de review:** o mesmo changeset pode produzir decisão distinta quando workflow, prompt, schema, parser, policy, modelo ou dependências executáveis do CODEX-01 forem alterados na `main`. Calcular `trusted_review_contract_digest` de manifest canônico e **completo de dependências transitivas efetivamente carregadas**, incluindo conteúdo/versões, e incorporá-lo ao `review_context_fingerprint`. A decisão READY revalida a revisão confiável atual; evidence clean de contrato antigo é inválida. Se CODEX-01 já foi pago para aquele HEAD, requer novo HEAD antes de outra inferência, preservando uma chamada por SHA. Mudança de `main_source_commit_sha` sem alteração do digest da closure não força nova inferência.
- **Identidade específica de causa do Remediator:** `operation_key` do Remediator inclui `root_cause_family_id` normalizado pelo trusted reducer, além de HEAD e `authorized_attempt`. Duas causas independentes podem ambas estar em attempt=0 no mesmo HEAD sem colisão. O contador anti-loop é conservado por causa/repo/PR **entre HEADs** e escala após três correções repetidas sem progresso; mensagens reformatadas ou novos commits não zeram tentativas. Classificação ambígua falha fechada e exige revisão/decisão humana.

Ambos integram a rev.5 aceita, sucessora da ADR-0013 rev.1; não habilitam execução paga antes dos canaries e gates próprios.

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

## 5. Decisão aceita

- **Opção:** D. Trusted intake com inbox durável; claim universal e writer financeiro global; review fingerprint de changeset + contrato trusted; Remediator por root_cause_family_id, dispatch main-only e fencing; orçamento de preço/caps imutáveis.
- **Motivo:** mantém exclusividade financeira/segurança e resolve os achados P1/P2 adicionais sem abrir nova arquitetura: evidência de review sempre ligada ao contrato trusted vigente e tentativas do Remediator isoladas por causa raiz estável.
- **Limite importante:** `concurrency.group` global, com `cancel-in-progress:false`, é controle operacional auxiliar de exclusão, mas **não é fila durável nem transação**. Ao habilitar execução paga, testar que TODO workflow mutador compartilha exclusivamente a mesma região crítica e que nenhuma execução paralela ou bypass existe. Se GitHub não comprovar, trocar backend antes de cobrar.

Esta decisão foi aceita pelo humano em 2026-10-09 (PR #2 comentário #6091567757); os controles de gastos e os canaries continuam obrigatórios antes de ativação.

## 6. Consequências

### Positivas

- Quota de autor/PR é guarda ADICIONAL só para fork. CODEX-01 same-repo e Remediator recebem claim universal sem depender da quota de fork.
- Chave lógica estável impede duplicatas: CODEX-01 por PR/HEAD com attempt 0; Remediator por PR/HEAD/família de causa/tentativa, com anti-loop por família entre HEADs. Evidência clean revalidada por fingerprint de changeset + contrato trusted.
- Writer único reduz superfícies concorrentes e permite orçamento global em um único limite conservador.
- Incerteza vira bloqueio auditável e não repetição automática de pagamento.

### Trade-offs

- Writer único limita throughput e exige drainer/reconciler e backpressure.
- O job pending do Actions pode ser substituído, por isso o ingresso em inbox GitHub é independente do writer e precede o wake-up; scanner periódico também rederiva intents elegíveis se o próprio evento/ingresso falhar.
- Crash entre claim e gasto requer distinguir pré-reserva comprovado (takeover fenced seguro sem segundo claim) de qualquer estado financeiro/dispatch ambíguo (bloqueio conservador).
- Storage Git é permitido SOMENTE se o canary demonstrar exclusão efetiva, monotonicidade lógica, recuperação e ausência de concorrente alternativo; caso contrário requer backend transacional.

## 7. Segurança e protocolo de execução

1. Trusted intake na main grava Issue inbox JSON antes do wake-up com issues:write mínimo; identidade de operação específica do consumidor: CODEX-01 `repo/pr/head/CODEX_01/0`, Remediator `repo/pr/head/REMEDIATOR/root_cause_family_id/authorized_attempt`, sem workflow_run_id. A família é calculada e validada pelo reducer trusted a partir de evidência estruturada de CI/finding, sem aceitar ID arbitrário de mensagem, e mantém contador entre HEADs. Duplicatas de inbox não criam chamadas.
2. Reconciler trusted da main verifica provenance, schema, PR/HEAD e revisão efetiva do changeset **e do contrato de review**. O reviewer obtém manifest `trusted_review_contract_digest=SHA256(canon(workflow,prompt,schema,parser,policy,modelo,configuração e dependências transitivas efetivamente carregadas))` com SHAs do código/config trusted da main, e `review_context_fingerprint=SHA256(canon(repo,pr,base_ref,merge_base_sha,head_sha,payload_digest,trusted_review_contract_digest))`. Verifica digest de contrato atual ANTES de aceitar READY. Novo contrato/changeset com mesmo HEAD invalida clean antigo; se já houve chamada paga, só novo HEAD permite outra. Base_tip sozinho não invalida se fingerprint idêntico, mas requer reconciliação CI/mergeabilidade.
3. Writer global único aceita intents elegíveis, aplica claim universal e quota adicional fork. CODEX-01 tem `authorized_attempt=0`, uma chamada por PR/HEAD. Remediator opera por `root_cause_family_id` confiável com contador de até três tentativas da mesma causa entre HEADs; duas causas distintas são independentes, rephrasing da mesma causa não reinicia contador. Executor `consumer_run_id`/`fencing_epoch` pode mudar somente por takeover comprovadamente pré-financeiro; incerteza bloqueia.
4. Só executor do claim/`fencing_epoch` vigente pede budget. O writer persiste cotação imutável: `price_catalog_version`, modelo/operação, limites realmente impostos, máximo em minor units e `pricing_snapshot_digest` canônico. Reserva é idempotente por operation_key; um snapshot novo NÃO gera segunda autorização de chamada. `committed + outstanding_max + new_max <= budget_limit` é validado sob writer único, inclusive para delta eventual de repricing permitido apenas após prova inequívoca de não-dispatch. Epoch obsoleto não custa.
5. Antes da API, o Budget Broker com chave exclusiva confere claim/epoch, UTC e prova de não-envio, além da igualdade EXATA de modelo, preço/versionamento e limites/caps com `pricing_snapshot_digest` reservado. Configuração diferente bloqueia envio (`BLOCKED_REPRICE`), mantendo custo pessimista e sem retry implícito. Só então registra autorização durável e impõe esses caps à API. `SENT`/`AMBIGUOUS` bloqueiam duplicata. Dispatcher e scripts vêm somente da `main`.
6. Rollover UTC **não refaz claim lógico** nem quota `CONSUMED`. Se nenhuma chamada foi enviada comprovadamente, o mesmo vencedor pode solicitar reserva FINANCEIRA no novo mês, sob writer global e idempotência da operação; reserva antiga fica conservadoramente comprometida até conciliação terminal. Se não há prova de não-envio, fail-closed.
7. Erro/timeout de API GitHub é reconciliado por readback de identidade, geração e epoch. Mesmo HTTP 200 não implica versão lógica correta. Se reserva/dispatch pode ter ocorrido, não fazer takeover nem liberar teto por timeout.
8. Reconciler periódico consulta Issue inbox e PR/HEAD elegíveis, reconstitui ingressos perdidos, e acorda dispatcher confiável APENAS por `repository_dispatch` na default branch ou `workflow_dispatch` com `ref: main` explícito. Nunca executar workflow/script/configuração/secrets da branch PR, mesmo same-repo, nem acordar por commits do ledger.
9. Sem comprovação da exclusão global do writer, branch/trust safety, preço e limite aprovado, bloquear chamadas (`BLOCKED_EXTERNAL`/`HUMAN_DECISION_REQUIRED`). Merge do produto continua gate humano.

## 8. Modelo de dados e contrato

Não afeta schema de produto. INBOX é Issue comments machine-readable com provenance e intenção. EVIDÊNCIA CODEX-01 fixa base_ref/merge_base/head/payload_digest e `trusted_review_contract_digest` da closure de workflow/prompt/schema/parser/policy/modelo/dependências da main (com `main_source_commit_sha` auditável). LEDGER CANÔNICO contém claim, quota fork, `operation_kind`, `authorized_attempt=0` para CODEX-01 ou `root_cause_family_id` para Remediator, contador anti-loop durável por família/repo/PR, `consumer_run_id`, fencing_epoch, reservas financeiras, pricing_snapshot_digest, período e estado de dispatch. Nenhuma garantia ACID indevida por Git ref, nenhuma execução de PR/fork no trusted intake.

## 9. Operação, custos e observabilidade

- Fonte para requests pendentes: inbox validado e PR/HEAD canônicos; fonte exclusiva para claim/quota/budget/dispatch: ledger do writer. Comentários e eventos NÃO autorizam gastos nem substituem ledger.
- Registrar vencedores e perdedores, geração antiga/nova, operação, budget, UTC, readback de retorno ambíguo, event sourcing e recusas.
- Guardar segredos exclusivamente em Budget Broker, nunca nos artefatos/modelo do fork.
- Calcular e PERSISTIR cotação imutável de preço/versão/caps/output/retries no `pricing_snapshot_digest`; conferir no dispatch antes da API, falhando fechado caso configure preço ou teto diferente. Idempotência por operação não é multiplicada por nova versão de preços.
- Falta de writer único comprovado, armazenamento transacional alternativo ou secret isolado bloqueia implantação paga.

## 10. Migração, rollout e canary

1. Após aprovação humana da SDD-0001 v1.6 e aceite da ADR-0014 rev.5, registrar sucessão da ADR-0013 rev.1 em metadados e histórico, preservando suas seções decisórias originais.
2. Bootstrap em PR separado: trusted intake com issues:write mínimo, Issue inbox, scanner de PR/HEAD, dispatcher `main`-only, writer global, Budget Broker, Quota Broker fork e Trusted Publisher. Audit tokens, branches/ref dispatch e todo mutador.
3. Canary SEM API paga: três consumidores e seis PRs, concorrência, error readback, FIFO/reconciler sem fila implicitamente durável, trusted main, UTC/fencing, fast-forward stale 5→2, alteração de preços/caps; ADICIONALMENTE: alterar workflow, prompt, schema e dependência transitiva do reviewer na main após clean e exigir invalidação de READY, sem segunda IA paga no mesmo HEAD; duas causas distintas de Remediator no mesmo HEAD/tentativa 0 geram chaves diferentes e mesma causa entre HEADs conserva 3-attempt anti-loop.
4. Critério crítico: tentativa de fast-forward com dados obsoletos (regressão 5→2) deve falhar no guard do writer ou motivar adoção de storage CAS server-side. É insuficiente que commits irmãos resultem 200/422.
5. Verificar que escritor privilegiado da `main` não executa código de fork nem expõe secrets; `OPENAI_API_KEY` somente no Budget Broker. Sem guardas completos, canary pago não inicia.
6. Apenas depois de todos os gates, modelo/preços/tetos humanos e CODEX-01 final, permitir canary pago controlado em escopo restrito. `DONE_ALLOWED`/PHASE-0-G continuam bloqueados até validação real pós-merge.

## 11. Rollback

- Desabilitar chamadas pagas e retornar Mode A interativo se a exclusão de writer/ledger/segredo não puder ser demonstrada.
- Nunca liberar automaticamente reservas ambíguas nem sobrescrever ledger a partir de snapshot obsoleto.
- Preservar journal e auditoria para reconciliação humana; rollback de código não implica desfazer gasto.

## 12. Relação com decisões existentes

- ADR-0013 rev.1: `Superseded` por esta ADR-0014 rev.5 aceita; decisões históricas não foram reescritas.
- ADR-0012 rev.7: `Superseded`, decisão histórica preservada.
- ADR-0010: mantém merge humano obrigatório, CI e gates.
- SDD-0001 v1.6: `Approved` como especificação, permanecendo gates de implementação/canary antes de uso pago.

## 13. Pareceres dos especialistas impactados

| Especialista | Avaliação documental | Evidência faltante antes do canary pago |
| --- | --- | --- |
| Security | Escopo arquitetural revisável | Isolamento de token, writer trusted e branch provenance reais |
| Platform & Observability | Requisitos especificados | Garantia de serialização global, crash recovery, backlog/durable ledger |
| QA & Quality | Cenários adversariais definidos | E2E contra regressão stale 5→2, 3 consumidores, UTC e idempotência |
| Backend / Frontend | Não aplicável | Sem feature de produto |

## 14. Riscos residuais e evidência externa

- Evidência real do CAS-Lab: [relatório](https://github.com/RamonRDR/SaaS-CAS-Lab/blob/main/docs/RESULTS_2026-10-09.md), [run com 15 jobs aprovados](https://github.com/RamonRDR/SaaS-CAS-Lab/actions/runs/37873320199); ambos com cleanup de refs. Os testes provaram concorrência de commits irmãos e refutaram CAS semântico de `force:false`.
- **Não comprovado:** fechamento transitivo real do manifest confiável, revalidação de contrato no READY, identidade de causa raiz normalizada sem spoof/rephrasing, writer global efetivo, price/cap dispatch, main-only pipeline e crash real. Canaries e gates humanos obrigatórios antes de API paga; o CAS-Lab sozinho não os comprova.
- Nenhuma mudança nesta ADR autoriza chamada paga ou merge sem decisão humana.

## 15. Histórico de revisão

| Data | Responsável | Alteração | Estado |
| --- | --- | --- | --- |
| 2026-10-08 | Product & SDD | Proposta sucessora à ADR-0013 para corrigir reserva monetária antes de quota claim | rev.1 `Proposed` |
| 2026-10-09 | Product & SDD | Revisão material: claim universal, writer global e contraexemplo CAS-Lab 5→2 | rev.2 `Proposed` |
| 2026-10-09 | Product & SDD | P1/P1/P2: ingresso independente, dispatch main-only e fencing pré-financeiro | rev.3 `Proposed` |
| 2026-10-09 | Product & SDD | P1/P1/P2: fingerprint de changeset, preço/caps imutáveis e CODEX-01 attempt 0 | rev.4 `Proposed` |
| 2026-10-09 | Product & SDD | P1/P2: closure de contrato trusted no review e família de causa raiz do Remediator | rev.5 `Proposed` |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pronto para aceite humano (parecer técnico favorável anterior à decisão)
- **Revisão revisada:** 5; blob `8f97b80946e638673e21da57e76773b974ee36b1`, HEAD avaliado `7613e8550bc1f973fc758a5446a120370a733a80`
- **Revisor:** Orchestrator / Tech Lead
- **Data:** 2026-10-09
- **Pendências bloqueantes:** Nenhuma para aceite documental da rev.5; testes do writer, identidade do revisor e anti-loop continuam obrigatórios antes de ativar IA paga.
- **Pendências não bloqueantes:** implementação, canaries de writer global e orçamento/secret antes de API paga.

## 17. Aceite humano

- **Aceito:** Sim
- **Responsável humano:** Ramon Rodriguez
- **Revisão aceita:** 5
- **Data:** 2026-10-09
- **Registro:** Aceite humano explícito em ChatGPT, PR #2 comentário #6091567757 (`ORCHESTRATOR_RECORDED_HUMAN_APPROVAL`), HEAD material original `7613e8550bc1f973fc758a5446a120370a733a80`; ADR-0013 rev.1 passa a `Superseded`.
