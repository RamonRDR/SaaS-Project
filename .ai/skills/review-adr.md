# Skill `review-adr`

## Missão

Revisar uma proposta de ADR quanto à necessidade, consistência arquitetural, alternativas, consequências e compatibilidade com decisões vigentes.

## Quando usar

Usar antes de qualquer ADR assumir estado aceito.

## Agentes autorizados

- Orchestrator / Tech Lead.

Especialistas técnicos impactados fornecem pareceres, mas não autoaceitam a decisão.

## Template oficial

A revisão deve usar `docs/adr/ADR-TEMPLATE.md` como referência estrutural e validar o lifecycle do ADR.

Um ADR só pode chegar a `Accepted` quando:

- o parecer técnico atual for `Pronto para aceite humano`;
- não existir pendência bloqueante;
- houver aceite humano explícito.

## Entradas obrigatórias

- ADR proposto;
- revisão decisória atual do ADR;
- ADRs vigentes relacionados;
- arquitetura atual;
- SDDs relacionadas;
- pareceres dos especialistas impactados;
- restrições técnicas e de produto.

## Procedimento

1. confirmar aderência ao template oficial, identificador, status, revisão decisória e rastreabilidade;
2. confirmar que a decisão realmente exige ADR;
3. verificar contexto, drivers e restrições;
4. verificar se alternativas relevantes foram consideradas de forma comparável;
5. verificar consequências e trade-offs;
6. verificar compatibilidade com arquitetura vigente;
7. verificar impacto em segurança, multi-tenancy e operação;
8. verificar impacto em dados, API e integrações;
9. verificar migração, rollout e reversibilidade;
10. verificar pareceres dos especialistas impactados;
11. verificar necessidade de superseder ADR anterior;
12. registrar pendências e classificá-las como bloqueantes ou não bloqueantes;
13. registrar explicitamente a revisão decisória avaliada;
14. emitir um dos pareceres: `Pronto para aceite humano`, `Retornar para ajustes` ou `Bloqueado`;
15. encaminhar para aceite humano somente quando o parecer for `Pronto para aceite humano`, não houver pendência bloqueante e a revisão decisória revisada for exatamente igual à revisão decisória atual.

## Outputs esperados

- parecer de revisão;
- revisão decisória efetivamente revisada;
- pendências bloqueantes e não bloqueantes;
- recomendação de pronto para aceite humano, retorno para revisão ou bloqueio.

## Não faz

- não aceita o ADR em nome do humano;
- não oculta conflito com decisão anterior;
- não rebaixa risco técnico sem justificativa;
- não encaminha ADR bloqueado ou com ajustes pendentes para aceite humano;
- não reutiliza parecer favorável emitido para revisão decisória anterior.

## Condições de parada

Parar quando:

- faltar opção relevante;
- houver conflito arquitetural não resolvido;
- especialista obrigatório não tiver contribuído;
- riscos críticos não estiverem tratados.

## Gates humanos

O gate humano só é aberto após parecer `Pronto para aceite humano`, ausência de pendências bloqueantes e correspondência exata entre a revisão decisória revisada e a revisão decisória atual.

Qualquer mudança material no conteúdo decisório após o parecer incrementa a revisão decisória, invalida o parecer anterior e exige nova execução de `review-adr`.

Somente aprovação humana explícita, após esse parecer favorável, muda o ADR para estado `Accepted`.

## Critério de conclusão

A skill termina com um parecer técnico rastreável e vinculado à revisão decisória avaliada. O caminho para aceite humano só fica liberado quando o resultado for `Pronto para aceite humano`, não houver pendência bloqueante e a revisão revisada coincidir com a revisão atual; nos demais casos, o ADR retorna para ajustes ou permanece bloqueado.
