# Skill `impact-analysis`

## Missão

Avaliar de forma estruturada os impactos de uma solicitação antes de qualquer decisão de implementação.

## Quando usar

Usar no início de toda entrega relevante e sempre que o escopo mudar durante a execução.

## Agentes autorizados

- Orchestrator / Tech Lead;
- Product & SDD.

Outros especialistas podem fornecer insumos, mas não substituem a coordenação do Orquestrador.

## Entradas obrigatórias

- objetivo solicitado;
- contexto funcional disponível;
- estado atual do projeto;
- branch e entrega em andamento;
- SDD existente, quando houver;
- ADRs relacionados, quando houver.

## Pré-condições

- contexto mínimo suficiente para entender a intenção;
- fontes de verdade relevantes acessíveis;
- nenhuma decisão bloqueante já conhecida sendo ignorada.

## Procedimento

1. identificar o comportamento de produto afetado;
2. avaliar impacto em backend;
3. avaliar impacto em frontend;
4. avaliar impacto em dados e migrations;
5. avaliar impacto em contratos de API;
6. avaliar autenticação, autorização e multi-tenancy;
7. avaliar segurança, privacidade e dados sensíveis;
8. avaliar observabilidade;
9. avaliar testes e evidências;
10. avaliar infraestrutura, ambientes e deploy;
11. avaliar integrações externas;
12. identificar breaking changes;
13. identificar necessidade de ADR;
14. identificar gates de aprovação humana;
15. registrar dependências, riscos e dúvidas abertas;
16. recomendar agentes e skills necessários.

## Outputs esperados

- matriz ou resumo de impactos;
- lista de agentes necessários;
- lista de skills necessárias;
- riscos identificados;
- gates humanos aplicáveis;
- decisão sobre necessidade de SDD nova/revisada;
- decisão sobre necessidade de ADR;
- dúvidas bloqueantes.

## Não faz

- não implementa código;
- não aprova escopo;
- não cria decisão arquitetural por conta própria;
- não substitui Security Review ou QA.

## Condições de parada

Parar quando:

- o objetivo estiver ambíguo a ponto de alterar materialmente a solução;
- existir conflito entre fontes de verdade;
- o impacto revelar mudança material de escopo;
- surgir decisão arquitetural sem autoridade para defini-la;
- um gate humano obrigatório for identificado e ainda estiver pendente.

## Gates humanos

A análise deve apontar explicitamente qualquer gate humano necessário, mas não pode considerá-lo aprovado sem registro real.

## Critério de conclusão

A skill termina quando existe uma visão rastreável dos domínios afetados, dos especialistas necessários, dos riscos, dos gates e da necessidade de SDD/ADR.
