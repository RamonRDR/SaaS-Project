# Architecture Decision Records

ADRs registram decisões técnicas duráveis, incluindo contexto, opções avaliadas, trade-offs, decisão aceita e consequências.

## Template oficial

Todo novo ADR deve partir de:

- `docs/adr/ADR-TEMPLATE.md`

Se uma seção não se aplicar, usar **Não aplicável** com justificativa.

## Convenção de nomes

Formato:

`ADR-XXXX-slug-curto.md`

Exemplo:

`ADR-0001-monolito-modular-django.md`

O identificador nunca é reutilizado.

## Lifecycle

1. `Proposed`
2. `Accepted`
3. `Rejected`
4. `Superseded`
5. `Deprecated`

Fluxo:

`create-adr -> review-adr -> Pronto para aceite humano -> aceite humano -> Accepted`

Product & SDD prepara a proposta quando autorizado. Orchestrator / Tech Lead revisa tecnicamente.

O estado `Accepted` exige cumulativamente:

- parecer `Pronto para aceite humano`;
- nenhuma pendência bloqueante;
- aceite humano explícito.

Parecer `Retornar para ajustes` ou `Bloqueado` impede `Accepted` até nova revisão técnica favorável.

## Revisão decisória

Cada ADR possui uma `Revisão decisória`.

O conteúdo decisório corresponde às seções 1 a 14 do template.

Antes de `Accepted`, qualquer mudança material nesse conteúdo:

- incrementa a revisão decisória;
- invalida o parecer técnico anterior;
- mantém ou devolve o ADR para `Proposed`;
- exige novo `review-adr`.

O parecer favorável deve registrar exatamente qual revisão decisória foi revisada. O aceite humano só pode aceitar essa mesma revisão.

Depois de `Accepted`, o conteúdo decisório é histórico e não deve ser reescrito. Mudança material exige um novo ADR sucessor.

## ADRs da PHASE-0-E

O catálogo abaixo registra o estado atual de cada ADR individualmente. A fonte de verdade final continua sendo o próprio arquivo do ADR.

| ADR | Decisão | Revisão decisória | Parecer técnico atual | Status | Aceite humano |
| --- | --- | ---: | --- | --- | --- |
| [ADR-0001](./ADR-0001-monolito-modular-django.md) | Monólito modular Django | 1 | Pronto para aceite humano | `Accepted` | Registrado |
| [ADR-0002](./ADR-0002-flutter-frontend-multiplataforma.md) | Flutter frontend multiplataforma | 1 | Pronto para aceite humano | `Accepted` | Registrado |
| [ADR-0003](./ADR-0003-postgresql-banco-transacional.md) | PostgreSQL banco transacional | 2 | Pronto para aceite humano | `Accepted` | Registrado |
| [ADR-0004](./ADR-0004-estrategia-multitenancy.md) | Estratégia multi-tenancy | 1 | Pronto para aceite humano | `Accepted` | Registrado |
| [ADR-0005](./ADR-0005-django-rest-framework-api.md) | Django REST Framework para API | 2 | Pronto para aceite humano | `Accepted` | Registrado |
| [ADR-0006](./ADR-0006-docker-ambientes.md) | Docker e ambientes | 2 | Pronto para aceite humano | `Accepted` | Registrado |
| [ADR-0007](./ADR-0007-fronteiras-n8n.md) | Fronteiras do n8n | 1 | Pronto para aceite humano | `Accepted` | Registrado |
| [ADR-0008](./ADR-0008-autenticacao-sessao.md) | Autenticação e sessão | 2 | Pronto para aceite humano | `Accepted` | Registrado |
| [ADR-0009](./ADR-0009-observabilidade-baseline.md) | Observabilidade baseline | 2 | Pronto para aceite humano | `Accepted` | Registrado |
| [ADR-0010](./ADR-0010-ci-cd-merge.md) | CI/CD e merge | 1 | Pronto para aceite humano | `Accepted` | Registrado |

Os 10 ADRs iniciais possuem parecer técnico favorável e aceite humano explicitamente registrado no próprio documento.

**Evidência comum do gate humano:** os ADRs 0001–0010 foram migrados como baseline `Accepted`. O aceite humano histórico foi registrado por `RamonRDR` em 2026-10-01; a evidência operacional original permanece no histórico privado anterior e não foi importada para este snapshot público.

Quando uma revisão decisória mudar, esta tabela deve ser atualizada no mesmo fluxo documental para não divergir dos ADRs.

## Supersessão

Um ADR sucessor pode citar o ADR vigente enquanto ainda está `Proposed`, mas isso não altera o estado do ADR anterior.

O ADR anterior permanece vigente até que o sucessor cumpra todo o lifecycle e alcance `Accepted`.

Somente depois do sucessor estar `Accepted` o ADR anterior pode ser atualizado para `Superseded`, com referência explícita ao ADR que o substituiu.

Se o sucessor for `Rejected`, abandonado ou permanecer `Proposed`, o ADR anterior continua vigente.

Não editar o passado para fazer uma decisão antiga parecer compatível com a nova.

## Idioma

Conteúdo em português do Brasil. Identificadores técnicos e exemplos de código permanecem em inglês conforme `docs/LANGUAGE_POLICY.md`.


## IDs históricos não importados

- **ADR-0011:** ID consumido por experimento privado de runtime unattended posteriormente descartado. O documento original não foi importado para o snapshot público e o ID não pode ser reutilizado.

## Decisão em revisão

| ADR | Decisão | Revisão decisória | Parecer técnico atual | Status | Aceite humano |
| --- | --- | ---: | --- | --- | --- |
| [ADR-0012](./ADR-0012-github-actions-codex-runtime-unattended.md) | GitHub Actions + Codex como runtime unattended | 5 | Nova revisão pendente | `Proposed` | Pendente |
