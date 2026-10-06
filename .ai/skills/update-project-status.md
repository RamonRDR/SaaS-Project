# Skill `update-project-status`

## Missão

Manter `docs/PROJECT_STATUS.md` fiel ao estado real do repositório e das entregas sem antecipar conclusões e sem criar ciclos de encerramento.

## Quando usar

Usar em dois modos:

- `WORKING_STATE`: ao iniciar um marco ou registrar mudanças reais durante o trabalho;
- `POST_MERGE_FINALIZATION`: depois que a entrega principal foi mergeada e seu checkpoint `POST_MERGE` autorizou a persistência do estado concluído.

## Agentes autorizados

- Docs & Release;
- Orchestrator / Tech Lead.

## Entradas obrigatórias

### WORKING_STATE

- estado real da branch;
- HEAD relevante;
- PRs relacionados;
- trabalho ativo;
- decisões estabelecidas;
- próximos passos aprovados.

### POST_MERGE_FINALIZATION

- evidência do `PRE_MERGE` da entrega principal com `MERGE_ALLOWED`;
- evidência do merge da entrega principal;
- evidência de verificação pós-merge;
- resultado `STATUS_FINALIZATION_ALLOWED` do checkpoint `POST_MERGE`;
- PR e commit principal relacionados;
- estado atual da branch alvo;
- próximo estado real do projeto.

## Procedimento

### WORKING_STATE

1. confirmar branch e HEAD;
2. confirmar estado dos PRs relacionados;
3. atualizar fase e marco atual sem antecipar eventos futuros;
4. registrar trabalho ativo real;
5. registrar decisões já estabelecidas;
6. registrar limitações e itens ainda não iniciados;
7. atualizar próximos passos;
8. revisar consistência com SDDs e ADRs.

### POST_MERGE_FINALIZATION

1. confirmar que a entrega principal já foi mergeada;
2. confirmar que a verificação pós-merge foi concluída;
3. confirmar `STATUS_FINALIZATION_ALLOWED`;
4. criar branch exclusiva a partir da branch alvo já atualizada;
5. criar um PR de finalização de status;
6. permitir nesse PR somente alteração de `docs/PROJECT_STATUS.md`;
7. registrar a entrega principal como concluída, com referência ao PR/merge relevante quando aplicável;
8. registrar o próximo estado real sem inventar trabalho ainda não iniciado;
9. entregar o PR administrativo ao Orquestrador para execução de `manage-pr-review-loop`;
10. exigir CI aplicável verde, incluindo `GOV-01`, `GOV-02` e `SEC-01`;
11. exigir Codex Review do HEAD final desse PR de finalização;
12. resolver findings bloqueantes conforme a política dentro do review loop;
13. executar `validate-definition-of-done` em `PRE_MERGE` para o PR administrativo corrente;
14. exigir `MERGE_ALLOWED` antes de `READY_FOR_HUMAN_MERGE`;
15. confirmar comentário `ORCHESTRATOR_READY` do PR administrativo com PR/HEAD e timestamp;
16. confirmar autorização administrativa válida: autorização humana específica ou, no Modo A, envelope da autorização final do PR principal conforme `.ai/runtime/MODE_A.md`;
17. fora do envelope do Modo A, mergear o PR de finalização somente quando `ready.created_at < authorization_record.created_at`; dentro do envelope, confirmar que o PR é estritamente administrativo e todos os gates exigidos estão verdes;
18. verificar na branch alvo que `PROJECT_STATUS.md` contém o estado persistido;
19. devolver ao Orquestrador as evidências do `PRE_MERGE`, `MERGE_ALLOWED`, comentário `ORCHESTRATOR_READY`, autorização aplicável e merge para o checkpoint `FINAL`.

## PR de finalização de status

O PR de `POST_MERGE_FINALIZATION` é um artefato administrativo do lifecycle da entrega principal, não uma nova entrega de produto ou engenharia.

Por isso:

- não exige uma nova SDD;
- não exige novo ADR;
- não exige um segundo PR de finalização para registrar a própria conclusão;
- continua exigindo o `manage-pr-review-loop` completo, incluindo CI, Codex Review no HEAD exato e `PRE_MERGE` com `MERGE_ALLOWED`;
- só pode alterar `docs/PROJECT_STATUS.md`;
- no Modo A, pode ser mergeado sob o envelope da autorização final do PR principal se não introduzir nova decisão e GOV-01, GOV-02, SEC-01 e CODEX-01 estiverem satisfatórios;
- qualquer outra alteração descaracteriza o PR de finalização e obriga retorno ao fluxo normal.

Essa regra encerra a cadeia e impede recursão de PRs de status.

## Outputs esperados

- `docs/PROJECT_STATUS.md` coerente com o estado real;
- no modo `WORKING_STATE`, estado intermediário fiel;
- no modo `POST_MERGE_FINALIZATION`, PR de finalização com review loop concluído, `MERGE_ALLOWED`, `READY_FOR_HUMAN_MERGE`, autorização administrativa válida (específica ou coberta pelo envelope do Modo A), merge e verificação;
- evidências de conclusão rastreáveis;
- próximos passos claros.

## Não faz

- não altera história para esconder pendência;
- não declara feature, entrega ou marco concluído antes do merge e da verificação pós-merge da entrega principal;
- não cria decisão arquitetural;
- não transforma estado esperado em estado já realizado;
- não usa o PR de finalização para código, configuração, SDD, ADR ou documentação arquitetural.

## Condições de parada

Parar quando:

- o estado real não puder ser confirmado;
- houver conflito entre repositório e documentação;
- a entrega principal não possuir evidência de merge;
- a entrega principal não possuir verificação pós-merge;
- o checkpoint `POST_MERGE` não tiver emitido `STATUS_FINALIZATION_ALLOWED`;
- o PR de finalização contiver alteração fora de `docs/PROJECT_STATUS.md`;
- o Codex Review do PR de finalização não corresponder ao HEAD atual;
- o `PRE_MERGE` do PR administrativo não tiver emitido `MERGE_ALLOWED`;
- o PR administrativo não estiver em `READY_FOR_HUMAN_MERGE` antes da autorização humana;
- faltar autorização administrativa válida, seja específica ou coberta pelo envelope do Modo A;
- existir finding bloqueante sem tratamento.

## Gates humanos

Mudanças que representem aceitação de marco, risco ou decisão pendente devem refletir aprovação humana real.

O PR de finalização não cria aprovação nova; ele apenas persiste um estado já comprovado pelos gates da entrega principal.

## Critério de conclusão

- `WORKING_STATE`: termina quando `PROJECT_STATUS.md` representa fielmente o estado intermediário;
- `POST_MERGE_FINALIZATION`: termina quando o PR exclusivo de status concluiu o `manage-pr-review-loop`, recebeu `MERGE_ALLOWED`, chegou a `READY_FOR_HUMAN_MERGE`, possui autorização administrativa válida (específica ou envelope do Modo A), foi mergeado e verificado na branch alvo.
