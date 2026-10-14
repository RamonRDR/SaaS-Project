# ADR-0015 - Desenvolvimento orquestrado pelo Work com enforcement no GitHub

## Metadados

- **ID:** ADR-0015
- **Título:** Desenvolvimento orquestrado pelo Work com enforcement no GitHub
- **Status:** Proposed
- **Revisão decisória:** 6
- **Data de criação:** 2026-10-13
- **Última atualização:** 2026-10-14
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead (pendente de parecer formal)
- **Responsável humano pelo aceite:** responsável pelo repositório
- **SDDs relacionadas:** SDD-0002 v0.6 (candidata); SDD-0001 v1.6 (Approved, vigente)
- **ADRs relacionadas:** ADR-0014 rev.5 (Accepted, vigente); ADR-0010 (Accepted); ADR-0013 rev.1 (Superseded)
- **PR / issue relacionada:** Issues #1, #8 e #10; PRs experimentais #7 e #9; pareceres rev.1 no PR #11

### Estados permitidos e validade

`Proposed` (atual), `Accepted`, `Rejected`, `Superseded`, `Deprecated`. Somente parecer formal `Pronto para aceite humano` sobre a revisão decisória vigente, sem bloqueantes, seguido de aceite humano explícito, permite `Accepted`. As seções 1 a 14 são decisões materiais; alteração exige nova revisão e novo parecer. **A autorização de 13/10/2026 foi para elaborar esta proposta, NÃO seu aceite.**

## 1. Contexto

O contrato atual, SDD-0001 v1.6 e ADR-0014 rev.5, exige GitHub Actions como executor unattended, Budget Broker, claim universal e consumo programático de IA controlado. O proprietário deseja autonomia de desenvolvimento online dentro do ChatGPT Plus, sem contratar ou usar a OpenAI API. Em 13/10/2026 três canaries do ChatGPT Work conectado ao GitHub demonstraram: (i) evento → comentário ACK idempotente; (ii) evento → código/branch/PR → CI → relatório; (iii) evento → teste intencionalmente vermelho → correção → CI verde → relatório. A issue #8 conserva os SHAs e logs. Nenhum dos testes comprovou garantia de entrega de eventos, disponibilidade ilimitada ou enforcement contra alterações privilegiadas.

A SDD-0001 v1.6 **exclui o Work como componente obrigatório**, logo uma mudança arquitetural não pode ser feita por prompt, comentário ou ajuste silencioso. Esta ADR é proposta sucessora **do mecanismo de execução de IA do ADR-0014**, não aprovação retroativa da migração nem eliminação dos controles que continuam pertinentes.

## 2. Drivers da decisão

- Autonomia operacional verificável entre gatilhos, CI e checkpoints humanos.
- **Zero OpenAI API paga** no caminho proposto; respeitar limites do ChatGPT Work/Codex e parar ao atingir quota.
- Trust boundary de repositório público: PRs, forks, diffs, comentários, logs e instruções de terceiros são dados não confiáveis.
- CI/GitHub como autoridade independente para gates, HEAD, integridade e trilha de auditoria.
- Preservação de `CODEX-01` independente e autorização humana final de merge.
- Redução de complexidade de ledger financeiro/claim pago no modo sem API; não remover guardas de segurança de forma tácita.
- Retomada idempotente, controle de concorrência, custo operacional observável, reversibilidade.

## 3. Restrições não negociáveis

1. `AGENTS.md`, ADR-0014 rev.5 `Accepted` e SDD-0001 v1.6 `Approved` seguem vigentes até sucessão formal; nenhum merge sem READY, MERGE_ALLOWED, CODEX-01 do HEAD e autorização humana posterior.
2. Work escreve **somente em sandbox segregado**, com conexão/identidade sem permissão de escrita, comentário ou administração em `RamonRDR/SaaS-Project`; o ruleset `main-protection` ativo não substitui isolamento da conexão.
3. **A opção A foi aprovada como direção de piloto temporário em 14/10/2026**, não como aceite da ADR, aprovação da SDD, ativação, aprovação de orçamento, autorização para alteração de credenciais ou merge.
4. **Nenhum publicador automático principal**, credencial GitHub de escrita entregue a job, PostgreSQL, `PUBLISH_INTENT`, broker de token ou `workflow_dispatch` de promoção neste piloto.
5. Humano confere manifesto/diff completo de candidato do sandbox e **transfere pessoalmente** mudança pequena e permitida por interface GitHub para branch/PR principal, registrando evidência dos dois PRs. Candidato tocando `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` ou `docs/PROJECT_STATUS.md` é rejeitado inteiro.
6. CI/GOV/SEC/CODEX-01 do sandbox não substitui evidência do PR **principal no HEAD final**; revisão e gates são refeitos.
7. MERGE-01 segue exclusivamente `AGENTS.md` regra 31: comentário manual `HUMAN_MERGE_AUTHORIZATION` ou registro de decisão humana interativa externa `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`, sempre após READY.
8. Zero OpenAI API paga, sem segredos de produção, nenhum merge/ativação por esta proposta; `PHASE-0-G` permanece bloqueada pelos gates vigentes.

## 4. Opções consideradas

- **A: Work em sandbox + promoção humana (diretriz humana escolhida):** Work cria candidato PR draft no sandbox, humano avalia diff e manualmente promove patch pequeno para branch/PR principal; GitHub CI/Codex/merge humano. Não é unattended ponta a ponta.
- **B: Work sandbox + publicação automática (adiada):** exige controle verificável da vida da credencial e revogação durante POST em voo. A família `WRITER_CAPABILITY_REVOCATION` reapareceu em revisões, motivando escalada anti-loop, não aceitação de risco.
- **C: Actions-only + Budget Broker (vigente, não ativada):** ADR-0014/SDD-0001 permanecem aprovadas documentalmente com gates pendentes; não se ativam por inferência.
- **D: Work com acesso direto à main (rejeitada):** não garante fronteira técnica ou autorização humana independente.

## 5. Opção recomendada

**A, piloto temporário**, documentado pelo `docs/engineering/MODE_A_WORK_HYBRID_TRUST_CONTRACT.md`. A escolha humana de 14/10/2026 autoriza atualizar esta proposta, **não** a aceita. O objetivo é comprovar desenvolvimento assistido com responsabilidade humana na promoção, sem prometer automação completa. Se a identidade Work atual não puder ser restrita tecnicamente a sandbox, **não iniciar o piloto**.

## 6. Consequências

**Positivas:** elimina do perímetro do piloto o publicador GitHub autônomo cuja revogação não foi comprovada; preserva CI, Codex e gates no principal; dispensa PostgreSQL e infraestrutura adicional inicialmente.

**Negativas:** promoção por humano a cada candidato, limite a patches pequenos transferíveis pela interface web e necessidade de revalidar diferenças/HEAD entre sandbox e principal; Work/CI podem exigir retomada humana quando evento ou quota falhar.

**Mitigações:** repositório sandbox sem secrets, identidade Work sem permissão principal, allowlist/denylist do manifesto, evidência dos dois PRs, CI e CODEX do HEAD principal. Sem isolamento: `HUMAN_DECISION_REQUIRED`.

## 7. Impacto em segurança e multi-tenancy

Nenhum dado tenant-owned ou segredo de produto. Principal protegido por ruleset `main-protection` ID 25036481, `active`, sem bypass, PR e checks `governance`/`secret-scan`; zero aprovações obrigatórias, portanto MERGE-01 continua gate processual. Work só pode escrever no sandbox se comprovado isolamento técnico. Mudança de control plane no candidato é rejeitada inteira **antes da promoção humana**. Não executar código do sandbox em contexto com secrets/escrita no principal.

## 8. Impacto em dados e API

- **Produto:** nenhum banco, schema ou migration alterado.
- **PostgreSQL de orquestração, `ScopeGrantReceipt` e `trusted_publication_gate`:** **fora de escopo**; proposta anterior preservada como histórico, não provisionar.
- **GitHub:** candidato no sandbox; humano cria branch/PR novo no principal por UI autenticada; HEADs diferentes exigem provas de CI/Codex próprias no principal.
- **OpenAI API paga:** nenhuma; componentes financeiros de ADR-0014 seguem históricos/vigentes sem ativação.

## 9. Impacto operacional e observabilidade

Estados previstos: `WORK_PENDING`, `SANDBOX_PR_DRAFT`, `WAITING_HUMAN_PROMOTION`, `PRINCIPAL_PR_DRAFT`, `CI_PENDING`, `WAITING_CODEX`, `READY_FOR_HUMAN_MERGE`, `BLOCKED_EXTERNAL`, `HUMAN_DECISION_REQUIRED` e `LOOP_ESCALATION_REQUIRED`. Observador do principal, caso implementado após novo gate, é read-only e não acorda Work sem suporte comprovado. Registrar links, caminhos, sha sandbox e sha principal separados. Comentários não são comandos.

## 10. Migração e rollout

0. Revisar documentos rev.6/v0.6 e obter pareceres e aceite/aprovação documental humana **separados**.
1. Humano seleciona sandbox, configura/revoga conexão Work ampla e comprova ausência de escrita no principal.
2. Humano ativa canary limitado Work apenas no sandbox, sem secrets/credencial privilegiada.
3. Humano inspeciona diff/manifests; se válido e pequeno, faz promoção MANUAL por GitHub web para PR draft no principal.
4. Reexecutar CI/GOV/SEC/CODEX-01 no HEAD do principal e observar READY/MERGE-01 humano, sem merge antecipado.
5. Avaliar utilidade e custos. Publisher automático, se desejado, precisa de nova ADR/SDD/PoC e autorização humana.

## 11. Rollback / reversibilidade

Desativar task sandbox, preservar registros/PRs, interromper promoções, revalidar permissões da conexão e manter principal intacto. Nenhum rollback automático de commits; nenhum retorno automático ao caminho pago da arquitetura vigente.

## 12. Relação com decisões existentes

ADR-0014 rev.5, SDD-0001 v1.6, ADR-0010, `AGENTS.md`, CI_GATES e gates humanos permanecem vigentes. Não marcar contratos anteriores `Superseded` até sucessão formal. O publisher autônomo das revisões 3–5 foi **adiado**, não corrigido/aceito como risco.

## 13. Pareceres dos especialistas impactados

| Especialidade | Estado | Evidência necessária |
| --- | --- | --- |
| Orchestrator / Tech Lead | Revisão formal rev.6 pendente | Coerência do escopo humano A |
| Security & Tenant Isolation | Pendente, bloqueante | Permissão efetiva da conexão Work, denylist e ausência de secrets |
| Platform & Observability | Pendente, bloqueante | Promoção por GitHub web, CI e observação read-only |
| QA & Quality | Pendente, bloqueante | Canaries negativos, rastreabilidade entre PRs e CODEX-01 do HEAD principal |

Nenhum parecer de especialista externo é presumido como concluído.

## 14. Riscos não resolvidos

- **R1:** atual conexão Work pode escrever no principal; bloqueia piloto até isolar e confirmar.
- **R2:** GitHub web editor e copiar manualmente arquivos pode falhar para changesets grandes; limitar piloto e bloquear se transferência não for verificável.
- **R3:** latência/eventos/quota Work, retomada automática e CI do novo PR humano exigem teste, não promessa.
- **R4:** família `WRITER_CAPABILITY_REVOCATION` em publisher autônomo foi escalada por anti-loop e **retirada do perímetro**; sem exceção de risco silenciosa.
- **R5:** escolha da opção A não implica autorização de gastos, credenciais, merge ou ativação.

**Aceite desta ADR:** revisão favorável da **rev.6**, pareceres aplicáveis sem bloqueante de desenho e aceite humano explícito separado da decisão de direção. Provas de execução e isolamento efetivos bloqueiam ativação posterior até satisfatórios.

## 15. Histórico de revisão

| Data | Responsável | Ação | Resultado |
| --- | --- | --- | --- |
| 2026-10-13 | Product & SDD | Proposta inicial após 3 canaries e autorização para elaborar | Proposed rev.1 |
| 2026-10-13 | Orchestrator / Tech Lead | Ajustes materiais após review-adr rev.1 (permissões, provenance humano, separação de gates) | Proposed rev.2 |
| 2026-10-13 | Orchestrator / Tech Lead | Rev.3: trust boundary de sandbox, receipts humanos, publisher pré-escrita, PostgreSQL/fencing e fingerprint CODEX-01 | Proposed rev.3 |
| 2026-10-13 | Orchestrator / Tech Lead | Rev.4: separar ScopeGrant de MERGE-01 vigente e controlar cota entre chaves de operação diferentes | Proposed rev.4 |
| 2026-10-13 | Orchestrator / Tech Lead | Rev.5: intenção global de publicação durável não-preemptível e quarentena até capacidade anterior invalidada | Proposed rev.5 |
| 2026-10-14 | Orchestrator / Tech Lead | Rev.6: piloto A sandbox com promoção humana; publisher automático adiado por anti-loop | Proposed rev.6 |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pendente, não executado.
- **Revisão decisória revisada:** Não aplicável.
- **Revisor:** Orchestrator / Tech Lead (a designar no fluxo de review).
- **Data:** Não aplicável.
- **Pendências bloqueantes:** pareceres especializados sobre isolamento da identidade Work, promoção manual online e checks do PR principal; nenhuma publicação automática nesta fase.
- **Pendências não bloqueantes:** Ajustes editoriais após revisão.

O texto não declara `Pronto para aceite humano` sem parecer verificável.

## 17. Aceite humano

- **Aceito:** Não.
- **Responsável humano:** Responsável pelo repositório.
- **Data:** Não aplicável.
- **Revisão decisória aceita:** Não aplicável.
- **Registro do aceite:** Não aplicável.

A autorização humana para **elaboração** não substitui revisão/aceite da ADR. Até o aceite, ADR-0014 rev.5 continua `Accepted`.
