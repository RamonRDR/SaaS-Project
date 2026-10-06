# ADR-XXXX - Título da decisão

> Copie este arquivo para registrar uma decisão arquitetural. Substitua os placeholders e preserve as seções obrigatórias.
>
> Se uma seção não se aplicar, registre **Não aplicável** e a justificativa.

## Metadados

- **ID:** ADR-XXXX
- **Título:** <decisão em linguagem direta>
- **Status:** Proposed
- **Revisão decisória:** 1
- **Data de criação:** YYYY-MM-DD
- **Última atualização:** YYYY-MM-DD
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** <nome ou papel>
- **SDDs relacionadas:** <SDD-XXXX ou Não aplicável>
- **ADRs relacionados:** <ADR-XXXX ou Não aplicável>
- **PR / issue relacionada:** <referência ou Não aplicável>

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável com parecer `Pronto para aceite humano`, nenhuma pendência bloqueante e aceite humano explicitamente registrado;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior identificado;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

Um ADR com parecer `Retornar para ajustes` ou `Bloqueado` não pode seguir para `Accepted`, mesmo que exista manifestação humana de concordância. Primeiro as pendências bloqueantes precisam ser resolvidas e o `review-adr` deve emitir novo parecer `Pronto para aceite humano`.

### Revisão decisória e validade do parecer

As seções **1 a 14** compõem o conteúdo decisório do ADR.

Antes de `Accepted`:

- qualquer alteração material nas seções 1 a 14 incrementa `Revisão decisória`;
- essa alteração invalida automaticamente qualquer parecer técnico anterior;
- o status permanece ou retorna para `Proposed`;
- o ADR precisa passar novamente por `review-adr`;
- um aceite humano ainda não concluído não pode reutilizar parecer de revisão decisória anterior.

As seções 15 a 17 registram histórico, revisão técnica e aceite. Atualizações puramente de auditoria nessas seções não incrementam a revisão decisória desde que não alterem o conteúdo da decisão.

Depois de `Accepted`, o conteúdo decisório das seções 1 a 14 é imutável. Mudança material exige novo ADR sucessor; não reescrever a decisão histórica aceita.

## 1. Contexto

Explique o problema arquitetural, o cenário atual e por que uma decisão durável é necessária.

## 2. Drivers da decisão

- segurança;
- multi-tenancy;
- manutenibilidade;
- custo;
- complexidade;
- performance;
- operação;
- reversibilidade;
- compliance;
- <outros aplicáveis>.

## 3. Restrições

- <restrição>

## 4. Opções consideradas

### Opção A - <nome>

**Descrição**

<descrição>

**Vantagens**
- <vantagem>

**Desvantagens**
- <desvantagem>

**Riscos**
- <risco>

**Impacto operacional / migração**
- <impacto>

### Opção B - <nome>

Repita a mesma estrutura.

## 5. Opção recomendada

- **Opção:** <nome>
- **Justificativa:** <por que é recomendada considerando os drivers>

Esta seção registra recomendação, não aceite.

## 6. Consequências

### Positivas
- <consequência>

### Negativas / trade-offs aceitos
- <consequência>

### Novas obrigações
- <testes, controles, monitoramento, documentação ou operação>

## 7. Impacto em segurança e multi-tenancy

Documente autenticação, autorização, isolamento de tenant, dados sensíveis, secrets e exposição de dados.

## 8. Impacto em dados e API

Documente modelo de dados, migrations, compatibilidade, contratos de API, breaking changes e versionamento.

## 9. Impacto operacional e observabilidade

Documente deploy, ambientes, rollback, health checks, logs, métricas, tracing, incident response e dependências externas.

## 10. Migração e rollout

Descreva etapas, coexistência temporária, backfill, feature flags, dependências e estratégia de rollout.

## 11. Rollback / reversibilidade

- **Reversível:** Sim / Parcialmente / Não
- **Estratégia:** <descrição>
- **Custo ou risco de reversão:** <descrição>

## 12. Relação com decisões existentes

- <ADR-XXXX - relação>

Se este ADR pretender substituir outro, identifique explicitamente o ADR anterior.

Enquanto este ADR estiver `Proposed`, `Rejected` ou ainda não tiver atingido `Accepted`, o ADR anterior permanece com seu estado vigente.

O ADR anterior só pode mudar para `Superseded` depois que este ADR sucessor estiver `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | <parecer> | <pendências> |
| Frontend | <parecer> | <pendências> |
| Security & Tenant Isolation | <parecer> | <pendências> |
| Platform & Observability | <parecer> | <pendências> |
| QA & Quality | <parecer> | <pendências> |

Especialistas não aplicáveis devem permanecer identificados com justificativa.

## 14. Riscos não resolvidos

- <risco ou Nenhum>

Risco crítico não tratado bloqueia o aceite.

## 15. Histórico de revisão

| Data | Responsável | Ação | Resultado |
| --- | --- | --- | --- |
| YYYY-MM-DD | <responsável> | Proposta inicial | Proposed |

## 16. Revisão técnica

- **Parecer de `review-adr`:** <Pronto para aceite humano / Retornar para ajustes / Bloqueado>
- **Revisão decisória revisada:** <número>
- **Revisor:** Orchestrator / Tech Lead
- **Data:** YYYY-MM-DD
- **Pendências bloqueantes:** <Nenhuma / lista>
- **Pendências não bloqueantes:** <Nenhuma / lista>

Somente o parecer `Pronto para aceite humano`, acompanhado de **Nenhuma** pendência bloqueante, libera o gate de aceite humano.

O parecer só é válido quando `Revisão decisória revisada` é exatamente igual à `Revisão decisória` atual do ADR. Se o conteúdo decisório mudar depois do parecer, ele fica invalidado e uma nova revisão é obrigatória.

## 17. Aceite humano

- **Aceito:** Sim / Não
- **Responsável humano:** <nome ou papel>
- **Data:** YYYY-MM-DD ou Não aplicável
- **Revisão decisória aceita:** <número>
- **Registro do aceite:** <referência>

O status só pode ser alterado para `Accepted` quando **todas** as condições abaixo forem verdadeiras:

1. o `review-adr` emitiu `Pronto para aceite humano`;
2. não existe pendência bloqueante;
3. `Revisão decisória revisada` é igual à `Revisão decisória` atual;
4. `Revisão decisória aceita` é igual à revisão decisória favoravelmente revisada;
5. o aceite humano foi explicitamente registrado.

Se qualquer condição falhar, o ADR permanece fora de `Accepted`.
