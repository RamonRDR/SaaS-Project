# SDD-0002 - Modo A com desenvolvimento orquestrado pelo Work

## Metadados

- **ID:** SDD-0002
- **Título:** Modo A com desenvolvimento orquestrado pelo Work e gates independentes no GitHub
- **Status:** In Review
- **Versão:** 0.2
- **Responsável pela especificação:** Product & SDD
- **Responsável humano pela aprovação:** responsável pelo repositório
- **Data de criação:** 2026-10-13
- **Última atualização:** 2026-10-13
- **Entrega / issue / PR relacionada:** Issues #1, #8, #10 e proposta documental desta branch
- **ADRs relacionados:** ADR-0015 rev.2 (`Proposed`), ADR-0014 rev.5 (`Accepted`), ADR-0010 (`Accepted`)
- **SDDs relacionadas:** SDD-0001 v1.6 (`Approved`, vigente, sucessão proposta)

### Estados permitidos e validade

`Draft`, `In Review`, `Approved`, `Superseded`. Versão **0.2 em revisão**, sem parecer `review-sdd` nem aprovação humana. As seções 1 a 24 são conteúdo material e qualquer modificação posterior exige controle de versão/parecer conforme `docs/specs/SDD-TEMPLATE.md`. A aprovação de elaborar a proposta **não é aprovação da SDD**. A SDD-0001 v1.6 continua vigente; não pode ser marcada `Superseded` antes da eventual aprovação da SDD-0002.

**Racional de sucessão:** a mudança não é ajuste pontual da v1.6; substitui o componente de IA/claim/Budget Broker e o requisito de não usar Work como caminho de execução. Um novo ID preserva o contrato anterior aprovado sem reescrita histórica.

## 1. Contexto

O repositório público `RamonRDR/SaaS-Project` possui engenharia de fundação, Mode A interativo e `PHASE-0-G` planejada. A SDD-0001 v1.6 descreve runtime Actions-only com inferência programática paga, claim universal, ledger financeiro, reviewer isolado e publisher trusted. O responsável quer executar desenvolvimento unattended dentro da franquia ChatGPT, sem comprar ou ativar OpenAI API. Três canaries do Work/GitHub em 13/10/2026 provaram wake-up, desenvolvimento/PR/CI e uma rodada CI failure → remediação → CI success (issue #8). Essas evidências não tornam confiáveis entrega de eventos, proteção de paths, review ou continuidade irrestrita.

## 2. Problema

A arquitetura vigente exige implementar uma infraestrutura financeira e de inferência que não corresponde ao orçamento autorizado, e os ciclos de implementação estão presos em `LOOP_ESCALATION_REQUIRED` para `INTAKE_RECOVERY_API_CAPACITY` (PR #4). O sistema ainda não possui um contrato aprovado para usar Work como executor contínuo de código sem quebrar os gates de revisão/segurança e sem aceitar prompts como controles de permissão.

## 3. Objetivo

Entregar um **piloto verificável de autonomia supervisionada**, com Work criando e corrigindo código exclusivamente dentro de escopo/branch confiáveis; GitHub mantendo evidências independentes de CI, integridade e proveniência; CODEX-01 separado do autor; merge sempre humano. Garantir pausa segura quando não houver Work, quota, evento, permissão ou evidência. **Não prometer alta disponibilidade nem autonomia incondicional.**

## 4. Escopo

- Contrato de tarefa Work acionada por atividade suportada no GitHub, com wake-up idempotente, fontes atuais e identificação humana.
- Estados, eventos, observabilidade, reconciliação read-only e timeout definidos.
- Desenvolvimento/correção de **PR same-repo** previamente autorizado, em branch isolada, sem permissões privilegiadas a partir de fork.
- GitHub Actions como CI independente e verificador de escopo/segurança; provar permissões efetivas, proteção de `main` e consequências de bypass.
- CODEX-01 independente, no HEAD congelado, e gate de aprovação humana antes do merge.
- Testes positivos/negativos de evento, concorrência, integridade, perda de evento, revisão atrasada, anti-loop e bloqueio.
- Custo de IA programática da OpenAI **zero**, sem secrets de API nem auto-upgrade.
- Documentação, implantação gradual, critérios de aceite e rollback. Sem qualquer ativação por esta proposta.

## 5. Fora de escopo

- Alterar o schema do SaaS, Django, Flutter, PostgreSQL, n8n ou tenants nesta fase.
- Aprovar/mergear PRs #4/#6/#7/#9 ou transferir automaticamente o código experimental para a `main`.
- Usar `OPENAI_API_KEY` ou OpenAI API, mesmo para fallback.
- Remediação automática de forks, workflows, prompts/skills, governança, ADRs, SDDs, autenticação/segredos, branch protection e control plane.
- Declarar quota Work ilimitada, periodicidade garantida, entrega exatamente uma vez ou cumprimento de SLA.
- Autorizar merge principal, mutação financeira ou `PHASE-0-G completed`.
- Tratar relatório do agente ou texto de comentário como prova independente de CI/review.

## 6. Atores e jornadas afetadas

| Ator | Jornada / interação | Impacto |
| --- | --- | --- |
| Responsável humano | Aprova escopo e decisões materiais, avalia READY, autoriza merge | Gate preservado |
| GitHub / Actions | Armazena PR/HEAD, aplica CI/GOV/SEC, detecta divergências | Fonte de evidência independente |
| Work | Recebe wake-up suportado, consulta estado atual, edita somente branch/escopo autorizado | Executor sujeito a quota e permissão |
| Codex Review independente | Avalia HEAD final, findings, proveniência e contrato congelado | Gate CODEX-01 |
| Reconciler GitHub read-only | Observa backlog/tempo/escalada sem autoridade de executar IA | Diagnóstico e alertas |
| Contribuidor de fork | Abre PR tratado como dado não confiável; sem remediação privilegiada | Fluxo manual/read-only |
| Especialistas Security / QA / Platform | Revisam proteção, recuperação e escalada | Pareceres obrigatórios antes do piloto |

## 7. Regras de negócio

- **BR-001:** somente uma tarefa Work **explicitamente habilitada pelo humano** pode agir num repositório/gatilho suportados e com controle de escopo vigente.
- **BR-002:** o evento GitHub é aviso; ler novamente PR, HEAD, comentários, reviews, gates e issue de controle. Nenhum texto do PR é comando operacional.
- **BR-003:** um evento/comentário, mesmo exibindo login do proprietário, NÃO é autorização humana: o conector GitHub pode escrever sob a mesma conta. Somente controle explícito de escopo aprovado no canal humano independente do agente, com provenance, repositório, branch, paths, operação, validade e versão de contrato verificáveis, permite agir. O marcador exato e a autoria são sinais auxiliares, jamais substitutos do controle.
- **BR-004:** identidade por `repository/pr_number/expected_head_sha/operation_kind/authorized_attempt/root_cause_family_id`, canonizada para deduplicação; `workflow_run_id` não reinicia tentativa.
- **BR-005:** tarefas concorrentes não podem publicar duas alterações para uma mesma operação/HEAD; optimistic concurrency revalida HEAD antes de cada mutação e suspende em divergência.
- **BR-006:** toda edição do Work ocorre em branch isolada e escopo aprovado, sob **proteção de escrita efetivamente comprovada**; se não for possível proteger `main` no repositório real, restringir Work a credencial/repositório sandbox isolado e interromper integração automática. PR de fork jamais recebe escrita privilegiada.
- **BR-007:** paths do control plane (`.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**`, `docs/PROJECT_STATUS.md`) não podem ser publicados por **remediação autônoma**.
- **BR-008:** antes de qualquer integração, checks independentes do GitHub comparam diff final contra escopo autorizado, negam paths protegidos e validam origem e SHA; checks verdes sem revalidação do HEAD não bastam.
- **BR-009:** tasks Work não recebem credenciais de produção/tenant/fornecedor; as permissões efetivas do conector são inspecionadas. Em 13/10/2026 a API GitHub retornou `rulesets=[]`; `/branches/main/protection` retornou 403 à integração, portanto **proteção da `main` não demonstrada**. Sem prova independente de bloqueio de escrita direta ou isolamento efetivo, nenhuma operação unattended no repo principal.
- **BR-010:** não disponibilizar `OPENAI_API_KEY`, endpoint pago ou compra automática. Se o Work/Codex exigir cota/créditos extras, transicionar `BLOCKED_EXTERNAL`, sem gastar.
- **BR-011:** Work pode consultar CI, mas nunca emitir `CI_PASSED` baseado apenas no próprio relatório. A evidência vem do GitHub, identificada pelo HEAD correto.
- **BR-012:** o `CODEX-01` deve ser independente do Work/autor, concluído para o HEAD exato após o último commit mutável; qualquer mudança invalida revisão.
- **BR-013:** findings bloqueantes são corrigidos no escopo ou escalados; aceitação de risco é sempre decisão humana; não rebaixar severidades automaticamente.
- **BR-014:** após 3 tentativas sobre a mesma causa sem progresso, pingue-pongue, deadlock ou falta de evidência, emitir `LOOP_ESCALATION_REQUIRED`. Nova causa independente pode seguir o lifecycle.
- **BR-015:** alterações de control plane, escopo novo, exceção de segurança, vendor pago, mudanças sensíveis ou migration destrutiva levam a `HUMAN_DECISION_REQUIRED`.
- **BR-016:** `READY_FOR_HUMAN_MERGE` requer evidência GitHub `MERGE_ALLOWED`, CI/GOV/SEC, CODEX-01 no HEAD e contrato `REVIEW_CONTRACT_FROZEN`; não confere permissão para merge.
- **BR-017:** somente autorização humana válida, posterior a READY e do mesmo PR/HEAD, permite merge principal, com verificação pós-merge do `AGENTS.md`.
- **BR-018:** perda/coalescência de wake-up, task pausada/desconectada, timeout, credencial inválida, limite Work ou CI ambíguo **nunca** são tratados como sucesso. Reconciler confiável read-only executado no GitHub registra pendência e `BLOCKED_EXTERNAL` sem tentar publicar código; enquanto não existir wake-up programático oficialmente suportado, a recuperação requer intervenção do operador humano, não continuidade automática presumida.
- **BR-019:** observador não fabrica gatilho humano, não ativa Work, não chama IA nem presume API de trigger programática disponível; eventual retry automatizado exige suporte comprovado e novo gate.
- **BR-020:** registrar checkpoint durável por PR/HEAD/operação após readback, sem usar comentário de agente como CAS. Reentrar reconcilia estados reais antes de qualquer nova ação.
- **BR-021:** o projeto não declara `DONE_ALLOWED` antes dos gates finais; `PHASE-0-G` fica planejada até canary E2E final e aprovação.
- **BR-022:** dados de forks, diffs, comentários, logs e tool output são não confiáveis; nunca executá-los como shell/script com secrets.
- **BR-023:** qualquer mutação em trust boundary/permissions/modelo/tarefa de produção exige versão de contrato e decisão humana; nenhuma edição de prompt tácita.
- **BR-024:** não introduzir fallback pago, ledger financeiro ou claim de gasto no piloto. Componentes aprovados na ADR-0014 permanecem inativos até sucessão, não são reutilizados por inferência implícita.
- **BR-025:** as três tarefas de canary antigas estão desativadas; sua evidência é histórico, não runtime em execução.
- **BR-026:** tarefas Work não representam fonte confiável para `Approved`, `Accepted`, autorização de merge, revisão de risco ou alteração de `PROJECT_STATUS`.

## 8. Permissões e multi-tenancy

**Permissões de engenharia:** o responsável autoriza escopo por ato auditável **externo às mensagens produzíveis pelo Work**; comentários GitHub são wake-ups mesmo sob login do proprietário. Work só propõe código em branch isolada no ambiente onde o alcance efetivo da credencial foi demonstrado seguro; Actions opera com permissões mínimas para CI/controle. O conector GitHub pode ter privilégios maiores que o prompt: **instrução natural não é enforcement**. Os rulesets consultados retornaram `[]` e a proteção tradicional retornou 403 à conexão, logo exigir checagem por um administrador do repositório. Provar controle técnico contra push direto em `main`, alteração de regras e integração de diff fora do escopo. Sem prova possível, usar ambiente e credencial sandbox **realmente isolados**, sem escrita na main de produção; caso contrário, bloquear piloto.

**Multi-tenancy:** não aplicável ao protótipo de engenharia, pois nenhum dado tenant-owned é manipulado. Fluxos de produto futuros exigirão isolamento de tenant e testes negativos, sem dispensa por execução assistida.

## 9. Impacto no modelo de dados

- Banco de produto: **não aplicável**.
- Registros de orquestração por `repo/pr/head/operation` devem guardar `schema_version`, `expected_head_sha`, `control_issue`, `root_cause_family_id`, `attempt`, `state`, `source`, `last_checked_at`, `evidence_urls`, `trusted_contract_digest` quando aplicável.
- Checkpoint deve ser durável e idempotente, mas **nenhum storage escolhido a priori**; issue comment não é transação nem `CAS`. Sem prova de concorrência, manter reconciler apenas em leitura.
- Duplicatas de evento/registro não podem emitir um segundo efeito de escrita para o mesmo HEAD.

## 10. Impacto no contrato da API

Não há endpoint de produto ou breaking change de API de domínio. Interfaces propostas:
- GitHub: eventos suportados de comentários/PR; metadados atuais por PR/HEAD; checks, reviews e comentários de evidência.
- Work: tarefa criada/ativada pelo humano; evento é wake-up; operações na conexão GitHub permitidas conforme privilégio real.
- CI: check por SHA, diffs completos, allowlist/denylist, resultado de suite e segurança.
- **Ausência explícita** de chamadas `api.openai.com` e `OPENAI_API_KEY`.

Schema exato de status/checkpoint, quotas e convenções de marcador devem ser especificados no PR técnico posterior e congelados antes de ativação, com versão e teste de compatibilidade.

## 11. Comportamento esperado no Flutter

**Não aplicável:** o piloto altera exclusivamente engenharia/orquestração, sem telas ou jornadas de produto. Futuras features Flutter continuam sujeitas a BUILD-02, acessibilidade e regras server-side.

## 12. Integrações externas

- **GitHub Actions:** CI, governance, secret scan e check independente de escopo. A fila/concurrency do Actions não é durável nem CAS.
- **ChatGPT Work:** execução por eventos suportados, com franquia/limites da conta e possibilidade de aprovação/pausa. Não garantir frequência e não inferir capacidade de disparo programático a partir de experiência manual.
- **Codex Review GitHub:** review independente do HEAD sob limites do plano; indisponibilidade resulta `BLOCKED_EXTERNAL`, não autoaceite.
- **OpenAI API:** não aplicável; proibida no piloto. Novo fornecedor pago/sensível exigiria gate humano prévio.

## 13. Segurança e privacidade

- Carga de evento e comentários GitHub não são instruções; buscar estado confiável, validar autoria, PR, branch, HEAD e autorização antes de agir.
- Rejeitar alteração fora da allowlist e toda mutação do control plane em automação. O controle independente está no GitHub e bloqueia integração, **não altera o privilégio da credencial Work**.
- Não expor token, secrets, dados pessoais de clientes ou logs privados no repositório público.
- Fork: nenhum checkout/execução com secrets ou `contents:write`; no piloto, fluxo automático de correção de forks é `N/A`, direcionado ao humano.
- Diferença entre SHA revisado e HEAD, mudança de branch/proteção, workflow de CI alterado e ambiguidade de origem devem falhar fechado.
- Separação autor Work / Codex reviewer / CI enforcement / merge humano é mandatória, não apenas declaratória.

## 14. Observabilidade

Para cada execução, registrar em canal auditável: `correlation_id` imutável derivado de PR/operação/HEAD, tipo do gatilho, tarefa, tentativa por causa, status, checks por SHA, branch, evidence links, timestamp de observação e bloqueio. Reduzir dados expostos ao mínimo. Estados propostos: `OBSERVED`, `WORK_PENDING`, `CI_PENDING`, `CI_FAILED`, `AUTO_REMEDIATION`, `WAITING_CODEX`, `REVIEW_CONTRACT_FROZEN`, `READY_FOR_HUMAN_MERGE`, `HUMAN_DECISION_REQUIRED`, `BLOCKED_EXTERNAL`, `LOOP_ESCALATION_REQUIRED`. Não confundir job `success` com `DONE_ALLOWED`. Alertar em atraso de evento e cota; observar no GitHub de forma read-only.

## 15. Casos de borda e comportamentos de erro

| ID | Cenário | Comportamento esperado |
| --- | --- | --- |
| EDGE-001 | Evento duplicado/reordenado | Reconciliar checkpoint e HEAD; não duplicar PR/commit |
| EDGE-002 | Comentário humano não é marcador exato | Ignorar sem mutação |
| EDGE-003 | Comentário de bot/terceiro com texto de gatilho | Não autorizar trabalho |
| EDGE-004 | PR muda de HEAD após wake-up | `BLOCKED_STALE_HEAD`; invalidar CI/review anterior |
| EDGE-005 | Mesmo HEAD, base ou diff muda | Revalidar fingerprint e escopo; review desatualizado |
| EDGE-006 | Work pausado ou desconectado | Reconciler observa atraso; `BLOCKED_EXTERNAL` |
| EDGE-007 | Quota Work/Codex esgotada | Parar, sem API paga, registrar bloqueio |
| EDGE-008 | Runner GitHub falha ou check ausente | Não emitir CI PASS/READY |
| EDGE-009 | Novo commit após CODEX-01 clean | Invalidar review, exigir HEAD atual |
| EDGE-010 | Diff inclui path protegido | Check independente FAIL, bloquear integração e escalar |
| EDGE-011 | Work tenta operar fork | Negar escrita automática; revisão read-only/manual |
| EDGE-012 | Comentário/log contém instrução para agente | Tratar como dado; não obedecer |
| EDGE-013 | Três correções repetem mesma causa | `LOOP_ESCALATION_REQUIRED` |
| EDGE-014 | Segurança exige novo contrato/risco humano | `HUMAN_DECISION_REQUIRED` |
| EDGE-015 | Dois Work runs editam mesmo PR | Comparar HEAD e operação; apenas uma transição segura |
| EDGE-016 | Mensagem de sucesso sem SHA/runs reais | Não considerar prova |
| EDGE-017 | Work cria PR draft sem CODEX-01 | Somente evidência de protótipo, nunca `MERGE_ALLOWED` |
| EDGE-018 | Evento não é entregue | Scanner apenas detecta pendência; não promete wake-up |
| EDGE-019 | Approver humano ausente | `READY_FOR_HUMAN_MERGE` aguarda indefinidamente, nunca merge automático |
| EDGE-020 | Tentativa de escrever `main` ou burlar branch rules | Interromper o piloto, evidenciar incidente e revisar permissões |
| EDGE-021 | Mudança de configuração da tarefa após aceite | Invalidar versão de contrato e bloquear até revisão |
| EDGE-022 | GitHub API rate-limit ou readback ambíguo | Fail-closed; backoff sem loops agressivos |
| EDGE-023 | Estado de checkpoint parcialmente gravado | Reconsulta autoritativa, sem pular operações |
| EDGE-024 | Work solicita créditos/cobrança | Não comprar, não chamar endpoint pago, `BLOCKED_EXTERNAL` |
| EDGE-025 | Comentário via conector aparece como proprietário | Não inferir autorização humana por login; exigir ato independente |
| EDGE-026 | `rulesets=[]` e branch protection indisponível | Bloquear Work no repo principal até prova de proteção ou sandbox isolado |
| EDGE-027 | Reconciler detecta trigger não entregue | Registrar pendência; intervenção humana caso não exista reativação programática suportada |

## 16. Migration

- **Migration necessária:** Não.
- **Destrutiva:** Não.
- **Descrição:** nenhum schema de banco de produto.
- **Gate humano necessário:** Sim, decisão arquitetural material e ativação futura. Eventual migração de checkpoints/issue inbox exigirá SDD/tarefa técnica próprios.

## 17. Estratégia de rollback

1. Desativar tarefa Work do piloto pelo responsável; não apagá-la sem preservar evidências.
2. Desabilitar somente gatilhos/write paths introduzidos no piloto, mantendo CI/governança/read-only.
3. Revogar/limitar credenciais comprometidas com ação humana e auditar PRs/commits produzidos.
4. Voltar ao fluxo interativo autorizado, sem ativar automaticamente o runtime Actions-only com API paga.
5. Preservar referências a logs, SHAs, comentários e pendências; não apagar evidência por conveniência.
6. Não marcar `PHASE-0-G` concluída durante rollback.

## 18. Testes obrigatórios

### Unitários
- Identidade de operação, deduplicação, estados, HEAD/fingerprint, lógica anti-loop por causa, validação de marcador/autoria e regex de paths protegidos.
- Simular exceção de quota/timeout, comentário adversarial, checkpoint parcial e cancelamento.

### Integração
- GitHub API read-only com mocks para retorno de PR/HEAD/CI/reviews atuais.
- Compatibilidade de workflows e acesso mínimo; rate limit/backpressure.
- Regras de branch/ruleset e check negativo de control plane por diff malicioso.

### E2E
- Reproduzir 3 canaries anteriores como baseline, mais três entregas **independentes** com CI e CODEX-01 final do HEAD antes de READY, sem merge.
- Perda/coalescência de wake-up: observador detecta `BLOCKED_EXTERNAL`, sem afirmar que reparou.
- Work em pausa/franquia limitada: status de bloqueio e retorno idempotente após reativação autorizada.
- Mudança de HEAD enquanto CI/review demora: rejeitar evidência obsoleta.
- Escrita de path protegido bloqueada independentemente antes de integração.

### Segurança / autorização / multi-tenancy
- PR de fork hostil, prompt injection, comentário bot, alteração da tarefa e tentativa de tocar `main`; nenhum secret exposto.
- Cross-tenant: N/A no piloto, pois não há código de produto ou dados de tenant.
- Permissões reais do conector e proteção da branch principal devem ter evidência verificada; não basta uma simulação.

### Regressão
- Testes de Governance Gates (GOV-01, SEC-01), suite de canary, ausência de API paga, gates de merge e revisão.
- Canary da implementação antiga permanece desativado e não é tratado como novo runtime.

## 19. Critérios de aceite

- **AC-001 (gate documental):** a arquitetura define explicitamente o controle de escopo/autorização, o mecanismo de proteção da `main` ou sandbox isolado, recuperação de falhas e o fallback bloqueado; depois obtém parecer favorável de `review-adr`/`review-sdd` e aceite/aprovação humanos **específicos**, sem simular resultados de implantação. Sem esse gate documental, nem iniciar implementação sob novo contrato.
- **AC-002 (gate de ativação):** tarefa Work com escopo/repo/evento/contrato/verificação humana independente, configuração conferida e credencial com alcance realmente isolado. Login de comentário não comprova autorização. Qualquer privilégio de escrita amplo não mitigado bloqueia.
- **AC-003:** o mesmo gatilho repetido não cria duplicata de PR/commit/relatório; demonstrar duas execuções e reentrada após timeout.
- **AC-004:** três execuções independentes chegam a `CI_PASSED`, `CODEX-01` no HEAD exato e `READY_FOR_HUMAN_MERGE` sem merge e sem pedido de continuação.
- **AC-005 (gate de ativação):** GitHub bloqueia PR com mudança de control plane e nunca declara `MERGE_ALLOWED`; **além disso** deve haver prova de bloqueio de push direto em `main` ou isolamento da credencial Work em outro repositório sem acesso privilegiado. Um check de PR sozinho não cobre push direto.
- **AC-006 (gate de ativação):** falha de evento/tarefa/quota detectada pelo observador GitHub read-only e marcada `BLOCKED_EXTERNAL` dentro de uma janela estabelecida após medição; sem compra automática de créditos nem suposição de retomada automática sem endpoint/gatilho confirmado.
- **AC-007:** reviewer CODEX-01 independente de Work, vinculado ao SHA final e revalidado após modificação.
- **AC-008:** nenhum arquivo da `main` alterado, merge não autorizado ou `PROJECT_STATUS completed` produzido pelo piloto.
- **AC-009:** observador read-only possui evento/PR/HEAD/correlation/timestamp/estado e evidence URL por transição sem secrets.
- **AC-010:** timeout, crash antes/depois de commit, branch concorrente e ACK ambíguo convergem ou bloqueiam sem efeitos duplicados.
- **AC-011:** nenhum código de fork executado com secrets e nenhuma remediação privilegiada de fork.
- **AC-012:** anti-loop escala após três tentativas sem progresso na mesma causa sem interromper causas independentes.
- **AC-013:** matriz de BR/EDGE/AC da SDD-0001/ADR-0014 documenta o que foi substituído, mantido ou desativado; nenhum controle removido por silêncio.
- **AC-014:** revisão de custos confirma que não há `OPENAI_API_KEY`, OpenAI API faturável nem fallback pago no piloto.
- **AC-015:** documentação de rollback, condições de falha, restrições Work/Codex e canal de retomada humana é revisada antes da execução real.
- **AC-016:** autorização de escopo e merge não pode ser forjada por agente usando a identidade GitHub do proprietário; teste negativo obrigatório.
- **AC-017:** auditoria independente de branch protection/rulesets ou sandbox/credencial isolados apresentada por administrador; `rulesets=[]` ou acesso 403 não contam como PASS.

## 20. Evidências de validação esperadas

- Links verificáveis dos três canaries: issue #8 e PRs #6/#7/#9.
- SHA e run URLs dos CI vermelhos e verdes, inclusive check jobs e timestamps.
- Captura da configuração efetiva da tarefa Work, limites/permissões e restrição de conexão.
- CI negativo de control plane, fork, perda de evento, HEAD obsoleto, quota e permissão.
- Pareceres de Security, Platform/Observability e QA com pendências resolvidas.
- Codex Review independente para HEAD do PR piloto congelado; evidência `REVIEW_CONTRACT_FROZEN`.
- Prova de que o gatilho não alterou `main` nem criou gasto via API.

## 21. Dependências

- ADR-0015 rev.2 em `Proposed`, revisão `review-adr` e aceite humano antes de se tornar vigente.
- SDD-0001 v1.6 e ADR-0014 rev.5 continuam vigentes até sucessão formal.
- GitHub Actions, permissões/rulesets verificáveis, tarefa Work e recursos disponíveis na assinatura.
- Suporte real a trigger de comentário PR, revisões independentes CODEX-01, branch de teste.
- Plano `docs/engineering/MODE_A_WORK_HYBRID_IMPLEMENTATION_PLAN.md`.
- Diagnóstico de PR #4/#6 não deve ser reaberto silenciosamente, pois segue em escalada específica.

## 22. Riscos conhecidos

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Quota Work e ausência de SLA | Paralisação de tarefas | `BLOCKED_EXTERNAL` + acompanhamento read-only + operador humano |
| Conector GitHub com escrita ampla | Bypass de caminhos protegidos | Escopo mínimo, branch protection, check independente e gate humano |
| Evento perdido/coalescido | Backlog sem progresso | Observador de estado, alerta, retomada somente com suporte confirmado |
| Revisão Codex ausente ou em SHA obsoleto | Merge inseguro | CODEX-01 independente com HEAD exato |
| Prompt injection e forks | Exfiltração/patch não confiável | Não seguir comentários/logs, não executar forks com secrets |
| Loop de remediação | Custo de franquia e atraso | 3 tentativas/cause + bloqueio explícito |
| Falsa sensação de autonomia por canaries | Ativação prematura | Provas negativas, métricas e aprovação humana final |
| Diferença de semântica entre Work e Actions | Estado divergente | GitHub como fonte de evidência, readback antes de toda transição |

## 23. Dúvidas abertas

**Dúvidas de desenho bloqueantes para aprovação documental:**
1. Qual controle técnico será adotado para isolar escrita do Work: ruleset/branch protection com evidência administrativa de não-bypass ou credencial e repositório sandbox dedicados sem acesso à `main` principal? A consulta atual não demonstra proteção.
2. Qual mecanismo de estado durável e propriedade de exclusão será usado para deduplicação e verificação de concorrência sem implementar CAS falso em Git, ao menos para o piloto delimitado?
3. Como a autorização humana de escopo será registrada fora de comentários GitHub e ações produzíveis pela mesma conta Work, com proveniência e validade? Quais limites Work/trigger serão medidos antes do piloto?
4. Na ausência de wake-up programático comprovado, o observador ficará apenas read-only com escalada ao operador. Qual é o canal de alerta e procedimento de intervenção humana? Um SLA numérico depende de medidas, não de hipótese.
5. Qual evento/artefato GitHub fornecerá prova auditável de CODEX-01 separado do Work, no HEAD exato, e de sua invalidação por novo commit?
6. Como arquivar ou isolar PR #4/#6 mantendo evidências e sem aceitar P2 residual silenciosamente? A decisão não libera integração.
7. Que duração/concorrência máximas serão medidas na implantação do piloto? O contrato pode exigir bloqueio conservador antes de qualquer número arbitrário.

**Separação de fases:** dúvidas 1–5 exigem estratégia arquitetural explícita antes de `Approved`; a instrumentação real, testes negativos e medidas só são possíveis nos PRs técnicos pós-aprovação, e continuam **bloqueios de ativação** até comprovados. Não marcar esta SDD `Approved` enquanto decisões materiais persistirem. Não exigir provas de software ainda não autorizado como pré-condição circular para aceitar o desenho.

## 24. ADRs necessários ou relacionados

- **ADR necessário:** Sim, ADR-0015 rev.2 `Proposed`.
- **Referências:** ADR-0014 rev.5 `Accepted`, ADR-0010 `Accepted`, ADR-0013 histórica.
- **Motivo:** alterar o executor de IA e desativar caminho financeiro/pago da arquitetura vigente exige nova decisão e sucessão formal; não implica aceitar a ADR proposta antecipadamente.

## 25. Histórico de revisão

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 0.1 | 2026-10-13 | Product & SDD | Criação de SDD sucessora após três canaries e autorização para elaborar |
| 0.2 | 2026-10-13 | Orchestrator / Tech Lead | Ajustes materiais após review-sdd v0.1, sem aprovação humana |

## 26. Aprovação

### Revisão

- **Parecer de `review-sdd`:** Pendente, não executado.
- **Versão revisada:** Não aplicável.
- **Pendências bloqueantes:** escolhas de autorização independente, trust boundary de escrita, idempotência/estado e pareceres especializados de segurança/plataforma; AC de implantação são gates posteriores.
- **Pendências não bloqueantes:** Formatação e detalhamento de observabilidade/implantação, sujeitos ao review.

### Gate humano

- **Aprovada:** Não.
- **Versão aprovada:** Não aplicável.
- **Responsável humano:** Responsável pelo repositório.
- **Data:** Não aplicável.
- **Registro da aprovação:** Não aplicável.

**SDD-0001 v1.6 permanece `Approved` até SDD-0002 aprovada formalmente.** Uma eventual substituição de status requer ação administrativa posterior e evidência humana explícita; não realizar nesta branch.
