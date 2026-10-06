# Engenharia

Este diretório contém contratos operacionais transversais que transformam a governança do projeto em critérios verificáveis.

## Fontes oficiais

- [Definition of Done](./DEFINITION_OF_DONE.md)
- [Catálogo de gates de CI e release](./CI_GATES.md)

## Relação com outras fontes

- `AGENTS.md` define as regras globais;
- SDDs definem o escopo e os critérios de aceite de cada entrega;
- ADRs definem decisões arquiteturais;
- este diretório define **quando uma entrega pode avançar entre os gates e ser considerada DONE**;
- `.ai/skills/validate-definition-of-done.md` executa este contrato.

Quando houver conflito, uma regra mais específica pode ser mais restritiva, mas nunca pode remover um gate global obrigatório sem decisão humana registrada e, quando arquitetural, ADR aplicável.
