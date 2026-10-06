# Skill `review-multitenancy`

## Missão

Verificar se uma alteração preserva corretamente as fronteiras entre tenants e evita leitura, escrita, inferência ou operação cross-tenant indevida.

## Quando usar

Usar em mudanças que afetem dados, consultas, APIs, permissões, jobs, uploads, cache, integrações ou qualquer recurso pertencente a tenant.

## Agentes autorizados

- Security & Tenant Isolation.

Backend e Platform podem fornecer evidências e contexto.

## Entradas obrigatórias

- SDD;
- modelo ou fluxo de dados afetado;
- endpoints ou serviços envolvidos;
- regras de autorização;
- implementação candidata quando existente.

## Procedimento

1. identificar o tenant owner de cada dado afetado;
2. verificar como o contexto de tenant é obtido;
3. verificar filtros de leitura;
4. verificar escopo de escrita;
5. verificar validação de relacionamentos;
6. verificar IDs previsíveis ou manipuláveis;
7. verificar jobs e tarefas assíncronas;
8. verificar uploads, storage e caminhos;
9. verificar cache e chaves;
10. verificar logs e evidências;
11. definir testes negativos cross-tenant;
12. classificar qualquer possibilidade de vazamento.

## Outputs esperados

- parecer de isolamento;
- riscos encontrados;
- testes obrigatórios;
- correções necessárias;
- bloqueio explícito quando houver risco relevante.

## Não faz

- não aceita acesso cross-tenant fora de decisão formal;
- não trata filtro apenas de frontend como controle suficiente;
- não substitui revisão de autorização geral.

## Condições de parada

Parar e bloquear quando houver possibilidade plausível de acesso cross-tenant não autorizado.

## Gates humanos

Mudança da estratégia de tenant isolation exige ADR e aprovação humana.

## Critério de conclusão

A skill termina quando o fluxo de tenant está explícito, testável e sem achado bloqueante pendente.
