# Etapa 2: dois runners independentes, artefatos e reconciliação

> Experimento restrito à branch `experiment/claim-budget-lab`. **Não** altera PR #2, `main`, credenciais ou orçamento pago.

## O que este experimento valida

Dois jobs de GitHub Actions, em **runners independentes**, geram propostas a partir do mesmo estado inicial e do mesmo `GITHUB_SHA`. Cada job publica um artefato imutável próprio. Um terceiro job (coordenador) baixa os dois artefatos e executa o protocolo de reconciliação determinística.

- Jobs `Separate runner / alpha` e `Separate runner / beta`: `strategy.matrix`, `max-parallel: 2`, `runs-on: ubuntu-latest`.
- Propostas `proposal-alpha` e `proposal-beta`, com SHA-256 de payload canônico, run ID, HEAD, identificação do worker e revisão de origem.
- Um claim lógico compartilhado com dois pretendentes: apenas `alpha` é selecionado na reconciliação.
- Seis solicitações distintas de orçamento e duas propostas repetidas: quatro reservas aceitas, duas negadas antes do dispatch.
- Falha injetada `UNKNOWN_AFTER_PERSIST`: o artefato de `alpha` é escrito e encontrado pelo coordenador, apesar do **ACK simulado** incerto.
- Falha injetada `req-lost`: o worker `beta` não persiste a solicitação simulada; o reconciliador não pode inventar um registro faltante.
- Todas as propostas devem corresponder ao mesmo `run_id` e `head_sha`. Proveniência ou payload divergente, duplicação de worker, arquivo ausente ou adulterado causam fail-closed.

O resultado fica disponível no artefato `reconciled-ledger` do workflow, além dos logs e do Job Summary.

## Execução verificada no GitHub

- **Workflow:** [Claim and Budget Lab, run #37871046739](https://github.com/RamonRDR/SaaS-Project/actions/runs/37871046739)
- **HEAD:** `e4a9566da6ee1da178218e8b9e939c73a2eb1eef`.
- **Resultado:** `success`, **32 testes / 32 aprovados**.
- **Worker alpha:** job `113628973339`, `success`; artefato `proposal-alpha` ID `11590706259`.
- **Worker beta:** job `113628973600`, `success`; artefato `proposal-beta` ID `11590591640`.
- **Coordenador:** job `113629008686`, `success`; artefato `reconciled-ledger` ID `11589859828`.
- **Resultado em log:** `DISTRIBUTED_PROPOSALS_PASSED: 2 independent jobs, 1 claim, 4/4 budget, 2 denied`.
- **Desempate:** worker `alpha`, pela política determinística simulada; o resultado não afirma CAS real da referência Git.
- **Injeção de falhas:** `UNKNOWN_AFTER_PERSIST` e `req-lost` simuladas; nenhum timeout real de transporte foi executado.

### Falha encontrada e corrigida na própria suíte

A execução inicial [#37871003516](https://github.com/RamonRDR/SaaS-Project/actions/runs/37871003516) demonstrou um problema de isolamento: uma lista `requests` em uma proposta era referência ao fixture global e um teste de adulteração a modificava, contaminando um teste seguinte. Os **dois jobs independentes e o reconciliador** já tinham passado, mas a suíte falhou em 1 dos 32 testes. O commit `e4a9566` corrigiu isso copiando os dados por worker, e o run #37871046739 passou integralmente.

### Resultado arquitetural

O teste confirma que Jobs Actions independentes conseguem publicar evidências imutáveis e que um reconciliador consegue processá-las fail-closed sem permissão Git de escrita. Isto sugere um modelo **multi-produtor / escritor único** para filas de entrada. Para reservas financeiras de produção, ainda precisamos de armazenamento com CAS real comprovado, recuperação de erros ambíguos e persistência entre runs, antes de permitir chamadas pagas.

## Limitações, sem atalhos semânticos

1. Os runners são independentes, mas **não disputam diretamente uma ref Git**. Eles publicam artefatos imutáveis e um coordenador aplica mudanças localmente. Não equivale a testar CAS do ledger persistido entre runners.
2. `UNKNOWN_AFTER_PERSIST` é falha **injetada** e verificada lendo o artefato. Não foi causada por timeout real do serviço GitHub.
3. SHA-256 comprova consistência do payload carregado; não é assinatura digital nem autenticação forte do produtor. A segurança vem do workflow confiável, das permissões e dos metadados de job/run.
4. O coordenador simula um **escritor único**. Para produção, é preciso provar durabilidade, atomicidade real e recuperação de escrita ambígua no armazenamento canônico.
5. Não há chamada à OpenAI, remediação real, custo de API, merge, `DONE_ALLOWED` ou autorização para PHASE-0-G.

## Resultado esperado e follow-up

Evidência desta etapa: **dois jobs de workers + um reconciliador** aprovados no GitHub Actions, e testes unitários adicionais cobrindo adulteração de artefato, falha pré-persistência, deduplicação e orçamento.

Próximo gate: estudar um mecanismo de **ledger transacional de um escritor** (ex.: job coordenador com ref Git dedicada, lease/compare-and-set de fato demonstrados ou alternativa com operações atômicas comprovadas), sem deixar o workflow executar código não confiável com token de escrita. Evitar `push` do ledger como wake-up recursivo do orquestrador.

A ADR-0013 já aceita continua imutável; a SDD v1.2 e a ADR-0014 rev.1 só serão consolidadas após revisão técnica e aprovação humana.
