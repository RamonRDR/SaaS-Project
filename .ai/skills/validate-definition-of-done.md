# Skill `validate-definition-of-done`

## Missão

Validar de forma rastreável os gates de uma entrega em três checkpoints distintos:

- `PRE_MERGE`: decidir se o pull request corrente em validação, principal ou administrativo de finalização, está apto para merge;
- `POST_MERGE`: verificar a integração da entrega principal e autorizar a persistência do estado concluído;
- `FINAL`: validar a finalização documental e decidir se a entrega está apta para DONE.

A separação impede dependências circulares entre review, merge, persistência de status e DONE.

## Fontes operacionais obrigatórias

Esta skill executa o contrato definido em:

- `docs/engineering/DEFINITION_OF_DONE.md`;
- `docs/engineering/CI_GATES.md`;
- `AGENTS.md`.

O catálogo de gates possui IDs estáveis. A validação deve registrar, para cada gate relevante: `PASS`, `FAIL` ou `N/A` com justificativa.

## Quando usar

Usar:

1. imediatamente antes do merge de qualquer PR governado pelo lifecycle, principal ou administrativo de finalização, no modo `PRE_MERGE`;
2. depois do merge e da verificação da branch alvo, no modo `POST_MERGE`;
3. depois do merge e da verificação do PR exclusivo de finalização de status, no modo `FINAL`.

## Agentes autorizados

- Orchestrator / Tech Lead;
- Docs & Release, para apoiar os checklists documentais.

A decisão final de transição entre estados é coordenada pelo Orquestrador.

## Entradas obrigatórias

### Comuns

- modo de validação;
- SDD final e escopo aprovado da entrega principal;
- handoff final;
- ADRs aplicáveis;
- resultados de testes;
- parecer de QA;
- pareceres de Security e Platform quando aplicáveis;
- resultado do CI;
- validações humanas;
- branch alvo;
- matriz dos gates aplicáveis conforme `docs/engineering/CI_GATES.md`;
- evidências associadas a cada gate obrigatório;
- justificativa para cada gate marcado como `N/A`.

### PRE_MERGE

- identidade e tipo do PR corrente em validação (`principal` ou `administrativo de finalização`);
- diff atual do PR corrente;
- SHA atual do HEAD do PR corrente;
- SHA explicitamente revisado pelo Codex;
- resultado do Codex Review associado a esse SHA;
- situação dos findings;
- documentação final pré-merge;
- evidência do `manage-pr-review-loop` de que CI aplicável está verde, CODEX-01 corresponde ao HEAD atual e não há finding bloqueante pendente.

### POST_MERGE

- evidência formal do `PRE_MERGE`;
- decisão `MERGE_ALLOWED`;
- URL/ID, autor e `created_at` do comentário canônico `ORCHESTRATOR_READY` para o PR/HEAD principal;
- URL/ID, autor e `created_at` do registro de autorização humana aplicável (`HUMAN_MERGE_AUTHORIZATION` ou `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`) para o mesmo PR/HEAD;
- evidência de que o registro de autorização foi criado **depois** de `ORCHESTRATOR_READY` e **antes** do merge principal;
- SHA do HEAD validado;
- SHA revisado pelo Codex;
- resultado do Codex Review;
- situação dos findings no momento de `MERGE_ALLOWED`;
- evidência do merge do PR principal;
- SHA efetivamente integrado à branch alvo;
- evidência da verificação pós-merge.

### FINAL

- resultado `STATUS_FINALIZATION_ALLOWED` do `POST_MERGE`;
- PR exclusivo de finalização de status;
- evidência de que esse PR alterou somente `docs/PROJECT_STATUS.md`;
- evidência do `manage-pr-review-loop` do PR administrativo;
- evidência formal do `PRE_MERGE` administrativo;
- decisão `MERGE_ALLOWED` emitida para o HEAD final do PR administrativo;
- URL/ID, autor e `created_at` do comentário canônico `ORCHESTRATOR_READY` do PR administrativo;
- evidência de autorização administrativa válida: registro específico para o PR final ou envelope do Modo A;
- quando houver registro específico, URL/ID, autor, `created_at` e ordem temporal válida; quando houver envelope, evidência de que todas as condições administrativas do Modo A foram satisfeitas;
- SHA final desse PR;
- SHA revisado pelo Codex nesse PR;
- resultado do Codex Review e situação dos findings;
- evidência de merge do PR de finalização;
- estado atual de `docs/PROJECT_STATUS.md` na branch alvo.

## Procedimento

### Validações comuns

1. verificar atendimento da SDD;
2. comparar diff e handoff final com o escopo aprovado;
3. bloquear mudanças materiais fora do escopo não aprovadas;
4. verificar ADRs necessários e aceitos;
5. verificar testes;
6. verificar QA;
7. verificar Security Review aplicável;
8. verificar Platform/Observability Review aplicável;
9. verificar CI;
10. verificar staging quando exigido;
11. verificar gates humanos conforme o modo atual: em `PRE_MERGE`, somente gates que precisam estar concluídos antes de `MERGE_ALLOWED`; em `POST_MERGE`, também exigir evidência da autorização ordinária do merge principal; em `FINAL`, exigir a autorização ordinária do merge administrativo;
12. registrar pendências e itens não aplicáveis com justificativa;
13. construir a matriz de evidências por ID de gate;
14. confirmar que todo gate obrigatório aplicável está em `PASS`;
15. confirmar que nenhum `N/A` foi usado para contornar uma condição de aplicabilidade existente.

### PRE_MERGE

O `PRE_MERGE` é chamado pelo `manage-pr-review-loop` somente depois que os estados operacionais de CI e Codex estiverem prontos para validação, tanto no PR principal quanto no PR administrativo de finalização. Ele ocorre **antes** de `READY_FOR_HUMAN_MERGE`; somente `MERGE_ALLOWED` autoriza o loop a emitir esse estado.

1. confirmar que o SHA revisado pelo Codex é exatamente igual ao HEAD atual do PR corrente em validação;
2. verificar o resultado do Codex Review desse SHA;
3. verificar o tratamento dos findings conforme a política de severidade;
4. confirmar que não há gate bloqueante pendente;
5. emitir `MERGE_ALLOWED` ou `BLOCKED`.

Qualquer novo commit no PR corrente em validação invalida o gate anterior do Codex.

### POST_MERGE

1. confirmar evidência de `PRE_MERGE` com `MERGE_ALLOWED`;
2. confirmar o comentário `ORCHESTRATOR_READY`, seu PR/HEAD, `created_at` e evidência de `MERGE_ALLOWED`;
3. confirmar um registro de autorização humana válido para o mesmo PR/HEAD: comentário manual legado `HUMAN_MERGE_AUTHORIZATION` ou registro transparente `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` produzido somente após decisão humana explícita no canal interativo;
4. confirmar `ready.created_at < authorization_record.created_at < merged_at`;
5. confirmar que o SHA revisado pelo Codex é igual ao HEAD aprovado;
6. confirmar que o HEAD aprovado é o mesmo HEAD de origem do PR efetivamente mergeado;
7. confirmar que os findings bloqueantes estavam tratados quando `MERGE_ALLOWED` foi emitido;
8. confirmar merge na branch alvo;
9. verificar o commit integrado;
10. verificar o estado pós-merge;
11. confirmar ausência de divergência inesperada entre conteúdo aprovado e integrado;
12. emitir `STATUS_FINALIZATION_ALLOWED` ou `BLOCKED`.

O modo `POST_MERGE` não declara DONE e não exige que `PROJECT_STATUS.md` já marque a entrega como concluída. Ele autoriza a criação do PR exclusivo de finalização de status.

### FINAL

1. confirmar `STATUS_FINALIZATION_ALLOWED`;
2. confirmar que o PR de finalização alterou somente `docs/PROJECT_STATUS.md`;
3. confirmar evidência de que o PR administrativo concluiu `manage-pr-review-loop`;
4. confirmar evidência do `PRE_MERGE` administrativo com `MERGE_ALLOWED`;
5. confirmar que o `MERGE_ALLOWED` corresponde exatamente ao HEAD final do PR administrativo;
6. confirmar o comentário `ORCHESTRATOR_READY` do PR administrativo, seu PR/HEAD, `created_at` e evidência de `MERGE_ALLOWED`;
7. confirmar autorização administrativa válida: registro humano específico para o PR administrativo ou, no `ORCHESTRATOR_MODE: A`, envelope da autorização final do PR principal quando o PR administrativo alterar exclusivamente `docs/PROJECT_STATUS.md`, não introduzir nova decisão e tiver GOV-01, GOV-02, SEC-01 e CODEX-01 satisfatórios;
8. quando houver autorização específica do PR administrativo, confirmar `ready.created_at < authorization_record.created_at < merged_at`; quando houver envelope do Modo A, confirmar que a autorização final do PR principal antecede o merge principal e que o PR administrativo foi criado somente depois de `STATUS_FINALIZATION_ALLOWED`;
9. confirmar que o SHA revisado pelo Codex é exatamente igual ao HEAD final desse PR;
10. verificar que não há finding bloqueante sem tratamento;
11. confirmar que o PR de finalização foi mergeado;
12. verificar na branch alvo que `PROJECT_STATUS.md` marca corretamente a entrega principal como concluída;
13. confirmar que o PR de finalização não introduziu decisão, código ou mudança de escopo;
14. emitir `DONE_ALLOWED` ou `BLOCKED`.

## Outputs esperados

- modo executado;
- checklist rastreável;
- bloqueios pendentes;
- `PRE_MERGE`: `MERGE_ALLOWED` ou `BLOCKED`;
- `POST_MERGE`: `STATUS_FINALIZATION_ALLOWED` ou `BLOCKED`;
- `FINAL`: `DONE_ALLOWED` ou `BLOCKED`;
- SHAs e PRs relevantes registrados;
- matriz de gates com ID, aplicabilidade, status e evidência;
- justificativas de todos os itens `N/A`.

## Não faz

- não considera gate pendente como concluído;
- não inventa evidência;
- não substitui aprovações especializadas;
- não reutiliza Codex Review de SHA diferente do HEAD correspondente;
- não declara DONE em `PRE_MERGE` ou `POST_MERGE`;
- não trata o PR de finalização como veículo para qualquer mudança além do status.

## Condições de parada

Bloquear quando:

- houver mudança material fora do escopo aprovado;
- faltar evidência obrigatória;
- existir gate humano **pré-merge** pendente;
- existir gate obrigatório aplicável sem evidência;
- existir gate automatizado obrigatório em falha;
- um gate tiver sido marcado como `N/A` sem justificativa válida;
- houver finding bloqueante sem tratamento;
- em `PRE_MERGE`, o SHA revisado pelo Codex diferir do HEAD do PR corrente em validação;
- em `POST_MERGE`, não existir `MERGE_ALLOWED` válido;
- em `POST_MERGE`, faltar comentário `ORCHESTRATOR_READY` válido para o PR/HEAD principal;
- em `POST_MERGE`, faltar registro de autorização humana válido para o mesmo PR/HEAD;
- em `POST_MERGE`, não for demonstrável `ready.created_at < authorization_record.created_at < merged_at`;
- em `POST_MERGE`, o HEAD aprovado não corresponder ao efetivamente mergeado;
- em `FINAL`, o PR de finalização alterar arquivo diferente de `docs/PROJECT_STATUS.md`;
- em `FINAL`, não existir evidência de `PRE_MERGE` administrativo com `MERGE_ALLOWED` para o HEAD final;
- em `FINAL`, faltar comentário `ORCHESTRATOR_READY` válido para o PR/HEAD administrativo;
- em `FINAL`, faltar autorização administrativa válida, seja específica do PR final ou coberta pelo envelope do Modo A;
- em `FINAL`, quando não houver envelope válido do Modo A, não for demonstrável `ready.created_at < authorization_record.created_at < merged_at`;
- em `FINAL`, o review do Codex não corresponder ao HEAD final do PR de finalização;
- em `FINAL`, o status final não estiver efetivamente presente na branch alvo.

## Gates humanos

Para `PRE_MERGE`, somente gates humanos que precisam estar concluídos **antes** de `MERGE_ALLOWED` são bloqueantes.

Exemplos de gates humanos pré-merge:

- SDD/ADR pendente;
- aceitação de risco;
- mudança material de escopo;
- migration destrutiva;
- breaking change inevitável;
- exceção de gate;
- decisão sensível de auth/tenant isolation;
- fornecedor externo sensível;
- operação irreversível.

A autorização ordinária de merge **não é gate de entrada do PRE_MERGE**.

`READY_FOR_HUMAN_MERGE` deve ser persistido em comentário `ORCHESTRATOR_READY` no PR, cujo `created_at` do GitHub é a evidência temporal.

A autorização humana válida pode ser registrada de duas formas:

1. comentário manual legado `HUMAN_MERGE_AUTHORIZATION` para o mesmo PR/HEAD;
2. comentário `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` publicado pelo Orquestrador depois de uma decisão humana explícita no canal interativo.

No segundo formato, o comentário deve declarar que é um registro do Orquestrador e não alegar autoria manual humana no GitHub. O Orquestrador continua proibido de inventar, inferir ou fabricar aprovação.

### Origem e identidade da autorização

Enquanto agentes e responsável humano compartilharem a mesma identidade GitHub, a API não prova quem originou uma decisão. Por isso, o registro deve ser semanticamente honesto sobre sua origem.

A aceitação de risco da PHASE-0-F em **HUMAN-RISK-ACCEPTANCE #5942843849** permanece como histórico da limitação anterior e não deve ser reinterpretada como prova técnica de identidade.

Quando os agentes passarem a publicar por identidade própria, a validação pode exigir separação técnica adicional de autores sem alterar o significado do gate humano.

Depois do merge principal, `POST_MERGE` deve demonstrar `ready.created_at < authorization_record.created_at < merged_at`.

No Modo A, a autorização final do PR principal pode cobrir o PR administrativo de finalização quando o envelope definido em `.ai/runtime/MODE_A.md` for satisfeito. Fora desse envelope, o PR administrativo exige autorização humana específica.

O PR de finalização não cria novo gate de produto; ele apenas registra o estado autorizado pelo processo.

## Critério de conclusão

- `PRE_MERGE`: `MERGE_ALLOWED` ou `BLOCKED`;
- `POST_MERGE`: `STATUS_FINALIZATION_ALLOWED` ou `BLOCKED`;
- `FINAL`: `DONE_ALLOWED` ou `BLOCKED`.

Somente `DONE_ALLOWED` no modo `FINAL` permite ao Orquestrador declarar a entrega DONE.
