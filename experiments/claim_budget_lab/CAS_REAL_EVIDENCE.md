# Evidência de concorrência real em Git refs (9 out 2026 UTC)

**Status:** experimento real na API GitHub, sem API paga de IA, sem alteração na `main` ou no PR #2.

## Resultado observado

| Prova | Observação |
| --- | --- |
| Claim da mesma solicitação | Dois commits irmãos A/B, construídos do mesmo parent; somente A apareceu na ref persistida |
| Vencedor | `worker-A`, commit `14bc554b956937d60390237f8fba4c349938fb86` |
| Orçamento | Seis propostas irmãs, originadas do mesmo parent; uma foi persistida inicialmente |
| Reconciliador | Releu o HEAD e acumulou reservas `op-01` a `op-04` em novos commits descendentes |
| Teto | **4/4**, sem reservas duplicadas; `op-05` e `op-06` foram negadas pela política antes de escrever |
| Snapshot final | `0ab1807b851638ceef2114539a55fd79faa31568`, revisão 5 |
| SHA esperado obsoleto | Proposta descendente `7488657d88b4ca65ca0476a8925d958d8245daa1` com `expected_sha` antigo não mudou o HEAD |
| Branches/ref descartáveis | Nenhuma ref extra criada: todos os commits foram propostos na branch experimental existente |
| Execução | Conector autorizado do GitHub; nenhuma chamada à OpenAI ou execução local |

**Fonte verificável versionada:** `cas-real-evidence.json` guarda SHA, parent, vencedores, tentativas e limitações. O ledger persistido no arquivo `cas-ledger.json` também está versionado no GitHub. Um teste CI adicional verifica invariantes estruturais.

## Particularidade mais importante: erro ambíguo

As tentativas perdedoras foram reportadas pelo conector como **`UNKNOWN: GithubGraphQLAPIError`**, e não como um HTTP 409/422 discriminável. Uma chamada de reconciliação também sofreu erro genérico depois de uma operação anterior ter sido confirmada no ledger.

**Regra proposta:** após falha, timeout ou exceção de escrita, reconcilie a ref e o payload persistido; nunca replique a reserva por achar que falhou. Somente ao observar geração/estado atuais e a identidade da operação o workflow pode decidir o próximo passo.

## O que foi comprovado e o que não foi

- **Observado:** snapshots lidos no GitHub após corridas tinham um só claim persistido e total financeiro dentro do teto de quatro.
- **Observado:** commits irmãos e tentativa descendente com `expected_sha` obsoleto não alteraram o estado vencedor (independentemente de a exceção ter código genérico).
- **Não comprovado:** código HTTP exato de conflito da API nativa; distinção entre falha de transporte e atualização rejeitada pela camada Git.
- **Não comprovado:** atomacidade entre múltiplas Git refs, nem concorrência entre runners independentes em execuções distintas de Actions.
- **Não comprovado:** tolerância a crash real na fronteira entre commit e dispatch de API, nem garantia de teto monetário real da OpenAI.

Os commits irmãos criados podem permanecer como objetos Git não referenciados. Isso não acrescenta branches e não interfere no PR #2.

## Efeito colateral confirmado: write no ledger pode acordar workflows

Cada um dos commits de ledger observados na branch experimental disparou uma execução `push` do GitHub Actions, pois o workflow tem filtro para `experiments/claim_budget_lab/**`. Exemplos:

- Claim vencedor `14bc554b` → run [#37870020642](https://github.com/RamonRDR/SaaS-Project/actions/runs/37870020642)
- Primeira reserva `2fbe3e1c` → run [#37870174739](https://github.com/RamonRDR/SaaS-Project/actions/runs/37870174739)
- Reserva `op-04`, `0ab1807b` → run [#37870351587](https://github.com/RamonRDR/SaaS-Project/actions/runs/37870351587)

Todos concluíram com `success`, mas esse comportamento tem implicação de custo/volume/loops.
**Para produção:** manter ledger em referência confiável dedicada, fora de filtros de `push` que acordem o orquestrador; o drainer/reconciler deve reagir apenas a sinais intencionais, nunca a cada commit do próprio ledger. A ausência de gatilhos acidentais também precisará de teste E2E.

## DE → PARA para a arquitetura

**DE:** regras de claim específicas de fork, claims ausentes para same-repo, reserva financeira antes de escolher o vencedor, hipóteses de transação distribuída e interpretação da resposta da API como verdade suficiente.

**PARA (proposta):** pedido único identificado por `repository/pr/head/kind/attempt`, claim universal, um ledger canônico de autorização com `CAS` sobre uma única referência persistente por operação crítica, reserva financeira conservadora e idempotente, e reconciliação obrigatória após resposta ambígua. Se quota e budget permanecerem em refs separadas, não reivindicar uma transação global não demonstrada.

## Próxima validação

Antes de aceitar SDD-0001 v1.2 / ADR-0014 rev.1, testar adversarialmente com **dois runners independentes**, reentradas e falhas de atualização API, usando uma implementação mínima de ledger unificado e sem credenciais de IA. Depois consolidar uma só revisão arquitetural e submeter Codex Review, sem mexer no PR #2 durante esta etapa.
