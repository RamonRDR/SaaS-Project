# Runtime do Orquestrador — Modo A

## Objetivo

O Modo A transforma os contratos de governança do repositório em execução assistida por agente, mantendo autonomia operacional alta e gates humanos somente quando uma decisão realmente humana for necessária.

O Modo A não significa autonomia irrestrita.

## Princípio

Dentro de um escopo já aprovado, o Orquestrador deve continuar sozinho enquanto a próxima ação for técnica, reversível e compatível com SDD, ADRs e gates vigentes.

Ele deve parar quando a próxima transição depender de decisão humana material.

## Estados

Estados normais:

- `INIT`
- `SDD_DRAFTING`
- `SDD_READY_FOR_HUMAN_APPROVAL`
- `IMPLEMENTING`
- `REVIEWING`
- `READY_FOR_HUMAN_MERGE`
- `MERGING`
- `FINALIZING`
- `DONE`

Estados terminais de interrupção:

- `HUMAN_DECISION_REQUIRED`
- `BLOCKED_EXTERNAL`
- `LOOP_ESCALATION_REQUIRED`

## Operações automáticas

Quando estiverem dentro do escopo aprovado, o runtime pode:

- criar e atualizar branch de trabalho;
- criar e revisar SDD;
- registrar estado de trabalho em `PROJECT_STATUS.md`;
- implementar código após aprovação da SDD quando ela for obrigatória;
- criar e atualizar testes;
- executar formatter, lint, análise estática, testes e builds;
- executar e reexecutar gates;
- analisar logs de CI;
- corrigir falhas técnicas;
- executar Codex em modo de review;
- corrigir findings objetivos;
- criar commits técnicos;
- abrir e atualizar PRs;
- congelar contrato de review;
- produzir evidência de `PRE_MERGE`;
- criar o PR administrativo pós-merge;
- validar e mergear o PR administrativo quando ele não introduzir nova decisão material e estiver coberto pela autorização humana final do PR principal.

## Gates humanos

O runtime deve parar para decisão humana quando houver:

- aprovação de SDD, quando exigida;
- ADR novo ou mudança material em ADR `Accepted`;
- mudança material de escopo;
- aceitação de risco relevante;
- migration destrutiva;
- breaking change inevitável;
- alteração sensível de autenticação, autorização ou tenant isolation;
- fornecedor externo pago, regulado ou sensível;
- operação irreversível;
- autorização final do merge principal.

## Autorização humana fora do GitHub

A decisão humana pode ocorrer no canal interativo usado com o Orquestrador.

Quando isso ocorrer, o Orquestrador pode registrar no GitHub:

`ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`

O registro deve incluir:

- PR;
- HEAD;
- tipo da decisão;
- origem declarada da decisão;
- observação explícita de que o comentário foi publicado pelo Orquestrador e apenas registra uma decisão humana dada fora do GitHub.

O Orquestrador não pode inventar, inferir ou fabricar uma aprovação inexistente.

O comentário manual legado `HUMAN_MERGE_AUTHORIZATION` continua aceito por compatibilidade, mas não é obrigatório quando existir registro transparente equivalente.

## Envelope da autorização final

No Modo A, a autorização humana final do PR principal pode cobrir também o PR administrativo de finalização, desde que:

- o PR administrativo altere exclusivamente `docs/PROJECT_STATUS.md`;
- não introduza decisão, código, configuração, SDD, ADR ou ampliação de escopo;
- GOV-01, GOV-02 e SEC-01 estejam verdes;
- CODEX-01 esteja verde no HEAD exato;
- não exista finding bloqueante;
- o conteúdo apenas persista um estado já comprovado pela entrega principal.

Se qualquer uma dessas condições falhar, o runtime volta para `HUMAN_DECISION_REQUIRED`.

## Executor

O contrato é independente do executor.

### Piloto — runtime interativo

O piloto inicial usa o Orquestrador na conversa ativa com acesso governado ao GitHub.

Nesse modo:

- o responsável humano inicia ou retoma a execução pela conversa;
- o Orquestrador realiza todas as operações técnicas permitidas sem pedir microautorizações;
- esperas e verificações de CI/Codex são responsabilidade do Orquestrador enquanto a execução atual puder permanecer ativa;
- decisões humanas explícitas dadas na conversa podem ser registradas de forma transparente no PR;
- nenhuma chave de API adicional é necessária para o piloto;
- o runtime não pode alegar execução em background quando não existir um executor assíncrono ativo.

### Futuro — runtime unattended

Depois de validar o piloto, o mesmo contrato pode ser executado por GitHub Actions com o Codex GitHub Action oficial.

Nesse modo futuro:

- credenciais ficam somente em GitHub Actions Secrets;
- permissões de workspace são mínimas;
- prompts permanecem versionados;
- execução falha fechado quando o executor não estiver configurado;
- nenhuma credencial é escrita no repositório.

A adoção do runtime unattended é uma mudança de infraestrutura operacional, não pré-condição para usar o Modo A interativo.

## Controle

Uma execução de fase usa uma issue de controle com:

```text
ORCHESTRATOR_MODE: A
PHASE: PHASE-0-G
OBJECTIVE: ...
```

A issue é o canal de estado durável entre execuções do GitHub Actions.

Aprovações registradas pelo Orquestrador usam comentários de controle estruturados.

## Compatibilidade

O Modo A complementa, e não substitui silenciosamente:

- `AGENTS.md`;
- SDDs aprovadas;
- ADRs `Accepted`;
- `DEFINITION_OF_DONE.md`;
- `CI_GATES.md`;
- `manage-pr-review-loop`;
- `validate-definition-of-done`.

Em conflito, as fontes de verdade de maior prioridade continuam prevalecendo.
