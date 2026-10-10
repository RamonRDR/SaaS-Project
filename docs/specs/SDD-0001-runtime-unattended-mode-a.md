# SDD-0001 - Runtime unattended cloud-native do Modo A

## Metadados

- **ID:** SDD-0001
- **Título:** Runtime unattended cloud-native do Modo A
- **Status:** Approved
- **Versão:** 1.6
- **Responsável pela especificação:** Product & SDD
- **Responsável humano pela aprovação:** Ramon Rodriguez
- **Data de criação:** 2026-10-06
- **Última atualização:** 2026-10-09
- **Entrega / issue / PR relacionada:** Issue #1
- **ADRs relacionados:** ADR-0010, ADR-0012 rev.7 (`Superseded`, histórico), ADR-0013 rev.1 (`Superseded`, histórica), ADR-0014 rev.5 (`Accepted`, vigente)
- **SDDs relacionadas:** Não aplicável

### Estados permitidos

- `Draft`: em elaboração;
- `In Review`: pronta para revisão, ainda não aprovada;
- `Approved`: revisão concluída e aprovação humana explicitamente registrada;
- `Superseded`: substituída por outra SDD identificada e já `Approved`.

Uma SDD não pode assumir `Approved` por decisão de um agente de IA.

### Versão da especificação e validade da aprovação

As seções 1 a 24 compõem o conteúdo material da especificação.

Esta versão 1.6 responde aos findings P1/P2 do Codex no HEAD `9ca3248`: o fingerprint do CODEX-01 precisa refletir não só changeset, mas a revisão imutável e COMPLETA do contrato trusted de review (workflow/prompt/schema/modelo/políticas/parser e dependências do caminho de execução); o Remediator precisa de `root_cause_family_id` confiável em sua `operation_key` para separar causas independentes e contar tentativas anti-loop por causa mesmo entre HEADs. A restrição de um CODEX-01 pago por HEAD e snapshot imutável de preço/caps permanecem. Mudança do contrato trusted invalida clean antigo; se já houve review pago no HEAD, nova inferência exige novo HEAD. ADR-0013 rev.1 era a decisão histórica vigente antes da sucessão. SDD v1.6 e ADR-0014 rev.5 foram aprovadas/aceitas explicitamente pelo responsável humano; ainda não há execução paga autorizada sem implementação e canaries seguros.

Qualquer mudança material nas seções 1 a 24 invalida este parecer técnico, incrementa a versão e exige novo ciclo de revisão e aprovação.

> **Nota administrativa posterior à aprovação (2026-10-09):** as referências de estado nas seções materiais 1–24 refletem o momento de elaboração/revisão. Seu texto está preservado exatamente como no blob humano-aprovado `42766e86cba23a8f3045d89a8b17c741bc8d7d26`. O estado jurídico-operacional atual prevalente nos metadados é: SDD-0001 v1.6 `Approved`, ADR-0014 rev.5 `Accepted` e ADR-0013 rev.1 `Superseded` por sucessão humana registrada no PR #2 comentário #6091567757. Esta anotação NÃO altera regra/decisão material; chamadas pagas continuam bloqueadas até canaries e limites aprovados.

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
- serialização do runtime por PR com `concurrency` e, separadamente, writer ÚNICO para transições financeiras/claim de TODOS os PRs/workflows;
- CI/gates atuais integrados ao fluxo;
- Codex para gerar propostas de remediação em job sem credencial GitHub com escrita;
- Trusted Publisher separado do processo Codex, responsável pela validação e publicação do patch;
- denylist obrigatória do control plane protegido antes de qualquer publicação automática;
- CODEX-01 como review independente do HEAD exato;
- CODEX-01 base-trusted para forks, executado por broker determinístico e tool-less da `main`, sem checkout, execução do código externo ou ferramentas agentivas;
- trust gate + quotas/idempotência antes de qualquer chamada paga disparada por fork;
- ingresso durável separado do writer financeiro, operado por código trusted da `main` com permissão mínima `issues:write` em issue de inbox dedicado, antes de wake-up; reconciler periódico também rederiva intents elegíveis de PR/HEAD;
- drainer base-trusted que reconcilia fila durável, quotas adicionais para fork e solicita claim UNIVERSAL ao escritor global;
- prova de completude do payload de fork derivado das árvores do **merge-base** e HEAD exatos, com base_tip registrada como metadado;
- Budget Broker global com writer único efetivo, idempotência, reserva pessimista e reconciliação; não presumir CAS de valor/versão por `force:false`;
- publicação automática de commits apenas na branch elegível do PR same-repo e somente pelo Trusted Publisher;
- dispatcher confiável previamente instalado na `main` como etapa de bootstrap;
- reentrada exclusiva no dispatcher confiável da `main`: `repository_dispatch` no default branch ou `workflow_dispatch` com `ref: main` explícito; PR/HEAD como dados, nunca scripts/permissions do PR;
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
- **BR-002:** PR originado de fork e seus jobs consumidores nunca recebem `OPENAI_API_KEY`, token com escrita ou secret privilegiado. O reviewer base-trusted, carregado da `main`, prepara o payload sem checkout nem execução de conteúdo do fork e solicita inferência ao Budget Broker isolado; somente o Budget Broker recebe `OPENAI_API_KEY` e realiza a chamada paga após os gates.
- **BR-003:** jobs de PR/fork não confiáveis nunca recebem token com escrita. **Exceções trusted exclusivamente da `main`**: intake mínimo para Issue inbox com `issues:write` e `contents:read`, sem secret OpenAI ou execução de PR/fork; Budget Broker/writer e Trusted Publisher com privilégios separados e gates rigorosos. CODEX-01 de fork continua read-only para conteúdo Git e sem execução de fork. Token Git não é delimitado por branch: toda operação privilegiada deve verificar ref, origem e identidade.
- **BR-004:** toda execução começa reconciliando PR, HEAD, checks, estado e evidências atuais.
- **BR-005:** `concurrency` por PR com `cancel-in-progress:false` é auxiliar. Mutação do ledger de claim/finanças exige exclusão de writer global entre TODOS os PRs/workflows. Grupo global de Actions não é fila durável, pode substituir run pending, nem fornece CAS de versão; precisa de prova E2E de exclusão e recuperação.
- **BR-006:** novo HEAD invalida CI, review, READY e autorização associados ao HEAD anterior.
- **BR-007:** CODEX-01 só é válido para o HEAD exato revisado.
- **BR-008:** Codex Remediator e CODEX-01 usam contextos/jobs separados.
- **BR-009:** CODEX-01 não possui permissão para publicar código.
- **BR-010:** o job que executa Codex Remediator não recebe token GitHub com `contents: write`; sua saída mutável é somente um patch/artefato estruturado associado ao PR e ao HEAD esperados.
- **BR-011:** a publicação Git da remediação ocorre em job separado, sem execução de Codex, chamado Trusted Publisher; antes de qualquer push ele valida origem same-repo confiável, HEAD esperado, ref de destino, escopo do patch e invariantes do contrato.
- **BR-012:** o Trusted Publisher só pode publicar na branch corrente do PR elegível; nunca diretamente na `main`.
- **BR-013:** a mesma causa raiz admite no máximo 3 tentativas automáticas antes de `LOOP_ESCALATION_REQUIRED`.
- **BR-014:** ausência ou ambiguidade de evidência resulta em fail-closed.
- **BR-015:** o Trusted Publisher solicita reentrada somente ao dispatcher confiável versionado na `main`; para `workflow_dispatch`, `ref: main` é obrigatório, nunca omitido/branch do PR; `repository_dispatch` é recebido pelo workflow da branch padrão. Reconciliar HEAD após o evento, sem depender de push com GITHUB_TOKEN.
- **BR-016:** workflow de reentrada é instalado na `main` por bootstrap aprovado antes do canary; validar ref/identidade do dispatcher antes de executar código privilegiado. Mesmo PR same-repo não pode fornecer workflow/ações/scripts/secrets de ref de PR via dispatch.
- **BR-017:** `READY_FOR_HUMAN_MERGE` só é emitido com CI verde, CODEX-01 limpo e evidências do mesmo HEAD.
- **BR-018:** merge principal exige autorização humana explícita vinculada ao PR/HEAD.
- **BR-019:** PHASE-0-G permanece bloqueada até canary E2E e `DONE_ALLOWED`.
- **BR-020:** o Trusted Publisher mantém denylist fail-closed do control plane protegido. No mínimo são proibidos patches automáticos em `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` e `docs/PROJECT_STATUS.md`. Se qualquer arquivo do patch corresponder à denylist, o patch inteiro não é publicado e a transição é `HUMAN_DECISION_REQUIRED`.
- **BR-021:** alterações na própria denylist, no Publisher, dispatcher, workflows, prompts, schemas, state machine ou contratos de governança nunca podem ser autoaprovadas pelo mesmo runtime que protegem; exigem PR/review/gate humano fora da remediação automática.
- **BR-022:** para PR de fork, CODEX-01 executa em contexto base-trusted a partir da branch padrão, usando somente workflow, prompt, schema e tooling da `main`; obtém metadados e diff pela API do GitHub, trata-os como dados não confiáveis, não faz checkout do HEAD do fork e não executa nenhum arquivo do PR.
- **BR-023:** a evidência CODEX-01 de fork deve registrar o `head.sha` exato. Se o HEAD mudar durante ou após o review, a evidência é stale e deve ser descartada antes de READY.
- **BR-024:** findings em fork não acionam Trusted Publisher nem remediação automática com escrita; o autor ou responsável humano produz novo HEAD e o fluxo reexecuta CI read-only e CODEX-01 base-trusted.
- **BR-025:** CODEX-01 de fork não usa Codex Action/CLI em modo agentivo. O broker de review, versionado na `main` e sem segredo do provedor, obtém o changeset de merge-base/HEAD via API Git, normaliza o payload e solicita inferência exclusivamente ao Budget Broker. O Budget Broker aplica quotas, reserva financeira global e chama a OpenAI; o modelo não recebe shell, filesystem, comandos, tools/functions, subprocessos ou acesso ao runner. Dados não confiáveis trafegam somente como payload estruturado, nunca interpolados em shell.
- **BR-026:** apenas o processo isolado do Budget Broker, carregado da `main`, recebe `OPENAI_API_KEY` para qualquer review ou remediação paga. O CODEX-01 de fork e o Codex Remediator não recebem a chave nem credenciais delegadas, mesmo quando são jobs confiáveis. O Budget Broker opera com menor privilégio possível, sem `sudo`/elevação ou execução de artefatos do fork; jamais inclui o segredo em prompt, output, artifact ou log. Ferramentas agentivas no reviewer de fork são fail-closed.
- **BR-027:** antes de uma chamada paga para fork, o runtime aplica trust gate. Autorização automática é restrita a `OWNER`, `MEMBER` ou `COLLABORATOR`; qualquer outro `author_association` exige aprovação explícita de maintainer vinculada ao PR antes da primeira chamada paga.
- **BR-028:** CODEX-01 (fork e same-repo) faz no máximo UMA chamada paga por `head_sha` em um mesmo PR, com `authorized_attempt=0` fixo, independentemente de eventos, base, contrato trusted ou reruns. Evidência clean vincula `review_context_fingerprint` a base_ref, merge_base_sha, payload_digest, HEAD e `trusted_review_contract_digest` da `main` (workflow, prompt, schema e todas as dependências executáveis/políticas do reviewer, incluindo parser e modelo efetivo). Se contexto OU contrato mudar mantendo HEAD após chamada paga, invalidar evidence clean e exigir NOVO HEAD antes de uma nova inferência paga; nunca reusar saída antiga nem fazer segunda API no mesmo HEAD. Mudança isolada de base_tip sem alteração de fingerprint exige reconciliação de CI/mergeabilidade. Quotas de fork adicionais são 3/PR e 5/autor externo por 24h.
- **BR-029:** trust gate ausente ou quota excedida bloqueia a chamada antes de consumir a API e produz `HUMAN_DECISION_REQUIRED`; eventual override humano deve ser explícito, auditável e vinculado ao PR/HEAD específico, sem desabilitar permanentemente as quotas.
- **BR-030:** identidade paga é discriminada por `operation_kind`: CODEX-01 = `repo/pr/head_sha/CODEX_01/authorized_attempt=0` (no máximo uma chamada por HEAD); Remediator = `repo/pr/head_sha/REMEDIATOR/root_cause_family_id/authorized_attempt`, com ID da causa normalizado/classificado pelo reducer confiável da `main`, não texto arbitrário de comentário/modelo. Remediator mantém também contador anti-loop durável por `repo/pr/root_cause_family_id` **entre HEADs**, limite de 3 tentativas da mesma causa, distinguindo causas independentes mesmo quando tentativa=0. `request_id` deriva da chave adequada sem `workflow_run_id`. Intake trusted separado grava JSON em Issue de inbox antes de wake-up, readback obrigatório. Evidência de CODEX-01 inclui `review_context_fingerprint` e provenance do contrato trusted.
- **BR-031:** separar **inbox de intents** (comentários de Issue de controle, criados pelo intake trusted com permissão issues:write, sem mutar ledger) de **ledger canônico** (claim, quota, orçamento, dispatch, mutável SOMENTE pelo writer global). Reconciler verifica identidade do autor trusted, schema, PR/HEAD, operation_key, páginas completas e provenance. Comentários inválidos, modificados ou truncados falham fechados. Somente ledger governa estados `PENDING → ELIGIBLE → CLAIMED → BUDGET_RESERVED → DISPATCH_AUTHORIZED → SENT/AMBIGUOUS → SETTLED/BLOCKED`.
- **BR-032:** o drainer base-trusted reconcilia backlog persistido e revalida origem/HEAD/trust/quota; apenas o writer global serializado decide claim, quota adicional e reserva monetária. Jobs consumidores não mutam ledger e não recebem secret do provedor. Backlog não é equiparado a um workflow run.
- **BR-033:** wake-up é best-effort APÓS persistência no inbox. Reconciler periódico trusted da `main` varre inbox E PRs/HEAD elegíveis para reparar evento perdido antes de ingresso; paginação/ACK desconhecidos exigem readback e fail-closed. Pending Actions coalescido não apaga pedido; writes do ledger não geram push-trigger recursivo.
- **BR-034:** quota fork usa reservation ID estável por autor/PR/HEAD e limites vigentes. Toda reserva financeira identifica `operation_key`, período UTC, modelo/operação, **pricing_snapshot_digest** imutável, versão do catálogo e caps aplicados. A unicidade de efeito financeiro e dispatch é por `operation_key`, não por snapshot/version adicional: mudança de preço ou caps NUNCA cria segundo gasto ou solta valor incerto. Reentrada lê a mesma reserva ou bloqueia, sem refazer claim.
- **BR-035:** claim universal por `operation_key` é único para fork/same-repo/Remediator, decidido pelo writer global; quota fork `RESERVED → CONSUMED` é adicional. Persistir owner executante `consumer_run_id` e `fencing_epoch` monotônico. Se worker morrer ANTES de qualquer reserva financeira, autorização ou dispatch, writer pode transferir execução sem novo claim somente após readback autoritativo provar ausência desses estados, confirmar lease anterior encerrado/expirado, incrementar epoch e impedir worker antigo de pagar. Qualquer ambiguidade bloqueia.
- **BR-036:** reviewer de fork não usa `pulls/{pr}/files` nem diff textual para provar completude. Fixa `base_ref`, `base_tip_sha`, `head_sha` e resolve merge-base commit pela API Git, comparando árvores completas `merge_base_sha..head_sha`, com vínculo ao mesmo PR e branch-alvo. Ausência/ambiguidade do merge-base, truncamento, alteração de target base ou HEAD divergente bloqueia review até nova reconciliação.
- **BR-037:** o changeset do PR é calculado exclusivamente por comparação das árvores completas de `merge_base_sha` e `head_sha` (sem usar a ponta `base_tip_sha` para diferenças). Para cada path alterado o broker obtém os objetos exigidos e registra adição, modificação, exclusão, modo e submódulo. A comparação deve refletir o diff de três pontos do PR, mesmo que a branch base avance após a divergência; conflito e mergeabilidade continuam gates separados.
- **BR-038:** broker registra `base_ref`, `base_tip_sha`, `merge_base_sha`, `head_sha`, manifests de árvores completos e payload_digest. Calcula `trusted_review_contract_digest=SHA256(manifest canônico de arquivos e dependências efetivamente executáveis do reviewer da main: workflow, prompt, schema, policy/config, broker/parser/normalizer, modelo/versão, parâmetros pertinentes)`, registrando origem `main_source_commit_sha`. O manifest deve listar dependências transitivas e versões/SHAs; componente omitido, alteração desconhecida ou fonte que não seja da main => fail-closed. `review_context_fingerprint=SHA256(canon(repo,pr,base_ref,merge_base_sha,head_sha,payload_digest,trusted_review_contract_digest))`. Revalidar digest trusted CURRENT e fingerprint no READY, não somente ao iniciar inferência. Alteração de contrato/completude com HEAD igual invalida clean antigo; após review pago, exigir NOVO HEAD para outra chamada, sem violar uma chamada por SHA. Mudança isolada de base_tip com fingerprint estável só revalida demais gates.
- **BR-039:** conteúdo binário não revisável, objeto Git não suportado, blob indisponível, qualquer truncamento detectado ou payload integral que exceda o limite configurado de review resulta em fail-closed e `HUMAN_DECISION_REQUIRED`. É proibido truncar, amostrar, omitir arquivos ou enviar apenas prefixo do diff e ainda considerar CODEX-01 válido.
- **BR-040:** reserva/dispatch possivelmente iniciado ou envio incerto preserva teto financeiro e bloqueia retry automático. Exceção para claim sem reserva/dispatch: reconciler pode solicitar takeover controlado do MESMO claim sob writer global, com prova negativa integral, fencing epoch novo e invalidação do worker antigo, nunca outro claim/quota CONSUMED.
- **BR-041:** TODA chamada de IA paga (fork, same-repo e Remediator) exige `operation_key`, claim universal e autorização financeira no mesmo Budget Broker trusted da `main`. Só Budget Broker recebe `OPENAI_API_KEY`; consumidores não usam SDK/CLI/Action para bypass. Sem writer global exclusivo efetivamente comprovado, bloquear API paga.
- **BR-042:** antes de habilitar o runtime, um responsável humano define orçamento mensal monetário global em unidade inteira mínima (por exemplo, centavos USD), mês-calendário UTC e catálogo versionado de preços/modelos/operações suportados. Sem limite positivo, preço conhecido, caps de entrada/saída ou forma verificável de contabilização, a chamada falha fechada em `BLOCKED_EXTERNAL`/`HUMAN_DECISION_REQUIRED`. Alertas e limites da plataforma não são tratados como o teto primário.
- **BR-043:** antes da API o Budget Broker calcula teto conservador para modelo/operação com catálogo versionado e limites realmente impostos (input/output, requests, retries, ferramentas/custos adicionais), serializando `pricing_snapshot_digest` canônico dos valores usados no `check+reserve`. Preços/caps desconhecidos, sem limite imposto ou fallback não cotado bloqueiam. O resumo de preço e caps é imutável após autorização de reserva; nunca recalcular para cima sem nova transição autorizada.
- **BR-044:** writer global único guarda `operation_key`, geração, `financial_reservation_id`, `pricing_snapshot_digest`, `price_catalog_version`, modelo/operação, caps, máximo reservado, período UTC, committed/outstanding e identidade do vencedor. Idempotência financeira por operação: rerun devolve registro existente apenas se todos os parâmetros de preço/caps e contexto ainda corresponderem, sem incrementar outstanding ou novo dispatch; divergência marca `BLOCKED_REPRICE` e não libera reserva anterior por timeout. `committed_minor+outstanding_max_minor+new_max_minor<=budget_limit_minor` sob exclusão real, com readback. Git `PATCH force:false` NÃO é CAS semântico: CAS-Lab provou stale 5→2. Configuração/preço alterados antes de envio exigem bloqueio; ajuste eventual requer prova inequívoca de não-dispatch e nova decisão serializada de orçamento, com delta integral reservado e sem segundo claim, nunca atualização silenciosa.
- **BR-045:** validar relógio UTC ao reservar e antes do envio; claim lógico universal é imutável e não pertence a mês financeiro. Rollover invalida autorização financeira antiga, nunca o claim. Novo `check+reserve` do bucket vigente somente para mesmo vencedor após prova inequívoca de não-envio; reserva antiga permanece conservadoramente comprometida.
- **BR-046:** aumento de teto, alteração de preço, caps ou versão do catálogo é controlado por decisão humana quando aplicável. O ledger referencia o snapshot imutável efetivamente reservado. Se o catálogo/caps vigentes divergirem do snapshot, a autorização pré-dispatch é INVÁLIDA: não reutilizar quota antiga, não enviar, não soltar reserva ambígua; escolher reconciliação segura com nova reserva/delta sob writer global e prova de não-dispatch, ou bloquear para novo HEAD/decisão humana. Versão inesperada do ledger falha fechada.
- **BR-047:** testar os 3 consumidores e seis PRs, exclusão global, stale Git 5→2, crash/readback, intake/main-only/fencing, UTC e teto; testes específicos de alteração de base_ref/merge-base/payload/contrato trusted de review em main com HEAD igual, recusa de evidência antiga no READY, segundo CODEX-01 negado, novas chamadas apenas em novo HEAD; duas causas independentes do Remediator com attempt=0, contador por família estável entre HEADs, limite de 3 e anti-loop sem alias de chaves.
- **BR-048:** antes de enviar chamada paga, Budget Broker confirma claim/fencing válido, operação sem envio anterior, UTC do período, preço/caps **idênticos ao `pricing_snapshot_digest` da reserva** e máximo de tokens/retries realmente imposto ao provedor. Divergência invalida dispatch mesmo que reserva antiga exista; sem nova decisão serializada/ajuste integral e prova de não-envio, fail-closed. Virada UTC renova apenas reserva financeira do mesmo vencedor após prova de não-dispatch, nunca claim/consumo fork.
- **BR-049:** ordem universal: `request durável → elegibilidade (trust/quota adicional somente fork) → claim lógico único → orçamento idempotente via writer global → UTC → autorização de dispatch durável → API → conciliação`. Reentrada por novo workflow_run_id nunca duplica claim, reserva ou chamada.

- **BR-050:** writer único serializa TODAS as mutações de quota, claim e dinheiro entre workflows e PRs, sem executar código de fork nem receber conteúdo de controle não confiável. Concurrency group global pode ser auxiliar, não prova transação nem fila. Inexistência de exclusão efetiva bloqueia calls.
- **BR-051:** cada transição financeira lê e verifica ledger imediatamente antes de gravar SOB exclusão global, persiste uma geração lógica monotônica e faz readback após retorno ambíguo. Não permitir fast-forward com snapshot lógico regressivo; se não for demonstrável, trocar storage por CAS server-side.
- **BR-052:** `consumer_run_id` é metadado e nunca gera operação nova. Chave CODEX-01 é por repo/PR/HEAD/kind/attempt fixo; chave Remediator acrescenta `root_cause_family_id` e attempt autorizado. Takeover pré-financeiro conserva mesma chave e eleva fencing_epoch; tentativa em causa diferente possui chave distinta, mas mesmo root não pode renovar contador anti-loop ao mudar HEAD.
- **BR-053:** intake trusted grava solicitação em Issue inbox antes de wake-up, com permissões mínimas `issues:write` sem `contents:write` nem secret de IA. Reconciler periódico varre inbox e PRs para reconstruir intents perdidas. Dispatch só com main trusted; ledger não emite wake-ups recursivos.
- **BR-054:** evidência empírica obrigatória: `RamonRDR/SaaS-CAS-Lab`, run `37873320199`, `docs/RESULTS_2026-10-09.md`. Commits irmãos retornaram 200/422, mas fast-forward stale retornou 200 e regrediu geração 5→2. Essas provas refutam CAS lógico por Git-ref isolado; ainda falta canary de writer global real no SaaS.
- **BR-055:** toda reentrada roda dispatcher/controle/prompt e script exclusivamente da `main` revisada. `workflow_dispatch` sempre inclui `ref: main` e nunca ref do PR; `repository_dispatch` só aciona o workflow da branch padrão. PR e HEAD são dados a validar, não fonte de permissões.
- **BR-056:** o intake confiável da `main` possui somente `issues:write` para persistir comentário de inbox e `contents:read`; sua ausência de `contents:write` e `OPENAI_API_KEY` é testada. Reconciler autentica provenance, valida completude da enumeração e reconstrói intenções elegíveis de PR/HEAD caso evento ou persistência tenham falhado; duplicatas não criam operações.
- **BR-057:** a retomada de `CLAIMED` sem reserva é permitida SOMENTE com prova negativa completa de qualquer reserva/autorização/dispatch/envio, writer global exclusivo, fencing_epoch novo e revogação da execução antiga. Worker stale não pode requisitar budget; dúvida financeira mantém fail-closed sem retry automático.
- **BR-058:** `review_context_fingerprint` governa validade de evidência do CODEX-01 por identidade de changeset E contrato trusted completo, mas não renova unicidade de pagamento por HEAD. Mudança em workflow/prompt/schema/policy/modelo/parser/dep executada da main, ainda com mesmo HEAD/payload, invalida clean anterior; READY exige versão trusted vigente. Se já houve pagamento, exigir novo HEAD, nunca segunda chamada CODEX-01 naquele SHA.
- **BR-059:** `pricing_snapshot_digest` é criado a partir de versão do catálogo, preço aplicável, modelo/operação, input/output caps, retries/request cap e custos adicionais. Budget Broker verifica exatamente esses limites também no dispatch e o ledger não aceita reuso silencioso quando versão/preços/caps mudam; bloquear ou ajustar delta positivamente sob writer serializado e prova de não-envio. Um snapshot novo NUNCA é mecanismo para gerar segunda operação paga do mesmo `operation_key`.
- **BR-060:** CODEX-01 fork/same-repo exige `authorized_attempt=0`, sem bypass por run ID ou versão de contrato. Remediator admite tentativas individualizadas por `root_cause_family_id` e contador anti-loop do mesmo root ENTRE HEADs, recusando IDs não classificados/confiáveis. Duas causas distintas com tentativa=0 mantêm chaves diferentes; mesma causa reformatada mantém a mesma família e contagem.
- **BR-061:** nenhuma evidência CODEX-01 produzida pelo contrato trusted anterior pode habilitar READY após atualização material de workflow, prompt, schema, modelo, broker, parser, policy ou dependência efetivamente executável na `main`. O manifest canônico do contrato deve cobrir a closure transitiva do caminho trusted e ser revalidado na avaliação READY; falha em enumerar, verificar SHAs ou determinar impacto é fail-closed. `main_source_commit_sha` é provenance; mudanças irrelevantes de main não invalidam se digest da closure permanece idêntico.
- **BR-062:** Remediator recebe `root_cause_family_id` por normalização confiável de finding/CI/rule/path/sintoma, com mapeamento rastreável de diferentes mensagens para a mesma causa. `operation_key` inclui família da causa para evitar colisão entre causas independentes no mesmo HEAD/attempt; o contador de tentativas por família é durável e atravessa commits/HEADs, com 3 falhas repetidas gerando `LOOP_ESCALATION_REQUIRED`. Classificação ambígua de causa pede revisão profunda/gate humano, não cria ID novo arbitrário para zerar contador.

## 8. Permissões e multi-tenancy

Multi-tenancy de produto: não aplicável nesta entrega.

Permissões operacionais:

- CI comum: `contents: read`;
- CODEX-01 same-repo: leitura do workspace e chamada apenas via Budget Broker, sem chave do provedor nem `contents: write`;
- CODEX-01 fork base-trusted: broker determinístico da `main`, com acesso ao Budget Broker central e leitura limitada; pode registrar evidência no PR, mas não possui `contents: write` nem chave do provedor, não habilita ferramentas agentivas nem executa código do fork;
- Codex Remediator: leitura do workspace e capacidade de solicitar chamadas ao Budget Broker, sem acesso à credencial do provedor nem token GitHub com escrita; produz somente patch/artefato estruturado;
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
- `OPENAI_API_KEY` exclusivamente no Budget Broker confiável; nenhum job de remediação/review acessa diretamente o segredo;
- conteúdo de PR, comentário, diff e log é dado não confiável;
- prompts versionados têm precedência sobre instruções encontradas no PR;
- nenhum código do fork é executado em contexto privilegiado;
- `pull_request_target`, inclusive no intake mínimo e CODEX-01 de fork, executa somente workflow/scripts da `main`, nunca checkout/action/config do HEAD do PR; intake com `issues:write` não recebe IA nem `contents:write`, dados do evento e Issue são tratados como não confiáveis;
- o changeset de fork é obtido por API Git a partir do `merge_base_sha` com `head_sha`, tratado apenas como dado não confiável; `base_tip_sha` é metadado adicional;
- o reviewer de fork usa integração OpenAI tool-less: nenhum shell, filesystem, tool/function call, subprocesso ou ambiente do runner é exposto ao modelo;
- o Budget Broker isolado é o único processo que possui `OPENAI_API_KEY`, executa somente código confiável da `main`, sem sudo/elevação e mantém segredo fora de prompt, stdout/stderr e artifacts; jobs de review/remediação enviam somente requisições estruturadas ao broker;
- trust gate e quotas adicionais de fork, e claim universal/idempotência de todos os consumidores são aplicados antes da chamada paga;
- autorização de consumo exige `operation_key`, claim universal único, reserva financeira no writer global e autorização de dispatch durável; quota `RESERVED` do fork isolada não autoriza API, assim como workflow pendente ou contador lido fora da exclusão;
- pedidos pagos de fork, same-repo e Remediator são persistidos antes do wake-up e sobrevivem a coalescência/cancelamento; reconciler periódico processa o backlog;
- custo máximo monetário global é reservado pelo writer único do Budget Broker sob exclusão efetiva e teste de invariantes; `force:false` em Git ref é apenas controle de fast-forward, não CAS transacional de dados;
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
| EDGE-001 | dois eventos simultâneos no mesmo PR | `concurrency` por PR é auxiliar; claim/budget são exclusivos pelo writer global e `operation_key` deduplica eventos |
| EDGE-002 | PR de fork | CI do fork roda read-only; CODEX-01 roda em workflow base-trusted da `main` lendo somente diff/API; remediação automática com escrita fica indisponível |
| EDGE-003 | HEAD muda durante job | abortar mutação e reconciliar |
| EDGE-004 | CI falha por causa corrigível em PR same-repo elegível | Codex Remediator recebe causa específica e pode produzir patch para novo HEAD |
| EDGE-005 | CI falha por decisão material | `HUMAN_DECISION_REQUIRED` |
| EDGE-006 | review encontra P0/P1/P2 corrigível em PR same-repo elegível | remediar e gerar novo HEAD automaticamente; em fork aplica-se BR-024 |
| EDGE-007 | terceiro fracasso da mesma causa | `LOOP_ESCALATION_REQUIRED` |
| EDGE-008 | API OpenAI indisponível/sem saldo/secret ausente | `BLOCKED_EXTERNAL` |
| EDGE-009 | push com GITHUB_TOKEN não dispara fluxo | Trusted Publisher executa `repository_dispatch` ou `workflow_dispatch` com ref main explícito, sem scripts da branch PR |
| EDGE-010 | dispatcher inexistente em main ou `workflow_dispatch` sem ref | bloquear canary e qualquer execução privilegiada antes de bootstrap trusted |
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
| EDGE-022 | eventos repetidos para mesmo HEAD do fork ou tentativa diferente | uma única inferência CODEX-01 por SHA, tentativa fixa 0; retornar evidência válida para mesmo fingerprint ou bloquear caso mudanças invalidem contexto |
| EDGE-023 | fork sem trust gate | não chamar OpenAI; emitir `HUMAN_DECISION_REQUIRED` |
| EDGE-024 | 4ª chamada do mesmo PR em 24h ou 6ª do mesmo autor externo em 24h | bloquear antes da API e emitir `HUMAN_DECISION_REQUIRED` |
| EDGE-025 | mesmo autor dispara forks em vários PRs | quota extra é contabilizada sob writer global e pedido é durável antes do wake-up |
| EDGE-026 | múltiplos wake-ups do drainer são coalescidos/substituídos pelo GitHub | nenhum pedido é perdido; próxima execução/reconciliação lê o backlog persistido e continua |
| EDGE-027 | crash antes/depois de envio pago sem certeza | não liberar quota/custo nem repetir mesmo `operation_key`; readback e gate humano |
| EDGE-028 | consumidor tenta chamar API sem claim universal e autorização financeira | Budget Broker nega; nenhum consumidor acessa segredo |
| EDGE-029 | drainer não recebe novo wake-up após existir backlog | reconciler periódico detecta `PENDING`/`RESERVED` incompleto e reacorda o fluxo sem intervenção humana |
| EDGE-030 | dois consumidores competem por mesma operação | claim universal único por writer; perdedor não ocupa orçamento |
| EDGE-031 | endpoint de arquivos/diff do PR omite ou trunca alterações | ignorar como prova; reconstruir por Git Trees/Blobs ou falhar fechado |
| EDGE-032 | tree/blob da API indica truncamento, está ausente ou não pode ser enumerado integralmente | não chamar modelo e emitir `HUMAN_DECISION_REQUIRED` |
| EDGE-033 | mudança contém binário/objeto não revisável ou payload integral excede limite do reviewer | não fazer review parcial; `HUMAN_DECISION_REQUIRED` |
| EDGE-034 | crash após `CONSUMED` antes de evidência inequívoca da chamada | manter consumo e bloquear retry automático do mesmo SHA |
| EDGE-035 | base_ref, merge-base ou digest mudam com HEAD inalterado | review_context_fingerprint muda; evidência antiga inválida, nenhuma segunda chamada CODEX-01 nesse HEAD; exige novo HEAD para re-review pago. Se somente base_tip avançar e fingerprint persistir, revalidar demais gates |
| EDGE-036 | merge-base ausente/ambíguo ou resolução falha | bloquear review; nenhuma evidência clean |
| EDGE-037 | seis PRs disputam teto global | writer global serializado autoriza apenas reservas até teto, reentradas idempotentes |
| EDGE-043 | runners fork/same-repo/remediator disputam mesmo `operation_key` | apenas `consumer_run_id` vencedor passa, perdedor sem custo |
| EDGE-044 | crash após claim antes de budget | readback comprova ausência de reserva/dispatch, writer incrementa fencing_epoch e transfere o mesmo claim; se incerto, bloqueia |
| EDGE-045 | mesma operação reaparece após versão de preços/caps alterada | snapshot imutável não corresponde à configuração; negar dispatch e não liberar reserva ambígua; ajuste conservador sob writer somente com prova de não-envio |
| EDGE-038 | orçamento não configurado, preço desconhecido ou custo máximo ilimitado | bloquear antes da API |
| EDGE-039 | custo/dispatch ambíguo ou crash após autorização de envio | conservar reserva máxima e bloquear chamada duplicada |
| EDGE-040 | mês UTC muda após elegibilidade/quota de fork e antes do claim universal | claim lógico não pertence ao bucket mensal; reservar orçamento somente no UTC vigente |
| EDGE-041 | mês UTC muda após claim e antes do dispatch | novo CAS financeiro do mês atual somente para mesmo winner e com prova de não-envio; NUNCA novo claim/`CONSUMED` |
| EDGE-042 | relógio confiável indisponível, divergente ou próximo demais da virada | bloquear novas chamadas pagas e registrar motivo fail-closed |

| EDGE-046 | dois workflows mutadores usam grupos concorrentes diferentes | configuração inválida, fail-closed; writer global único entre PRs/workflows |
| EDGE-047 | Git `force:false` aceita fast-forward com conteúdo baseado em geração antiga | guard semântico rejeita regressão de valor/versão; sem exclusão real, bloquear API |
| EDGE-048 | update do ledger retorna erro depois de possível persistência | readback por HEAD/identidade, jamais repetir operação sem reconciliar |
| EDGE-049 | dois run IDs para mesma intent | intake pode registrar duplicata, mas writer usa operation_key único |
| EDGE-050 | pending Actions coalescido | inbox durável e scanner periódico de PR/HEAD reencontram solicitação |
| EDGE-051 | crash entre autorização durável de envio e HTTP | estado ambíguo, máximo reservado, nenhum retry pago automático |
| EDGE-052 | falha de intake antes de wake-up | sem execução paga; scanner periódico rederiva PR/HEAD e persiste intenção antes de novo wake-up |
| EDGE-053 | duplicação/edição de comentários do inbox | verificar provenance e schema; deduplicar por operation_key; inválidos bloqueiam |
| EDGE-054 | workflow_dispatch recebe ref omitido ou branch PR | negar, só ref main explícito; repository_dispatch via default branch |
| EDGE-055 | worker antigo acorda após takeover | fencing_epoch stale barra reserva e dispatch |
| EDGE-056 | claim parece pré-reserva mas ledger/provenance incerto | sem takeover, manter bloqueio humano |
| EDGE-057 | merge-base ou contrato trusted do revisor muda com mesmo HEAD após CODEX-01 pago | invalidar evidence clean, bloquear segundo review pago e requerer novo HEAD; registrar digest/versão trusted atual no READY |
| EDGE-058 | catálogo/caps muda entre reserva e dispatch | `pricing_snapshot_digest` diverge, negar API, preservar custo reservado, submeter delta sob exclusão e prova de não-envio ou bloquear |
| EDGE-059 | caller de CODEX-01 incrementa `authorized_attempt` para repetir | rejeitar valor diferente de zero antes de claim, budget e quota; Remediator obedece tentativa própria |
| EDGE-060 | workflow/prompt/schema/parser/política/modelo do reviewer muda na main, mas o PR mantém HEAD e merge-base | `trusted_review_contract_digest` muda, evidence clean anterior falha no READY; exigir novo HEAD antes de nova inferência paga |
| EDGE-061 | duas causas independentes do Remediator coexistem no mesmo HEAD com attempt 0 | root_cause_family_id diferente torna operation_key diferente; anti-loop de cada família separado, sem gasto duplicado |
| EDGE-062 | mesma causa raiz reaparece após novo HEAD com texto reformatado | reducer conserva root_cause_family_id e contador entre HEADs; 3 repetições provocam LOOP_ESCALATION_REQUIRED, sem reset por novo SHA |

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
- claim universal por `operation_key` para fork, same-repo e Remediator, com `RESERVED → CONSUMED` como quota extra apenas para fork;
- prova de que dois consumidores concorrentes da mesma reserva geram no máximo uma chamada paga;
- enumeração completa de base/HEAD por Git Trees e obtenção integral de blobs/objetos alterados;
- detecção fail-closed de respostas truncadas, objetos ausentes, binários não revisáveis e payload acima do limite;
- geração e validação do manifest/digest de completude vinculado ao HEAD;
- teste de diff de três pontos com base avançada após divergência, verificando `merge_base_sha` e ausência de alterações exclusivas da base;
- teste com mudança efetiva de base_ref/merge-base/payload digest SEM alterar HEAD: invalidar review anterior e exigir novo HEAD, sem segunda API CODEX-01; mudança isolada de base_tip preserva fingerprint após reconciliação dos gates;
- teste de atualização em main do workflow, prompt, schema, parser, política e dependência transitiva do reviewer sem alteração de HEAD: fingerprint muda e READY invalida clean antigo; mudanças não participantes não disparam nova API;
- teste de duas causas raiz Remediator simultâneas com mesmo HEAD/tentativa e de mesma causa após HEAD novo, provando keys distintas e contador de 3 por família;
- teste de preços/caps versionados: reserva sob catálogo antigo, alteração antes de dispatch, falha fechada e nenhum excesso de orçamento; tentativa diferente de zero para CODEX-01 recusa antes de gastar;
- teste sem ancestral comum, mudança de base_tip e HEAD stale bloqueando evidência;
- orçamento global com writer único efetivo, preços/caps verificados e teste negativo de fast-forward stale (geração 5→2), sem confundir `force:false` com CAS lógico;
- testes de budget: seis PRs, todos os três consumidores, mesmo `operation_key`, disputa entre workflows, erro ACK/readback, crash entre claim/budget/dispatch, virada UTC sem segundo claim;
- teste UTC com relógio controlado demonstra claim lógico imutável e renovação somente financeira no mês novo com prova inequívoca de não-envio;
- teste de janela de segurança em fronteira de mês, falha de relógio, drift e interrupção de dispatch comprova ausência de chamada paga;
- regressão de storage recusa fast-forward com ledger obsoleto, writer múltiplo e perda de pending em `concurrency`;
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
- teste prova que qualquer consumidor, inclusive same-repo e Remediator, é bloqueado sem `operation_key`, claim universal, reserva financeira e dispatch autorizado no mesmo HEAD;
- teste concorrente executa dois consumidores para o mesmo `operation_key` nos três tipos; apenas um claim universal e um dispatch pago são permitidos; fork aplica `RESERVED → CONSUMED` adicional sob writer único;
- teste simula crash após claim universal/`CONSUMED` fork e comprova que reconciler/retry não faz outra chamada paga;
- teste cria cenário com quantidade de arquivos acima do que o endpoint de arquivos do PR consegue representar e comprova que o broker não depende desse endpoint para completude;
- testes simulam resposta truncada, blob ausente, binário e payload acima do limite e comprovam que nenhum CODEX-01 clean é emitido;
- teste valida que o manifest/digest cobre exatamente todos os paths alterados derivados das árvores base/HEAD;
- remediação não escreve `main`;
- reviewer não publica código;
- teste garante que Codex Action/CLI não possua credencial/rota direta capaz de contornar o Budget Broker;
- teste negativo verifica a ausência de `OPENAI_API_KEY` (e de tokens delegados do provedor) no ambiente, outputs e permissões de Codex Remediator, CODEX-01 same-repo, CODEX-01 de fork e Trusted Publisher; somente o job isolado do Budget Broker pode obter o secret;
- teste de integração bloqueia qualquer chamada paga quando um consumidor tenta acessar a API sem passar pelo Budget Broker;
- limite monetário global falha fechado em qualquer condição desconhecida;
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
- **AC-005:** código/ambiente de fork, CODEX-01 base-trusted, CODEX-01 same-repo, Codex Remediator e Trusted Publisher não recebem `OPENAI_API_KEY` nem acesso direto à inferência paga; somente o Budget Broker isolado da `main` detém o segredo, sem checkout/execução de conteúdo do fork.
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
- **AC-021:** CODEX-01 (fork e same-repo) limita inferência paga a UMA por HEAD independentemente do número de eventos/`authorized_attempt`; no fork trust gate e quota adicional se aplicam.
- **AC-022:** o baseline bloqueia antes da API a 4ª chamada paga do mesmo PR em 24h e a 6ª do mesmo autor externo em 24h, salvo override humano explícito e vinculado ao HEAD.
- **AC-023:** cada solicitação elegível de fork é persistida como `PENDING` com `request_id` determinístico antes do wake-up; teste concorrente com pelo menos 6 PRs comprova que nenhum pedido é perdido mesmo se execuções pendentes do drainer forem coalescidas.
- **AC-024:** quotas adicionais de fork por PR/autor são serializadas entre PRs, sem bloquear same-repo/Remediator por ausência de quota de fork.
- **AC-025:** nenhuma chamada paga ocorre sem solicitação durável, claim universal, reserva financeira válida e autorização de dispatch para o mesmo `operation_key`/HEAD; quota adicional de fork permanece obrigatória.
- **AC-026:** uma reserva ambígua por crash não é reutilizada para uma segunda chamada automática do mesmo SHA; ela continua contando na quota até expiração ou override humano explícito.
- **AC-027:** reconciler da main lê inbox e estado canônico PR/HEAD para recuperar intents não persistidas por falha de evento ou ingresso, sem wake-up humano e sem gastos duplicados.
- **AC-028:** um claim universal por `operation_key` nos três consumidores; quota `RESERVED → CONSUMED` extra só no fork.
- **AC-029:** CODEX-01 de fork só pode ser considerado válido quando existe prova de completude do payload derivada dos Git Trees/Blobs integrais do base e HEAD exatos.
- **AC-030:** review fork com changeset truncado, incompleto ou incapaz de provar merge-base, objetos ou digest falha-closed; não substituir evidência stale por re-review pago do mesmo SHA.
- **AC-031:** reviewer registra base_ref/merge_base_sha/head_sha/payload_digest e manifest `trusted_review_contract_digest` da closure completa de workflow/prompt/schema/parser/policy/modelo, com SHAs e proveniência na main. READY recomputa fingerprint do contrato atual. Mudança material do changeset OU contrato com HEAD igual invalida evidence clean, exige novo HEAD para segunda inferência paga; mudança apenas de base_tip não invalida se fingerprint igual.
- **AC-032:** merge-base é calculado/verificado a partir da história Git para o par base_tip/HEAD, e apenas `merge_base_sha..head_sha` define as mudanças revisadas; teste com base avançada comprova ausência de remoções falsas.
- **AC-033:** sem orçamento global positivo, preço/caps conhecidos e teto imposto não há API; reserva persiste `pricing_snapshot_digest` imutável da cotação conservadora.
- **AC-034:** chamada paga exige claim universal, writer global e reserva versionada por preços/caps no ledger; mudança de versão/caps antes do dispatch bloqueia reuso do registro até reconciliação e ajuste do teto sob exclusão real, sem segundo claim/call.
- **AC-035:** seis PRs concorrentes mantêm teto global; crash ambíguo retém custo e writer prova exclusão entre workflows.
- **AC-036:** alteração do catálogo, preço ou caps após reserva não libera valor incerto nem permite envio acima da reserva original; dispatch valida snapshot idêntico à configuração realmente usada na API.
- **AC-037:** UTC do budget é validado ao reservar e antes da API; claim universal permanece único e não muda com o mês.
- **AC-038:** teste de rollover entre claim universal, orçamento e dispatch prova autorização financeira do UTC vigente e NENHUM segundo claim após mudança de mês, inclusive relógio incerto/janela insegura.
- **AC-039:** dois workers do mesmo `operation_key` em fork/same-repo/Remediator disputam claim universal, só winner pode reservar.
- **AC-040:** idempotência financeira por operation_key; crash comprovadamente pré-financeiro pode retomar mesmo claim com fencing_epoch novo, mas ambiguidade após reserva/dispatch não autoriza repetição.

- **AC-041:** writer global efetivo serializa as alterações de claim/quota/budget de TODOS os workflows; teste prova invariantes além de `concurrency` por PR.
- **AC-042:** teste negativo CAS-Lab (run 37873320199) é regressão obrigatória: atualizar ledger com commit fast-forward stale 5→2 é barrado pelo guard de writer ou backend com CAS server-side; `force:false` isolado não satisfaz gate.
- **AC-043:** resposta ambígua de escrita exige readback por identidade e geração; falhas antes/depois da autorização de dispatch não repetem gasto.
- **AC-044:** reentrada, novo consumer e rollover UTC não geram segundo claim/dispatch; somente renovação financeira do mês com evidência de não-envio.
- **AC-045:** fila de intenções resiste a pending Actions substituído e reconciler periódico progride sem triggers recursivos do ledger.
- **AC-046:** intake trusted com somente issues:write/contents:read persiste comentário JSON no inbox ANTES do wake-up; falhas, duplicatas, paginação e autor inválido são tratados; scanner de PR/HEAD reconstrói intent perdida.
- **AC-047:** `workflow_dispatch` sempre tem `ref: main` explícito e `repository_dispatch` só usa dispatcher da branch padrão; PR same-repo que altera workflow não consegue executar código privilegiado não revisado.
- **AC-048:** após crash comprovadamente pré-reserva, escritor retoma sem novo claim lógico incrementando fencing_epoch; worker antigo não reserva nem despacha; HEAD original preservado.
- **AC-049:** reserva, dispatch ou envio potencialmente iniciado/ambíguo bloqueia takeover e mantém teto comprometido até conciliação ou decisão humana.
- **AC-050:** quando apenas base_tip avança e fingerprint/trusted contract não muda, revalidar CI/mergeabilidade sem segunda inferência. Alterar base_ref/merge-base/payload_digest/contrato trusted (inclusive workflow, prompt ou schema na main) com HEAD igual invalida evidence CODEX-01 e exige novo HEAD antes de nova chamada paga.
- **AC-051:** reserva persistida tem versão/preços/caps/digest imutáveis; reentrada após alteração de catálogo/caps não envia API usando reserva antiga. Reconciliação de delta sob writer com prova de não-dispatch preserva teto ou fail-closed.
- **AC-052:** CODEX-01 em fork/same-repo mantém authorized_attempt=0; Remediator exige root_cause_family_id classificado pelo trusted reducer, com tentativa e contador por causa ao longo de HEADs. Attempts manipulados ou IDs de causa sem provenance são recusados antes de pagar.
- **AC-053:** canary troca workflow, prompt, schema e uma dependência transitiva do CODEX-01 na main após evidence clean, sem mexer HEAD/merge-base; READY rejeita evidência de contrato anterior, não chama IA outra vez no mesmo HEAD, exige novo HEAD. Mudança de arquivo não participante do contrato não deve causar retry pago.
- **AC-054:** duas causas independentes do Remediator no mesmo HEAD e na tentativa 0 produzem request/operation keys distintos, enquanto rephrasing da mesma causa em HEAD novo preserva contador e atinge LOOP_ESCALATION_REQUIRED na 3ª repetição, sem bypass por ID alternativo.

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
- ADR-0013 rev.1 permanece `Accepted` até aceite humano da ADR-0014 rev.5; SDD v1.6/ADR-0014 rev.5 são propostas em revisão e não autorizam API paga.

## 22. Riscos conhecidos

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| custo inesperado de API | gasto financeiro | Budget Broker com escritor global efetivo, reserva conservadora, idempotência e readback; Git force:false não implementa CAS financeiro de valor/versão |
| abuso por fork/PR externo | consumo de API, indisponibilidade do gate, perda de pedidos, review parcial ou tentativa de exfiltração | reviewer tool-less + trust gate + fila durável + claim atômico exclusivo antes da API + prova de completude por Git Trees/Blobs + fail-closed para payload não integral + idempotência por SHA + quotas + hard budget global |
| prompt injection | alteração indevida | contrato versionado + outputs estruturados + fail-closed |
| patch de IA altera o próprio control plane | bypass de gates ou persistência maliciosa | denylist fail-closed de paths protegidos + `HUMAN_DECISION_REQUIRED` antes da escrita |
| processo Codex obtém capacidade de escrita | push indevido | job de geração sem escrita + Trusted Publisher separado e validado |
| dispatcher ausente da branch padrão | reentrada não ocorre no primeiro rollout | bootstrap do dispatcher na `main` antes do canary |
| corrida entre eventos | commits conflitantes | concurrency por PR auxiliar, writer global serializado e reconciler de backlog durável |
| loop de remediação | custo/instabilidade | 3 tentativas por causa raiz |
| indisponibilidade OpenAI | fluxo interrompido | `BLOCKED_EXTERNAL` + fallback interativo |
| mudança de política de runners | custo/limite futuro | monitorar billing e manter arquitetura portável |

## 23. Dúvidas abertas

Nenhuma lacuna impeditiva para revisão documental; single-writer efetivo, recuperação de falha e storage continuam exigências de canary da implementação, não garantias já provadas no SaaS.

Antes do canary devem ser definidos como configuração operacional:

- modelo Codex/OpenAI usado em remediação e review;
- orçamento monetário mensal global do Budget Broker, precificação conservadora por modelo e caps de tokens/retries, obrigatórios antes de qualquer chamada;
- alertas/limites da plataforma como defesa adicional (enforcement pode ter atraso);
- forma exata de armazenar/parsear output estruturado;
- demonstrar exclusão global do writer em todos os workflows. Se não comprovável com GitHub, selecionar storage com CAS server-side antes de habilitar API paga.

Esses itens não podem reduzir os controles descritos nesta SDD.

## 24. ADRs necessários ou relacionados

- **ADR necessário:** Sim
- **Referências:** ADR-0010, ADR-0012 rev.7 (`Superseded`), ADR-0013 rev.1 (`Accepted`, vigente), ADR-0014 rev.5 (`Proposed`, contrato trusted e identity de causa Remediator)
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
| 0.8 | 2026-10-07 | Product & SDD | substitui `concurrency` como fila por journal durável + drainer/reconciler idempotente; versão aprovada humanamente no PR #2 |
| 0.9 | 2026-10-07 | Product & SDD | exige completude integral do payload de fork e claim atômico exclusivo da reserva antes da API |
| 1.0 | 2026-10-08 | Product & SDD | corrige diff para merge-base/head e exige orçamento global independente, atômico e bloqueante antes de toda chamada paga |
| 1.1 | 2026-10-08 | Product & SDD | revalida mês UTC no claim e no dispatch; restaura ADR-0012 imutável e propõe ADR-0013 como sucessora; aprovada pelo humano no PR #2 |
| 1.2 | 2026-10-08 | Product & SDD | P2: claim quota antes do budget; referências ADR-0012/0013 alinhadas |
| 1.3 | 2026-10-09 | Product & SDD | claim universal, UTC imutável, writer global, prova CAS-Lab |
| 1.4 | 2026-10-09 | Product & SDD | intake mínimo, ref main e takeover fenced (P1/P1/P2) |
| 1.5 | 2026-10-09 | Product & SDD | fingerprint de changeset, snapshot de preços e CODEX-01 attempt fixo |
| 1.6 | 2026-10-09 | Product & SDD | contrato trusted completo no fingerprint e root_cause_family_id no Remediator; P1/P2 do HEAD 9ca3248 |

## 26. Aprovação

### Revisão

- **Parecer de `review-sdd`:** Pronta para aprovação (parecer técnico favorável anterior à decisão humana)
- **Versão revisada:** 1.6; blob `42766e86cba23a8f3045d89a8b17c741bc8d7d26`, HEAD avaliado `7613e8550bc1f973fc758a5446a120370a733a80`
- **Revisor:** Orchestrator / Tech Lead
- **Data:** 2026-10-09
- **Evidência anterior:** SDD v1.1 aprovada, Codex no HEAD `a58a1f7` identificou P1 same-repo e P2 UTC; CAS-Lab demonstrou o limite de `force:false` no run #37873320199.
- **Pendências bloqueantes:** Nenhuma para aprovação documental de v1.6; requisitos de implementação e canary permanecem obrigatórios.
- **Pendências não bloqueantes:** implementação, configuração de orçamento/preços e canary E2E antes de uso pago.

### Gate humano

- **Aprovada:** Sim
- **Versão aprovada:** 1.6
- **Responsável humano:** Ramon Rodriguez
- **Data:** 2026-10-09
- **Registro da aprovação atual:** PR #2 comentário #6091567757 (`ORCHESTRATOR_RECORDED_HUMAN_APPROVAL`), decisão humana expressa no ChatGPT para SDD v1.6, HEAD material `7613e8550bc1f973fc758a5446a120370a733a80`.
- **Aprovação histórica preservada:** SDD v0.8/ADR-0012 rev.7 (#6043168597), SDD v1.1/ADR-0013 rev.1 (#6070726649); limitadas às próprias versões.
