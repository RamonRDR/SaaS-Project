# Skill `create-sdd`

## Missão

Transformar uma intenção de produto aprovada para refinamento em uma Software Design Document clara, testável e rastreável.

## Quando usar

Usar antes da implementação de qualquer feature ou alteração significativa de comportamento.

## Agentes autorizados

- Product & SDD.

O Orquestrador coordena a necessidade da SDD, mas não substitui este papel na especificação funcional.

## Template oficial

Toda execução deve usar `docs/specs/SDD-TEMPLATE.md` como base. Se uma seção obrigatória não se aplicar, registrar **Não aplicável** com justificativa; não remover silenciosamente a seção.

## Entradas obrigatórias

- problema ou oportunidade;
- objetivo;
- análise de impacto;
- contexto de produto;
- restrições conhecidas;
- decisões já aprovadas;
- ADRs vigentes aplicáveis.

## Pré-condições

- intenção suficientemente compreendida;
- escopo inicial definido;
- conflitos críticos de produto resolvidos ou explicitamente registrados.

## Procedimento

1. copiar o template oficial sem eliminar seções obrigatórias;
2. atribuir identificador único à SDD e iniciar `Versão` em `0.1`;
3. registrar contexto e problema;
4. registrar objetivo;
5. definir escopo;
6. definir fora de escopo;
7. documentar atores, jornadas, regras de negócio e permissões;
8. registrar multi-tenancy e impactos em dados;
9. registrar impactos em API e Flutter;
10. registrar integrações externas;
11. registrar requisitos de segurança e privacidade;
12. registrar requisitos de observabilidade;
13. registrar casos de borda e erros;
14. registrar migration e rollback;
15. registrar testes obrigatórios;
16. registrar critérios de aceite verificáveis;
17. registrar evidências esperadas;
18. registrar dependências e riscos;
19. registrar ADRs relacionados;
20. registrar dúvidas abertas;
21. manter histórico de revisão sem preencher ou simular o gate humano;
22. ao alterar materialmente uma SDD existente, incrementar `Versão`, invalidar parecer/aprovação anteriores para a nova versão e retornar o status para `Draft`;
23. encaminhar explicitamente a SDD para `review-sdd`.

## Outputs esperados

- SDD completa em português do Brasil;
- critérios de aceite objetivos;
- escopo e fora de escopo explícitos;
- dependências e riscos documentados;
- versão atual identificada;
- handoff explícito para `review-sdd`.

## Não faz

- não aprova a própria SDD;
- não implementa a solução;
- não toma decisão arquitetural durável no lugar de ADR;
- não transforma hipótese em requisito confirmado;
- não preserva `Approved` nem aprovação anterior após mudança material de versão;
- não marca SDD anterior como `Superseded` antes de a sucessora atingir `Approved`;
- não libera nem preenche o gate humano antes de parecer favorável de `review-sdd`.

## Condições de parada

Parar quando:

- existir ambiguidade material não resolvida;
- surgir conflito com ADR aceita;
- o escopo depender de decisão humana ainda pendente;
- requisito crítico não puder ser determinado.

## Gates humanos

`create-sdd` não abre diretamente o gate humano de aprovação.

O gate humano só pode ser aberto por `review-sdd` quando a versão atual receber parecer `Pronta para aprovação` e não houver pendência bloqueante.

## Critério de conclusão

A skill termina quando a SDD está completa, revisável, com versão identificada e formalmente encaminhada para `review-sdd`.

Ela não termina como pronta para aprovação humana; essa transição pertence a `review-sdd`.
