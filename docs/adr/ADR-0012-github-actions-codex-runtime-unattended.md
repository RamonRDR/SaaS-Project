# ADR-0012 - GitHub Actions + Codex como runtime unattended

## Metadados

- **ID:** ADR-0012
- **Título:** GitHub Actions + Codex como runtime unattended
- **Status:** Proposed
- **Revisão decisória:** 8
- **Data de criação:** 2026-10-06
- **Última atualização:** 2026-10-07
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Ramon Rodriguez
- **SDDs relacionadas:** SDD-0001 v0.9
- **ADRs relacionados:** ADR-0010; ADR-0011 histórico privado não importado
- **PR / issue relacionada:** Issue #1

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável sem pendência bloqueante e aceite humano;
- `Rejected`: proposta rejeitada;
- `Superseded`: substituída por ADR posterior;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

### Revisão decisória e validade do parecer

As seções 1 a 14 compõem o conteúdo decisório. Qualquer mudança material antes do aceite incrementa a revisão decisória e invalida o parecer atual.

## 1. Contexto

O projeto exige um runtime unattended que continue o Mode A sem máquina local e sem mensagens humanas operacionais.

Um desenho experimental anterior usou um runtime externo reativo como elo entre eventos do GitHub e o ciclo CI/review. A continuidade real não foi suficientemente determinística. Esse experimento foi encerrado e não foi importado para o histórico público.

GitHub já é a fonte de verdade de PR, HEAD, workflows, permissões e merge. O runtime deve, portanto, residir no mesmo plano operacional sempre que possível.

## 2. Drivers da decisão

- autonomia real sem wake-up humano;
- zero runtime local;
- determinismo de eventos;
- segurança em repositório público;
- isolamento de secrets;
- auditabilidade;
- idempotência e concorrência;
- custo previsível;
- redução de componentes externos;
- reversibilidade;
- independência entre remediator e reviewer.

## 3. Restrições

- repositório público;
- standard GitHub-hosted runners;
- merge principal continua humano;
- forks são entradas não confiáveis;
- secrets não podem chegar a código de fork;
- nenhuma infraestrutura própria adicional;
- PHASE-0-G bloqueada até validação do runtime;
- GitHub Actions permanece compatível com ADR-0010.

## 4. Opções consideradas

### Opção A - Runtime externo reativo no critical path

**Descrição**

Eventos do GitHub acordam um runtime externo, que reconcilia o estado e executa uma transição por vez.

**Vantagens**
- baixo acoplamento com workflows;
- aproveita ferramenta conversacional já disponível.

**Desvantagens**
- continuidade depende de reativação externa após cada evento;
- comportamento de wake-up não oferece as garantias necessárias ao loop transacional.

**Riscos**
- fluxo fica parado sem sinal claro;
- intervenção humana volta a funcionar como polling manual.

**Impacto operacional / migração**
- arquitetura já experimentada e descartada.

### Opção B - GitHub Actions + Codex

**Descrição**

GitHub Actions executa a state machine, CI, guards, dispatch e transições. Codex é chamado em jobs específicos para geração de remediação e review, sempre sem credencial GitHub com escrita. A publicação do patch é feita por um Trusted Publisher separado, sem processo Codex e sem `OPENAI_API_KEY`, que também aplica denylist fail-closed ao control plane. PRs de fork usam CODEX-01 base-trusted carregado exclusivamente da `main`, por broker determinístico/tool-less que envia apenas diff/metadados ao modelo, sem shell/tools. Cada solicitação é persistida primeiro em fila/ledger GitHub durável; um Quota Broker/drainer reconciliador consome o backlog e só chama a API após trust gate, reserva persistida e claim atômico exclusivo `RESERVED → CONSUMED`. O reviewer reconstrói o conjunto completo de mudanças por Git Trees/Blobs do base e do HEAD; qualquer impossibilidade de provar completude bloqueia o review em vez de permitir análise parcial. Wake-ups são best-effort e podem ser coalescidos sem perda de pedidos.

**Vantagens**
- eventos, concurrency, permissions e runners no mesmo sistema;
- nenhuma máquina local;
- reentrada explícita;
- separação clara de privilégios;
- excelente auditabilidade;
- standard runners em repo público reduzem pressão sobre quota privada atual.

**Desvantagens**
- exige OpenAI API key e billing separado;
- workflows ficam mais sofisticados;
- requer hardening rigoroso para forks.

**Riscos**
- custo de API;
- prompt injection;
- erro de configuração de permissions.

**Impacto operacional / migração**
- novo runtime versionado no próprio repositório;
- Mode A interativo permanece fallback.

### Opção C - Orquestrador próprio externo

**Descrição**

Servidor/worker dedicado controla fila, estado e agentes.

**Vantagens**
- controle máximo;
- sem limitações de lifecycle do Actions.

**Desvantagens**
- nova infraestrutura, custo, deploy, segurança e observabilidade;
- desproporcional à fase atual.

**Riscos**
- aumenta superfície operacional antes do produto existir.

**Impacto operacional / migração**
- exige provedor e operação contínua.

### Opção D - Manter apenas Mode A interativo

**Descrição**

Fluxo continua dependente da conversa ativa.

**Vantagens**
- zero custo de API unattended;
- simples.

**Desvantagens**
- não atende o objetivo de autonomia.

**Riscos**
- humano continua sendo scheduler/poller.

**Impacto operacional / migração**
- nenhum, mas objetivo da issue #1 permanece aberto.

## 5. Opção recomendada

- **Opção:** B — GitHub Actions + Codex
- **Justificativa:** concentra o critical path no sistema que já controla PR, HEAD, eventos, permissions e CI; oferece mecanismos nativos de concurrency e dispatch; remove a dependência de wake-up externo; mantém o computador local fora do runtime; separa Codex Remediator de CODEX-01; e impede que o processo Codex de remediação detenha credencial GitHub com escrita ao delegar a publicação a um Trusted Publisher independente.

Esta seção registra recomendação, não aceite.

## 6. Consequências

### Positivas
- continuidade unattended determinística;
- runtime 100% cloud;
- menos componentes no critical path;
- concorrência serializada por PR;
- audit trail nativo;
- secrets governáveis;
- reviewer separado do executor;
- caminho claro até `READY_FOR_HUMAN_MERGE`.

### Negativas / trade-offs aceitos
- API OpenAI passa a ter custo separado;
- configuração de workflows/permissions torna-se componente crítico;
- automação privilegiada deve ser bloqueada para forks;
- Action/CLI do Codex vira dependência operacional.

### Novas obrigações
- manter projeto OpenAI dedicado ou segregado para automação;
- configurar hard budget/alerts antes do canary;
- pin de Actions por SHA;
- revisar segurança de cada workflow privilegiado;
- manter geração de patch e publicação Git em jobs distintos, sem compartilhamento de credenciais privilegiadas;
- manter denylist versionada e fail-closed para impedir que remediação automática altere o próprio control plane;
- prover CODEX-01 base-trusted para forks por broker tool-less, sem checkout/execução de código externo e sem ferramentas agentivas;
- aplicar trust gate, idempotência por HEAD e quotas por PR/autor antes de chamadas pagas originadas por fork;
- persistir cada solicitação de review de fork em fila GitHub durável antes de qualquer wake-up;
- drenar/reconciliar backlog em seção crítica global, deduplicando pedidos e persistindo reserva antes da API, sem tratar `concurrency` como fila de solicitações;
- manter reconciler periódico para garantir progresso quando wake-ups forem coalescidos ou perdidos;
- realizar claim atômico `RESERVED → CONSUMED`, vinculado a `consumer_run_id`, antes da API e rejeitar consumidores concorrentes;
- provar completude do conteúdo revisado por manifests de Git Trees/Blobs do base e HEAD, sem depender do endpoint limitado de arquivos do PR;
- bloquear review parcial quando houver truncamento, objeto ausente, binário não revisável ou payload integral acima do limite;
- tratar consumo ambíguo por crash como consumo conservador, sem retry pago automático do mesmo SHA;
- instalar dispatcher, Trusted Publisher, fila/ledger, Quota Broker/drainer, reconciler e entrypoint seguro de review de fork na `main` em bootstrap anterior ao canary do runtime;
- testar concurrency, dispatch e reentrada;
- documentar mudanças de modelo/custo.

## 7. Impacto em segurança e multi-tenancy

Multi-tenancy de produto não muda.

Segurança operacional:

- `OPENAI_API_KEY` em GitHub Actions Secrets;
- nenhum secret em forks;
- jobs de remediação de IA com `OPENAI_API_KEY` exigem PR same-repo e guards de provenance;
- CODEX-01 same-repo sem permissão de escrita;
- CODEX-01 de fork pode usar `OPENAI_API_KEY` somente em broker base-trusted carregado da `main`, sem checkout do fork, sem execução de qualquer arquivo do PR, sem `contents: write` e sem expor shell/filesystem/tools ao modelo; o código confiável que contém a chave não recebe comandos derivados do diff e executa sem sudo/elevação;
- Codex Remediator sem token GitHub com `contents: write`; ele produz somente patch/artefato estruturado;
- Trusted Publisher separado, sem `OPENAI_API_KEY` e sem execução de Codex, é o único componente de remediação autorizado a `contents: write`;
- antes do push, o Trusted Publisher valida same-repo confiável, HEAD esperado, ref de destino, escopo do patch, invariantes do contrato e denylist do control plane;
- a denylist mínima cobre `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` e `docs/PROJECT_STATUS.md`; qualquer match rejeita o patch inteiro e exige decisão humana;
- o runtime nunca pode autoalterar Publisher, dispatcher, workflows, prompts, schemas, state machine ou contratos que governam seus próprios privilégios;
- para forks, o diff é obtido via API e vinculado ao `head.sha`; workflow, prompt, schema e broker vêm exclusivamente da branch padrão;
- conteúdo do fork trafega como JSON/stdin/HTTP e nunca é interpolado em shell; prompt injection não ganha capacidade de ler env, `/proc`, filesystem ou subprocessos;
- chamadas pagas para forks exigem trust gate (`OWNER`/`MEMBER`/`COLLABORATOR` ou aprovação explícita de maintainer), uma única chamada por `head.sha`, máximo de 3 por PR/24h e 5 por autor externo/24h;
- antes de qualquer wake-up, o pedido é persistido como `PENDING` com `request_id` determinístico em fila GitHub dedicada; wake-ups não são fonte de verdade;
- um Quota Broker/drainer global da `main` reconcilia o journal e materializa a autorização como `RESERVED` antes da API; coalescência de workflows não apaga pedidos e um reconciler periódico garante eventual progresso;
- o job OpenAI de fork rejeita execução sem reserva persistida para o mesmo autor/PR/HEAD/request; reservas ambíguas após crash contam na quota e não permitem nova cobrança automática do mesmo SHA;
- `main` fora da autoridade unattended;
- conteúdo do PR é untrusted input;
- não usar `pull_request_target` para executar código não confiável com secrets;
- output de IA validado por schema/guard antes de mutação.

## 8. Impacto em dados e API

Nenhum impacto em dados/API do produto.

Nova integração operacional paga com OpenAI API. O estado do runtime permanece no GitHub.

## 9. Impacto operacional e observabilidade

Fontes de evidência:

- workflow runs;
- job conclusions;
- PR/HEAD;
- `ORCHESTRATOR_STATE_V2`;
- output estruturado Codex;
- commits de remediação;
- root cause/attempts;
- checkpoints;
- billing/usage do projeto OpenAI.

Falha de GitHub ou OpenAI nunca é convertida em sucesso presumido.

## 10. Migração e rollout

1. aprovar explicitamente a SDD-0001 v0.8 após parecer técnico favorável para essa mesma versão;
2. aceitar explicitamente o ADR-0012 rev.7 após parecer técnico favorável para essa mesma revisão;
3. implementar e revisar um **PR de bootstrap** contendo o dispatcher confiável, o Trusted Publisher mínimo com denylist fail-closed, o broker base-trusted/tool-less do CODEX-01 para forks, a fila/ledger GitHub dedicada, o Quota Broker/drainer e o reconciler periódico; cada pedido persiste `PENDING` antes do wake-up e cada consumo persiste `RESERVED` antes da API; o Publisher não executa Codex nem usa `OPENAI_API_KEY`;
4. após CI/revisão, realizar merge humano do bootstrap na `main`, tornando os entrypoints confiáveis de dispatch e review de fork existentes na branch padrão;
5. configurar projeto/API OpenAI, hard budget/alerts e adicionar `OPENAI_API_KEY` como secret;
6. implementar reducer V2, jobs de geração Codex sem escrita e CODEX-01 same-repo no **PR do runtime**, mantendo publicação privilegiada e CODEX-01 de fork nos componentes base-trusted já bootstrapados;
7. executar unit/integration/security tests;
8. executar canary controlado pré-merge acionando o dispatcher já presente na `main` contra PR/HEAD same-repo elegível;
9. no canary same-repo, cada remediação corrigível deve seguir `Codex sem escrita → patch estruturado → validação de denylist → Trusted Publisher → novo HEAD → dispatch explícito`; um canary separado de fork deve provar `persistir PENDING → wake-up best-effort → drainer/reconciler → reserva durável → fork HEAD → diff/API → broker tool-less → CODEX-01 → evidência vinculada ao SHA`, incluindo pelo menos 6 PRs simultâneos, coalescência de wake-ups, reconciliação do backlog, crash após reserva, exfiltração negativa e bloqueio antes da API;
10. obter autorização humana e fazer merge do PR do runtime;
11. executar canary pós-merge do ciclo completo;
12. somente então `DONE_ALLOWED`.

## 11. Rollback / reversibilidade

- **Reversível:** Sim
- **Estratégia:** desabilitar workflow unattended, remover/rotacionar secret e usar Mode A interativo.
- **Custo ou risco de reversão:** baixo; não há dados de produto nem migration.

## 12. Relação com decisões existentes

- **ADR-0010 — CI/CD e merge:** permanece `Accepted`; este ADR estende sua governança para o runtime unattended.
- **ADR-0011 — experimento histórico privado:** o ID foi consumido por uma arquitetura Work-centric descartada e intencionalmente não importada ao Git público. O ID não será reutilizado. O catálogo público registra essa lacuna histórica. Quando ADR-0012 for `Accepted`, sua decisão substitui a direção experimental anterior.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Não aplicável | sem feature/backend |
| Frontend | Não aplicável | sem feature/frontend |
| Security & Tenant Isolation | Favorável com controles | denylist do control plane, fork tool-less/base-trusted, isolamento de secrets, trust/quota gate e prompt injection devem seguir SDD |
| Platform & Observability | Favorável | budget, run IDs, fail-closed e dispatch explícito |
| QA & Quality | Favorável | E2E de concorrência, remediation loop e READY obrigatório |

## 14. Riscos não resolvidos

Nenhum risco crítico não tratado.

Antes do canary ainda é obrigatório definir modelo e hard budget de API. Essa escolha não pode enfraquecer os limites de tentativas nem os controles de segurança.

## 15. Histórico de revisão

| Data | Responsável | Ação | Resultado |
| --- | --- | --- | --- |
| 2026-10-06 | Product & SDD | Proposta inicial | Proposed |
| 2026-10-06 | Orchestrator / Tech Lead | Revisão técnica da rev.1 | Retornar para ajustes após achados P1 de privilégio e bootstrap |
| 2026-10-06 | Product & SDD | Ajustes de segurança e rollout | Revisão decisória 2 proposta |
| 2026-10-06 | Orchestrator / Tech Lead | Revisão técnica da rev.2 | Retornar para ajustes após achados P1 de control plane e forks |
| 2026-10-06 | Product & SDD | Hardening de control plane e caminho seguro para forks | Revisão decisória 3 proposta |
| 2026-10-06 | Orchestrator / Tech Lead | Revisão técnica da rev.3 | Retornar para ajustes após achados P1/P2 de versionamento e critérios same-repo/fork |
| 2026-10-06 | Product & SDD | Alinhamento do rollout e dos critérios de remediação | Revisão decisória 4 proposta |
| 2026-10-06 | Orchestrator / Tech Lead | Revisão técnica da rev.4 | Retornar para ajustes após achados P1 de isolamento de chave e abuso de custo em forks |
| 2026-10-06 | Product & SDD | Reviewer de fork tool-less + trust gate e quotas | Revisão decisória 5 proposta |
| 2026-10-06 | Orchestrator / Tech Lead | Revisão técnica da rev.5 | Retornar para ajustes após P1 de corrida de quota entre PRs |
| 2026-10-07 | Product & SDD | Quota Broker com reserva atômica cross-PR e ledger durável | Revisão decisória 6 proposta |
| 2026-10-07 | Orchestrator / Tech Lead | Revisão técnica da rev.6 | Retornar para ajustes após P2 sobre perda de execuções pendentes em `concurrency` |
| 2026-10-07 | Product & SDD | Fila durável + drainer/reconciler idempotente | Revisão decisória 7 proposta |
| 2026-10-07 | Ramon Rodriguez | Aceite humano da rev.7 | Accepted no comentário #6043168597 |
| 2026-10-07 | Orchestrator / Tech Lead | Review pós-formalização da rev.7 | Retornar para ajustes após P1 de completude do payload e consumo atômico da reserva |
| 2026-10-07 | Product & SDD | Completude por Git Trees/Blobs + claim exclusivo de consumo | Revisão decisória 8 proposta |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Nova revisão pendente após P1 de completude e consumo exclusivo
- **Revisão decisória revisada:** Não aplicável à rev.8 até conclusão do novo ciclo
- **Revisor:** Orchestrator / Tech Lead
- **Data:** 2026-10-07
- **Evidência anterior:** rev.7 foi aceita humanamente, mas o review do HEAD de formalização encontrou dois P1 materiais
- **Pendências bloqueantes:** validar payload integral e consumo exclusivo antes da chamada paga
- **Pendências não bloqueantes:** definir modelo e hard budget antes do canary

## 17. Aceite humano

- **Aceito:** Não para a revisão atual
- **Responsável humano:** Ramon Rodriguez
- **Data:** Não aplicável à rev.8
- **Revisão decisória aceita:** Não aplicável à rev.8
- **Registro do aceite atual:** Pendente
- **Aceite histórico preservado:** rev.7, PR #2, comentário #6043168597 (`HUMAN_APPROVAL`); invalidado para rev.8 por mudança material
