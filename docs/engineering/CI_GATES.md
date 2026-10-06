# Catálogo de gates de CI e release

## 1. Objetivo

Este catálogo atribui IDs estáveis aos gates usados pela Definition of Done.

Os IDs devem ser citados em PRs, handoffs, CI e evidências. A automação pode evoluir, mas o significado de um ID não deve mudar silenciosamente.

## 2. Classes

- **Sempre**: aplicável a todo PR, salvo regra administrativa explicitamente mais específica;
- **Condicional**: aplicável quando o diff satisfaz a condição descrita;
- **Release**: gate fora ou além do CI tradicional, necessário para progressão do lifecycle.

## 3. Gates

| ID | Gate | Classe | Aplicabilidade | Evidência mínima | Bloqueia |
| --- | --- | --- | --- | --- | --- |
| GOV-01 | Arquivos de governança obrigatórios | Sempre | Todo PR | workflow `governance` verde | PRE_MERGE |
| GOV-02 | Escopo do PR de finalização | Condicional | marcador `GOV:PHASE-*` transita para `completed` em relação ao merge-base | diff contém somente `docs/PROJECT_STATUS.md` | PRE_MERGE |
| DOC-01 | Documentação coerente | Sempre | Todo PR | revisão documental/handoff e links atualizados | PRE_MERGE |
| SCOPE-01 | Escopo aprovado | Sempre | Todo PR | SDD/issue/objetivo e diff coerentes | PRE_MERGE |
| CODE-01 | Formatter e lint | Condicional | código executável alterado | checks do stack verdes | PRE_MERGE |
| CODE-02 | Análise estática / type checking | Condicional | stack suportar análise estática | checks verdes | PRE_MERGE |
| TEST-01 | Testes unitários | Condicional | regra/unidade executável alterada | suite relevante verde | PRE_MERGE |
| TEST-02 | Testes de integração | Condicional | banco/API/fila/integração alterada | suite relevante verde | PRE_MERGE |
| TEST-03 | E2E / jornada crítica | Condicional | jornada crítica ou contrato ponta a ponta alterado | evidência E2E | PRE_MERGE |
| TENANT-01 | Isolamento multi-tenant | Condicional | dados/operação tenant-owned alterados | cenários Tenant A x Tenant B + review | PRE_MERGE |
| AUTH-01 | Autorização e acesso negativo | Condicional | auth/permission/recurso protegido alterado | testes positivos e negativos | PRE_MERGE |
| DATA-01 | Migrations e compatibilidade | Condicional | schema/persistência alterados | migration check + plano de rollback | PRE_MERGE |
| SEC-01 | Secret scan | Sempre | Todo PR, inclusive documentação | job `secret-scan` verde | PRE_MERGE |
| SEC-02 | Dependency/security scan | Condicional | dependências alteradas ou stack executável presente | scanner verde | PRE_MERGE |
| OBS-01 | Contrato de observabilidade | Condicional | comportamento executável/failure mode alterado | review + testes/log evidence | PRE_MERGE |
| BUILD-01 | Backend build/check | Condicional | backend Django existir e ser afetado | `django check`/build equivalente verde | PRE_MERGE |
| BUILD-02 | Flutter analyze/test/build | Condicional | frontend Flutter existir e ser afetado | analyze/test/build relevante verde | PRE_MERGE |
| CODEX-01 | Codex Review no HEAD final | Sempre | Todo PR | SHA revisado = HEAD e findings tratados | PRE_MERGE |
| STAGE-01 | Staging e smoke test | Condicional | mudança comportamental/operacional requer validação integrada | deploy + smoke evidence | PRE_MERGE |
| HUMAN-01 | Gate humano aplicável | Condicional | SDD, ADR, migration destrutiva, produção ou decisão sensível | registro humano verificável | checkpoint aplicável |
| MERGE-01 | Integração na main | Release | após `MERGE_ALLOWED` e `READY_FOR_HUMAN_MERGE` | comentário `ORCHESTRATOR_READY` + registro válido de autorização humana (`HUMAN_MERGE_AUTHORIZATION` ou `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`) do mesmo PR/HEAD + `ready.created_at < authorization_record.created_at < merged_at` + SHA verificado | POST_MERGE |
| STATUS-01 | Finalização administrativa | Release | após integração principal | PR exclusivo + Codex + `ORCHESTRATOR_READY` + autorização humana específica ou envelope válido do Modo A + merge + verificação do estado final | FINAL |

## 4. Gates automatizados na PHASE-0-F

A PHASE-0-F automatiza imediatamente:

### GOV-01

O workflow `.github/workflows/governance-gates.yml` valida a presença das fontes mínimas de governança.

### GOV-02

O GOV-02 não interpreta Markdown. O estado usado por máquina fica em um bloco reservado dentro de `docs/PROJECT_STATUS.md`:

```text
<!-- GOV:PROJECT_STATUS:BEGIN -->
<!-- GOV:PHASE-0-F:active -->
<!-- GOV:PHASE-0-G:planned -->
<!-- GOV:PROJECT_STATUS:END -->
```

Os únicos estados aceitos são `planned`, `active` e `completed`. Cada fase pode aparecer uma única vez. Marcador inválido, duplicado, removido ou fora do bloco reservado faz o gate falhar fechado.

O script `.github/scripts/check_project_status_finalization.py` compara o merge-base com o HEAD. Uma fase nova ou existente que passe para `completed` torna o GOV-02 aplicável; nessa condição, o diff deve conter exclusivamente `docs/PROJECT_STATUS.md`.

As transições são monotônicas: `planned -> active -> completed` pode avançar, com salto direto para `completed` permitido, mas `active -> planned` e qualquer regressão de `completed` são inválidas.

O merge-base continua sendo o referencial para impedir que avanço posterior da branch base absorva uma transição introduzida pelo PR. Falha de Git, bloco ausente no HEAD ou estado inválido termina em erro.

Durante a migração desta própria PHASE-0-F, o merge-base legado pode não possuir o bloco. Isso é aceito apenas como origem sem marcadores; o HEAD já deve conter um bloco válido.

O contrato possui testes unitários versionados em `.github/scripts/test_check_project_status_finalization.py`. Como o enforcement lê somente os marcadores reservados, headings, code fences, indentação, HTML ou outras construções Markdown não alteram o estado de governança.

### SEC-01

Todo PR executa secret scan automatizado sobre o histórico/diff disponível no checkout. Documentação não é exceção: README, Markdown, YAML e qualquer outro arquivo versionado podem conter credenciais acidentalmente.

Esses gates funcionam antes do bootstrap tecnológico.

## 5. Gates ativados na PHASE-0-G

Quando Django, Flutter, PostgreSQL e Docker forem introduzidos, o mesmo marco deve materializar os checks aplicáveis para:

- CODE-01;
- CODE-02;
- TEST-01;
- TEST-02;
- SEC-02;
- BUILD-01;
- BUILD-02;
- DATA-01, assim que existir primeira migration;
- OBS-01, assim que existir primeiro serviço executável.

TENANT-01 e AUTH-01 tornam-se obrigatórios assim que existir o primeiro fluxo tenant-owned/protegido.

A ausência atual desses stacks permite `N/A` apenas enquanto a condição de aplicabilidade não existir.

## 6. Review loop operacional

A skill `manage-pr-review-loop` é o motor que conduz os gates existentes até o checkpoint `PRE_MERGE`. Ela não cria um gate adicional, evitando dependência circular com `validate-definition-of-done`.

Estados intermediários como `WAITING_CODEX`, `CI_VALIDATION` e `AUTO_REMEDIATION` não são gates humanos.

O loop pode corrigir automaticamente findings de qualquer prioridade quando existir correção segura e objetiva dentro do escopo aprovado. A severidade continua sendo preservada e determina o bloqueio enquanto a correção não estiver validada.

O loop não pode aceitar risco em nome do humano. Quando a alternativa à correção for aceitar risco, o estado correto é `HUMAN_DECISION_REQUIRED`. A autorização ordinária de merge usa o protocolo auditável `ORCHESTRATOR_READY` -> registro de autorização humana -> merge, para o mesmo PR/HEAD, e o checkpoint seguinte valida os timestamps. O registro pode ser o comentário manual legado `HUMAN_MERGE_AUTHORIZATION` ou `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` quando uma decisão humana explícita tiver sido dada no canal interativo.

Não existe limite global fixo de ciclos por PR. O anti-loop é controlado por causa raiz.

O Orquestrador deve rastrear cada família de finding e pode executar até 3 tentativas automáticas para a mesma causa raiz.

Escalar imediatamente para `LOOP_ESCALATION_REQUIRED` quando:

- a mesma causa raiz reaparecer após 3 tentativas;
- uma correção reintroduzir repetidamente finding já resolvido;
- duas correções entrarem em pingue-pongue;
- houver indício de deadlock entre gates;
- não houver progresso mensurável.

Findings novos e independentes permanecem em `AUTO_REMEDIATION` e não herdam o contador de outra causa.

Quando `validate-definition-of-done` retornar `BLOCKED` em `PRE_MERGE`, o Orquestrador deve classificar a causa: remediação técnica volta a `AUTO_REMEDIATION`; decisão excepcional vira `HUMAN_DECISION_REQUIRED`; bloqueio externo vira `BLOCKED_EXTERNAL`; impasse anti-loop vira `LOOP_ESCALATION_REQUIRED`.

Quando a correção exigir mudança material de escopo, aceitação de risco ou outra decisão reservada ao humano, o estado correto é `HUMAN_DECISION_REQUIRED`; esse estado tem precedência sobre `LOOP_ESCALATION_REQUIRED`.

### Contrato congelado do review

Antes do `CODEX-01` final, registrar `REVIEW_CONTRACT_FROZEN` no PR.

Findings depois desse ponto são classificados em:

- `BUG_TO_FIX`: defeito concreto/violação do contrato atual;
- `HUMAN_DECISION_REQUIRED`: risco, exceção ou mudança material reservada ao humano;
- `ACCEPTED_RESIDUAL_RISK`: causa já coberta por aceitação humana válida;
- `FOLLOW_UP`: melhoria/hardening não bloqueante para o contrato atual;
- `BLOCKED_EXTERNAL`: dependência externa.

Risco aceito só volta a bloquear se surgir evidência nova material ou se o caso sair do escopo da aceitação.

Codex é o gate oficial. Segunda opinião independente não é gate paralelo.

## 6.1 Modo A

No `ORCHESTRATOR_MODE: A`:

- CI, Codex, correções técnicas e novas rodadas continuam automaticamente enquanto houver progresso;
- `READY_FOR_HUMAN_MERGE` pausa para autorização humana final do PR principal;
- a autorização humana pode ser registrada pelo Orquestrador quando tiver sido dada explicitamente no canal interativo, com origem declarada;
- `STATUS-01` pode usar o envelope dessa autorização final para o PR administrativo quando o diff for exclusivamente `docs/PROJECT_STATUS.md`, não houver nova decisão e GOV-01, GOV-02, SEC-01 e CODEX-01 estiverem satisfatórios;
- qualquer desvio do envelope retorna para `HUMAN_DECISION_REQUIRED`.

## 7. Regras de bloqueio

1. Gate obrigatório aplicável em `FAIL` bloqueia.
2. Gate obrigatório sem evidência bloqueia.
3. Check automatizado obrigatório cancelado, skipped indevidamente ou ausente não conta como `PASS`.
4. `N/A` exige justificativa.
5. Novo commit depois de CODEX-01 invalida CODEX-01.
6. Finding bloqueante mantém o gate correspondente em `FAIL` até tratamento.
7. Branch protection indisponível não muda nenhuma regra deste catálogo.

## 8. Evolução do catálogo

Novo gate:

- recebe novo ID;
- documenta aplicabilidade, evidência e checkpoint;
- atualiza PR template e skill quando necessário.

Mudança material no significado de gate existente deve ser tratada como alteração de governança e não como simples renomeação.
