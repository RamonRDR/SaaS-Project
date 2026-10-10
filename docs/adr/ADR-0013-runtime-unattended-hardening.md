# ADR-0013 - Hardening do runtime unattended: Budget Broker e forks

## Metadados

- **ID:** ADR-0013
- **Título:** Hardening do runtime unattended: Budget Broker e forks
- **Status:** Superseded
- **Revisão decisória:** 1
- **Data de criação:** 2026-10-08
- **Última atualização:** 2026-10-09 (somente metadata/lifecycle, sem alteração das seções decisórias)
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Ramon Rodriguez
- **SDDs relacionadas:** SDD-0001 v1.1
- **ADRs relacionados:** ADR-0010; ADR-0012 rev.7 (`Superseded` após aceite da ADR-0013); ADR-0011 histórico não importado
- **PR / issue relacionada:** Issue #1

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável sem pendência bloqueante e aceite humano;
- `Rejected`: proposta rejeitada;
- `Superseded`: substituída por ADR posterior;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`. A ADR-0012 rev.7 permaneceu `Accepted` e vigente durante a fase `Proposed` da ADR-0013; seu estado passou a `Superseded` somente após o aceite humano desta sucessora, sem reescrever seu conteúdo decisório.

### Revisão decisória e validade do parecer

As seções 1 a 14 compõem o conteúdo decisório. Qualquer mudança material antes do aceite incrementa a revisão decisória e invalida o parecer atual.

## 1. Contexto

O projeto exige um runtime unattended que continue o Mode A sem máquina local e sem mensagens humanas operacionais. A arquitetura cloud-native foi aceita na **ADR-0012 rev.7** com evidência humana no PR #2 (comentário `HUMAN_APPROVAL` #6043168597). Ajustes materiais posteriores não podem sobrescrever aquela decisão histórica; esta **ADR-0013 rev.1**, após parecer técnico favorável e aceite humano próprios, formaliza o hardening adicional e sucede a ADR-0012 rev.7.

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

GitHub Actions executa a state machine, CI, guards, dispatch e transições. Codex é chamado em jobs específicos para geração de remediação e review, sempre sem credencial GitHub com escrita. A publicação do patch é feita por um Trusted Publisher separado, sem processo Codex e sem `OPENAI_API_KEY`, que também aplica denylist fail-closed ao control plane. PRs de fork usam CODEX-01 base-trusted carregado exclusivamente da `main`, por broker determinístico/tool-less que envia apenas diff/metadados ao modelo, sem shell/tools. Cada solicitação é persistida primeiro em fila/ledger GitHub durável; um Quota Broker/drainer reconciliador consome o backlog e só chama a API após trust gate, reserva persistida e claim atômico exclusivo `RESERVED → CONSUMED`. O reviewer resolve o merge-base real entre `base_tip_sha` e `head_sha`, e reconstrói o changeset de três pontos a partir das árvores desse ancestral e do HEAD; a ponta base é só metadado. Completude não comprovada bloqueia o review. TODAS as chamadas pagas (fork, same-repo e remediação) exigem ainda autorização de um Budget Broker global com reserva monetária pessimista e atômica, sem rota de API direta nos jobs consumidores. Wake-ups são best-effort e podem ser coalescidos sem perda de pedidos.

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
- definir orçamento monetário mensal global, caps de tokens e tabela de preços antes de qualquer chamada; alertas/limites da plataforma são apenas defesa adicional;
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
- provar completude do conteúdo revisado por manifests de Git Trees/Blobs do **merge-base** e HEAD, sem usar a ponta da base diretamente nem depender do endpoint limitado de arquivos do PR;
- bloquear review parcial quando houver truncamento, objeto ausente, binário não revisável ou payload integral acima do limite;
- tratar consumo ambíguo por crash como comprometimento conservador de quota e custo máximo, sem retry pago automático do mesmo SHA;
- centralizar credenciais pagas no Budget Broker da `main` e bloquear acesso direto à API por Codex Remediator, CODEX-01 same-repo e fork;
- reservar custo monetário máximo antes de qualquer chamada de IA usando ledger GitHub durável e compare-and-set real, abrangendo todos os PRs e papéis;
- negar preço desconhecido, entrada ou saída ilimitada, modelo/fallback fora de catálogo e indisponibilidade de ledger;
- instalar dispatcher, Trusted Publisher, fila/ledger, Quota Broker/drainer, reconciler e entrypoint seguro de review de fork na `main` em bootstrap anterior ao canary do runtime;
- testar concurrency, dispatch e reentrada;
- documentar mudanças de modelo/custo.

## 7. Impacto em segurança e multi-tenancy

Multi-tenancy de produto não muda.

Segurança operacional:

- `OPENAI_API_KEY` em GitHub Actions Secrets, injetado exclusivamente no job isolado do Budget Broker (nunca em Codex Remediator, CODEX-01 same-repo/fork ou Trusted Publisher);
- nenhum secret em forks;
- jobs de remediação de IA e CODEX-01, inclusive same-repo, não recebem `OPENAI_API_KEY`; operam apenas por solicitações estruturadas ao Budget Broker. A elegibilidade same-repo e os guards de provenance permanecem obrigatórios para remediação com escrita;
- CODEX-01 same-repo sem permissão de escrita;
- CODEX-01 de fork usa broker de review base-trusted carregado da `main`, sem receber `OPENAI_API_KEY` ou token delegado. O broker obtém apenas dados do fork, sem checkout ou execução de arquivos externos, sem `contents: write` e sem shell/filesystem/tools expostos ao modelo. A chamada paga é feita exclusivamente pelo Budget Broker isolado, que recebe a chave, rejeita comandos derivados do diff e opera sem sudo/elevação;
- Codex Remediator sem token GitHub com `contents: write`; ele produz somente patch/artefato estruturado;
- Trusted Publisher separado, sem `OPENAI_API_KEY` e sem execução de Codex, é o único componente de remediação autorizado a `contents: write`;
- antes do push, o Trusted Publisher valida same-repo confiável, HEAD esperado, ref de destino, escopo do patch, invariantes do contrato e denylist do control plane;
- a denylist mínima cobre `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` e `docs/PROJECT_STATUS.md`; qualquer match rejeita o patch inteiro e exige decisão humana;
- o runtime nunca pode autoalterar Publisher, dispatcher, workflows, prompts, schemas, state machine ou contratos que governam seus próprios privilégios;
- para forks, o changeset é obtido por API Git a partir de `merge_base(base_tip_sha,head_sha)` até `head_sha`; a ponta da base não entra no cálculo de alterações; workflow, prompt, schema e broker vêm exclusivamente da branch padrão;
- conteúdo do fork trafega como JSON/stdin/HTTP e nunca é interpolado em shell; prompt injection não ganha capacidade de ler env, `/proc`, filesystem ou subprocessos;
- chamadas pagas para forks exigem trust gate (`OWNER`/`MEMBER`/`COLLABORATOR` ou aprovação explícita de maintainer), uma única chamada por `head.sha`, máximo de 3 por PR/24h e 5 por autor externo/24h;
- antes de qualquer wake-up, o pedido é persistido como `PENDING` com `request_id` determinístico em fila GitHub dedicada; wake-ups não são fonte de verdade;
- um Quota Broker/drainer global da `main` reconcilia o journal e materializa a autorização como `RESERVED` antes da API; coalescência de workflows não apaga pedidos e um reconciler periódico garante eventual progresso;
- o job de review de fork só executa para o único `consumer_run_id` que venceu a transição atômica `RESERVED → CONSUMED`; consumidores subsequentes encerram antes da API e consumo ambíguo após crash não permite nova chamada automática do mesmo SHA;
- o broker enumera integralmente as árvores Git de merge-base/HEAD, busca todos os objetos alterados necessários e emite manifest/digest de completude com `base_tip_sha`, `merge_base_sha`, `head_sha`; qualquer truncamento, ausência, binário não revisável, objeto não suportado ou payload integral acima do limite resulta em `HUMAN_DECISION_REQUIRED`, sem CODEX-01 clean;
- exclusivamente o Budget Broker possui a chave do provedor, executa inferência paga e impõe orçamento mensal global em unidades monetárias inteiras, custo máximo pessimista baseado em preços versionados, tokens e número de requests/retries limitados; nenhum job consumidor pode carregar o secret, repassá-lo ou usar SDK/CLI com acesso direto ao provedor;
- cada autorização monetária é `check + reserve` por CAS do ledger global; o total `committed + outstanding_max + new_max` não ultrapassa o limite. Jobs de Codex não possuem credencial nem endpoint que contorne o broker;
- o claim final e o dispatch HTTP da chamada paga devem validar o relógio UTC confiável e confirmar que `budget_period_utc` da reserva/claim corresponde ao **mês UTC vigente**. Se houver virada de mês, a autorização anterior não é reutilizada, a chamada é cancelada antes do envio e nova reserva/claim deve ser feita no bucket atual com CAS; a reserva antiga segue comprometida até conciliação inequívoca;
- fronteiras de mês possuem margem de segurança fail-closed para evitar envio com autorização de período anterior; erro de relógio ou período incerto bloqueia a chamada;
- custo de resposta inconclusiva permanece reservado pelo máximo. Preço desconhecido, ledger indisponível ou orçamento não definido bloqueia execução. Alertas e hard limits da plataforma podem auxiliar, mas eventual enforcement tardio não é a garantia primária;
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
- ledger de budget do broker: período UTC, teto, comprometido, reservado máximo, decisões CAS, custo conciliado;
- billing/usage do projeto OpenAI (telemetria auxiliar).

Falha de GitHub ou OpenAI nunca é convertida em sucesso presumido.

## 10. Migração e rollout

1. aprovar explicitamente a SDD-0001 v1.1 após parecer técnico favorável para essa mesma versão;
2. aceitar explicitamente o ADR-0013 rev.1 após parecer técnico favorável para essa mesma revisão;
3. implementar e revisar **PR de bootstrap** com dispatcher, Trusted Publisher, fila/ledger, Quota Broker/drainer, Budget Broker global exclusivo e reconciler; somente um claim atômico libera a chamada após reservar quota e custo máximo global por CAS **e revalidar mês UTC vigente no claim e no dispatch HTTP**; o review de fork usa merge-base/HEAD para provar completude;
4. após CI/revisão, realizar merge humano do bootstrap na `main`, tornando os entrypoints confiáveis de dispatch e review de fork existentes na branch padrão;
5. configurar limite monetário global positivo aprovado humanamente, catálogo/versionamento de preços e caps máximos de tokens/retries; atribuir chave OpenAI somente ao Budget Broker e configurar alertas/limites na plataforma como proteção adicional;
6. implementar reducer V2, jobs de geração Codex sem escrita e CODEX-01 same-repo no **PR do runtime**, mantendo publicação privilegiada e CODEX-01 de fork nos componentes base-trusted já bootstrapados;
7. executar unit/integration/security tests;
8. executar canary controlado pré-merge acionando o dispatcher já presente na `main` contra PR/HEAD same-repo elegível;
9. canaries same-repo e fork devem provar `budget CAS global → quota/claim exclusivo → revalidar período UTC no claim e no dispatch HTTP → API`, sem bypass. Simular virada UTC entre `RESERVED` e claim, e entre claim e dispatch, garantindo nova reserva no mês correto ou bloqueio antes do envio, sem liberar reserva ambígua do mês anterior. Para fork, `merge-base(base_tip,head) → diff três pontos → payload integral → CODEX-01`. Incluir base avançada, merge-base indisponível, truncamento, 6 PRs concorrentes, coalescência, crash e exfiltração negativa;
10. obter autorização humana e fazer merge do PR do runtime;
11. executar canary pós-merge do ciclo completo;
12. somente então `DONE_ALLOWED`.

## 11. Rollback / reversibilidade

- **Reversível:** Sim
- **Estratégia:** desabilitar workflow unattended, remover/rotacionar secret e usar Mode A interativo.
- **Custo ou risco de reversão:** baixo; não há dados de produto nem migration.

## 12. Relação com decisões existentes

- **ADR-0010 — CI/CD e merge:** permanece `Accepted`; este ADR estende sua governança para o runtime unattended.
- **ADR-0011 — experimento histórico privado:** ID consumido por arquitetura descartada, não importada ao Git público e não reutilizável.
- **ADR-0012 rev.7 — decisão histórica:** foi aceita em 2026-10-07 e seu conteúdo decisório permanece preservado. Após o aceite humano da ADR-0013 rev.1 em 2026-10-08, seu status foi atualizado para `Superseded` com referência explícita à sucessora, sem reescrita da decisão original.

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

Antes de qualquer canary pago é obrigatório o Budget Broker com orçamento positivo aprovado, custos máximos verificáveis, tabela de preços versionada, limites efetivos de entrada/saída/retries e ledger atômico global. Nenhum orçamento apenas informativo pode ser tratado como bloqueante.

## 15. Histórico de revisão

| Data | Responsável | Ação | Resultado |
| --- | --- | --- | --- |
| 2026-10-08 | Product & SDD | Proposta sucessora à ADR-0012 rev.7 para hardening de fork, merge-base, credenciais exclusivas e orçamento global com revalidação do período UTC no claim/dispatch | Revisão decisória 1 `Proposed` |
| 2026-10-08 | Ramon Rodriguez | Aceite humano expresso em ChatGPT, registrado no PR #2 comentário #6070726649 | Revisão decisória 1 `Accepted` |
| 2026-10-09 | Ramon Rodriguez | Sucessão após aceite humano da ADR-0014 rev.5, registrado no PR #2 comentário #6091567757; conteúdo decisório 1 a 14 preservado | rev.1 `Superseded` por ADR-0014 rev.5 |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pronto para aceite humano
- **Revisão decisória revisada:** 1
- **Revisor:** Orchestrator / Tech Lead
- **Data:** 2026-10-08
- **Evidência técnica:** CODEX-01 clean no HEAD `c949295e8fe5a81ff7ca2a1575ff11f2cbc423c6` e Governance Gates #25 `success`. ADR-0012 rev.7 mantida imutável até o aceite desta sucessora.
- **Pendências bloqueantes:** Nenhuma para aceite da decisão arquitetural/documental.
- **Pendências não bloqueantes:** definir budget humano, modelo/tabela de preços, implementar e testar o Budget Broker antes de ativar chamadas pagas

## 17. Aceite humano

- **Aceito:** Sim
- **Responsável humano:** Ramon Rodriguez
- **Data:** 2026-10-08
- **Revisão decisória aceita:** 1
- **Registro do aceite atual:** PR #2, comentário #6070726649 (`ORCHESTRATOR_RECORDED_HUMAN_APPROVAL`), decisão humana expressa em ChatGPT
- **Aceite histórico preservado:** ADR-0012 rev.7 (decisão diferente), PR #2 comentário #6043168597 (`HUMAN_APPROVAL`); não aprova ADR-0013 rev.1.
- **Estado posterior ao aceite:** `Superseded` desde 2026-10-09 por ADR-0014 rev.5, conforme aprovação humana registrada no PR #2 comentário #6091567757.
