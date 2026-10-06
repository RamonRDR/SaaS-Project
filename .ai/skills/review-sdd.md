# Skill `review-sdd`

## Missão

Verificar se uma SDD está completa, coerente, testável e compatível com as fontes de verdade antes da aprovação ou implementação.

## Quando usar

Usar após criação ou alteração material de uma SDD e antes de liberar implementação.

## Agentes autorizados

- Product & SDD;
- Orchestrator / Tech Lead.

O autor pode fazer auto-revisão inicial, mas a aprovação humana continua separada.

## Template oficial

A revisão deve usar `docs/specs/SDD-TEMPLATE.md` como referência estrutural. Seções marcadas como **Não aplicável** precisam conter justificativa suficiente.

## Entradas obrigatórias

- SDD candidata;
- versão atual da SDD;
- análise de impacto;
- documentação de produto relacionada;
- ADRs aplicáveis;
- estado atual do projeto.

## Procedimento

1. verificar aderência ao template oficial, metadados, lifecycle e justificativas de itens não aplicáveis;
2. verificar problema e objetivo;
3. verificar escopo e fora de escopo;
4. validar consistência das regras de negócio;
5. verificar critérios de aceite;
6. validar cobertura de casos de borda;
7. verificar impactos em dados e migrations;
8. verificar impacto de API e Flutter;
9. verificar permissões e multi-tenancy;
10. verificar segurança, privacidade e observabilidade;
11. verificar testes e evidências obrigatórias;
12. verificar rollback quando necessário;
13. verificar conflitos com ADRs;
14. verificar dependências, riscos e dúvidas abertas;
15. classificar pendências em bloqueantes ou não bloqueantes;
16. registrar explicitamente a versão da SDD revisada;
17. emitir um dos pareceres: `Pronta para aprovação`, `Necessita ajustes` ou `Bloqueada`;
18. liberar o gate humano somente quando o parecer for `Pronta para aprovação`, não houver pendência bloqueante e a versão revisada for exatamente igual à versão atual.

## Outputs esperados

- parecer de revisão;
- versão da SDD efetivamente revisada;
- pendências bloqueantes e não bloqueantes;
- lista de inconsistências;
- lista de lacunas;
- confirmação de prontidão para aprovação humana ou devolução para ajuste.

## Não faz

- não aprova a SDD em nome do humano;
- não altera silenciosamente requisito;
- não resolve decisão arquitetural sem ADR;
- não reutiliza parecer favorável emitido para versão anterior da SDD;
- não libera gate humano quando houver pendência bloqueante.

## Condições de parada

Parar quando houver:

- conflito documental material;
- decisão arquitetural pendente;
- requisito crítico indefinido;
- ausência de critério de aceite para comportamento relevante.

## Gates humanos

A revisão só pode declarar a SDD `Pronta para aprovação` para a versão explicitamente revisada e sem pendências bloqueantes.

Qualquer mudança material posterior incrementa a versão, invalida o parecer anterior e exige nova execução de `review-sdd`.

Somente o responsável humano pode aprovar a mesma versão favoravelmente revisada.

## Critério de conclusão

A skill termina com parecer explícito e vinculado à versão revisada. O gate humano só fica liberado quando o resultado for `Pronta para aprovação`, não houver pendência bloqueante e a versão revisada coincidir com a versão atual.
