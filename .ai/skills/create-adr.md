# Skill `create-adr`

## Missão

Documentar uma decisão arquitetural relevante de forma comparável, rastreável e preparada para revisão técnica e aceite humano.

## Quando usar

Usar quando uma decisão técnica tiver impacto durável, transversal, difícil de reverter ou alterar princípios arquiteturais vigentes.

## Agentes autorizados

- Product & SDD, quando autorizado pelo Orquestrador para preparar a proposta.

O Orchestrator / Tech Lead coordena a necessidade, os handoffs e a revisão do ADR, mas não executa `create-adr` no lugar do agente autorizado.

Especialistas impactados devem fornecer contexto técnico.

## Template oficial

Toda execução deve usar `docs/adr/ADR-TEMPLATE.md` como base. O status inicial é `Proposed`; somente revisão técnica seguida de aceite humano pode produzir `Accepted`.

Se uma seção obrigatória não se aplicar, registrar **Não aplicável** com justificativa.

## Entradas obrigatórias

- contexto da decisão;
- problema arquitetural;
- restrições;
- opções reais consideradas;
- impactos conhecidos;
- especialistas envolvidos.

## Procedimento

1. copiar o template oficial sem eliminar seções obrigatórias;
2. atribuir identificador ADR único;
3. registrar status inicial como `Proposed` e revisão decisória inicial como `1`;
4. documentar contexto, drivers e restrições;
5. descrever opções consideradas de forma comparável;
6. registrar prós, contras e riscos de cada opção;
7. registrar opção recomendada sem tratá-la como aceita;
8. registrar consequências e novas obrigações;
9. registrar impactos em segurança, multi-tenancy, dados, API e operação;
10. registrar migração, rollout e reversibilidade;
11. registrar relação com SDDs e ADRs existentes, sem marcar ADR anterior como `Superseded` antes de o sucessor atingir `Accepted`;
12. registrar pareceres dos especialistas impactados;
13. encaminhar para `review-adr`.

## Outputs esperados

- ADR proposto;
- alternativas comparáveis;
- consequências explícitas;
- links para artefatos relacionados;
- revisão decisória inicial registrada.

## Não faz

- não aceita a própria decisão;
- não omite alternativas relevantes apenas para justificar uma escolha;
- não substitui aprovação humana;
- não autoriza o Orquestrador a assumir a autoria operacional da skill;
- não marca ADR vigente como `Superseded` enquanto o sucessor ainda não estiver `Accepted`.

## Condições de parada

Parar quando:

- não houver contexto técnico suficiente;
- existir conflito com ADR aceita sem plano explícito de supersessão;
- uma opção essencial não puder ser avaliada;
- a decisão exigir especialista ainda não envolvido.

## Gates humanos

O ADR só pode se tornar aceito após revisão técnica e aprovação humana explícita.

## Critério de conclusão

A skill termina quando o ADR proposto está completo e pronto para `review-adr`.
