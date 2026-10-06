# Skill `manage-pr-review-loop`

## Missão

Gerenciar autonomamente o ciclo operacional de um pull request desde o primeiro HEAD pronto para revisão até um estado terminal, sem exigir que o responsável humano solicite manualmente verificações de CI, consulta ao Codex, correção de findings ou nova revisão.

A skill não elimina gates humanos. Ela elimina intervenção humana em trabalho operacional repetitivo.

## Quando usar

Usar em todo PR principal depois que:

- o escopo estiver aprovado;
- implementação/documentação mutável prevista para a rodada estiver pronta;
- reviews especializados aplicáveis tiverem sido executados ou explicitamente marcados como não aplicáveis;
- o PR existir e possuir HEAD verificável.

Deve ser usada também em todo PR administrativo de finalização, respeitando seu escopo exclusivo.

## Agentes autorizados

- Orchestrator / Tech Lead.

Especialistas podem receber handoffs de correção, mas somente o Orquestrador controla o estado global do loop.

## Entradas obrigatórias

- número do PR;
- branch base e branch head;
- HEAD atual;
- escopo aprovado;
- SDD/ADRs aplicáveis;
- matriz de gates aplicáveis;
- resultados de reviews especializados;
- política de severidade do Codex;
- histórico de causas raiz e número de tentativas de remediação por causa.

## Estados

### Intermediários

- `CI_VALIDATION`
- `CODEX_REVIEW_REQUESTED`
- `WAITING_CODEX`
- `FINDINGS_RECEIVED`
- `AUTO_REMEDIATION`

### Terminais

- `READY_FOR_HUMAN_MERGE`
- `HUMAN_DECISION_REQUIRED`
- `BLOCKED_EXTERNAL`
- `LOOP_ESCALATION_REQUIRED`

Estados intermediários não autorizam devolução do fluxo ao responsável humano apenas para pedir continuidade. O resultado `BLOCKED` de `validate-definition-of-done` também não é estado terminal por si só; ele deve ser mapeado para remediação ou para um dos estados terminais definidos nesta skill.

## Procedimento

1. confirmar PR, base, HEAD e escopo;
2. entrar em `CI_VALIDATION`;
3. verificar todos os gates automatizados aplicáveis ao HEAD;
4. se um gate falhar por causa tecnicamente corrigível dentro do escopo, executar ou delegar a correção;
5. após correção, registrar novo HEAD, incrementar ciclo de remediação e retornar a `CI_VALIDATION`;
6. quando CI aplicável estiver verde, solicitar Codex Review do HEAD atual;
7. entrar em `WAITING_CODEX`;
8. consultar o resultado do Codex quando disponível, sem exigir prompt humano de continuidade;
9. se houver findings, entrar em `FINDINGS_RECEIVED` e preservar a severidade atribuída;
10. classificar cada finding em:
   - `BUG_TO_FIX`: defeito corrigível dentro do escopo;
   - `HUMAN_DECISION_REQUIRED`: exige decisão humana;
   - `ACCEPTED_RESIDUAL_RISK`: mesma causa coberta por aceitação humana válida e ainda dentro do escopo dessa aceitação;
   - `FOLLOW_UP`: melhoria/hardening fora dos critérios bloqueantes do contrato congelado;
   - `BLOCKED_EXTERNAL`: bloqueio externo;
11. para `BUG_TO_FIX`, entrar em `AUTO_REMEDIATION`, encaminhar ao especialista apropriado quando necessário e aplicar a correção; `ACCEPTED_RESIDUAL_RISK` e `FOLLOW_UP` devem ser registrados com evidência/justificativa e não geram commit por si só;
12. responder/resolver threads somente depois da correção correspondente estar presente;
13. qualquer novo commit invalida o Codex Review anterior;
14. retornar a `CI_VALIDATION` e repetir;
15. quando o HEAD atual tiver CI aplicável verde, Codex Review válido para o mesmo SHA e zero finding bloqueante, executar `validate-definition-of-done` em `PRE_MERGE`;
16. se `PRE_MERGE` emitir `MERGE_ALLOWED`, publicar no PR um comentário canônico de evidência e então emitir `READY_FOR_HUMAN_MERGE`:

```text
ORCHESTRATOR_READY
PR: <número>
HEAD: <sha>
MERGE_ALLOWED_EVIDENCE: <link ou identificador>
```

O `created_at` desse comentário no GitHub é o instante auditável de entrada em `READY_FOR_HUMAN_MERGE`;
17. se `PRE_MERGE` emitir `BLOCKED`, classificar a causa e fazer uma transição determinística:
   - causa tecnicamente corrigível dentro do escopo -> `AUTO_REMEDIATION` e depois `CI_VALIDATION`;
   - decisão excepcional humana -> `HUMAN_DECISION_REQUIRED`;
   - dependência externa não resolvível pelo repositório -> `BLOCKED_EXTERNAL`;
   - 3 falhas da mesma causa, pingue-pongue, deadlock ou ausência de progresso -> `LOOP_ESCALATION_REQUIRED`;
18. após `READY_FOR_HUMAN_MERGE`, aplicar a regra de autorização conforme o tipo de PR:

   - **PR principal:** aguardar autorização humana explícita para o mesmo PR/HEAD. Ela pode ser registrada pelo comentário manual legado `HUMAN_MERGE_AUTHORIZATION` ou, no Modo A, por `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` depois de decisão humana explícita no canal interativo. O registro deve ter `created_at` posterior a `ORCHESTRATOR_READY`, referenciar o mesmo PR/HEAD e anteceder o merge.
   - **PR administrativo de finalização:** aceitar autorização humana específica para o mesmo PR/HEAD em qualquer modo. No Modo A, essa autorização específica é uma alternativa válida ao `MODE_A_ADMIN_ENVELOPE`. Se não existir autorização específica, o envelope pode ser usado quando o PR altera exclusivamente `docs/PROJECT_STATUS.md`, não introduz nova decisão, possui GOV-01/GOV-02/SEC-01/CODEX-01 satisfatórios e referencia a autorização final válida do PR principal. Se não houver autorização específica nem envelope válido, retornar `HUMAN_DECISION_REQUIRED`.

O Orquestrador é proibido de fabricar aprovação e também é proibido de emitir o marcador legado `HUMAN_MERGE_AUTHORIZATION`;
19. parar e apresentar ao responsável humano PR, HEAD, gates, Codex e evidências apenas quando alcançar um estado terminal.

## Contrato congelado de revisão

Antes do review final que pretende satisfazer `CODEX-01`, o Orquestrador deve registrar no PR um `REVIEW_CONTRACT_FROZEN` contendo:

- PR e HEAD;
- escopo aprovado;
- SDD/ADRs aplicáveis;
- versão vigente de DoD/gates;
- riscos residuais já aceitos e seus registros;
- findings já classificados como `FOLLOW_UP`.

Depois desse registro, reviewers avaliam a entrega contra esse contrato congelado.

Um finding só é bloqueante quando:

- demonstra violação do contrato congelado;
- demonstra defeito concreto de segurança, integridade ou comportamento fail-open dentro do escopo atual;
- demonstra que um risco residual aceito mudou materialmente ou que a aceitação não cobre o caso encontrado.

Melhoria, preferência de hardening ou ampliação de governança que não satisfaça uma dessas condições deve ser classificada como `FOLLOW_UP` e não reabrir o gate atual.

Risco residual explicitamente aceito pelo humano não volta a bloquear pela mesma causa raiz sem evidência nova material. O registro de aceitação precisa ser citado no tratamento do finding.

`CODEX-01` é o reviewer oficial obrigatório do PR. Segunda opinião independente, como Claude Code, é mecanismo de escalada/diagnóstico e não cria um segundo gate obrigatório nem reinicia o contrato indefinidamente.

## Política de remediação automática

Pode corrigir automaticamente, inclusive P0/P1/P2, quando:

- a causa e a correção forem objetivas;
- a mudança estiver dentro do escopo já aprovado;
- nenhuma decisão humana reservada for tomada;
- nenhuma nova arquitetura material for introduzida;
- nenhuma exceção a gate for necessária.

Se um finding puder ser corrigido, o Orquestrador deve preferir corrigir em vez de pedir ao humano para aceitar risco.

P3 pode ser corrigido quando melhorar a entrega sem expansão material de escopo. Caso não seja necessário para DoD, pode ser registrado como não bloqueante com justificativa.

## Gates humanos

Emitir `HUMAN_DECISION_REQUIRED` quando for necessário tomar uma decisão excepcional que altere risco, escopo, contrato ou outro aspecto reservado ao humano. Esse estado tem precedência sobre `LOOP_ESCALATION_REQUIRED` quando a continuidade depender dessa decisão:

- aceitar risco em vez de corrigir finding bloqueante;
- alterar materialmente escopo aprovado;
- criar/alterar decisão arquitetural;
- executar migration destrutiva;
- introduzir breaking change inevitável;
- alterar estratégia sensível de autenticação, autorização ou tenant isolation;
- introduzir fornecedor externo pago, regulado ou sensível;
- executar operação irreversível;
- decidir conflito entre fontes de verdade de mesmo nível;
- conceder exceção a gate obrigatório;

## Política anti-loop por causa raiz

Não existe limite global fixo de ciclos enquanto os findings forem materialmente diferentes e houver progresso mensurável.

Para cada finding ou família de findings, o Orquestrador deve registrar uma assinatura de causa raiz e contar tentativas de remediação dessa mesma causa.

Escalar para `LOOP_ESCALATION_REQUIRED` quando houver impasse técnico/operacional que não dependa de uma decisão humana reservada:

- a mesma causa raiz reaparecer depois de **3 tentativas de correção**;
- uma correção reintroduzir repetidamente finding já resolvido;
- duas correções entrarem em pingue-pongue ou se anularem;
- CI e Codex criarem requisitos incompatíveis;
- não houver progresso mensurável entre tentativas.

Findings novos, independentes e objetivamente corrigíveis não consomem o limite de outro assunto e devem continuar em `AUTO_REMEDIATION`.

O contador é por causa raiz, não por PR. Espera por CI/Codex não conta como tentativa. Um novo commit só incrementa o contador das causas que ele pretende corrigir.

Quando uma causa atingir 3 tentativas sem solução, não criar automaticamente uma quarta correção. O estado deve ser `LOOP_ESCALATION_REQUIRED` e o handoff deve recomendar revisão aprofundada e, quando útil, segunda opinião independente. Se a tentativa de resolução exigir mudança material de escopo, aceitação de risco ou qualquer outra decisão reservada ao humano, usar `HUMAN_DECISION_REQUIRED`.

## Tratamento de espera

`WAITING_CODEX` e execução de CI são estados operacionais, não gates humanos.

Dentro de uma execução agentiva que permaneça ativa, o Orquestrador deve continuar consultando os resultados e avançar sozinho.

Quando o ambiente de execução não puder permanecer ativo ou receber eventos assíncronos, o estado deve ser persistido no PR/status para retomada determinística; essa limitação de runtime não altera o contrato de governança nem transforma espera em aprovação humana.

## Evidência obrigatória

Registrar no PR ou handoff:

- HEAD de cada rodada;
- workflow runs relevantes;
- SHA revisado pelo Codex;
- findings recebidos e severidade;
- correções realizadas;
- threads resolvidas;
- causas raiz rastreadas e número de tentativas por causa;
- estado terminal;
- para `READY_FOR_HUMAN_MERGE`, URL/ID e timestamp do comentário `ORCHESTRATOR_READY`;
- quando houver merge, URL/ID, autor e timestamp do registro de autorização aplicável: `HUMAN_MERGE_AUTHORIZATION` ou `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`;
- quando a autorização tiver ocorrido fora do GitHub, evidência explícita de que o registro apenas documenta a decisão humana e não simula autoria manual;
- timestamp e ator do evento de merge.

## Outputs esperados

### READY_FOR_HUMAN_MERGE

- PR;
- HEAD final;
- CI/gates aplicáveis verdes;
- Codex Review no HEAD exato;
- zero finding bloqueante pendente;
- `MERGE_ALLOWED` emitido por `validate-definition-of-done`;
- identidade exata do PR/HEAD ao qual eventual autorização humana deve se vincular;
- URL/ID do comentário `ORCHESTRATOR_READY`, usando o timestamp do GitHub como evidência temporal;
- resumo objetivo para review humano final.

### HUMAN_DECISION_REQUIRED

Esse estado não é usado para a autorização ordinária de merge depois de `MERGE_ALLOWED`. No fluxo normal, a autorização acontece após `READY_FOR_HUMAN_MERGE`, referencia o mesmo PR/HEAD e deve anteceder o evento de merge.

- decisão específica;
- opções permitidas;
- riscos;
- evidências;
- ponto exato do fluxo bloqueado.

### BLOCKED_EXTERNAL

- dependência externa;
- evidência do bloqueio;
- condição necessária para retomar.

### LOOP_ESCALATION_REQUIRED

- causa raiz que disparou a escalada;
- findings recorrentes;
- tentativas realizadas para essa causa;
- causa provável do deadlock.

## Não faz

- não aprova SDD ou aceita ADR em nome do humano;
- não aceita risco bloqueante em nome do humano;
- não altera escopo material silenciosamente;
- não rebaixa severidade do Codex;
- não considera review de SHA antigo como válido;
- não faz merge de PR principal sem autorização humana explícita;
- não publica, simula nem reproduz o marcador reservado `HUMAN_MERGE_AUTHORIZATION`;
- pode publicar `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` somente depois de uma decisão humana explícita já recebida no canal interativo, declarando que o comentário é registro do Orquestrador;
- no Modo A, só pode mergear automaticamente o PR administrativo sob o envelope da autorização final do PR principal quando ele alterar exclusivamente `docs/PROJECT_STATUS.md`, não introduzir nova decisão e estiver com gates administrativos e CODEX-01 verdes;
- não mascara CI vermelho;
- não resolve thread sem correção/evidência correspondente.

## Critério de conclusão

A skill termina somente em um dos quatro estados terminais.

Para o fluxo normal de entrega, o resultado desejado é `READY_FOR_HUMAN_MERGE`.

No `ORCHESTRATOR_MODE: A`, atingir esse estado pausa o trabalho apenas para a autorização humana final. Depois da autorização, operações de merge, verificação pós-merge e finalização administrativa podem continuar automaticamente dentro do envelope definido em `.ai/runtime/MODE_A.md`.
