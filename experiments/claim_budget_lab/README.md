# Laboratório isolado: claim universal, quota e orçamento

> **Status:** experimento, sem valor de `Accepted`/implementação de produção.
> **Branch:** `experiment/claim-budget-lab`, originada da `main` pública.
> **Escopo:** PR #2, SDD e ADRs são **somente insumos de leitura**; este experimento não modifica aquele PR.

## Objetivo

Reproduzir os conflitos de causa raiz identificados pelo CODEX-01 e validar uma
hipótese arquitetural única antes de editar novamente a SDD-0001/ADR-0014.

O laboratório utiliza apenas Python standard library, mocks e relógio UTC
controlável. **Não há chamada ao provedor, chave de API, pagamento, segredo ou
runner local do usuário.** Roda em GitHub-hosted standard runner a cada push na
branch experimental.

## Contrato DE → PARA

| Domínio | DE: inconsistência observada | PARA: invariante simulado |
| --- | --- | --- |
| Chamada de fork | quota/claim definido apenas no reviewer de fork | claim universal precede reserva de budget |
| Chamada same-repo | sem claim válido para liberar gasto | `same_repo_review` também cria `PENDING → RESERVED → CLAIMED` |
| Codex Remediator | pode ficar bloqueado antes de Budget Broker | `remediator` segue protocolo idêntico |
| Quota | confundida com autorização monetária | limites 3/PR e 5/autor externo/24h são adicionais e só para fork |
| Concorrência | workers perdedores podiam imobilizar custo | apenas vencedor do claim autoriza reserva financeira |
| Idempotência | reentrada podia criar compromisso duplicado | budget por chave lógica e período, sem nova reserva por repetição |
| UTC | tabela EDGE exigia segundo claim de quota | claim único imutável, CAS financeiro específico do período |
| Falha | retorno ambíguo podia permitir nova chamada | marcar envio conservadoramente e bloquear retry |
| Limite global | concorrência entre PRs | reservas conservadoras serializadas no orçamento mensal comum |
| Governança | reescrita material de ADR aceita | ADR-0013 não é editada; ADR-0014 só entra em vigor após gate humano |

## Dois estados separados

**Máquina de operação paga (proposta):**

`PENDING → RESERVED (eligibility/quota) → CLAIMED (consumidor único) → BUDGET_RESERVED (CAS financeiro) → DISPATCH (só um envio) → COMPLETED`

A transição `CLAIMED` **não** reserva nem gasta dinheiro por si só.
A reserva financeira pertence a um `budget_period_utc`, que pode mudar
sem duplicar o claim de quota, desde que seja comprovado não ter ocorrido
envio. Incerteza bloqueia.

**Máquina de governança do PR:** `INIT → SDD_DRAFTING → ... → REVIEWING → READY_FOR_HUMAN_MERGE → ...`,
com os gates humanos e a política anti-loop definidos no repositório.
Ela é **separada** do estado da operação paga. Este laboratório não a modifica.

### Identidades e privilégios

O `request_id` identifica a operação lógica por
`repository + pr + head + kind + attempt`. O `consumer_run_id` identifica
apenas o worker vencedor. Os três `kind` são:

- `fork_review`: trust gate e quota especial por autor/PR/HEAD.
- `same_repo_review`: claim universal sem quota especial de autor externo.
- `remediator`: claim universal e tentativa declarada para o mesmo HEAD.

O Budget Broker de produção deverá possuir acesso exclusivo ao provedor;
**o simulador contém somente `MockProvider`, sem nenhuma credencial**.

## Matriz executável

O arquivo `test_protocol.py` implementa a matriz abaixo. Todos os cenários
usam relógio falso, CAS in-memory e provedor simulado.

| Família | Critério |
| --- | --- |
| Trust/quotas | rejeitar fork externo sem aprovação; 4º review no mesmo PR e 6º por autor externo/24h |
| Elegibilidade universal | fork, same-repo e remediator alcançam o mesmo claim |
| Deduplicação | mesmo request não vira outro registro |
| Corrida para mesmo request | apenas um vencedor entre 32 workers; perdedores não reservam budget |
| CAS monetário global | 10 PRs concorrentes não ultrapassam limite, sem liberar custo indevido |
| Retry financeiro | duplicata de mesma chave não duplica `outstanding_max` nem autoriza segunda chamada |
| Crash pré-budget | quota claim permanece consumido, sem chamada paga/reclaim automático |
| Crash após envio | custo pessimista fica comprometido, sem segunda chamada |
| UTC entre etapas | orçamento anterior não autoriza novo período; novo CAS só com prova de não-envio |
| Relógio | bloquear emissão perto do fim do mês e entradas sem timezone |
| Optimistic concurrency | atualização com revisão obsoleta é rejeitada |

## Executar no GitHub

Workflow em `.github/workflows/claim-budget-lab.yml`:

- evento: `push` **exclusivamente** na branch `experiment/claim-budget-lab`;
- runner: `ubuntu-latest`, com `contents: read`;
- dependências: nenhuma além de Python 3;
- comando: `python3 -m unittest discover -s experiments/claim_budget_lab -p 'test_*.py' -v`;
- evidência: conclusão, logs e resumo no run de GitHub Actions.

O workflow **não** faz merge, não cria PR e não altera `docs/PROJECT_STATUS.md`. A prova com Git refs foi realizada pela conexão autorizada do GitHub, deixando o workflow apenas com `contents: read`.

## Segundo experimento: runners independentes

Validamos dois jobs GitHub Actions independentes, cada um publicando seu próprio artefato imutável. Um terceiro job realizou a reconciliação sem token de escrita, com falhas injetadas: **32 testes aprovados** no [run #37871046739](https://github.com/RamonRDR/SaaS-Project/actions/runs/37871046739).

- [Relatório com jobs, artefatos, limitações e descoberta do isolamento de fixtures](./DISTRIBUTED_RUNNERS.md).
- [Modelo do protocolo distribuído com dados determinísticos](./distributed_protocol.py).
- [Testes automatizados de validação de payload e reconciliação](./test_distributed_protocol.py).

Esse teste **não** executou duas escritas paralelas no mesmo ledger Git remoto. Falta validar CAS distribuído em condições reais antes da implementação de pagamento automatizado.

## Gate para escritor CAS privilegiado

A auditoria de permissões encontrou a `main` pública sem proteção. **Não ativar `contents: write` nesta branch**. Testes de autorização fail-closed estão em [test_privilege_gate.py](./test_privilege_gate.py) e o desenho para um repositório descartável separado está em [PRIVILEGED_CAS_GATE.md](./PRIVILEGED_CAS_GATE.md). Ainda não existe prova de dois escritores remotos independentes no mesmo ledger.

## Limitações e próximos gates

**Importante:** o `SimulatedCASLedger` modela o comportamento esperado com
locks Python; um resultado verde **não comprova** que duas Git refs sejam
atômicas, nem a durabilidade após reinício real, nem fechamento da janela
entre a última consulta UTC e a aceitação da cobrança pelo provedor.

Antes de aprovar a arquitetura definitiva será necessário:

1. **Primeira evidência real de Git refs concluída via conector**, sem token de escrita em Actions. Consultar [CAS_REAL_EVIDENCE.md](./CAS_REAL_EVIDENCE.md) e [cas-real-evidence.json](./cas-real-evidence.json). Ainda não comprova CAS distribuído entre runners.
2. Testes E2E com dois runners independentes, fault injection, timeouts e recuperação de erro de API com leitura posterior obrigatória.
3. Verificação prática da janela de fronteira UTC e do custo/token cap do Budget Broker real.
4. Revisão da SDD v1.2 e ADR-0014 rev.1 baseada nessas evidências, com aprovação/aceite humano.
5. Novo Codex Review no HEAD final do PR #2, gates e autorização humana de merge.

Este experimento não cumpre CODEX-01, `DONE_ALLOWED` nem libera PHASE-0-G.
