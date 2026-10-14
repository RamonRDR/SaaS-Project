# Mode A: contrato do piloto com promoção humana (proposta)

**Status:** piloto temporário proposto, não implementado nem ativado. **Atualização:** 2026-10-14. **Referências:** ADR-0015 rev.6, SDD-0002 v0.6, issues #8 e #10, PR #11.

## 1. Limites de confiança

1. **Principal:** `RamonRDR/SaaS-Project`, `main` protegida pelo ruleset `main-protection` ID 25036481, ativo, sem bypass, com PR e checks `governance` / `secret-scan`. **Zero aprovações obrigatórias** no ruleset: a autorização humana continua exigência processual e deve ser comprovada; não declarar enforcement de revisor externo.
2. **Sandbox:** repositório GitHub separado e sem segredos, escolhido e conferido pelo responsável antes de ativar. `RamonRDR/SaaS-CAS-Lab` existe, mas **é somente candidato**, não sandbox autorizado automaticamente. O código admissível deve ser limitado a caminhos e tarefa reversível definidos pelo humano.
3. **Work:** a identidade/conexão GitHub efetivamente usada pelo Work precisa ter permissões de escrita **apenas no sandbox**, sem `contents:write`, `pull_requests:write`, `issues:write`, `workflows:write` ou administração no principal, nem capacidade de reconfigurar estas permissões. **A conexão atual do proprietário ao principal não serve de prova de isolamento.** Antes de qualquer canary mutável, o humano deve revisar a instalação/escopo do app, retirar a delegação ampla e testar acesso negativo ao principal. Se o conector não permitir esse limite, **não ativar o piloto Work**.
4. **GitHub Actions principal:** somente CI, governança e observação read-only. Nenhuma credencial de publicação `contents:write` é entregue a job que processe mudanças do sandbox. Nenhum importador, broker de tokens, PostgreSQL ou automação de publicação foi autorizado nesta fase.
5. **Humano:** escolhe o escopo, inspeciona o candidato e **transporta pessoalmente** as mudanças permitidas pelo navegador para branch e PR novos no principal; não delega esse ato ao Work nem a workflow que receba instruções do sandbox. A promoção não é merge. Só o PR no principal, com HEAD e diff próprios, é candidato à integração final.

## 2. Autorização e fluxo do piloto

1. Registrar escopo humano do canary em decisão interativa auditável: repositório sandbox, issue/objetivo, caminhos permitidos, base da tarefa, proibições, expiração e limite de tentativas. **O aceite da Opção A em 14/10/2026 autoriza esta revisão documental, não liga tarefa Work nem autoriza PR/merge por antecipação.**
2. Depois de comprovado o isolamento da conexão, humano habilita uma tarefa Work temporária **somente no sandbox**, sem segredos, com wake-up por evento suportado; Work relê estado real. Comentários, patches e logs são dados não confiáveis, jamais autorizações.
3. Work produz branch/PR draft no sandbox e CI sandbox sem secrets de escrita do principal. Pode iterar em tarefas pequenas e reversíveis, sujeito a quotas e às regras de anti-loop. Evento perdido ou quota indisponível → `BLOCKED_EXTERNAL` e intervenção humana; não alegar recuperação automática.
4. Humano confere **diff completo, caminhos, modos, blobs, exclusões/renames e conteúdo**, aprova apenas se dentro da allowlist, sem secrets. Denylist mínima: `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` e `docs/PROJECT_STATUS.md`. **Qualquer caminho proibido invalida todo o candidato**, não selecionar trechos do patch malicioso como se ele tivesse sido aprovado.
5. Se aprovado, **humano cria uma branch no repositório principal via interface GitHub autenticada** e reproduz **manualmente** as alterações permitidas, depois abre um PR próprio em draft. Na primeira prova, limitar a mudança pequena que seja praticável pelo editor web. Não utilizar workflow de importação com credencial automática. Registrar links para PR sandbox, manifesto verificado, branch/HEAD final principal e descrição de diferenças de conteúdo. Se a transferência não couber com segurança no navegador, **bloquear e pedir nova decisão humana**, sem inventar um importador.
6. A identidade de código e SHA do PR principal **serão diferentes** dos do sandbox. Portanto, execute GOV-01, SEC-01, testes aplicáveis e `CODEX-01` independentes **no HEAD real do PR principal após a promoção**. Não reutilizar check/review do sandbox como prova de integração. Se qualquer arquivo, base, HEAD ou contrato de revisão mudar, invalidar evidência e repetir gate.
7. `READY_FOR_HUMAN_MERGE` é registrado somente depois de todos os gates do PR principal e `REVIEW_CONTRACT_FROZEN`. **MERGE-01 usa exatamente AGENTS.md regra 31:** `HUMAN_MERGE_AUTHORIZATION` manual posterior ao READY, ou `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` apenas quando o humano decidir no canal interativo externo ao GitHub. A autorização da Opção A NÃO é autorização de merge. Não fazer merge nesta etapa documental.

## 3. Revogação, rollback e bloqueios

- Revogar escopo de trabalho ou desabilitar Work interrompe **novas decisões e execuções autorizadas**; não afirmar que revogar um token/cancelar um job aborta requisição GitHub já recebida.
- O risco `WRITER_CAPABILITY_REVOCATION` foi escalado após repetidas correções Codex; **não é aceito como residual**. É **eliminado do envelope do piloto** porque Work não pode escrever no principal e nenhum publicador automático principal recebe token. Se essa premissa for violada, bloquear piloto (`HUMAN_DECISION_REQUIRED`).
- Publicações já realizadas no sandbox não são revertidas automaticamente. Preservar evidências, isolar branch e desabilitar task após falha; não apagar histórico para simular limpeza.
- Controle de concorrência do sandbox: uma tarefa por escopo pequeno, idempotência por item/HEAD, reconsulta antes de escrever, limite de tentativas e nenhuma garantia de exactly-once do Work. Duplicação no sandbox não causa efeito no principal sem promoção humana.
- Não ativar OpenAI API paga, não registrar `OPENAI_API_KEY`, não contratar banco ou provedor. Não reativar tarefas canary antigas.
- Se a separação de conexão não puder ser confirmada, **não iniciar M2**, nem permitir que o Work atual use o principal. O GitHub Actions principal continua read-only para observação, mesmo diante de falhas.

## 4. Testes de segurança e critérios de ativação do piloto

| Caso | Experimento | Evidência exigida |
| --- | --- | --- |
| ISO-01 | Work tenta ler/escrever ou comentar no principal via conexão de sandbox | Permissões demonstram ausência de escrita; ação negativa quando cabível; nenhum efeito no principal |
| ISO-02 | Work tenta alterar `.github/**` ou arquivo de governança no sandbox | Candidato integralmente rejeitado na avaliação humana; não promover |
| FLOW-01 | Gatilho duplicado, bot ou comentário adversarial | Não executar comando vindo do evento; no máximo um candidato lógico ou escalada |
| FLOW-02 | Timeout/quota/evento perdido | `BLOCKED_EXTERNAL`; sem criação silenciosa de tarefas ou uso de API paga |
| TRANSFER-01 | Humano reproduz mudança pequena e autorizada por interface web | Registro dos dois PRs, manifesto conferido, HEAD e diff exato do principal |
| TRANSFER-02 | Base, conteúdo ou escopo divergem após transferência | Pausa, reavaliação; checks e CODEX-01 do sandbox jamais substituem os do principal |
| MERGE-01 | Tentativa sem READY/autorização humana posterior | Nenhum merge; ordem READY → autorização → merge respeitada |
| REV-01 | Conexão Work ainda pode escrever no principal, ou administração não isolada | `HUMAN_DECISION_REQUIRED` antes de ativar |
| COST-01 | Quota Work insuficiente, proposta de serviço pago | Bloquear sem compra nem fallback faturável |

**Não chamar esses testes de PASS antes de evidência real**. Os três canaries históricos da issue #8 demonstram utilidade, mas não demonstram isolamento de credenciais no piloto A.

## 5. Publicador autônomo: pesquisa futura, fora do piloto A

A linha experimental anterior, descrita na ADR-0015 rev.5 / SDD-0002 v0.5, propunha PostgreSQL, `ScopeGrantReceipt`, `trusted_publication_gate`, `PUBLISH_INTENT` e emissão de tokens. **Todos esses componentes deixam de ser requisitos/implementações do piloto A**; o histórico permanece no Git e no relatório da issue #10.

Qualquer retorno à publicação automática principal requer **nova decisão humana** e proposta arquitetural separada, incluindo: isolamento real da credencial; revogação de grant durante pausa pré-POST; quiescência verificável de operações em voo; token expirado/revogado; CI disparado por PR automatizado; custos e testes negativos. A ausência de garantia externa causa bloqueio, não relaxamento do contrato.

## 6. Gates de progressão

**M0 (agora):** revisão documental ADR-0015 rev.6 `Proposed` e SDD-0002 v0.6 `In Review` no PR #11; CI/pareceres e decisão humana de aprovação específicas ainda pendentes.

**M1 (depois de aprovação documental):** humano escolhe/confere sandbox, restringe instalação/conexão Work e registra resultado de teste negativo no principal; sem prova, não avançar.

**M2:** humano ativa canary Work sandbox de tarefa pequena e reversível; nenhuma mutação privilegiada no principal.

**M3:** humano promove manualmente candidato validado para PR draft principal; CI/governança/Codex no HEAD final do principal.

**M4:** decisão humana sobre READY/MERGE-01 de cada PR; avaliar métricas/limitações. Qualquer iniciativa futura de publisher automático terá projeto/gates próprios.

A documentação **não habilita nem comprova a execução dos marcos M1–M4**. A `PHASE-0-G` e a issue #16 permanecem sujeitas aos bloqueios e à governança vigente.
