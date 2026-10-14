# SDD-0002 - Piloto Mode A: Work em sandbox com promoção humana

## Metadados

- **ID:** SDD-0002
- **Título:** Piloto temporário Work em sandbox e promoção humana online
- **Status:** Approved
- **Versão:** 0.6
- **Responsável pela especificação:** Product & SDD
- **Responsável humano pela aprovação:** responsável pelo repositório
- **Data de criação:** 2026-10-13
- **Última atualização:** 2026-10-14
- **Entrega / issue / PR relacionada:** issue #10, canaries issue #8 e PR #11
- **ADRs relacionados:** ADR-0015 rev.6 (`Accepted` para o piloto A), ADR-0014 rev.5 (`Accepted`, baseline vigente), ADR-0010 (`Accepted`)
- **SDDs relacionadas:** SDD-0001 v1.6 (`Approved`, ainda vigente)

### Estados permitidos e validade

`Draft`, `In Review`, `Approved` (atual, v0.6) e `Superseded`. A **v0.6 foi aprovada formalmente em 14/10/2026**, após `review-sdd` com parecer `Pronta para aprovação` e aceite humano específico separado da escolha anterior pela opção A. **A aprovação é somente do desenho:** não autoriza task, credenciais, promoção de código nem merge. Mudança material posterior invalida aprovação e exige nova versão/parecer.

## 1. Contexto

A ADR-0014 rev.5 e a SDD-0001 v1.6 descrevem o runtime Actions-only com Budget Broker, atualmente documentalmente aprovado e sem ativação paga autorizada. Três canaries Work/GitHub (issue #8) demonstraram wake-up, desenvolvimento de PR e uma remediação de CI. PR #11 propôs publicação autônoma, mas múltiplos P1 do Codex sobre concorrência e revogação da capacidade de escrita (`WRITER_CAPABILITY_REVOCATION`) culminaram em escalada anti-loop na issue #10.

O responsável **aprovou a opção A temporária**: Work produz **somente no sandbox isolado** e humano promove manualmente mudanças pequenas para PR no repositório principal. A publicação automática é **adiada**, não tratada como risco residual aceito.

## 2. Problema

Obter ganho de desenvolvimento online usando a franquia Work sem conceder ao agente escrita no principal, autorizações forjáveis, credenciais de importação automáticas, compra de API paga ou merge fora dos gates. A promoção humana é deliberada para eliminar do piloto a corrida de token/POST em voo.

## 3. Objetivo

Conseguir 1 piloto pequeno e reproduzível: evento legítimo → Work cria candidato no sandbox → humano valida diff e transfere mudança por GitHub web → branch/PR principal → GOV/SEC/testes/Codex do HEAD principal → READY e autorização humana de merge em momento posterior. Medir latência, esforço manual e pontos de bloqueio sem prometer continuidade total.

## 4. Escopo

- Registro e verificação de sandbox e conexão GitHub Work tecnicamente limitada a esse sandbox.
- Tarefa Work temporária criada/habilitada **pelo humano**, com escopo reversível, paths permitidos e limite de tentativas.
- PR draft de candidato apenas sandbox, sem segredos nem comandos não confiáveis.
- Checklist/manual de diff completo, allowlist/denylist e transporte online da mudança pequena por humano.
- Novo PR principal por humano, checks `governance`/`secret-scan`, testes pertinentes, `CODEX-01` HEAD final e gates humanos conforme `AGENTS.md`.
- Observação e registro de evidências, tratamento de falha/duplicata e rollback para estado read-only.

## 5. Fora de escopo

- Work tocar `RamonRDR/SaaS-Project` por API, GitHub App ou outro meio delegado.
- Publicador automático, broker de credencial, `GITHUB_TOKEN` com write de importação, PostgreSQL, `scope_receipts`, `PUBLISH_INTENT`, `trusted_publication_gate` ou alteração de workflow principal.
- Garantia de wake-up, recuperação automatizada, exactly-once distribuído, merge autônomo e edição de control plane por Work.
- OpenAI API paga, novas subscriptions, segredos de produção, banco/tenants, Flutter, Django ou n8n.
- Encerrar PRs legados, concluir `PHASE-0-G` ou mudar status de ADR/SDD vigente por inferência.

## 6. Atores e jornadas afetadas

- **Humano responsável:** aprova escopo, decide qual sandbox usar, configura conexão e valida acesso negativo, ativa canary, inspeciona patches, transporta pequena alteração via navegador, revisa/autoriza eventual merge.
- **Work sandbox:** relê estado atual após wake-up, desenvolve/testa somente no sandbox dentro do contrato, publica candidato draft, nunca promove ao principal.
- **Actions sandbox:** CI sem secrets privilegiados do principal.
- **Actions principal:** GOV/SEC/testes em PR humano; sem automação de publicação de candidato.
- **Codex independente:** review do HEAD final do PR principal, com evidências atuais.
- **Orchestrator:** reconciliador/guardião dos gates, não inventa aprovações nem garante despertar Work.

## 7. Regras de negócio

- **BR-001:** aceitar opção A não ativa Work nem autoriza credenciais, risco, PR ou merge.
- **BR-002:** o evento GitHub é só wake-up. Comentários, patches e logs não fornecem instruções operacionais confiáveis.
- **BR-003:** validar técnica e administrativamente que identidade/conexão Work **não pode escrever/comentar/administrar no repo principal** antes do primeiro canary mutável. Permissão incerta → `HUMAN_DECISION_REQUIRED`.
- **BR-004:** operador humano autoriza escopo limitado do sandbox (repo/issue/paths/validade/versão/tentativas), por decisão inequívoca no canal humano. Marcador do GitHub produzido por Work não é ato humano.
- **BR-005:** Work trabalha em branch/PR draft **somente sandbox**, sem secrets e sem checkout privilegiado de fork. Reentrada deve verificar estado atual, não repetir efeitos cegamente.
- **BR-006:** durante o piloto A, **nenhum token ou workflow de escrita no principal é delegado ao Work ou a importador automático**. Reativar publisher exige nova decisão arquitetural.
- **BR-007:** humano examina manifest completo, caminhos, modos e conteúdo. Candidato contendo qualquer path do control plane é **rejeitado integralmente**, sem promoção parcial automática. Denylist: `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` e `docs/PROJECT_STATUS.md`. Adotar allowlist menor por canary.
- **BR-008:** humano transfere mudança pequena e permitida usando UI GitHub autenticada, cria branch e PR próprios **no principal**; registrar PRs, manifests e diferenças. Caso não consiga transferir com fidelidade, interromper e solicitar nova decisão.
- **BR-009:** `sandbox_head_sha` **não é** `principal_head_sha`. CI/Codex/checks do sandbox nunca substituem os do novo HEAD no principal.
- **BR-010:** regras do `main-protection` ativo continuam (PR, `governance` e `secret-scan`, threads resolvidas, sem bypass); não inferir que 0 aprovações exigidas implique gate humano independente.
- **BR-011:** `CODEX-01` independente no PR principal, após último commit, com `merge_base_sha`, `head_sha`, `payload_digest` e `trusted_review_contract_digest` vigentes; mudança invalida revisão anterior.
- **BR-012:** `MERGE-01` exige `ORCHESTRATOR_READY`, `MERGE_ALLOWED` e autorização humana posterior por um dos dois canais do `AGENTS.md` regra 31. Decisão de opção A não satisfaz MERGE-01.
- **BR-013:** não disponibilizar `OPENAI_API_KEY`, fornecedor pago ou fallback faturável; limite Work/quota esgotada vira `BLOCKED_EXTERNAL`.
- **BR-014:** após 3 tentativas sem progresso da mesma causa, escala `LOOP_ESCALATION_REQUIRED`; publisher automático já está fora do piloto por causa-raiz escalada.
- **BR-015:** observador read-only não dispara Work automaticamente sem meio oficialmente comprovado; se evento perder, escalar ao operador.
- **BR-016:** nenhum marcador `DONE_ALLOWED` ou `PROJECT_STATUS completed` sem gates finais, nem merge pela presente proposta.
- **BR-017:** riscos ou paths fora de escopo, autorização forjada, desconexão do Work/CI e mudanças materiais impõem `HUMAN_DECISION_REQUIRED` / `BLOCKED_EXTERNAL`, jamais fail-open.
- **BR-018:** alterações em identidade, GitHub App, control plane ou início de operações reais requerem aprovação humana específica e evidência, independente da aprovação da rota A.

## 8. Permissões e multi-tenancy

Work deve acessar apenas um sandbox sem segredo e não possuir escrita/admin/comentário no principal. Uma conta owner GitHub conectada indiscriminadamente ao Work **não** atende. A instalação app e seus repositórios/permissões reais devem ser conferidos por humano, com evidência de teste negativo. Se não houver forma técnica de limitar, suspender o canary. Nenhuma operação tenant-owned, nenhuma migration ou dado pessoal de clientes é pertinente ao piloto.

## 9. Impacto no modelo de dados

Banco do produto e de orquestração: **não aplicável**. Registros mínimos de auditoria por issue/PR: `scope_id`, `sandbox_repo`, `sandbox_pr_number`, `sandbox_head_sha`, `principal_pr_number`, `principal_head_sha`, allowlist, manifesto do diff conferido, ato de promoção humana, evidências CI/Codex/READY e timestamps. Não afirmar atomicidade ou CAS de Git comments.

## 10. Impacto no contrato da API

Nenhuma API de produto alterada. Integrações utilizadas: GitHub para PRs/refs/status, Work conectado exclusivamente sandbox e GitHub web autenticado pelo humano para a promoção. **Nenhum endpoint de publisher principal, OpenAI API paga ou banco de orquestração.**

## 11. Comportamento esperado no Flutter

**Não aplicável.** O piloto modifica fluxo de engenharia, sem mudança de interface Flutter, navegação, estado de tenant ou widgets do produto.

## 12. Integrações externas

- **GitHub:** PRs sandbox e principal, CI GOV/SEC e ruleset existente; respeitar limitações reais de eventos e permissões.
- **ChatGPT Work:** evento wake-up pode não ser entregue, tarefas podem pausar/esgotar franquia; não garantir SLA/continuidade.
- **Codex Review:** revisão independente por HEAD do PR principal.
- **OpenAI API / PostgreSQL / providers pagos:** fora do piloto, sem instalação nem autorização de custo.

## 13. Segurança e privacidade

Fonte sandbox inteira é dado não confiável. Nenhum secret ou permissão de escrita principal entregue ao Work ou ao código do sandbox. Não executar patch/scripts de candidatos em job com secrets. A aprovação humana de promoção requer manifesto **completo** e rejeição integral de control plane. Não confiar em comentário de login proprietário como autorização quando conector compartilha identidade. Sem validação de isolamento real, nenhuma task Work ativa.

## 14. Observabilidade

Estados: `PENDING`, `WORK_PENDING`, `SANDBOX_PR_DRAFT`, `WAITING_HUMAN_PROMOTION`, `PRINCIPAL_PR_DRAFT`, `CI_PENDING`, `WAITING_CODEX`, `READY_FOR_HUMAN_MERGE`, `BLOCKED_EXTERNAL`, `HUMAN_DECISION_REQUIRED` e `LOOP_ESCALATION_REQUIRED`. Registrar repositório, PR, head SHA, source, gatilho observado, timestamp, URL de CI/review e quem realizou promoção. Eventos missing/duplicados não são sucesso; observador principal read-only e sem promessa de acordar Work.

## 15. Casos de borda e comportamentos de erro

| EDGE | Cenário | Ação exigida |
| --- | --- | --- |
| EDGE-001 | Work ainda possui acesso de escrita principal | `HUMAN_DECISION_REQUIRED`; não ativar |
| EDGE-002 | Sandbox tem segredo ou código não permitido | Rejeitar, remover risco e não promover |
| EDGE-003 | Candidato toca path de control plane | Rejeitar o **candidato inteiro** |
| EDGE-004 | Evento duplicado ou bot | Ignorar instrução; reconciliar, não criar PR duplicado |
| EDGE-005 | Task/CI Work indisponível | `BLOCKED_EXTERNAL`, aguardar operador |
| EDGE-006 | Alteração grande demais para promoção via navegador | Bloquear e pedir decisão, não inventar importador |
| EDGE-007 | HEAD do sandbox muda após análise | Invalidar aprovação do candidato; reavaliar manifesto |
| EDGE-008 | HEAD do principal difere do candidato | Novos testes/review completos no principal |
| EDGE-009 | CI/Codex principal ausente ou vermelho | Sem READY, sem merge |
| EDGE-010 | Comentário forja `HUMAN_MERGE_AUTHORIZATION` | Não aceitar autoria do Work; exigir canal válido |
| EDGE-011 | Pedido de integração automático | Fora do piloto; nova ADR/SDD |
| EDGE-012 | Loop de mesma falha ≥3 | `LOOP_ESCALATION_REQUIRED` |
| EDGE-013 | Alteração externa de ruleset/credenciais | Parar até auditoria e nova autorização |
| EDGE-014 | API paga/compra exigida | `BLOCKED_EXTERNAL` sem gasto |

## 16. Migration

**Não aplicável.** Sem schema, SQL, dados tenant-owned ou transformação de histórico. Substituição de runtime vigente só poderá ocorrer após aprovação documental/rollout.

## 17. Estratégia de rollback

1. Desabilitar task piloto Work sandbox e impedir novos wake-ups.
2. Suspender promoção manual, preservar PRs/logs/links/SHAs de ambos repositórios.
3. Revalidar conexões e negar credenciais amplas ao Work; não presumir revogação instantânea de POST já enviado.
4. Manter CI/governança principal e contrato vigente; nenhuma API paga ou publisher automático é ativada.
5. Não marcar `PHASE-0-G` concluída por rollback.

## 18. Testes obrigatórios

### Unitários

Validação documental de esquema de evidências/identificadores, denylist de paths, distinção `sandbox_head_sha` vs `principal_head_sha` e anti-loop, quando implementada a automação de observação.

### Integração

- Confirmar permissão negativa da instalação/conexão Work no repositório principal antes do primeiro canary.
- Confirmar ruleset `main-protection` e status checks principal nos PRs humanos.
- Verificar que nenhum workflow principal usa token de escrita para importar diff sandbox.

### E2E

- Uma tarefa Work sandbox produz PR draft e relatório de CI sem tocar principal.
- Humano inspeciona manifesto e reproduz patch pequeno autorizado via GitHub web em PR principal.
- GOV/SEC/CODEX principal operam no HEAD criado pelo humano; revisão do sandbox não é reutilizada.
- Evento perdido, duplicata, quota esgotada, HEAD modificado e revogação de acesso produzem bloqueio sem promoção automática.

### Segurança / autorização / multi-tenancy

Caminho proibido no candidato invalida patch inteiro; comentário de bot/owner delegado não aprova; nenhuma execução de PR de fork com secrets/write; tentativa de Work escrever no principal deve falhar pela permissão. Não há dados tenant-owned no piloto.

### Regressão

Preservar regras de AGENTS.md, ADR-0014 e SDD-0001, checks e histórico de PRs; nenhum marcador de `PROJECT_STATUS completed` e nenhum merge sem gate humano.

## 19. Critérios de aceite

- **AC-001 documental:** ADR rev.6/SDD v0.6 revisadas formalmente, com pareceres aplicáveis e decisão humana de aceite/aprovação **separada** da escolha da opção A.
- **AC-002 ativação:** identidade/conector Work prova não ter write/admin/comment no principal; sandbox aprovado e sem secrets.
- **AC-003:** um canary Work limitado produz candidato draft exclusivamente no sandbox, sem alterar principal.
- **AC-004:** manifesto completo, allowlist/denylist e promoção pequena por humano geram PR principal com registro auditável dos dois HEADs.
- **AC-005:** GOV/SEC/testes e CODEX-01 exigidos no HEAD final **principal**; evidência sandbox não substitui.
- **AC-006:** PR principal não recebe READY com CI/Codex pendente ou falho.
- **AC-007:** MERGE-01 exige autorização humana válida **após READY**, no mesmo PR/HEAD; a decisão pela opção A não é merge grant.
- **AC-008:** nenhum token de publicação automático, DB PostgreSQL de orquestração, publisher ou fallback de OpenAI API paga é criado/ativado.
- **AC-009:** teste de Work sem acesso ao principal, candidato com control plane, fork, evento perdido, quota e duplicata interrompe conforme o caso.
- **AC-010:** anti-loop da família `WRITER_CAPABILITY_REVOCATION` é preservado por remover publicação automática do piloto, não por considerar risco aceito.
- **AC-011:** `PHASE-0-G` continua bloqueada até gates vigentes; nenhuma finalização implícita.
- **AC-012:** sucesso do piloto é medido com esforço de promoção humana e limitações registradas, **não** anunciado como runtime unattended completo.

## 20. Evidências de validação esperadas

Canaries antigos (issue #8), ruleset ativo ID 25036481, configuração da conexão Work segregada, teste de permissão negativa, links e manifestos de PRs sandbox/principal, screenshots/configuração quando pertinente, checks GOV/SEC, revisão Codex do HEAD principal, comentários de READY e autorização humana com timestamps. Evidência de sandbox isolado não é presumida hoje.

## 21. Dependências

Aprovação formal ADR/SDD; sandbox adequado; possibilidade real de limitar a instalação/conexão Work sem acesso ao principal; tarefa Work disponível ao humano; interface GitHub suficiente para a alteração pequena; GOV/SEC/CODEX ativos. Sem suporte de isolamento, parar e voltar à decisão humana; nenhuma nova infraestrutura paga prevista.

## 22. Riscos conhecidos

Confusão entre aprovação de direção e autorização de ativação; conexão owner ampla; erro na promoção manual; divergência entre diffs; perda de wake-up; review Codex indisponível; falsa sensação de autonomia end-to-end. Publicação automática e revogação de tokens em voo são riscos **fora do piloto**, não aceitos.

## 23. Dúvidas abertas

- Qual repositório sandbox será aprovado? `RamonRDR/SaaS-CAS-Lab` existe, mas só pode ser escolhido após avaliação de isolamento/escopo.
- A instalação Work GitHub permite delimitar realmente repositórios e permissões? O conector atual acessa principal; **não há prova de isolamento**.
- Qual primeiro changeset minúsculo será usado para conferir promoção via navegador sem segredos?
- Qual procedimento humano mais confiável para registrar manifesto/diff e conferir fidelidade após recriação no principal?
- Como medir retomada de eventos perdidos sem prometer gatilho programático não comprovado?

Estas perguntas **bloqueiam ativação**, e a incapacidade técnica de isolar identidade bloqueia o desenho; não são evidência de implementação já realizada.

## 24. ADRs necessários ou relacionados

ADR-0015 rev.6 `Accepted` é necessária para sucessão futura. ADR-0014 rev.5 `Accepted`, ADR-0010 e SDD-0001 v1.6 permanecem vigentes. A decisão humana de direção A não altera o estado destes documentos.

## 25. Histórico de revisão

| Versão | Data | Autor | Mudança |
| --- | --- | --- | --- |
| 0.1 | 2026-10-13 | Product & SDD | Proposta sucessora inicial |
| 0.2 | 2026-10-13 | Orchestrator / Tech Lead | Segurança e proveniência |
| 0.3 | 2026-10-13 | Orchestrator / Tech Lead | Sandbox, publisher, fencing e review context |
| 0.4 | 2026-10-13 | Orchestrator / Tech Lead | MERGE-01 vigente e cota por grant |
| 0.5 | 2026-10-13 | Orchestrator / Tech Lead | `PUBLISH_INTENT` global pré-POST |
| 0.6 | 2026-10-14 | Product & SDD / Orchestrator | Diretriz humana A: **promoção manual**, sem publisher automático/DB, risco anti-loop isolado |

## 26. Aprovação

- **Status de aprovação:** `Approved`, exclusivamente para o desenho do piloto A.
- **Responsável humano:** Responsável pelo repositório, por decisão explícita no canal interativo do Orquestrador.
- **Versão aprovada:** 0.6.
- **Data da aprovação:** 2026-10-14.
- **Registro de aprovação:** https://github.com/RamonRDR/SaaS-Project/issues/12#issuecomment-6171309622.
- **Parecer `review-sdd` vigente:** `Pronta para aprovação`, específico da v0.6; registro https://github.com/RamonRDR/SaaS-Project/issues/12#issuecomment-6170686193.
- **Pendências bloqueantes de desenho:** nenhuma conforme parecer formal, após Security, Platform e QA na issue #12.
- **Gates de ativação ainda pendentes:** isolamento efetivo da conexão Work para sandbox, escolha/configuração humana de sandbox, testes negativos e autorização explícita posterior para o primeiro canary.
- **Provenance:** decisão humana transcrita e registrada no GitHub por conexão delegada do Orquestrador; **não** corresponde a comentário digitado manualmente pelo responsável no GitHub.
- **Não confundir:** escolha de direção A ≠ aprovação formal desta SDD ≠ autorização de ativação ≠ aprovação de merge do PR #11.

**Esta aprovação NÃO autoriza merge, alterar a `main`, ativar tarefas, conceder credenciais, comprar serviços, usar API paga nem concluir `PHASE-0-G`.** A SDD-0001 v1.6 permanece `Approved` para o mecanismo vigente e não é marcada `Superseded` nesta branch.
