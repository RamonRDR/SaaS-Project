# ADR-0014 - Claim exclusivo antes de reserva monetária idempotente

## Metadados

- **ID:** ADR-0014
- **Título:** Claim exclusivo antes de reserva monetária idempotente
- **Status:** Proposed
- **Revisão decisória:** 1
- **Data de criação:** 2026-10-08
- **Última atualização:** 2026-10-08
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Ramon Rodriguez
- **SDDs relacionadas:** SDD-0001 v1.2
- **ADRs relacionados:** ADR-0013 rev.1 (`Accepted`, vigente); ADR-0012 rev.7 (`Superseded`); ADR-0010
- **PR / issue relacionada:** PR #2 / Issue #1

Nenhum agente de IA pode marcar esta ADR `Accepted`. A ADR-0013 permanece vigente enquanto esta sucessora estiver `Proposed`. O conteúdo decisório compreende as seções 1 a 14 e será imutável após o aceite.

## 1. Contexto

O CODEX-01 do HEAD `81255f16b3719fe56227f1827acbf37194906810` identificou P2 na sequência de canary da ADR-0013 rev.1: `budget CAS global → quota/claim exclusivo → API`. Dois consumers do mesmo request poderiam ocupar duas reservas monetárias antes da escolha do vencedor. Como a ADR-0013 já foi aceita, uma alteração material nessa ordem exige sucessora, não reescrita do histórico.

## 2. Drivers da decisão

- Exclusividade de chamadas pagas e de reservas monetárias.
- Limite mensal global efetivamente bloqueante.
- Continuidade idempotente sob concorrência, crash e retries.
- Separação de privilégios e preservação do histórico de decisões.
- Segurança de repositório público e rastreabilidade por HEAD.

## 3. Restrições

- O Quota Broker e Budget Broker são base-trusted, sem execução de código de fork.
- Apenas Budget Broker detém `OPENAI_API_KEY`.
- Nenhuma chamada é liberada sem budget CAS e período UTC válido.
- Não existe transação atômica distribuída pressuposta entre dois ledgers separados; falha entre etapas é tratada conservadoramente.
- Regras `fail-closed`, anti-loop, gate humano de merge e PHASE-0-G permanecem vigentes.

## 4. Opções consideradas

### Opção A - Reservar budget antes de escolher o consumidor vencedor

Rejeitada. Pode haver duas reservas financeiras para apenas uma chamada. Sem deduplicação e devolução comprovada, consumidores derrotados bloqueiam legitimamente o orçamento.

### Opção B - Primeiro claim exclusivo de quota, depois reserva financeira idempotente (escolhida)

Somente quem vence CAS `RESERVED → CONSUMED` com `consumer_run_id` persistido acessa o Budget Broker. O broker reserva custo máximo via CAS financeiro com chave canônica da solicitação. Repetições retornam o mesmo registro sem incremento nem autorização para nova chamada. Perdedores não possuem reserva monetária.

### Opção C - Transação única envolvendo quota e budget

Possível evolução se houver armazenamento transacional comum com garantias reais. Não pressupor atomicidade distribuída em múltiplas Git refs. Até haver evidência técnica dessa implementação, usa-se a opção B.

## 5. Opção recomendada

- **Opção:** B, claim exclusivo antes de budget com idempotência financeira por identidade.
- **Justificativa:** elimina ocupação dupla por consumidores perdedores e mantém fail-closed entre operações Git distintas, sem atribuir garantias transacionais não demonstradas.

Esta seção propõe uma decisão; não constitui aceite.

## 6. Consequências

### Positivas

- Um único vencedor por reserva de quota.
- Nenhum orçamento consumido por perdedor de claim.
- Idempotência da reserva financeira mesmo sob retransmissão.
- Rastro auditável da ordem `quota claim → budget reserve → dispatch`.

### Trade-offs e obrigações

- Crash após quota claim e antes do budget pode manter uma solicitação sem chamada: bloquear retry pago do mesmo HEAD até decisão humana.
- Duas Git refs não são tratadas como transação atômica distribuída.
- Reconciler precisa distinguir `quota claimed / no financial reservation` de `paid call ambiguous`.
- O controle financeiro deve permanecer global e conservador sob concorrência entre solicitações diferentes.

## 7. Segurança e isolamento

1. Trust gate e quota `RESERVED` precedem claim.
2. Apenas CAS `RESERVED → CONSUMED` vencedor registra `consumer_run_id`, `request_id`, `reservation_id`, PR e HEAD.
3. Somente o vencedor pede reserva ao Budget Broker. Identidade financeira canônica: `(request_id, reservation_id, consumer_run_id, budget_period_utc, model, operation)`.
4. O Budget Broker confirma autorização de claim e executa CAS `check + reserve` global considerando `committed + outstanding_max + new_max <= budget_limit`; repetição da chave retorna o mesmo registro sem nova contabilização.
5. Chave divergente, estado ambíguo ou tentativa de reutilização da autorização para outra chamada bloqueia antes da API.
6. Período UTC é revalidado no claim financeiro e antes do dispatch. Nova reserva mensal exige comprovação de não-envio da chamada anterior e novo CAS, sempre para o mesmo consumidor exclusivo; gastos ambíguos não são liberados automaticamente.
7. Falhas ou crash antes de reserva financeira não autorizam retry pago para o mesmo HEAD; nunca se promete progresso sem evidência de estado seguro.

## 8. Dados e contratos da API

Nenhuma mudança em dados ou API do produto. O ledger persistente inclui `request_id`, `reservation_id`, `consumer_run_id`, `budget_period_utc`, `model`, `operation`, `max_cost_minor`, versão CAS, estado e provenance. O broker rejeita identidades inconsistentes.

## 9. Operação e observabilidade

Registrar tentativa de claim, CAS vencedor/perdedor, solicitação financeira, resultado de deduplicação, mês UTC, autorização de dispatch, sucesso/falha e custo conciliado. Nunca registrar secrets ou dados sensíveis do fork em logs operacionais.

## 10. Migração e rollout

1. Obter review técnico favorável e aprovação humana de SDD-0001 v1.2.
2. Obter review técnico favorável e aceite humano de ADR-0014 rev.1.
3. Implementar a sequência **`quota RESERVED → quota claim CAS exclusivo → budget CAS idempotente → revalidar mês UTC → dispatch API`** no bootstrap em PR próprio.
4. Canary negativo: dois consumidores do mesmo `request_id` iniciam simultaneamente; exatamente um faz reserva financeira; perdedor não incrementa `outstanding_max_minor`.
5. Canary de retry da reserva pelo mesmo vencedor: idempotência por chave, sem segunda reserva nem segunda chamada.
6. Canary de crash após claim e antes de budget: sem chamada e sem cobrança, escalando recuperação; crash depois de dispatch ambíguo mantém custo máximo comprometido.
7. Canary UTC: rollover entre quota claim, budget e dispatch exige CAS no bucket atual; não executar chamada com autorização de mês anterior.
8. Manter ADR-0013 como `Accepted` até que a ADR-0014 seja aceita; só então marcar a anterior `Superseded`, sem alterar seu conteúdo decisório.

## 11. Rollback e reversibilidade

- **Reversível:** Sim, durante rollout do runtime.
- **Estratégia:** desabilitar chamadas pagas e voltar a Mode A interativo se os testes falharem.
- **Custo:** backlog poderá exigir intervenção humana, sem comprometer credenciais ou criar reservas duplicadas.

## 12. Relação com decisões existentes

- **ADR-0013 rev.1:** vigente e `Accepted`; esta ADR propõe suceder especificamente a ordem de claim/reserva de budget. Somente após aceite humano a ADR-0013 poderá ser marcada `Superseded`.
- **ADR-0012 rev.7:** decisão histórica `Superseded` pela ADR-0013. Não reescrever.
- **ADR-0010:** regras de CI e merge humano permanecem.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer preliminar | Pendências |
| --- | --- | --- |
| Security | Requer validação | Isolamento, chaves e idempotência |
| Platform & Observability | Requer validação | CAS concorrente e rastreabilidade |
| QA & Quality | Requer validação | Interleavings e testes negativos |
| Backend / Frontend | Não aplicável | Sem feature de produto |

## 14. Riscos não resolvidos

Sem teste real de CAS e budget broker implementado, as garantias permanecem **requisitos arquiteturais**, não funcionalidades comprovadas. A ambiguidade de chamada paga mantém custo reservado e exige gate humano quando não é recuperável com evidência segura.

## 15. Histórico de revisão

| Data | Responsável | Alteração | Estado |
| --- | --- | --- | --- |
| 2026-10-08 | Product & SDD | Proposta sucessora à ADR-0013 para corrigir reserva monetária antes de quota claim | rev.1 `Proposed` |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pendente
- **Revisão revisada:** Ainda não revisada, rev.1 proposta
- **Revisor:** Orchestrator / Tech Lead
- **Data:** Não aplicável até conclusão
- **Pendências bloqueantes:** verificar claim-first e CAS financeiro idempotente, inclusive rollover UTC.
- **Pendências não bloqueantes:** implementar e provar canaries antes da integração paga.

## 17. Aceite humano

- **Aceito:** Não
- **Responsável humano:** Ramon Rodriguez
- **Revisão aceita:** Não aplicável
- **Data:** Pendente
- **Registro:** Pendente. Aceite de ADR-0013 rev.1 (#6070726649) não equivale ao aceite desta ADR-0014.
