# Mode A Unattended: inbox durável e reconciler de leitura

## Escopo e situação

Incremento da Issue #1 com base na SDD-0001 v1.6 Approved e na ADR-0014 rev.5 Accepted. Continuação do bootstrap do PR #3.

**Implementado em código, ainda desabilitado para operação:** publicar estes workflows na main não ativa gravações. A habilitação exige uma issue de inbox dedicada, variáveis configuradas e canary. Nenhuma API paga, Budget Broker, ledger financeiro, Trusted Publisher ou merge automático foi implementado.

## Componentes e fronteiras de privilégio

- **mode-a-intake.yml:** código somente da main, acionado por pull_request_target e scanner horário. Permissões issues:write, pull-requests:read e contents:read. Consulta PR e HEAD atuais via API, valida a issue de controle e grava apenas comentários PENDING na inbox dedicada. Não executa código, ferramenta ou prompt do fork.
- **mode-a-reconciler.yml:** código trusted da main, acionado por schedule, repository_dispatch ou execução manual no ref main. Somente issues:read, pull-requests:read e contents:read. Enumera a inbox e os PRs atuais; relata intenções faltantes, obsoletas ou duplicadas sem mutações.
- **mode-a-inbox-checks.yml:** testes isolados, Ruff e auditoria de dependências, com contents:read.

O runner faz checkout explícito de main, sem credenciais Git persistidas. O evento é tratado como dica, e nunca como autorização. Referência, repositório e origem são validados. O job de intake tem escrita APENAS na issue de inbox previamente validada.

## Configuração de canary futuro, não ativar neste PR

Criar uma **issue dedicada** no repositório cuja primeira linha do corpo seja exatamente:

    MODE_A_INBOX_V1

Configurar em Settings > Secrets and variables > Actions > Variables:

- MODE_A_INBOX_ISSUE: número da issue dedicada, diferente da issue de controle.
- MODE_A_INTAKE_ENABLED=true: habilita gravações após aprovação operacional e canary.
- MODE_A_INBOX_RECONCILE_ENABLED=true: habilita reconciliação de leitura.

Sem variáveis, token, issue ou permissões válidas, o fluxo falha fechado ou é pulado. Não configurar OPENAI_API_KEY.

## Modelo de intenção

Os comentários possuem prefixo MODE_A_INBOX_V1 seguido de JSON canônico: schema mode_a_inbox_v1, state PENDING, repository, pr_number, head_sha, base_ref, control_issue, operation_kind CODEX_01, authorized_attempt 0, operation_key, request_id e main_source_sha.

request_id é SHA-256 de operation_key baseada em repo/PR/HEAD/operação/tentativa, independente do workflow_run_id e da revisão da main. O leitor verifica o autor GitHub Actions Bot, os campos esperados, a canonicalização e a identidade reconstruída. Comentários de terceiros não concedem autoridade.

O intake tenta persistir somente depois de consultar PR/HEAD e issue de controle atuais e sempre exige readback. Em ACK incerto, busca evidência na inbox antes de declarar sucesso. Duplicatas físicas ocasionais são toleradas como intenções, nunca como autorização de orçamento; um ledger futuro deve implementar unicidade financeira em writer global próprio.

## Recuperação e limites

- Um scanner horário de PRs abertos reconstitui ingressos perdidos no próximo ciclo de intake ativo.
- O reconciler read-only compara a inbox com os PRs vigentes. HEAD novo torna registro antigo stale. Não exclui histórico e não altera ledger.
- Paginação incompleta, controle inválido ou comment bot alterado resulta em bloqueio conservador.
- GitHub Actions concurrency é apenas auxiliar; NÃO é fila durável, CAS semântico, writer financeiro ou garantia de unicidade física de comentários.
- O intake implementa somente a intenção CODEX-01. Remediator, claim universal, trust/quota e Budget Broker são incrementos separados.
- O wake-up após gravação ainda não foi integrado ao drainer real, que não existe neste incremento. Reconciler periódico permite inspecionar backlog sem operar pagamentos.
- PHASE-0-G permanece planned. A Issue #1 não pode ser considerada DONE por esta entrega.

## Evidências e rollback

Suite: python3 -m unittest discover -s .github/scripts -p 'test_mode_a_inbox.py' -v

Testes simulam evento perdido, repetição idempotente, duplicata, HEAD stale, ACK incerto, spoof de autor, registro alterado, paginação e controle inválido. Para merge: gates de governança, secret scan, lint, testes, SEC-02 e CODEX-01 do HEAD exato.

Rollback: desligar MODE_A_INTAKE_ENABLED e MODE_A_INBOX_RECONCILE_ENABLED; preservar a issue e seus registros históricos. O Mode A interativo permanece independente.
