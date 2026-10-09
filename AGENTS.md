# AGENTS.md

Este arquivo é o contrato principal de engenharia para pessoas e agentes de IA que trabalham neste repositório.

## Política de linguagem

A linguagem documental oficial do projeto é português do Brasil.

Regras:

1. Nomes de funções, classes, métodos, variáveis, módulos, packages, eventos, tabelas técnicas e identificadores de código devem ser escritos em inglês.
2. Documentação, SDDs, ADRs, READMEs, relatórios, critérios de aceite e descrições operacionais devem ser escritos em português do Brasil.
3. Comentários e docstrings devem ser escritos em português do Brasil.
4. Comentários devem explicar intenção, contexto ou motivo. Não devem narrar código óbvio linha por linha.
5. Termos técnicos amplamente consolidados, como tenant, endpoint, middleware, rollback, health check, CI/CD, pull request e staging, podem permanecer em inglês.
6. Não misturar idiomas dentro do mesmo identificador técnico.
7. Textos exibidos ao usuário devem seguir o idioma definido pelo produto. O mercado inicial é pt-BR.

Consulte também `docs/LANGUAGE_POLICY.md`.

## Regras fundamentais

1. Leia a documentação relevante antes de alterar código.
2. Confirme branch, estado do repositório, escopo e SDD ativa antes de implementar.
3. Features significativas exigem SDD aprovada antes de mudanças de código.
4. Decisões arquiteturais significativas exigem ADR revisado pelo Orchestrator / Tech Lead e aceito pelo responsável humano.
5. Nenhuma operação de domínio pode ignorar isolamento de tenant.
6. Regras críticas de negócio pertencem ao backend, não ao Flutter ou ao n8n.
7. Secrets nunca podem ser commitados. O gate `SEC-01` é obrigatório em todo PR, inclusive quando o diff contém apenas documentação.
8. Migrations destrutivas exigem aprovação humana explícita.
9. Código gerado por IA deve seguir os mesmos padrões exigidos de código humano.
10. Testes, segurança, observabilidade, documentação e atualização de status fazem parte da entrega.
11. Uma tarefa não pode ser marcada como DONE apenas porque o código compila.
12. Operações irreversíveis ou sensíveis à segurança exigem aprovação humana.
13. Todo pull request deve receber Codex Review antes do merge.
14. Achados bloqueantes do Codex Review devem ser resolvidos ou explicitamente avaliados pelo responsável humano antes do merge.
15. O Codex Review só é válido para merge quando o SHA revisado é exatamente igual ao HEAD atual do pull request. Qualquer novo commit exige nova revisão.
16. O Codex Review válido para o gate PRE_MERGE deve acontecer após o último commit mutável do PR principal, incluindo atualizações finais de documentação.
17. Depois do merge principal, a transição de `PROJECT_STATUS.md` para concluído deve ocorrer em PR administrativo exclusivo, limitado a esse arquivo, também sujeito a Codex Review. Para enforcement de `GOV-02`, o estado de máquina é lido exclusivamente do bloco reservado `GOV:PROJECT_STATUS`; qualquer fase cujo marcador `GOV:PHASE-*` transite para `completed` em relação ao merge-base torna o PR de finalização aplicável e exige alteração exclusiva de `docs/PROJECT_STATUS.md`. O gate não interpreta headings, `Concluída.` ou outras construções Markdown. Marcadores são monotônicos e não podem ser removidos ou regredir. O nome da branch é apenas convenção. Esse PR não gera recursivamente outro PR de finalização.
18. Novas SDDs e ADRs devem partir dos templates oficiais em `docs/specs/SDD-TEMPLATE.md` e `docs/adr/ADR-TEMPLATE.md`. Se uma seção obrigatória não se aplicar, ela deve permanecer com justificativa.
19. Parecer técnico favorável de ADR é válido somente para a revisão decisória explicitamente revisada. Mudança material posterior invalida o parecer e exige nova revisão.
20. Um ADR vigente só pode mudar para `Superseded` depois que o ADR sucessor tiver atingido `Accepted`.
21. Parecer favorável e aprovação humana de SDD são válidos somente para a versão explicitamente revisada e aprovada. Mudança material posterior incrementa a versão, invalida ambos e exige nova revisão e aprovação.
22. Uma SDD vigente só pode mudar para `Superseded` depois que a SDD sucessora tiver atingido `Approved`.
23. A Definition of Done operacional oficial está em `docs/engineering/DEFINITION_OF_DONE.md` e é obrigatória para toda entrega.
24. O catálogo oficial de gates está em `docs/engineering/CI_GATES.md`; todo PR deve declarar gates aplicáveis, evidências e itens não aplicáveis com justificativa.
25. Gate obrigatório automatizado em estado diferente de sucesso bloqueia merge. Falta temporária de automação não dispensa a evidência manual exigida pelo contrato.
26. Um gate só pode ser marcado como `N/A` quando sua condição de aplicabilidade não existir e a justificativa estiver registrada no PR ou handoff.
27. A introdução de um novo stack executável deve habilitar, no mesmo marco de bootstrap ou antes da primeira feature, os gates técnicos aplicáveis definidos no catálogo.
28. A indisponibilidade de branch protection por limitação de plano não remove nenhuma regra processual de PR, CI, Codex Review ou gate humano.
29. Depois que um PR entra no ciclo de revisão, o Orquestrador deve executar `manage-pr-review-loop` até um estado terminal; espera por CI/Codex e findings tecnicamente corrigíveis não constituem gate humano.
30. O responsável humano não precisa solicitar manualmente verificação de Codex, correção de findings ou nova revisão. O Orquestrador é responsável por repetir CI -> Codex -> correção -> CI enquanto a correção permanecer dentro do escopo aprovado.
31. Todo merge governado por este lifecycle exige evidência auditável da sequência `READY -> autorização humana -> merge`. O Orquestrador registra `READY_FOR_HUMAN_MERGE` em comentário `ORCHESTRATOR_READY` no PR. A autorização humana pode ser registrada de duas formas equivalentes: comentário manual legado `HUMAN_MERGE_AUTHORIZATION` no mesmo PR/HEAD, ou registro transparente `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` quando a decisão explícita tiver ocorrido no canal interativo do Orquestrador. Neste segundo caso, o comentário deve declarar que foi publicado pelo Orquestrador e apenas registra uma decisão humana externa ao GitHub; agentes continuam proibidos de inventar, inferir ou fabricar aprovação. O checkpoint pós-merge deve comprovar `ready.created_at < authorization_record.created_at < merged_at`.
32. O review loop deve escalar para decisão humana quando a correção exigir aceitação de risco, mudança material de escopo, nova decisão arquitetural, migration destrutiva, breaking change, mudança sensível de auth/tenant isolation, fornecedor sensível ou operação irreversível.
33. O resultado `BLOCKED` de `validate-definition-of-done` é intermediário e deve ser classificado: causa corrigível retorna a `AUTO_REMEDIATION`; decisão excepcional humana vira `HUMAN_DECISION_REQUIRED`; dependência externa vira `BLOCKED_EXTERNAL`; impasse anti-loop vira `LOOP_ESCALATION_REQUIRED`.
34. O review loop não possui limite global fixo de rodadas. Ele deve rastrear causas raiz e escalar para `LOOP_ESCALATION_REQUIRED` quando a mesma causa reaparecer após 3 tentativas de correção, quando correções entrarem em pingue-pongue, quando houver deadlock ou quando não existir progresso mensurável. Findings novos e independentes continuam em remediação automática. Se a próxima ação exigir mudança material de escopo, aceitação de risco ou outra decisão excepcional reservada ao humano, `HUMAN_DECISION_REQUIRED` tem precedência. Tanto `LOOP_ESCALATION_REQUIRED` quanto `HUMAN_DECISION_REQUIRED`, `BLOCKED_EXTERNAL` e `READY_FOR_HUMAN_MERGE` devolvem o controle ao responsável humano.
35. Antes do Codex final, o PR deve registrar `REVIEW_CONTRACT_FROZEN` com escopo, HEAD, SDD/ADRs, gates, riscos residuais aceitos e follow-ups. Depois disso, somente violação desse contrato, defeito concreto no escopo atual, fail-open, segurança/integridade ou mudança material de risco pode bloquear. Hardening/preferência nova vira `FOLLOW_UP`.
36. Quando o `ORCHESTRATOR_MODE: A` estiver ativo, o Orquestrador deve continuar automaticamente em trabalho técnico reversível dentro do escopo aprovado e só devolver o controle humano em `SDD_READY_FOR_HUMAN_APPROVAL`, `HUMAN_DECISION_REQUIRED`, `READY_FOR_HUMAN_MERGE`, `BLOCKED_EXTERNAL` ou `LOOP_ESCALATION_REQUIRED`. Microautorizações operacionais são proibidas nesse modo.
37. No Modo A, a autorização humana final do PR principal pode cobrir o PR administrativo de finalização somente quando esse PR alterar exclusivamente `docs/PROJECT_STATUS.md`, não introduzir nova decisão e possuir GOV-01, GOV-02, SEC-01 e CODEX-01 satisfatórios. Qualquer desvio desse envelope exige novo `HUMAN_DECISION_REQUIRED`.
38. `CODEX-01` é o único reviewer de IA obrigatório para merge. Claude Code ou outra segunda opinião é usado em escalada/diagnóstico e não cria gate paralelo permanente.
39. Finding cuja causa raiz já esteja coberta por aceitação humana explícita deve ser classificado como `ACCEPTED_RESIDUAL_RISK` enquanto não houver evidência nova material.
40. Remediação automática do Modo A nunca pode publicar alteração no control plane protegido. A denylist mínima inclui `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` e `docs/PROJECT_STATUS.md`. Se um patch automático tocar qualquer um desses paths, o patch inteiro deve ser rejeitado antes da escrita e o fluxo deve transicionar para `HUMAN_DECISION_REQUIRED`.
41. Para PR originado de fork, `CODEX-01` deve executar em contexto base-trusted carregado da branch padrão, sem checkout ou execução do HEAD externo. Workflow, prompt, schema e broker vêm somente da `main`; diff e metadados do fork entram apenas como dados não confiáveis vinculados ao `head.sha`. Nenhum código do fork recebe secrets ou `contents: write`, e findings do fork não acionam remediação automática com escrita.
42. O CODEX-01 de fork deve ser tool-less: o modelo não recebe shell, filesystem, tools/functions, subprocessos nem acesso ao ambiente do runner. O broker de review, carregado somente da `main`, prepara dados estruturados e solicita a inferência ao Budget Broker isolado; o reviewer não recebe `OPENAI_API_KEY` nem um cliente autenticado do provedor. Somente o Budget Broker mantém a chave e realiza a chamada paga, sem sudo/elevação, checkout ou execução de conteúdo do fork. Conteúdo não confiável nunca é interpolado em comandos. Teste negativo de exfiltração de secret é obrigatório.
43. Chamadas pagas de CODEX-01 originadas por fork exigem trust gate antes da API. `OWNER`, `MEMBER` e `COLLABORATOR` são confiáveis automaticamente; demais autores exigem aprovação explícita de maintainer. Cada `head.sha` admite no máximo uma chamada paga; o baseline limita a 3 chamadas por PR/24h e 5 por autor externo/24h. Cada solicitação deve ser persistida como `PENDING` em fila/ledger GitHub durável antes de qualquer wake-up. Um Quota Broker/drainer da `main` reconcilia o backlog e persiste `RESERVED` antes da API; `concurrency` pode serializar o drainer, mas nunca é tratado como fila de solicitações. Falta de trust, reserva inválida ou quota excedida bloqueia antes da API e resulta em `HUMAN_DECISION_REQUIRED`.
44. Wake-ups do drainer são best-effort. Coalescência/cancelamento de execuções pendentes não pode remover pedidos persistidos; reconciler periódico da `main` deve retomar backlog `PENDING`/`RESERVED` incompleto sem intervenção humana. Consumo ambíguo após crash é fail-closed: continua contando na janela e não autoriza segunda chamada automática para o mesmo `head.sha`.
45. Antes de qualquer tentativa de reserva monetária para review de fork, o Quota Broker deve executar claim exclusivo CAS `RESERVED → CONSUMED` e gravar `consumer_run_id`. Somente o vencedor confirmado pode solicitar ao Budget Broker a reserva financeira idempotente por `request_id`/`reservation_id`/`consumer_run_id`/mês UTC, antes da chamada paga. Perdedores não ocupam o orçamento. Claim após crash não autoriza segunda chamada automática e `CONSUMED` nunca é revertido automaticamente.
46. CODEX-01 de fork só pode emitir evidência válida após provar completude do payload do HEAD exato. Resolver `merge_base_sha` entre `base_tip_sha` e `head_sha` e comparar Git Trees/Blobs **merge-base → HEAD**, nunca base_tip → HEAD; base_tip é metadado. Truncamento, ancestral ambíguo, objeto ausente, binário não revisável ou payload acima do limite exige fail-closed e `HUMAN_DECISION_REQUIRED`.
47. Toda chamada paga de IA (Codex Remediator, CODEX-01 same-repo e fork) deve passar por Budget Broker global confiável da `main`. Exclusivamente o job/processo isolado do Budget Broker recebe `OPENAI_API_KEY` e efetua inferência paga depois da reserva financeira; jobs consumidores, reviewers e Trusted Publisher nunca recebem o segredo, token delegado ou acesso direto ao provedor. SDK/CLI/Action usados nesses jobs não podem contornar o broker.
48. O Budget Broker exige orçamento monetário mensal global positivo aprovado humanamente, catálogo versionado de preços e limite superior conservador por requisição (input/output tokens, retries e outros custos). **Somente após o claim exclusivo de quota** executa reserva financeira global CAS, idempotente pela chave canônica por solicitação, sem cobrar novamente repetição da mesma chave. Sob CAS em ledger GitHub, somente libera chamada se `committed_minor + outstanding_max_minor + new_max_minor <= budget_limit_minor`, para o **mês UTC corrente no momento do claim e do dispatch**. Se o mês mudar entre `RESERVED`, claim e envio, bloqueia, exige nova reserva/claim no bucket atual e mantém reserva antiga conservadoramente comprometida; relógio incerto ou proximidade insegura da virada também bloqueia. Orçamento indefinido, modelo desconhecido, ledger indisponível ou custo sem teto bloqueia antes da API.
49. Reservas monetárias ambíguas após crash ficam comprometidas pelo máximo; retry pago exige nova reserva/budget e governança apropriada. Mudança no orçamento/catálogo exige autorização humana auditável. Alertas e spend limits do provedor são defesa adicional e não substituem o ledger bloqueante.
50. Decisões de ADR em estado `Accepted` são históricas e imutáveis nas seções decisórias. Alterações materiais exigem ADR sucessora proposta sob novo ID; a ADR aceita permanece `Accepted` até a sucessora também ser aceita por gate humano, quando poderá ser marcada `Superseded` apenas com referência formal.

## Política de severidade do Codex Review

Quando o Codex Review informar prioridade, essa classificação deve ser preservada no fluxo:

- `P0` e `P1`: bloqueiam o merge até correção ou até o responsável humano registrar no PR que o achado é não aplicável ou falso positivo, com justificativa;
- `P2`: bloqueia o merge por padrão até correção ou aceitação explícita do risco pelo responsável humano, com justificativa registrada no PR;
- `P3` ou sugestão sem caráter corretivo: não bloqueia por padrão, salvo escalonamento pelo Orquestrador por impacto em segurança, tenant isolation, perda de dados, breaking change, compliance ou operação irreversível;
- achado sem prioridade explícita: o Orquestrador classifica usando o mapeamento objetivo abaixo e registra a classificação no PR.

### Mapeamento para achados sem prioridade

- `P0`: risco crítico e imediato, incluindo acesso cross-tenant, exposição de secrets, perda/corrupção grave de dados, comprometimento de segurança ativo, operação irreversível indevida ou indisponibilidade crítica de produção;
- `P1`: risco alto que pode causar violação relevante de segurança, autorização, privacidade, integridade de dados, arquitetura obrigatória ou bypass de gate crítico antes de produção;
- `P2`: problema material de correção, consistência, confiabilidade, governança ou manutenção que deve ser resolvido antes do merge, mas sem impacto crítico ou alto imediato;
- `P3`: melhoria de clareza, estilo, ergonomia documental ou robustez de baixo risco, sem alteração material de comportamento, segurança, dados ou gates.

Quando um achado se enquadrar em mais de uma categoria ou houver dúvida entre duas prioridades adjacentes, usar a prioridade mais alta.

O Orquestrador não pode rebaixar silenciosamente uma prioridade atribuída pelo Codex. Exceções dependem de decisão humana registrada.

## Fluxo obrigatório de execução

Ideia
-> triagem do Orquestrador
-> análise de impacto
-> criação/revisão da SDD
-> aprovação humana
-> ADR, quando necessário
-> implementação
-> QA
-> revisão de segurança
-> revisão de plataforma e observabilidade
-> CI
-> staging
-> validação humana
-> atualização final de documentação/status sem antecipar conclusão
-> checagem documental final somente leitura
-> `manage-pr-review-loop` do PR principal, incluindo CI, Codex e PRE_MERGE
-> `READY_FOR_HUMAN_MERGE`
-> review final e autorização humana
-> registro auditável da autorização para o mesmo PR/HEAD
-> merge do PR principal
-> verificação pós-merge com evidência do registro da autorização humana
-> validação POST_MERGE
-> PR exclusivo de finalização de `PROJECT_STATUS.md`
-> `manage-pr-review-loop` do PR de finalização, incluindo CI, Codex e PRE_MERGE
-> `READY_FOR_HUMAN_MERGE` do PR de finalização
-> no Modo A, merge administrativo coberto pelo envelope da autorização final quando todas as condições da regra 37 forem satisfeitas; fora desse envelope, nova autorização humana
-> validação FINAL
-> DONE

Etapas sem impacto real podem ser marcadas como não aplicáveis pelo Orquestrador, mas o Codex Review do pull request é obrigatório para todo PR.

## Fontes de verdade

- intenção do produto: documentação de produto e SDDs aprovadas;
- arquitetura: `docs/architecture/` e `docs/adr/`;
- estado da entrega: `docs/PROJECT_STATUS.md`;
- workflow de agentes: `.ai/agents/`;
- procedimentos reutilizáveis: `.ai/skills/`;
- contrato de autonomia operacional: `.ai/runtime/MODE_A.md` quando `ORCHESTRATOR_MODE: A` estiver ativo;
- Definition of Done operacional: `docs/engineering/DEFINITION_OF_DONE.md`;
- catálogo de gates e evidências: `docs/engineering/CI_GATES.md`.

## Condições de parada

Os agentes devem interromper a execução e solicitar aprovação humana quando:

- o escopo mudar materialmente;
- uma migration destrutiva for necessária;
- a arquitetura de autenticação ou autorização mudar;
- a estratégia de isolamento entre tenants mudar;
- um novo provedor externo pago, regulado ou sensível for introduzido;
- um breaking change de API for inevitável;
- uma operação irreversível em produção for proposta;
- um Codex Review apontar achado bloqueante que não possa ser corrigido com segurança dentro do escopo aprovado ou cuja resolução exija decisão humana, aceitação de risco, exceção de gate ou mudança material de contrato;
- a mesma causa raiz de finding persistir após 3 tentativas de correção, situação em que deve ser feita revisão aprofundada antes de nova tentativa.
