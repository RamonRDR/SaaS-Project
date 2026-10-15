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

**Travar a conversa da issue (Lock conversation) antes de qualquer ativação.**
O intake e o reconciler verificam `locked=true` e falham fechados se a
inbox estiver aberta ao público. O GitHub permite que colaboradores com
escrita e proprietários comentem em conversas travadas; a issue é um canal
de controle, não um fórum. O lock NÃO substitui `request_id`, validação
de autor bot ou auditoria; todos continuam obrigatórios.

No canary, a issue deve nascer sem comentários de terceiros e ser travada
antes da primeira gravação. Se o lock for revogado durante uma varredura,
o intake para de gravar na próxima revalidação pré-POST. O processo não
destrava, tranca nem altera issues automaticamente.

Configurar em Settings > Secrets and variables > Actions > Variables:

- MODE_A_INBOX_ISSUE: número da issue dedicada, diferente da issue de controle.

A issue de controle referenciada por CONTROL_ISSUE precisa ter sido criada pelo responsável RamonRDR, estar aberta, não ser pull request e conter exatamente um campo por linha para ORCHESTRATOR_MODE: A, PHASE: PHASE-... e OBJECTIVE: texto não vazio. Uma issue aberta genérica, inclusive a inbox, nunca é controle válido. **A descrição atual da Issue #1 ainda exige adequação desse bloco antes do canary real; este PR não a altera nem ativa ingestão.** Durante varredura global, candidatos inválidos são ignorados sem impedir que outros PRs válidos avancem; falhas de rede/paginação continuam bloqueantes.
- MODE_A_INTAKE_ENABLED=true: habilita gravações após aprovação operacional e canary.
- MODE_A_INBOX_RECONCILE_ENABLED=true: habilita reconciliação de leitura.

Sem variáveis, token, issue ou permissões válidas, o fluxo falha fechado ou é pulado. Não configurar OPENAI_API_KEY.

## Modelo de intenção

Os comentários possuem prefixo MODE_A_INBOX_V1 seguido de JSON canônico: schema mode_a_inbox_v1, state PENDING, repository, pr_number, head_sha, base_ref, control_issue, operation_kind CODEX_01, authorized_attempt 0, operation_key, request_id e main_source_sha.

request_id é SHA-256 de operation_key baseada em repo/PR/HEAD/operação/tentativa, independente do workflow_run_id e da revisão da main. O leitor verifica o autor GitHub Actions Bot, os campos esperados, a canonicalização e a identidade reconstruída. Comentários de terceiros não concedem autoridade.

O intake valida PR/HEAD **e revalida tanto a issue de controle quanto a própria inbox (estado, marcador e lock) imediatamente antes de cada gravação**. Após POST bem-sucedido, faz readback autoritativo pelo ID do comentário retornado pela API (incluindo IDs de 64 bits), evitando reler a inbox inteira para cada novo registro. Se o ACK do POST for ambíguo, procura evidência na inbox integral antes de declarar sucesso; sem prova, falha fechado. Duplicatas físicas ocasionais são toleradas como intenções, nunca como autorização de orçamento; um ledger futuro deve implementar unicidade financeira em writer global próprio.

## Recuperação e limites

- Um scanner horário de PRs abertos reconstitui ingressos perdidos no próximo ciclo de intake ativo.
- A listagem pagina até a primeira resposta curta, inclusive quando há múltiplos exatos de página. Cada página contém até **50 itens**, reduzindo a exposição a expansões de JSON. Um teto **conservador de 5.000 itens por listagem** exige no máximo 101 leituras paginadas, abaixo da cota típica de 1.000 requisições/hora por repositório do GitHub Actions, reservando capacidade para outras operações. Exceder este teto gera `INBOX_CAPACITY_SAFETY_GATE`; **não se declara a inbox permanentemente escalável nem se permite truncar registros**.
- **Canary/ativação:** a rotação/arquivamento de inbox e seu contrato de proveniência devem ser implementados, revisados e testados em incremento próprio *antes* que o volume histórico se aproxime dos 5.000 registros. Enquanto essa prova não existir, a entrega atual é um bootstrap deliberadamente desabilitado; atingir o teto bloqueia de maneira segura, não apaga nem ignora intents.
- Cada resposta da API é lida integralmente com limite de **48 MiB** por resposta, jamais interpretando JSON truncado. O teste simula uma página de **50 comentários de 65.536 emojis** (caracteres de 4 bytes, expandidos em pares substitutos de 12 bytes no JSON), verificando o pior caso comum de expansão Unicode sob o limite de transporte. A inbox travada impede inserção de comentários gigantes por contribuidores públicos; o teto de bytes permanece defesa de recursos e resultados excepcionalmente maiores falham fechados. O limite não é promessa para payloads arbitrariamente grandes de colaboradores privilegiados, que pertencem à fronteira de confiança da issue.
- O limite de 5.000 registros é deliberado para **canary de baixo volume**. Rotação/arquivamento verificável continua pré-requisito antes de ampliar esse alcance; não afirmar que o código escala indefinidamente.
- A proveniência `main_source_sha` é obtida de `git rev-parse HEAD` após checkout confiável da main. O SHA do evento pode estar antigo e não é usado como origem do código executado. Os registros são vinculados ao commit realmente carregado.
- O parser aceita cabeçalhos de metadados de PR tanto com `LF` quanto `CRLF`, sem afrouxar a rejeição de campos duplicados ou inválidos.
- O reconciler read-only compara a inbox com os PRs vigentes. HEAD novo torna registro antigo stale. Não exclui histórico e não altera ledger.
- Na varredura periódica, se **um PR específico** mudar HEAD/metadados ou perder a validade de sua issue de controle entre a descoberta e a gravação, somente esse candidato é ignorado; o próximo ciclo rederiva o estado atual. Em evento direcionado (`only=PR`), a mesma mudança falha explicitamente com gate fechado. Falhas de API, invalidação da inbox compartilhada, paginação incompleta ou alteração de registros do bot permanecem bloqueantes para o lote inteiro. Não se ignora perda de evidência global.
- GitHub Actions concurrency usa dois domínios separados: por PR nos eventos `pull_request_target` e um grupo exclusivo para `schedule`. Eventos de um PR podem coalescer no seu grupo, mas **não substituem o slot de recovery periódico**. Corridas entre grupos podem gerar comentários físicos duplicados; a reconciliação usa request_id estável e o ledger futuro será responsável por claim único. Concurrency NÃO é fila durável, CAS semântico, writer financeiro ou garantia de unicidade física de comentários.
- O intake implementa somente a intenção CODEX-01. Remediator, claim universal, trust/quota e Budget Broker são incrementos separados.
- O wake-up após gravação ainda não foi integrado ao drainer real, que não existe neste incremento. Reconciler periódico permite inspecionar backlog sem operar pagamentos.
- PHASE-0-G permanece planned. A Issue #1 não pode ser considerada DONE por esta entrega.

## Evidências e rollback

Suite: python3 -m unittest discover -s .github/scripts -p 'test_mode_a_inbox.py' -v

Testes simulam evento perdido, repetição idempotente, duplicata, HEAD stale, ACK incerto, spoof de autor, registro alterado, paginação e controle inválido. Para merge: gates de governança, secret scan, lint, testes, SEC-02 e CODEX-01 do HEAD exato.

Rollback: desligar MODE_A_INTAKE_ENABLED e MODE_A_INBOX_RECONCILE_ENABLED; preservar a issue e seus registros históricos. O Mode A interativo permanece independente.
