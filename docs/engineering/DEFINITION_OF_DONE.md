# Definition of Done operacional

## 1. Objetivo

A Definition of Done, ou DoD, define o conjunto mínimo de evidências necessárias para declarar uma entrega concluída.

`DONE` não significa apenas código implementado, build concluído ou testes unitários verdes. Uma entrega só chega a `DONE` quando o lifecycle completo definido em `AGENTS.md` termina com `DONE_ALLOWED` no checkpoint `FINAL`.

## 2. Escopo

A DoD se aplica a:

- features;
- correções;
- refactors;
- mudanças arquiteturais;
- migrations;
- infraestrutura;
- automações;
- documentação de governança;
- releases;
- PRs administrativos de finalização, respeitando seu escopo especial.

Nem todo gate se aplica a toda entrega. A aplicabilidade é determinada pelo catálogo `CI_GATES.md`.

## 3. Estados de gate

Cada gate deve ter exatamente um estado:

- `PASS`: gate aplicável, executado e com evidência satisfatória;
- `FAIL`: gate aplicável e não atendido;
- `N/A`: condição de aplicabilidade ausente e justificativa registrada.

Regras:

1. `FAIL` em gate obrigatório bloqueia a transição correspondente.
2. `N/A` não é atalho. Precisa citar por que o gate não se aplica ao diff e ao escopo.
3. Ausência de automação não transforma gate em `N/A`. Quando aplicável, a evidência deve ser produzida manualmente até a automação existir.
4. Evidência deve ser rastreável ao PR, SHA, ambiente ou artefato pertinente.

## 4. DoD universal

### 4.1 Escopo e rastreabilidade

A entrega precisa:

- estar vinculada à SDD aprovada quando a mudança for significativa;
- estar alinhada aos ADRs `Accepted` aplicáveis;
- permanecer dentro do escopo aprovado;
- registrar mudanças materiais de escopo antes da implementação;
- manter handoff final coerente com o diff real.

### 4.2 Qualidade de implementação

Quando houver código:

- formatter e lint aplicáveis devem passar;
- análise estática/type checking aplicável deve passar;
- código morto, debug temporário e TODO bloqueante não podem permanecer sem registro;
- regras críticas de domínio devem permanecer no backend;
- identificadores seguem a política de linguagem.

### 4.3 Testes

A evidência de teste deve ser proporcional ao risco e incluir, quando aplicável:

- testes unitários para regras e unidades alteradas;
- testes de integração para banco, API, filas e integrações;
- testes de contrato para interfaces públicas;
- testes de regressão para bugs;
- testes E2E para jornadas críticas;
- cenários negativos de autorização;
- isolamento Tenant A x Tenant B em qualquer fluxo tenant-owned.

Cobertura percentual isolada não substitui cenários de risco.

### 4.4 Segurança e multi-tenancy

Toda entrega aplicável precisa demonstrar:

- nenhum secret commitado;
- `SEC-01` executado em todo PR, inclusive em alterações exclusivamente documentais;
- autorização server-side;
- isolamento de tenant preservado;
- nenhum lookup de recurso tenant-owned somente por ID sem contexto autorizado;
- validação de acesso negativo;
- dependências e superfície de exposição avaliadas;
- dados sensíveis ausentes de logs técnicos.

Finding de segurança não pode ser reclassificado silenciosamente para contornar gate.

### 4.5 Dados e migrations

Quando houver mudança de persistência:

- migration versionada;
- migration testada;
- constraints e índices coerentes com a regra de negócio;
- estratégia de compatibilidade definida;
- expand/contract usado quando rollback de imagem anterior depender do schema;
- migration destrutiva somente com gate humano explícito;
- backup/restauração ou rollback testado quando exigido pelo risco.

### 4.6 Observabilidade

Quando o comportamento executável mudar:

- logs estruturados suficientes para diagnóstico;
- `request_id` / `correlation_id` quando aplicável;
- erros tratados e capturados no mecanismo central;
- health/readiness preservados quando aplicável;
- novos failure modes possuem sinal observável;
- logs obedecem à allowlist aprovada;
- auditoria de negócio fica separada de logs técnicos.

### 4.7 Documentação

Antes do Codex Review final:

- SDD/ADR/documentação afetada deve estar atualizada;
- documentação não pode afirmar conclusão antes da evidência correspondente;
- `PROJECT_STATUS.md` pode registrar trabalho ativo no PR principal;
- a marcação final de conclusão ocorre somente no PR administrativo pós-merge;
- o estado de máquina de `PROJECT_STATUS.md` usa exclusivamente o bloco reservado `GOV:PROJECT_STATUS`; texto Markdown humano não é interpretado pelo GOV-02.

### 4.8 CI

- todo gate automatizado obrigatório e aplicável deve estar verde;
- checks devem corresponder ao SHA do PR quando a ferramenta permitir essa associação;
- falha intermitente não pode ser ignorada sem diagnóstico;
- rerun bem-sucedido precisa manter evidência e não pode esconder falha determinística.

### 4.9 Staging e validação humana

Staging é obrigatório quando a mudança tiver comportamento de produto ou operação que não possa ser validado adequadamente apenas em testes automatizados.

Quando aplicável:

- deploy de staging concluído;
- smoke test concluído;
- critérios de aceite validados;
- gate humano registrado.

Mudança puramente documental pode marcar staging como `N/A` com justificativa.

### 4.10 PR review loop

Depois que o PR estiver funcionalmente pronto para revisão, o Orquestrador executa `manage-pr-review-loop`.

O loop deve:

- observar os gates automatizados do HEAD atual;
- corrigir falhas tecnicamente corrigíveis dentro do escopo;
- solicitar Codex Review quando o HEAD estiver apto;
- classificar e tratar findings conforme severidade;
- invalidar revisão anterior após qualquer novo commit;
- repetir sem exigir instrução humana para passos operacionais;
- terminar somente em `READY_FOR_HUMAN_MERGE`, `HUMAN_DECISION_REQUIRED`, `BLOCKED_EXTERNAL` ou `LOOP_ESCALATION_REQUIRED`;
- rastrear tentativas por causa raiz e escalar somente quando a mesma causa persistir após 3 tentativas, houver pingue-pongue/deadlock ou ausência de progresso;
- usar `HUMAN_DECISION_REQUIRED` com precedência quando a próxima ação exigir mudança material de escopo aprovado, aceitação de risco ou outra decisão reservada ao humano;
- tratar `BLOCKED` de `PRE_MERGE` como resultado intermediário que precisa ser mapeado para `AUTO_REMEDIATION`, `HUMAN_DECISION_REQUIRED`, `BLOCKED_EXTERNAL` ou `LOOP_ESCALATION_REQUIRED` conforme a causa.

`READY_FOR_HUMAN_MERGE` não autoriza merge automático por si só. O estado é persistido no PR por comentário `ORCHESTRATOR_READY` com PR, HEAD e evidência de `MERGE_ALLOWED`. A autorização ordinária pode ser registrada pelo comentário manual legado `HUMAN_MERGE_AUTHORIZATION` ou pelo registro transparente `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` quando a decisão explícita ocorreu no canal interativo. O Orquestrador não pode inventar aprovação. O checkpoint pós-merge valida o mesmo PR/HEAD e a ordem `ready.created_at < authorization_record.created_at < merged_at`.

### 4.11 Contrato congelado de revisão

Antes do Codex final, o PR deve registrar `REVIEW_CONTRACT_FROZEN` com o HEAD, escopo, SDD/ADRs, gates, riscos residuais já aceitos e follow-ups conhecidos.

Após o congelamento:

- `CODEX-01` é o único review de IA obrigatório para merge;
- segunda opinião independente é diagnóstica e usada apenas em escalada;
- finding repetido já coberto por aceitação humana válida vira `ACCEPTED_RESIDUAL_RISK`, salvo evidência nova material;
- melhoria/hardening que não demonstra violação do contrato, defeito concreto, fail-open ou risco material vira `FOLLOW_UP`;
- mudança material do próprio contrato exige decisão humana e novo congelamento explícito.

### 4.12 Codex Review

Todo PR exige Codex Review.

Para o checkpoint `PRE_MERGE`:

- o SHA revisado pelo Codex deve ser exatamente o HEAD atual;
- findings devem estar tratados conforme a severidade;
- qualquer commit novo invalida o review anterior.

### 4.13 Fechamento

O encerramento segue:

`PR principal: manage-pr-review-loop -> PRE_MERGE -> MERGE_ALLOWED -> comentário ORCHESTRATOR_READY -> registro válido de autorização humana do mesmo PR/HEAD -> merge posterior -> POST_MERGE (valida timestamps) -> STATUS_FINALIZATION_ALLOWED`

`PR administrativo: manage-pr-review-loop -> PRE_MERGE -> MERGE_ALLOWED -> comentário ORCHESTRATOR_READY -> autorização humana específica OU envelope válido do Modo A -> merge -> FINAL -> DONE_ALLOWED`

O PR administrativo:

- altera exclusivamente `docs/PROJECT_STATUS.md`;
- não cria nova decisão;
- não implementa código;
- executa os gates automatizados aplicáveis, incluindo `GOV-01`, `GOV-02` e `SEC-01`;
- passa por Codex Review no HEAD final;
- executa `validate-definition-of-done` em `PRE_MERGE` antes de qualquer merge;
- só pode chegar a `READY_FOR_HUMAN_MERGE` depois de `MERGE_ALLOWED`;
- exige autorização humana específica para merge fora do envelope do Modo A;
- no Modo A, pode usar a autorização final do PR principal quando alterar exclusivamente `docs/PROJECT_STATUS.md`, não introduzir nova decisão e tiver GOV-01, GOV-02, SEC-01 e CODEX-01 satisfatórios;
- não gera outro PR de finalização.

## 4.14 Modo A

Quando `ORCHESTRATOR_MODE: A` estiver ativo:

- trabalho técnico reversível dentro do escopo aprovado deve continuar sem microautorizações;
- o runtime só pausa em gates humanos materiais ou estados terminais de bloqueio;
- aprovação de SDD continua obrigatória quando a SDD for exigida;
- autorização final do merge principal continua humana;
- decisões humanas dadas no canal interativo podem ser registradas pelo Orquestrador com origem explícita;
- o PR administrativo pode ser concluído sob o envelope da autorização final quando permanecer estritamente administrativo e todos os gates aplicáveis estiverem verdes;
- o piloto interativo não implica execução em background.

## 5. Evidência mínima no PR

O PR principal deve conter ou referenciar:

- SDD/ADR aplicáveis;
- lista de gates aplicáveis;
- resultado por ID de gate;
- comandos/checks executados;
- links para CI;
- evidência de testes;
- pareceres de QA/Security/Platform quando aplicáveis;
- staging/validação humana quando aplicáveis;
- Codex Review final do HEAD.

## 6. Exceções

Uma exceção nunca pode ser silenciosa.

Se um gate obrigatório não puder ser satisfeito:

1. interromper o avanço;
2. registrar motivo e risco;
3. classificar se o impedimento é temporário ou estrutural;
4. obter decisão humana quando a governança permitir;
5. criar ADR se a exceção alterar arquitetura aceita;
6. nunca declarar `PASS` para evidência inexistente.

## 7. Critério de DONE

Somente `DONE_ALLOWED`, emitido pela skill `validate-definition-of-done` no modo `FINAL`, autoriza o Orchestrator a declarar a entrega `DONE`.
