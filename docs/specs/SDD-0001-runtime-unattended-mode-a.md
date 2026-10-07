# SDD-0001 - Runtime unattended cloud-native do Modo A

## Metadados

- **ID:** SDD-0001
- **Título:** Runtime unattended cloud-native do Modo A
- **Status:** Approved
- **Versão:** 0.8
- **Responsável pela especificação:** Product & SDD
- **Responsável humano pela aprovação:** Ramon Rodriguez
- **Data de criação:** 2026-10-06
- **Última atualização:** 2026-10-07
- **Entrega / issue / PR relacionada:** Issue #1
- **ADRs relacionados:** ADR-0010, ADR-0012 rev.7
- **SDDs relacionadas:** Não aplicável

### Estados permitidos

- `Draft`: em elaboração;
- `In Review`: pronta para revisão, ainda não aprovada;
- `Approved`: revisão concluída e aprovação humana explicitamente registrada;
- `Superseded`: substituída por outra SDD identificada e já `Approved`.

Uma SDD não pode assumir `Approved` por decisão de um agente de IA.

### Versão da especificação e validade da aprovação

As seções 1 a 24 compõem o conteúdo material da especificação.

Esta versão 0.8 substitui a proposta pública 0.7 e remove a dependência incorreta de GitHub Actions `concurrency` como fila de espera. Cada solicitação de review de fork é persistida primeiro em uma fila/ledger durável no GitHub; um drainer base-trusted e idempotente reconcilia o backlog e executa `check + reserve` de quota em seção crítica global antes da chamada à OpenAI. Execuções do drainer podem ser coalescidas sem perda de pedidos, porque o wake-up é apenas um sinal e a fila persistida é a fonte de verdade; uma reconciliação periódica garante eventual progresso. Reservas ambíguas após falha continuam consumindo quota até expirar e nunca autorizam uma segunda cobrança automática. A versão experimental 0.1 permanece preservada apenas no histórico privado anterior e não foi importada para o Git público sanitizado por depender de uma arquitetura descartada e de evidências operacionais privadas.

Qualquer mudança material nas seções 1 a 24 invalida este parecer técnico, incrementa a versão e exige novo ciclo de revisão e aprovação.

## 1. Contexto

O Mode A interativo já possui máquina de estados, gates humanos, anti-loop, invalidação por HEAD e ciclo de PR/CI/review. O objetivo remanescente é executar esse fluxo sem depender de uma conversa ativa ou de uma máquina local.

Um experimento anterior colocou um runtime externo reativo no critical path. O teste real mostrou que a continuidade entre eventos assíncronos não era suficientemente determinística: CI ou review podiam terminar sem que o runtime voltasse a executar automaticamente.

O repositório público foi reinicializado a partir de uma baseline sanitizada anterior a esse experimento. A nova solução deve usar mecanismos cloud-native do próprio GitHub como motor de continuidade.

## 2. Problema

O projeto não possui hoje um executor unattended confiável que consiga, sem intervenção humana operacional:

1. reagir a um PR elegível;
2. executar CI;
3. classificar falha corrigível;
4. pedir ao Codex uma remediação;
5. publicar novo HEAD;
6. repetir CI;
7. executar review independente;
8. remediar findings corrigíveis;
9. chegar a `READY_FOR_HUMAN_MERGE`.

O fluxo não pode depender de uma mensagem humana para "acordar" e não pode exigir computador local ligado.

## 3. Objetivo

Implementar um runtime unattended **100% online** cuja continuidade seja controlada por GitHub Actions e que use Codex apenas nas etapas de inteligência necessárias.

O caminho saudável deve chegar sozinho a `READY_FOR_HUMAN_MERGE`. A autorização do merge principal permanece obrigatoriamente humana.

## 4. Escopo

- GitHub Actions como runtime/orquestrador unattended;
- standard GitHub-hosted runners;
- execução em repositório público;
- reducer/state machine versionado no repositório;
- estado auditável `ORCHESTRATOR_STATE_V2`;
- serialização por PR com `concurrency`;
- CI/gates atuais integrados ao fluxo;
- Codex para gerar propostas de remediação em job sem credencial GitHub com escrita;
- Trusted Publisher separado do processo Codex, responsável pela validação e publicação do patch;
- denylist obrigatória do control plane protegido antes de qualquer publicação automática;
- CODEX-01 como review independente do HEAD exato;
- CODEX-01 base-trusted para forks, executado por broker determinístico e tool-less da `main`, sem checkout, execução do código externo ou ferramentas agentivas;
- trust gate + quotas/idempotência antes de qualquer chamada paga disparada por fork;
- fila durável de solicitações de review de fork no GitHub, criada antes de qualquer drainer/wake-up;
- Quota Broker/drainer base-trusted que reconcilia o backlog persistido e reserva quota atomicamente antes da API;
- publicação automática de commits apenas na branch elegível do PR same-repo e somente pelo Trusted Publisher;
- dispatcher confiável previamente instalado na `main` como etapa de bootstrap;
- reentrada explícita via `workflow_dispatch` ou `repository_dispatch` atendida pelo dispatcher já presente na branch padrão;
- secrets via GitHub Actions Secrets;
- proteção específica para forks e conteúdo não confiável;
- anti-loop por causa raiz;
- canary E2E antes de `DONE_ALLOWED`.

## 5. Fora de escopo

- execução local;
- self-hosted runner;
- VPS, servidor, Redis, fila ou banco externo;
- merge automático da `main`;
- features de produto da PHASE-0-G;
- uso de ChatGPT Work como componente obrigatório do runtime;
- `pull_request_target` com checkout, execução de código, scripts, actions ou configuração proveniente do PR não confiável;
- entrega de secrets ou token privilegiado ao código/ambiente controlado pelo fork;
- remediação automática com escrita em PR originado de fork;
- segundo reviewer obrigatório além de CODEX-01.

## 6. Atores e jornadas afetadas

| Ator | Jornada / interação | Impacto |
| --- | --- | --- |
| Responsável humano | aprova decisões e merge | deixa de atuar como wake-up operacional |
| GitHub Actions | executa runtime, CI e transições | passa a ser o motor unattended |
| Codex Remediator | gera patch para causa raiz específica | opera sem token GitHub com escrita e não publica commits |
| Trusted Publisher | valida e publica patch aprovado pelo contrato | é o único job de remediação same-repo com `contents: write`; não executa Codex e rejeita control plane protegido |
| CODEX-01 same-repo | revisa HEAD exato | permanece independente da remediação e sem `contents: write` |
| CODEX-01 fork base-trusted | revisa diff do HEAD externo como dado | usa broker determinístico/tool-less da `main`; o modelo não recebe shell, filesystem, tools/functions ou `contents: write` |
| Orchestrator / Tech Lead | define reducer, gates e contratos | coordena arquitetura e critérios |
| GitHub | fonte de verdade | persiste PR, HEAD, runs, comentários e estado |

## 7. Regras de negócio

- **BR-001:** o runtime só opera em PR com `ORCHESTRATOR_MODE: A` e `CONTROL_ISSUE` válido.
- **BR-002:** PR originado de fork nunca recebe `OPENAI_API_KEY`, token com escrita ou qualquer secret dentro de ambiente controlado pelo código do fork; o reviewer base-trusted pode usar `OPENAI_API_KEY` somente em workflow carregado da `main`, sem checkout nem execução de conteúdo do fork.
- **BR-003:** jobs com escrita Git só operam em branch do mesmo repositório e origem considerada confiável. O único job privilegiado permitido para fork é o CODEX-01 base-trusted, limitado a leitura de repositório/PR e publicação de evidência de review, sem `contents: write`.
- **BR-004:** toda execução começa reconciliando PR, HEAD, checks, estado e evidências atuais.
- **BR-005:** `concurrency` serializa o runtime por PR com `cancel-in-progress: false`.
- **BR-006:** novo HEAD invalida CI, review, READY e autorização associados ao HEAD anterior.
- **BR-007:** CODEX-01 só é válido para o HEAD exato revisado.
- **BR-008:** Codex Remediator e CODEX-01 usam contextos/jobs separados.
- **BR-009:** CODEX-01 não possui permissão para publicar código.
- **BR-010:** o job que executa Codex Remediator não recebe token GitHub com `contents: write`; sua saída mutável é somente um patch/artefato estruturado associado ao PR e ao HEAD esperados.
- **BR-011:** a publicação Git da remediação ocorre em job separado, sem execução de Codex, chamado Trusted Publisher; antes de qualquer push ele valida origem same-repo confiável, HEAD esperado, ref de destino, escopo do patch e invariantes do contrato.
- **BR-012:** o Trusted Publisher só pode publicar na branch corrente do PR elegível; nunca diretamente na `main`.
- **BR-013:** a mesma causa raiz admite no máximo 3 tentativas automáticas antes de `LOOP_ESCALATION_REQUIRED`.
- **BR-014:** ausência ou ambiguidade de evidência resulta em fail-closed.
- **BR-015:** após publicar novo HEAD, o runtime inicia explicitamente o próximo ciclo por dispatch suportado, sem depender de recursão implícita de eventos gerados por `GITHUB_TOKEN`.
- **BR-016:** o workflow que recebe o dispatch de reentrada deve existir previamente na branch padrão. A implementação adota bootstrap em merge anterior ao canary para instalar esse dispatcher confiável na `main`.
- **BR-017:** `READY_FOR_HUMAN_MERGE` só é emitido com CI verde, CODEX-01 limpo e evidências do mesmo HEAD.
- **BR-018:** merge principal exige autorização humana explícita vinculada ao PR/HEAD.
- **BR-019:** PHASE-0-G permanece bloqueada até canary E2E e `DONE_ALLOWED`.
- **BR-020:** o Trusted Publisher mantém denylist fail-closed do control plane protegido. No mínimo são proibidos patches automáticos em `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` e `docs/PROJECT_STATUS.md`. Se qualquer arquivo do patch corresponder à denylist, o patch inteiro não é publicado e a transição é `HUMAN_DECISION_REQUIRED`.
- **BR-021:** alterações na própria denylist, no Publisher, dispatcher, workflows, prompts, schemas, state machine ou contratos de governança nunca podem ser autoaprovadas pelo mesmo runtime que protegem; exigem PR/review/gate humano fora da remediação automática.
- **BR-022:** para PR de fork, CODEX-01 executa em contexto base-trusted a partir da branch padrão, usando somente workflow, prompt, schema e tooling da `main`; obtém metadados e diff pela API do GitHub, trata-os como dados não confiáveis, não faz checkout do HEAD do fork e não executa nenhum arquivo do PR.
- **BR-023:** a evidência CODEX-01 de fork deve registrar o `head.sha` exato. Se o HEAD mudar durante ou após o review, a evidência é stale e deve ser descartada antes de READY.
- **BR-024:** findings em fork não acionam Trusted Publisher nem remediação automática com escrita; o autor ou responsável humano produz novo HEAD e o fluxo reexecuta CI read-only e CODEX-01 base-trusted.
- **BR-025:** CODEX-01 de fork não usa Codex Action/CLI em modo agentivo. Um broker confiável versionado na `main` obtém o diff/metadados pela API, normaliza o payload e chama a API OpenAI sem disponibilizar ao modelo shell, filesystem, comandos, tools/functions, subprocessos ou acesso ao ambiente do runner. Conteúdo não confiável nunca é interpolado em comando de shell; trafega apenas por JSON/stdin/HTTP como dado.
- **BR-026:** o processo confiável que contém `OPENAI_API_KEY` para review de fork executa somente código da `main`, com menor privilégio possível, sem `sudo`/elevação e sem executar artefatos do fork. O segredo nunca é incluído no prompt, output, artifact ou log. Qualquer configuração que habilite ferramentas agentivas para esse reviewer é fail-closed.
- **BR-027:** antes de uma chamada paga para fork, o runtime aplica trust gate. Autorização automática é restrita a `OWNER`, `MEMBER` ou `COLLABORATOR`; qualquer outro `author_association` exige aprovação explícita de maintainer vinculada ao PR antes da primeira chamada paga.
- **BR-028:** reviews pagos de fork são idempotentes por `head.sha`: no máximo uma chamada CODEX-01 por SHA. Além disso, o baseline limita a 3 chamadas pagas por PR em janela móvel de 24h e 5 chamadas pagas por autor externo em janela móvel de 24h no repositório. A contabilização usa reservas duráveis, não apenas evidência posterior à chamada.
- **BR-029:** trust gate ausente ou quota excedida bloqueia a chamada antes de consumir a API e produz `HUMAN_DECISION_REQUIRED`; eventual override humano deve ser explícito, auditável e vinculado ao PR/HEAD específico, sem desabilitar permanentemente as quotas.
- **BR-030:** todo evento elegível de fork deve persistir, antes de qualquer tentativa de drenar/processar, uma solicitação machine-readable em fila GitHub dedicada. `request_id` é determinístico para `repository + pr + head_sha + author_id`; registrar novamente o mesmo pedido é idempotente. O wake-up posterior não é fonte de verdade e pode ser perdido/coalescido sem perder a solicitação.
- **BR-031:** a fila e o ledger de quota residem em recurso GitHub dedicado criado no bootstrap e aceitam mutações apenas da identidade confiável do runtime. O journal é append-only lógico e registra no mínimo `request_id`, `reservation_id` quando houver, `author_id`, `pr`, `head_sha`, `workflow_run_id`, timestamps e estados `PENDING`, `RESERVED`, `CONSUMED`, `DONE`, `REJECTED`; nenhuma informação secreta é armazenada.
- **BR-032:** o Quota Broker opera como drainer base-trusted com uma única seção crítica global para mutações do ledger. Uma execução reconcilia a fila persistida, deduplica por `request_id`, revalida trust/HEAD, aplica quotas de autor/PR/SHA e persiste `RESERVED` antes da API. O drainer pode processar um lote limitado por execução, mas nunca depende de uma correspondência 1:1 entre solicitação e workflow run.
- **BR-033:** o wake-up do drainer é best-effort e pode usar `repository_dispatch`/`workflow_dispatch`. A continuidade não depende da preservação de todas as execuções pendentes de `concurrency`: um reconciler periódico na `main` varre solicitações `PENDING`/`RESERVED` incompletas e reacorda o drainer. Coalescência/cancelamento de wake-ups não altera o ledger nem remove pedidos.
- **BR-034:** `reservation_id` é determinístico para `author_id + pr + head_sha`. Se já houver reserva/evidência para o mesmo SHA, o broker não cria outra. Uma reserva `RESERVED` sem conclusão comprovada após crash é tratada como consumo de quota até expirar e bloqueia nova chamada automática para o mesmo SHA; recuperação exige decisão humana explícita, evitando cobrança duplicada em estado ambíguo.
- **BR-035:** o job que chama a OpenAI para fork só executa após validar uma reserva persistida e correspondente ao mesmo `author_id`, PR, HEAD e request autorizado. Ausência, divergência ou reserva stale resulta em fail-closed antes da API.

## 8. Permissões e multi-tenancy

Multi-tenancy de produto: não aplicável nesta entrega.

Permissões operacionais:

- CI comum: `contents: read`;
- CODEX-01 same-repo: leitura do workspace e acesso à API OpenAI, sem `contents: write`;
- CODEX-01 fork base-trusted: broker determinístico da `main` com `contents: read`, leitura de metadados/diff e acesso à API OpenAI; pode registrar evidência de review no PR, mas não possui `contents: write`, não usa agente com ferramentas, não faz checkout do fork e não executa conteúdo do PR;
- Codex Remediator: leitura do workspace + `OPENAI_API_KEY`, sem token GitHub com escrita; produz somente patch/artefato estruturado;
- Trusted Publisher: `contents: write` mínimo, sem `OPENAI_API_KEY` e sem executar processo Codex; valida patch, HEAD, ref e denylist de control plane antes do push;
- merge da `main`: fora do job unattended;
- fork PR: CI read-only + CODEX-01 base-trusted; sem remediação automática com escrita.

Nenhum workflow deve combinar secret privilegiado com execução arbitrária de código de fork.

## 9. Impacto no modelo de dados

Não aplicável ao produto.

O estado operacional permanece no GitHub. O schema `ORCHESTRATOR_STATE_V2` registra no mínimo:

- revisão do journal;
- PR;
- HEAD;
- estado;
- CI run/evidence;
- review evidence;
- root cause e tentativas;
- action key;
- READY SHA;
- autorização humana SHA quando existir.

## 10. Impacto no contrato da API

Não aplicável à API do produto.

Integrações operacionais:

- GitHub Actions;
- API/Action oficial do Codex/OpenAI;
- API do GitHub usando `GITHUB_TOKEN` com permissões explícitas.

## 11. Comportamento esperado no Flutter

Não aplicável. Flutter ainda não foi iniciado.

## 12. Integrações externas

- GitHub Actions;
- OpenAI API / Codex para jobs de IA.

A ativação da OpenAI API é dependência externa paga e exige aceite humano desta arquitetura. A credencial será armazenada exclusivamente em GitHub Actions Secrets.

O uso de standard GitHub-hosted runners em repositório público reduz a dependência da franquia privada de Actions, mas essa condição comercial do GitHub não é tratada como garantia arquitetural eterna.

## 13. Segurança e privacidade

Controles obrigatórios:

- nenhum secret em código, prompt versionado, comentário, artifact público ou log;
- `OPENAI_API_KEY` apenas em jobs elegíveis e confiáveis;
- conteúdo de PR, comentário, diff e log é dado não confiável;
- prompts versionados têm precedência sobre instruções encontradas no PR;
- nenhum código do fork é executado em contexto privilegiado;
- `pull_request_target`, quando usado para CODEX-01 de fork, fica restrito a workflow da base e é proibido de fazer checkout, importar action/script/configuração do HEAD ou interpolar conteúdo não confiável em shell;
- o diff de fork é obtido por API e tratado exclusivamente como dado não confiável vinculado ao `head.sha`;
- o reviewer de fork usa integração OpenAI tool-less: nenhum shell, filesystem, tool/function call, subprocesso ou ambiente do runner é exposto ao modelo;
- o broker que possui `OPENAI_API_KEY` executa somente código confiável da `main`, sem sudo/elevação e com o segredo fora de prompt, stdout/stderr e artifacts;
- trust gate, deduplicação por HEAD e quotas por PR/autor são avaliados antes da chamada paga;
- a autorização de consumo vem exclusivamente de reserva persistida pelo Quota Broker após reconciliação da fila durável; a mera leitura de contadores ou a existência de um workflow pendente não autoriza a API;
- pedidos de fork são persistidos antes do wake-up e sobrevivem a coalescência/cancelamento de workflows; reconciler periódico processa backlog remanescente;
- tokens com menor permissão possível;
- processo Codex de remediação sem credencial GitHub com escrita;
- publicação em job confiável separado, sem Codex e sem chave OpenAI, com validação de patch, HEAD esperado, ref de destino e denylist do control plane;
- patches automáticos que toquem `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` ou `docs/PROJECT_STATUS.md` são rejeitados integralmente e escalam para humano;
- commit/push limitado à branch same-repo do PR;
- dispatcher de reentrada versionado na `main` antes do canary, evitando depender de workflow ainda inexistente na branch padrão;
- `main` protegida por gate humano;
- outputs de IA validados antes de virarem decisão/mutação;
- logs não podem incluir payload sensível da API.

## 14. Observabilidade

Cada ciclo deve tornar auditável:

- workflow run ID;
- PR e HEAD;
- decisão do reducer;
- CI status;
- action key;
- root cause e contador;
- chamada de remediação/review;
- digest ou ID da evidência CODEX-01;
- novo HEAD quando houver;
- razão de NO_OP/bloqueio;
- estado terminal/gate.

Custos de API devem ser acompanháveis pelo projeto OpenAI usado na automação.

## 15. Casos de borda e comportamentos de erro

| ID | Cenário | Comportamento esperado |
| --- | --- | --- |
| EDGE-001 | dois eventos simultâneos no mesmo PR | `concurrency` serializa; segunda execução reconcilia estado novo |
| EDGE-002 | PR de fork | CI do fork roda read-only; CODEX-01 roda em workflow base-trusted da `main` lendo somente diff/API; remediação automática com escrita fica indisponível |
| EDGE-003 | HEAD muda durante job | abortar mutação e reconciliar |
| EDGE-004 | CI falha por causa corrigível em PR same-repo elegível | Codex Remediator recebe causa específica e pode produzir patch para novo HEAD |
| EDGE-005 | CI falha por decisão material | `HUMAN_DECISION_REQUIRED` |
| EDGE-006 | review encontra P0/P1/P2 corrigível em PR same-repo elegível | remediar e gerar novo HEAD automaticamente; em fork aplica-se BR-024 |
| EDGE-007 | terceiro fracasso da mesma causa | `LOOP_ESCALATION_REQUIRED` |
| EDGE-008 | API OpenAI indisponível/sem saldo/secret ausente | `BLOCKED_EXTERNAL` |
| EDGE-009 | push com `GITHUB_TOKEN` não gera novo workflow | Trusted Publisher solicita dispatch explícito ao dispatcher já presente na `main` |
| EDGE-010 | dispatcher ainda não existe na branch padrão | canary fica bloqueado; concluir bootstrap primeiro |
| EDGE-011 | review pertence a HEAD antigo | ignorar e pedir/reexecutar review |
| EDGE-012 | output Codex inválido ao schema | fail-closed |
| EDGE-013 | Codex tenta publicar diretamente | negar; job Codex não possui escrita Git |
| EDGE-014 | patch diverge do HEAD/ref esperados | Trusted Publisher aborta sem push e força reconciliação |
| EDGE-015 | tentativa de escrever `main` | negar |
| EDGE-016 | workflow de origem não confiável tenta acessar secret | negar antes do step privilegiado |
| EDGE-017 | autorização humana para HEAD antigo | invalidar |
| EDGE-018 | patch de remediação toca control plane protegido | rejeitar patch inteiro antes da escrita e emitir `HUMAN_DECISION_REQUIRED` |
| EDGE-019 | fork tenta influenciar workflow/prompt do reviewer | ignorar versão do fork; carregar workflow/prompt/schema exclusivamente da `main` |
| EDGE-020 | HEAD do fork muda durante CODEX-01 | descartar evidência stale e revisar o novo SHA somente após novo trust/quota check |
| EDGE-021 | diff de fork tenta instruir leitura de env, `/proc`, shell ou filesystem | modelo não possui ferramentas; broker trata texto como dado e nenhum secret é retornado/logado |
| EDGE-022 | mesmo `head.sha` de fork dispara eventos repetidos | reutilizar evidência existente; nenhuma nova chamada paga |
| EDGE-023 | fork sem trust gate | não chamar OpenAI; emitir `HUMAN_DECISION_REQUIRED` |
| EDGE-024 | 4ª chamada do mesmo PR em 24h ou 6ª do mesmo autor externo em 24h | bloquear antes da API e emitir `HUMAN_DECISION_REQUIRED` |
| EDGE-025 | mesmo autor dispara reviews simultâneos em vários PRs | cada pedido vira `PENDING` durável antes do wake-up; drainer global reconcilia todos e respeita a quota ao reservar sequencialmente |
| EDGE-026 | múltiplos wake-ups do drainer são coalescidos/substituídos pelo GitHub | nenhum pedido é perdido; próxima execução/reconciliação lê o backlog persistido e continua |
| EDGE-027 | crash após `RESERVED` e antes/depois da chamada OpenAI sem evidência conclusiva | não liberar nem duplicar automaticamente; reserva conta na quota e o mesmo SHA fica fail-closed até expiração ou decisão humana |
| EDGE-028 | job tenta chamar API sem reserva válida do Quota Broker | negar antes da chamada e emitir `HUMAN_DECISION_REQUIRED` |
| EDGE-029 | drainer não recebe novo wake-up após existir backlog | reconciler periódico detecta `PENDING`/`RESERVED` incompleto e reacorda o fluxo sem intervenção humana |

## 16. Migration

- **Migration necessária:** Não
- **Destrutiva:** Não
- **Descrição:** substituição do runtime operacional; sem dados de produto.
- **Gate humano necessário:** Sim, por decisão arquitetural e adoção de integração paga com API.

## 17. Estratégia de rollback

- desabilitar o workflow unattended;
- remover/rotacionar secret de API;
- retornar ao Mode A interativo;
- manter CI read-only;
- nenhuma migration de produto precisa ser revertida.

## 18. Testes obrigatórios

### Unitários
- reducer V2;
- estados e transições;
- invalidação por HEAD;
- anti-loop;
- guards de fork/origem;
- action keys idempotentes.

### Integração
- eventos duplicados;
- concurrency por PR;
- stale HEAD;
- dispatch explícito atendido por workflow previamente existente na `main`;
- bootstrap do dispatcher antes do canary;
- handoff Codex Remediator → patch estruturado → Trusted Publisher;
- validação de HEAD/ref e denylist de control plane antes do push;
- rejeição atômica de patch misto que contenha ao menos um path protegido;
- CODEX-01 de fork carregado da `main`, tool-less, sem checkout do fork e vinculado ao `head.sha` exato;
- trust gate antes da API para autor externo;
- idempotência de review por `head.sha`;
- quotas de fork por PR/autor e bloqueio antes de chamada paga;
- persistência idempotente de `request_id` antes de qualquer wake-up do drainer;
- Quota Broker/drainer global com fila/ledger durável e processamento por reconciliação, sem usar `concurrency` como fila;
- reconciler periódico da `main` para backlog `PENDING`/`RESERVED` incompleto;
- teste concorrente com múltiplos PRs do mesmo autor provando que todos os pedidos permanecem no ledger, mesmo quando wake-ups são coalescidos, e que o limite global de quota é respeitado;
- validação obrigatória da reserva no job que chama a API;
- schema de output do reviewer;
- publicação em branch correta.

### E2E
- PR same-repo: CI verde → CODEX-01 → READY;
- PR same-repo: CI falha corrigível → remediação → novo HEAD → CI → review → READY;
- PR same-repo: finding corrigível → remediação → novo HEAD → CI → novo review;
- PR de fork: CI read-only + CODEX-01 base-trusted → READY quando não houver finding; se houver finding, aguardar novo HEAD do autor/responsável humano e então repetir os gates automáticos;
- fluxo same-repo saudável sem interação humana operacional até `READY_FOR_HUMAN_MERGE`;
- autorização humana final sem merge automático indevido.

### Segurança / autorização / multi-tenancy
- fork não recebe secret;
- PR text com prompt injection não altera contrato;
- job Codex Remediator não possui token GitHub com escrita;
- Trusted Publisher não recebe `OPENAI_API_KEY` e não executa Codex;
- patch com HEAD/ref divergente não é publicado;
- patch que altere qualquer path protegido do control plane não é publicado, mesmo quando misturado a arquivos permitidos;
- PR de fork não consegue fornecer workflow, prompt, action ou script executável ao CODEX-01 privilegiado;
- CODEX-01 de fork recebe apenas diff/metadados como dados e nunca faz checkout do HEAD externo;
- teste negativo injeta no diff instruções para ler `OPENAI_API_KEY`, `env`, `/proc/*/environ`, executar shell e imprimir secrets; o reviewer não dispõe de tools e a evidência/log não contém o sentinel secret;
- teste negativo prova que conteúdo do diff com metacaracteres de shell não é interpolado em comandos;
- teste prova que autor externo sem trust gate não gera chamada OpenAI;
- teste prova que eventos duplicados do mesmo HEAD não geram segunda cobrança;
- testes de quota bloqueiam a 4ª chamada do PR e a 6ª chamada do autor externo na janela de 24h antes da API;
- teste concorrente dispara pelo menos 6 pedidos em PRs distintos do mesmo autor, comprova que os 6 `request_id` permanecem duráveis mesmo com coalescência de wake-ups e que no máximo 5 chegam a `RESERVED` na janela;
- teste simula substituição/cancelamento de workflows pendentes e comprova que o reconciler posterior drena os `PENDING` restantes;
- teste de crash entre reserva e conclusão comprova que retry automático do mesmo SHA não produz segunda chamada paga;
- teste prova que chamada à OpenAI sem `reservation_id` persistido e correspondente ao mesmo autor/PR/HEAD é bloqueada;
- remediação não escreve `main`;
- reviewer não publica código;
- logs não expõem chave.

### Regressão
- Mode A interativo permanece funcional;
- GOV e secret-scan continuam verdes;
- gates humanos existentes permanecem.

## 19. Critérios de aceite

- **AC-001:** nenhuma etapa do caminho saudável exige máquina local.
- **AC-002:** nenhum wake-up operacional humano é necessário.
- **AC-003:** runtime é acionado/controlado pelo GitHub Actions.
- **AC-004:** duas execuções concorrentes do mesmo PR não publicam duas remediações conflitantes.
- **AC-005:** código/ambiente do fork não obtém `OPENAI_API_KEY` nem escrita privilegiada; o CODEX-01 base-trusted pode usar a chave apenas no contexto seguro da `main`, sem checkout/execução do fork.
- **AC-006:** em PR same-repo elegível, CI corrigível produz novo HEAD automaticamente; em PR de fork, remediação com escrita é proibida e o novo HEAD depende do autor ou responsável humano conforme BR-024.
- **AC-007:** em PR same-repo elegível, finding corrigível do CODEX-01 produz novo HEAD automaticamente; em PR de fork, o finding bloqueia READY até que o autor ou responsável humano publique novo HEAD, sem Trusted Publisher.
- **AC-008:** cada novo HEAD passa novamente por CI e CODEX-01.
- **AC-009:** mesma causa raiz não ultrapassa 3 tentativas automáticas.
- **AC-010:** caminho saudável chega sozinho a `READY_FOR_HUMAN_MERGE`.
- **AC-011:** `main` não é mergeada sem autorização humana explícita para PR/HEAD exatos.
- **AC-012:** o dispatcher necessário à reentrada está previamente instalado na `main` por um bootstrap aprovado antes do canary do runtime.
- **AC-013:** o processo Codex que gera remediação não possui credencial GitHub com escrita; somente o Trusted Publisher separado pode publicar após validar patch, HEAD e ref.
- **AC-014:** um canary pós-merge comprova o ciclo completo antes de `DONE_ALLOWED`.
- **AC-015:** PHASE-0-G permanece planejada até AC-014.
- **AC-016:** Trusted Publisher rejeita integralmente qualquer patch automático que toque o control plane protegido e escala para `HUMAN_DECISION_REQUIRED` antes de qualquer push.
- **AC-017:** PR de fork consegue produzir CODEX-01 válido para o HEAD exato por workflow base-trusted da `main`, via broker tool-less, sem checkout/execução de código do fork, sem ferramentas agentivas e sem `contents: write`.
- **AC-018:** novo HEAD de fork invalida automaticamente a evidência CODEX-01 anterior e exige nova avaliação de trust/quota antes de eventual nova chamada paga.
- **AC-019:** prompt injection no diff não consegue acessar `OPENAI_API_KEY`, variáveis de ambiente, `/proc`, filesystem ou shell porque o modelo de fork não recebe ferramentas; teste negativo com sentinel secret deve passar sem vazamento em output/log/artifact.
- **AC-020:** autor de fork fora de `OWNER`/`MEMBER`/`COLLABORATOR` não consome API antes de aprovação explícita de maintainer.
- **AC-021:** o mesmo `head.sha` de fork gera no máximo uma chamada paga de CODEX-01.
- **AC-022:** o baseline bloqueia antes da API a 4ª chamada paga do mesmo PR em 24h e a 6ª do mesmo autor externo em 24h, salvo override humano explícito e vinculado ao HEAD.
- **AC-023:** cada solicitação elegível de fork é persistida como `PENDING` com `request_id` determinístico antes do wake-up; teste concorrente com pelo menos 6 PRs comprova que nenhum pedido é perdido mesmo se execuções pendentes do drainer forem coalescidas.
- **AC-024:** o drainer reconcilia a fila durável em seção crítica global e o limite de 5 reservas/autor/24h não pode ser ultrapassado por corrida entre PRs.
- **AC-025:** nenhuma chamada paga de fork ocorre sem reserva durável válida persistida antes da API e correspondente ao mesmo autor/PR/HEAD/request.
- **AC-026:** uma reserva ambígua por crash não é reutilizada para uma segunda chamada automática do mesmo SHA; ela continua contando na quota até expiração ou override humano explícito.
- **AC-027:** backlog persistido progride sem wake-up humano: reconciler periódico da `main` detecta pedidos não concluídos e reacorda o drainer.

## 20. Evidências de validação esperadas

- unit/integration tests;
- workflow runs;
- secret scan;
- logs de decisões sem secrets;
- commits/HEADs do canary;
- output estruturado CODEX-01;
- parecer Security;
- parecer Platform/Observability;
- parecer QA;
- checkpoint PRE_MERGE, POST_MERGE e FINAL.

## 21. Dependências

- repositório GitHub público;
- standard GitHub-hosted runners;
- GitHub Actions;
- dispatcher, Trusted Publisher e entrypoint base-trusted do CODEX-01 de fork presentes na `main` antes do canary do runtime;
- GitHub Actions Secret `OPENAI_API_KEY`;
- conta/projeto OpenAI API com billing habilitado;
- Codex Action/CLI/SDK suportado para CI;
- ADR-0010 vigente;
- ADR-0012 aceito antes da implementação.

## 22. Riscos conhecidos

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| custo inesperado de API | gasto financeiro | limite de tentativas, projeto dedicado, hard budget/alerts antes do canary |
| abuso por fork/PR externo | consumo de API, indisponibilidade do gate, perda de pedidos ou tentativa de exfiltração | reviewer tool-less + trust gate + fila durável antes do wake-up + drainer reconciliador + reserva antes da API + idempotência por SHA + quotas por PR/autor + hard budget global + nenhuma escrita de contents |
| prompt injection | alteração indevida | contrato versionado + outputs estruturados + fail-closed |
| patch de IA altera o próprio control plane | bypass de gates ou persistência maliciosa | denylist fail-closed de paths protegidos + `HUMAN_DECISION_REQUIRED` antes da escrita |
| processo Codex obtém capacidade de escrita | push indevido | job de geração sem escrita + Trusted Publisher separado e validado |
| dispatcher ausente da branch padrão | reentrada não ocorre no primeiro rollout | bootstrap do dispatcher na `main` antes do canary |
| corrida entre eventos | commits conflitantes | `concurrency` + reconciliação de HEAD |
| loop de remediação | custo/instabilidade | 3 tentativas por causa raiz |
| indisponibilidade OpenAI | fluxo interrompido | `BLOCKED_EXTERNAL` + fallback interativo |
| mudança de política de runners | custo/limite futuro | monitorar billing e manter arquitetura portável |

## 23. Dúvidas abertas

Nenhuma dúvida bloqueante para aprovação arquitetural.

Antes do canary devem ser definidos como configuração operacional:

- modelo Codex/OpenAI usado em remediação e review;
- hard budget e alertas do projeto de API;
- forma exata de armazenar/parsear output estruturado.

Esses itens não podem reduzir os controles descritos nesta SDD.

## 24. ADRs necessários ou relacionados

- **ADR necessário:** Sim
- **Referências:** ADR-0010, ADR-0012
- **Motivo:** mover o runtime para GitHub Actions + Codex, introduzir API paga e definir fronteiras de privilégio é decisão transversal e durável.

## 25. Histórico de revisão

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 0.1 | 2026-10-04 | Product & SDD | versão experimental privada, não importada ao Git público |
| 0.2 | 2026-10-06 | Product & SDD | redesenho cloud-native com GitHub Actions + Codex |
| 0.3 | 2026-10-06 | Product & SDD | separa geração de patch da publicação privilegiada e adiciona bootstrap do dispatcher antes do canary |
| 0.4 | 2026-10-06 | Product & SDD | protege control plane contra patches automáticos e define CODEX-01 base-trusted para forks sem execução de código externo |
| 0.5 | 2026-10-06 | Product & SDD | limita remediação automática a PRs same-repo e alinha critérios/rollout às versões atuais |
| 0.6 | 2026-10-06 | Product & SDD | torna review de fork tool-less e adiciona trust gate, idempotência e quotas antes de chamadas pagas |
| 0.7 | 2026-10-07 | Product & SDD | torna reserva de quota atômica entre PRs por autor e fail-closed em reservas ambíguas |
| 0.8 | 2026-10-07 | Product & SDD | substitui `concurrency` como fila por journal durável + drainer/reconciler idempotente |

## 26. Aprovação

### Revisão

- **Parecer de `review-sdd`:** Pronta para aprovação
- **Versão revisada:** 0.8
- **Evidência técnica:** CODEX-01 clean no HEAD `85a7541646ce22c5d9a2784c8a6623e42675890a` e Governance Gates #9 com sucesso
- **Pendências bloqueantes:** Nenhuma
- **Pendências não bloqueantes:** definir modelo e hard budget de API antes do canary

### Gate humano

- **Aprovada:** Sim
- **Versão aprovada:** 0.8
- **Responsável humano:** Ramon Rodriguez
- **Data:** 2026-10-07
- **Registro da aprovação:** PR #2, comentário #6043168597 (`HUMAN_APPROVAL`)
