# SDD-0001 - Runtime unattended cloud-native do Modo A

## Metadados

- **ID:** SDD-0001
- **Título:** Runtime unattended cloud-native do Modo A
- **Status:** In Review
- **Versão:** 1.3
- **Responsável pela especificação:** Product & SDD
- **Responsável humano pela aprovação:** Ramon Rodriguez
- **Data de criação:** 2026-10-06
- **Última atualização:** 2026-10-09
- **Entrega / issue / PR relacionada:** Issue #1
- **ADRs relacionados:** ADR-0010, ADR-0012 rev.7 (histórico, `Superseded`), ADR-0013 rev.1 (`Accepted`, vigente), ADR-0014 rev.2 (`Proposed`, sucessora)
- **SDDs relacionadas:** Não aplicável

### Estados permitidos

- `Draft`: em elaboração;
- `In Review`: pronta para revisão, ainda não aprovada;
- `Approved`: revisão concluída e aprovação humana explicitamente registrada;
- `Superseded`: substituída por outra SDD identificada e já `Approved`.

Uma SDD não pode assumir `Approved` por decisão de um agente de IA.

### Versão da especificação e validade da aprovação

As seções 1 a 24 compõem o conteúdo material da especificação.

Esta versão 1.3 consolida o P1/P2 do Codex Review no HEAD `a58a1f7` e a prova real `RamonRDR/SaaS-CAS-Lab` run #37873320199. O claim de inferência paga passa a ser UNIVERSAL para fork, same-repo CODEX-01 e Codex Remediator; quotas adicionais valem apenas para fork. O orçamento exige writer único global confiável e recuperação fail-closed; Git PATCH `force:false` NÃO é CAS transacional de geração (teste aceitou geração stale 5→2 com HTTP 200). O claim lógico não é refeito na virada UTC, somente a autorização financeira pode ser renovada após prova de não-envio. SDD v1.1 e ADR-0013 rev.1 já aceitas permanecem históricas; SDD v1.3 e ADR-0014 rev.2 exigem novo parecer e decisão humana antes de vigorar.

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
- serialização do runtime por PR com `concurrency` e, separadamente, writer ÚNICO para transições financeiras/claim de TODOS os PRs/workflows;
- CI/gates atuais integrados ao fluxo;
- Codex para gerar propostas de remediação em job sem credencial GitHub com escrita;
- Trusted Publisher separado do processo Codex, responsável pela validação e publicação do patch;
- denylist obrigatória do control plane protegido antes de qualquer publicação automática;
- CODEX-01 como review independente do HEAD exato;
- CODEX-01 base-trusted para forks, executado por broker determinístico e tool-less da `main`, sem checkout, execução do código externo ou ferramentas agentivas;
- trust gate + quotas/idempotência antes de qualquer chamada paga disparada por fork;
- fila durável de solicitações de review de fork no GitHub, criada antes de qualquer drainer/wake-up;
- drainer base-trusted que reconcilia fila durável, quotas adicionais para fork e solicita claim UNIVERSAL ao escritor global;
- prova de completude do payload de fork derivado das árvores do **merge-base** e HEAD exatos, com base_tip registrada como metadado;
- Budget Broker global com writer único efetivo, idempotência, reserva pessimista e reconciliação; não presumir CAS de valor/versão por `force:false`;
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
- **BR-002:** PR originado de fork e seus jobs consumidores nunca recebem `OPENAI_API_KEY`, token com escrita ou secret privilegiado. O reviewer base-trusted, carregado da `main`, prepara o payload sem checkout nem execução de conteúdo do fork e solicita inferência ao Budget Broker isolado; somente o Budget Broker recebe `OPENAI_API_KEY` e realiza a chamada paga após os gates.
- **BR-003:** jobs com escrita Git só operam em branch do mesmo repositório e origem considerada confiável. O único job privilegiado permitido para fork é o CODEX-01 base-trusted, limitado a leitura de repositório/PR e publicação de evidência de review, sem `contents: write`.
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
- **BR-025:** CODEX-01 de fork não usa Codex Action/CLI em modo agentivo. O broker de review, versionado na `main` e sem segredo do provedor, obtém o changeset de merge-base/HEAD via API Git, normaliza o payload e solicita inferência exclusivamente ao Budget Broker. O Budget Broker aplica quotas, reserva financeira global e chama a OpenAI; o modelo não recebe shell, filesystem, comandos, tools/functions, subprocessos ou acesso ao runner. Dados não confiáveis trafegam somente como payload estruturado, nunca interpolados em shell.
- **BR-026:** apenas o processo isolado do Budget Broker, carregado da `main`, recebe `OPENAI_API_KEY` para qualquer review ou remediação paga. O CODEX-01 de fork e o Codex Remediator não recebem a chave nem credenciais delegadas, mesmo quando são jobs confiáveis. O Budget Broker opera com menor privilégio possível, sem `sudo`/elevação ou execução de artefatos do fork; jamais inclui o segredo em prompt, output, artifact ou log. Ferramentas agentivas no reviewer de fork são fail-closed.
- **BR-027:** antes de uma chamada paga para fork, o runtime aplica trust gate. Autorização automática é restrita a `OWNER`, `MEMBER` ou `COLLABORATOR`; qualquer outro `author_association` exige aprovação explícita de maintainer vinculada ao PR antes da primeira chamada paga.
- **BR-028:** reviews pagos de fork são idempotentes por `head.sha`: no máximo uma chamada CODEX-01 por SHA. Além disso, o baseline limita a 3 chamadas pagas por PR em janela móvel de 24h e 5 chamadas pagas por autor externo em janela móvel de 24h no repositório. A contabilização usa reservas duráveis, não apenas evidência posterior à chamada.
- **BR-029:** trust gate ausente ou quota excedida bloqueia a chamada antes de consumir a API e produz `HUMAN_DECISION_REQUIRED`; eventual override humano deve ser explícito, auditável e vinculado ao PR/HEAD específico, sem desabilitar permanentemente as quotas.
- **BR-030:** TODA solicitação paga elegível (fork, same-repo CODEX-01, Remediator) é persistida antes do wake-up. Chave lógica estável `operation_key = repository/pr/head_sha/operation_kind/authorized_attempt` e `request_id` derivado dela, sem `workflow_run_id`. No fork CODEX-01 admite somente `authorized_attempt=0` para mesmo HEAD, com `author_id` vinculado; reentradas não criam novos gastos.
- **BR-031:** fila/journal e ledger financeiro são recursos GitHub confiáveis com mutação exclusivamente pelo writer global. Estado universal de operação `PENDING → ELIGIBLE → CLAIMED → BUDGET_RESERVED → DISPATCH_AUTHORIZED → SENT/AMBIGUOUS → SETTLED/BLOCKED` e prova durável por `operation_key`, HEAD, consumer vencedor, período UTC, reserva e provenance; quota de fork `RESERVED → CONSUMED` é guarda adicional, não claim separado. Nunca persistir secrets.
- **BR-032:** o drainer base-trusted reconcilia backlog persistido e revalida origem/HEAD/trust/quota; apenas o writer global serializado decide claim, quota adicional e reserva monetária. Jobs consumidores não mutam ledger e não recebem secret do provedor. Backlog não é equiparado a um workflow run.
- **BR-033:** wake-ups/dispatch são best-effort; reconciliação periódica na `main` varre pedidos duráveis mesmo quando pending de `concurrency` é substituído. Gatilhos `push` do ledger são isolados de reentrada; comentários, payload do evento e logs não são fonte suficiente para execução.
- **BR-034:** quota de fork tem `quota_reservation_id` estável por autor/PR/HEAD e limites atuais (3/PR/24h, 5/autor externo/24h). Reserva financeira de TODOS os consumidores deriva de `operation_key + budget_period_utc + model + operation`. Uma nova execução GitHub não muda a chave e não autoriza outro envio; estado ambíguo é fail-closed.
- **BR-035:** o writer global realiza claim UNIVERSAL `ELIGIBLE → CLAIMED` para fork, same-repo CODEX-01 e Remediator, persistindo o ÚNICO `consumer_run_id` por `operation_key`. No fork, `RESERVED → CONSUMED` de quota é executado sob a mesma exclusão, não é um segundo claim independente. Somente vencedor recebe budget; perdedores sem reserva/API. Crash claim→budget não concede retry pago automático.
- **BR-036:** o reviewer de fork não usa o endpoint `pulls/{pr}/files` nem diff textual do PR como prova de completude. Ele fixa `base_tip_sha` e `head_sha`, resolve por API Git confiável o **merge-base commit** de ambos, verifica que é ancestral comum e constrói os manifests canônicos das árvores de `merge_base_sha` e `head_sha`. `base_tip_sha` é apenas metadado adicional e não é o lado esquerdo do diff. Ausência ou ambiguidade de merge-base, resposta truncada ou HEAD divergente bloqueia CODEX-01.
- **BR-037:** o changeset do PR é calculado exclusivamente por comparação das árvores completas de `merge_base_sha` e `head_sha` (sem usar a ponta `base_tip_sha` para diferenças). Para cada path alterado o broker obtém os objetos exigidos e registra adição, modificação, exclusão, modo e submódulo. A comparação deve refletir o diff de três pontos do PR, mesmo que a branch base avance após a divergência; conflito e mergeabilidade continuam gates separados.
- **BR-038:** antes do modelo, o broker produz evidência de completude com `base_tip_sha`, `merge_base_sha`, `head_sha`, total de paths alterados, lista canônica before/after com object SHAs/modes, tamanhos e digest do payload normalizado. A evidência clean exige associação ao mesmo par merge-base/HEAD; alteração da base_tip exige reconciliação de CI/mergeabilidade antes de READY.
- **BR-039:** conteúdo binário não revisável, objeto Git não suportado, blob indisponível, qualquer truncamento detectado ou payload integral que exceda o limite configurado de review resulta em fail-closed e `HUMAN_DECISION_REQUIRED`. É proibido truncar, amostrar, omitir arquivos ou enviar apenas prefixo do diff e ainda considerar CODEX-01 válido.
- **BR-040:** falha/timeout do vencedor após claim, reserva ou dispatch ambíguo mantém claim e custo máximo comprometidos, sem reverter `CONSUMED` de fork nem repetir chamada por reentrada. Reconciler exige evidência terminal inequívoca antes de recuperação ou escala decisão humana.
- **BR-041:** TODA chamada de IA paga (fork, same-repo e Remediator) exige `operation_key`, claim universal e autorização financeira no mesmo Budget Broker trusted da `main`. Só Budget Broker recebe `OPENAI_API_KEY`; consumidores não usam SDK/CLI/Action para bypass. Sem writer global exclusivo efetivamente comprovado, bloquear API paga.
- **BR-042:** antes de habilitar o runtime, um responsável humano define orçamento mensal monetário global em unidade inteira mínima (por exemplo, centavos USD), mês-calendário UTC e catálogo versionado de preços/modelos/operações suportados. Sem limite positivo, preço conhecido, caps de entrada/saída ou forma verificável de contabilização, a chamada falha fechada em `BLOCKED_EXTERNAL`/`HUMAN_DECISION_REQUIRED`. Alertas e limites da plataforma não são tratados como o teto primário.
- **BR-043:** o Budget Broker calcula **limite superior conservador** por chamada antes da API: máximo de tokens de entrada aceitos, máximo de saída explicitamente imposto, quantidade máxima de requisições e retries, tabelas de preços versionadas e quaisquer custos adicionais possíveis. Entrada ou output não limitado, preço desconhecido, custos não cobertos e fallback não cotado bloqueiam a chamada. Quotas de fork continuam sendo guardas adicionais.
- **BR-044:** ledger global persiste `operation_key`, geração, request/finance reservation IDs, modelo, consumer vencedor, período, `committed_minor`, `outstanding_max_minor`. Apenas writer único global validado executa `check+reserve` de custo máximo depois do claim universal; repetição da chave retorna mesma reserva sem incrementar custo nem habilitar outra chamada. Critério: `committed_minor + outstanding_max_minor + new_max_minor <= budget_limit_minor`. Prova negativa CAS-Lab run #37873320199: `PATCH force:false` aceitou descendente com geração 5→2; logo NÃO é CAS de valor/versão. Writer precisa revalidar invariantes imediatamente antes de persistir sob exclusão efetiva; sem prova disso, fail-closed ou backend com CAS real.
- **BR-045:** validar relógio UTC ao reservar e antes do envio; claim lógico universal é imutável e não pertence a mês financeiro. Rollover invalida autorização financeira antiga, nunca o claim. Novo `check+reserve` do bucket vigente somente para mesmo vencedor após prova inequívoca de não-envio; reserva antiga permanece conservadoramente comprometida.
- **BR-046:** limite configurado não pode ser elevado nem política de preços enfraquecida por PR, bot, comentário ou execução automatizada. Mudança de orçamento, mês/catálogo de preços ou permissão de bypass exige decisão humana auditável e controle de acesso; nenhuma chamada prossegue se o ledger estiver indisponível, inconsistente ou com versão inesperada.
- **BR-047:** testar os três consumidores, seis PRs competindo por teto global, concorrência entre workflows, versão stale fast-forward, writer único, retries por chave estável, falha/timeout e readback ambíguo, janela UTC, fonte de verdade, isolamento de secrets e recuperação de wake-ups. Evidência do CAS-Lab não substitui canary E2E do writer de produção.
- **BR-048:** imediatamente antes da API, Budget Broker confirma vencedor universal, autorização financeira do mês UTC atual, janela temporal segura e estado durável de dispatch. Na virada UTC não refazer claim lógico nem quota `CONSUMED`; renovar SOMENTE autorização financeira para mesmo vencedor e após prova de não-envio. Envio ambíguo conserva custo máximo e bloqueia retry automático.
- **BR-049:** ordem universal: `request durável → elegibilidade (trust/quota adicional somente fork) → claim lógico único → orçamento idempotente via writer global → UTC → autorização de dispatch durável → API → conciliação`. Reentrada por novo workflow_run_id nunca duplica claim, reserva ou chamada.

- **BR-050:** writer único serializa TODAS as mutações de quota, claim e dinheiro entre workflows e PRs, sem executar código de fork nem receber conteúdo de controle não confiável. Concurrency group global pode ser auxiliar, não prova transação nem fila. Inexistência de exclusão efetiva bloqueia calls.
- **BR-051:** cada transição financeira lê e verifica ledger imediatamente antes de gravar SOB exclusão global, persiste uma geração lógica monotônica e faz readback após retorno ambíguo. Não permitir fast-forward com snapshot lógico regressivo; se não for demonstrável, trocar storage por CAS server-side.
- **BR-052:** `consumer_run_id` é metadado do vencedor, não componente da chave que permite novo gasto; `operation_key` é estável por HEAD/tipo/tentativa autorizada, inclusive em reentrada, crash e rollover UTC.
- **BR-053:** reconciler periódico identifica requests perdidas por pending Actions substituído e acorda writer; estado de envio ambíguo é escalado e não repetido. Commits no ledger não podem realimentar wake-up.
- **BR-054:** evidência empírica obrigatória: `RamonRDR/SaaS-CAS-Lab`, run `37873320199`, `docs/RESULTS_2026-10-09.md`. Commits irmãos retornaram 200/422, mas fast-forward stale retornou 200 e regrediu geração 5→2. Essas provas refutam CAS lógico por Git-ref isolado; ainda falta canary de writer global real no SaaS.

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
- `pull_request_target`, quando usado para CODEX-01 de fork, fica restrito a workflow da base e é proibido de fazer checkout, importar action/script/configuração do HEAD ou interpolar conteúdo não confiável em shell;
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
| EDGE-035 | base avança após fork divergir | calcular diff por `merge_base(base_tip, head)...head`, nunca `base_tip..head`; nova base_tip exige reconciliação dos gates |
| EDGE-036 | merge-base ausente/ambíguo ou resolução falha | bloquear review; nenhuma evidência clean |
| EDGE-037 | seis PRs disputam teto global | writer global serializado autoriza apenas reservas até teto, reentradas idempotentes |
| EDGE-043 | runners fork/same-repo/remediator disputam mesmo `operation_key` | apenas `consumer_run_id` vencedor passa, perdedor sem custo |
| EDGE-044 | crash após claim e antes do budget | claim imutável, leitura/reconciliação e sem retry pago ambíguo |
| EDGE-045 | mesmo pedido financeiro reaparece com novo run ID | retorna mesma reserva por chave estável e não repete dispatch |
| EDGE-038 | orçamento não configurado, preço desconhecido ou custo máximo ilimitado | bloquear antes da API |
| EDGE-039 | custo/dispatch ambíguo ou crash após autorização de envio | conservar reserva máxima e bloquear chamada duplicada |
| EDGE-040 | mês UTC muda após elegibilidade/quota de fork e antes do claim universal | claim lógico não pertence ao bucket mensal; reservar orçamento somente no UTC vigente |
| EDGE-041 | mês UTC muda após claim e antes do dispatch | novo CAS financeiro do mês atual somente para mesmo winner e com prova de não-envio; NUNCA novo claim/`CONSUMED` |
| EDGE-042 | relógio confiável indisponível, divergente ou próximo demais da virada | bloquear novas chamadas pagas e registrar motivo fail-closed |

| EDGE-046 | dois workflows mutadores usam grupos concorrentes diferentes | configuração inválida, fail-closed; writer global único entre PRs/workflows |
| EDGE-047 | Git `force:false` aceita fast-forward com conteúdo baseado em geração antiga | guard semântico rejeita regressão de valor/versão; sem exclusão real, bloquear API |
| EDGE-048 | update do ledger retorna erro depois de possível persistência | readback por HEAD/identidade, jamais repetir operação sem reconciliar |
| EDGE-049 | dois eventos criam run IDs diferentes da mesma chamada lógica | mesmo `operation_key`, claim/reserva/dispatch únicos |
| EDGE-050 | pending Actions substituído por novo wake-up | solicitação permanece durável, reconciler periódico restaura progresso |
| EDGE-051 | crash entre autorização durável de envio e HTTP | estado ambíguo, máximo reservado, nenhum retry pago automático |

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
- **AC-021:** o mesmo `head.sha` de fork gera no máximo uma chamada paga de CODEX-01.
- **AC-022:** o baseline bloqueia antes da API a 4ª chamada paga do mesmo PR em 24h e a 6ª do mesmo autor externo em 24h, salvo override humano explícito e vinculado ao HEAD.
- **AC-023:** cada solicitação elegível de fork é persistida como `PENDING` com `request_id` determinístico antes do wake-up; teste concorrente com pelo menos 6 PRs comprova que nenhum pedido é perdido mesmo se execuções pendentes do drainer forem coalescidas.
- **AC-024:** quotas adicionais de fork por PR/autor são serializadas entre PRs, sem bloquear same-repo/Remediator por ausência de quota de fork.
- **AC-025:** nenhuma chamada paga ocorre sem solicitação durável, claim universal, reserva financeira válida e autorização de dispatch para o mesmo `operation_key`/HEAD; quota adicional de fork permanece obrigatória.
- **AC-026:** uma reserva ambígua por crash não é reutilizada para uma segunda chamada automática do mesmo SHA; ela continua contando na quota até expiração ou override humano explícito.
- **AC-027:** backlog persistido progride sem wake-up humano: reconciler periódico da `main` detecta pedidos não concluídos e reacorda o drainer.
- **AC-028:** um claim universal por `operation_key` nos três consumidores; quota `RESERVED → CONSUMED` extra só no fork.
- **AC-029:** CODEX-01 de fork só pode ser considerado válido quando existe prova de completude do payload derivada dos Git Trees/Blobs integrais do base e HEAD exatos.
- **AC-030:** truncamento, arquivo/objeto ausente, binário não revisável ou payload que não caiba integralmente no envelope configurado bloqueia antes do modelo ou antes da evidência clean e produz `HUMAN_DECISION_REQUIRED`.
- **AC-031:** o manifest de completude registra todos os paths alterados, before/after SHAs/modes e digest do payload normalizado para o mesmo `head.sha`, incluindo `merge_base_sha`.
- **AC-032:** merge-base é calculado/verificado a partir da história Git para o par base_tip/HEAD, e apenas `merge_base_sha..head_sha` define as mudanças revisadas; teste com base avançada comprova ausência de remoções falsas.
- **AC-033:** sem budget monetário global positivo e configurado, preços/versionamento conhecidos e teto pessimista de tokens/requisições aplicável, nenhuma chamada paga de IA ocorre.
- **AC-034:** toda chamada paga requer claim universal e orçamento no writer global, com prova de teto `committed_minor + outstanding_max_minor + new_max_minor <= budget_limit_minor`.
- **AC-035:** seis PRs concorrentes mantêm teto global; crash ambíguo retém custo e writer prova exclusão entre workflows.
- **AC-036:** alteração humana do orçamento é auditável; indisponibilidade/inconsistência do ledger, modelo sem preço ou custo sem teto resulta em fail-closed.
- **AC-037:** UTC do budget é validado ao reservar e antes da API; claim universal permanece único e não muda com o mês.
- **AC-038:** teste de rollover entre claim universal, orçamento e dispatch prova autorização financeira do UTC vigente e NENHUM segundo claim após mudança de mês, inclusive relógio incerto/janela insegura.
- **AC-039:** dois workers do mesmo `operation_key` em fork/same-repo/Remediator disputam claim universal, só winner pode reservar.
- **AC-040:** idempotência financeira deriva de operação lógica e período, sem novo custo por workflow_run_id; crash claim→budget ou dispatch não gera segundo pagamento.

- **AC-041:** writer global efetivo serializa as alterações de claim/quota/budget de TODOS os workflows; teste prova invariantes além de `concurrency` por PR.
- **AC-042:** teste negativo CAS-Lab (run 37873320199) é regressão obrigatória: atualizar ledger com commit fast-forward stale 5→2 é barrado pelo guard de writer ou backend com CAS server-side; `force:false` isolado não satisfaz gate.
- **AC-043:** resposta ambígua de escrita exige readback por identidade e geração; falhas antes/depois da autorização de dispatch não repetem gasto.
- **AC-044:** reentrada, novo consumer e rollover UTC não geram segundo claim/dispatch; somente renovação financeira do mês com evidência de não-envio.
- **AC-045:** fila de intenções resiste a pending Actions substituído e reconciler periódico progride sem triggers recursivos do ledger.

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
- ADR-0013 rev.1 permanece `Accepted` até aceite da ADR-0014 rev.2, ADR-0012 rev.7 `Superseded`. SDD v1.3 e ADR-0014 rev.2 exigem revisão e decisão humana. O CAS-Lab é evidência delimitada, não executor de produção.

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
- **Referências:** ADR-0010, ADR-0012 rev.7 (histórica, `Superseded`), ADR-0013 rev.1 (`Accepted`, vigente), ADR-0014 rev.2 (`Proposed`, writer global e claim universal)
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
| 1.3 | 2026-10-09 | Product & SDD | P1/P2: claim universal, UTC imutável, writer global; regressão CAS-Lab 5→2; requer revisão e novo gate humano |

## 26. Aprovação

### Revisão

- **Parecer de `review-sdd`:** Pendente de revisão técnica de v1.3
- **Versão revisada:** Não aplicável à v1.3 até novo parecer
- **Revisor:** Orchestrator / Tech Lead
- **Data:** 2026-10-09
- **Evidência anterior:** SDD v1.1 aprovada, Codex no HEAD `a58a1f7` identificou P1 same-repo e P2 UTC; CAS-Lab demonstrou o limite de `force:false` no run #37873320199.
- **Pendências bloqueantes:** review cruzado de v1.3/ADR-0014 rev.2 e aprovação humana pendentes; garantias operacionais do writer são testes/canaries da implementação.
- **Pendências não bloqueantes:** implementação, configuração de orçamento/preços e canary E2E antes de uso pago.

### Gate humano

- **Aprovada:** Não para a versão atual
- **Versão aprovada:** Não aplicável à v1.3
- **Responsável humano:** Ramon Rodriguez
- **Data:** Pendente para v1.3
- **Registro da aprovação atual:** Pendente. Aprovação da SDD v1.1 no comentário #6070726649 não aprova v1.3.
- **Aprovação histórica preservada:** SDD v0.8/ADR-0012 rev.7 (#6043168597) e SDD v1.1/ADR-0013 rev.1 (#6070726649); não aprovam SDD v1.3/ADR-0014 rev.2.
