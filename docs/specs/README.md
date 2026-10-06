# Especificações

O desenvolvimento de features é orientado por Software Design Documents (SDDs).

Cada entrega significativa deve possuir uma SDD aprovada antes da implementação.

## Template oficial

Toda nova SDD deve partir de:

- `docs/specs/SDD-TEMPLATE.md`

Se uma seção não se aplicar, usar **Não aplicável** com justificativa.

## Convenção de nomes

Formato:

`SDD-XXXX-slug-curto.md`

Exemplo:

`SDD-0001-agendamento-multisservico.md`

O identificador permanece estável durante toda a vida da especificação.

## Lifecycle

1. `Draft`
2. `In Review`
3. `Approved`
4. `Superseded`

O estado `Approved` exige cumulativamente:

- parecer `Pronta para aprovação`;
- nenhuma pendência bloqueante;
- versão revisada igual à versão atual;
- versão aprovada igual à versão favoravelmente revisada;
- aprovação humana explícita.

Parecer `Necessita ajustes` ou `Bloqueada` impede `Approved`.

## Versionamento e invalidação

As seções 1 a 24 do template formam o conteúdo material da SDD.

Qualquer mudança material nesse conteúdo:

- incrementa `Versão`;
- invalida o parecer de revisão anterior;
- invalida aprovação humana anterior para a nova versão;
- mantém ou devolve a SDD para `Draft`;
- exige novo `review-sdd` e novo gate humano antes de `Approved`.

O parecer deve registrar a versão revisada, e a aprovação humana deve registrar a mesma versão.

Quando uma mudança representar nova entrega ou substituir substancialmente a intenção anterior, o Orquestrador pode exigir uma nova SDD sucessora.

## Supersessão

Uma SDD sucessora pode referenciar uma SDD vigente enquanto ainda está `Draft` ou `In Review`, mas isso não altera o estado da anterior.

A SDD anterior só pode mudar para `Superseded` depois que a sucessora atingir `Approved`.

Se a sucessora for abandonada ou permanecer sem aprovação, a SDD anterior mantém seu estado vigente.

## Responsabilidades

- Product & SDD cria e mantém a SDD;
- `create-sdd` governa a criação;
- `review-sdd` governa a revisão;
- Orchestrator / Tech Lead coordena o gate;
- o responsável humano aprova.

A SDD não substitui ADR para decisões arquiteturais duráveis.

## Idioma

Conteúdo em português do Brasil. Identificadores técnicos e exemplos de código permanecem em inglês conforme `docs/LANGUAGE_POLICY.md`.


## Catálogo público atual

| SDD | Entrega | Versão | Status |
| --- | --- | ---: | --- |
| [SDD-0001](./SDD-0001-runtime-unattended-mode-a.md) | Runtime unattended cloud-native do Mode A | 0.2 | `In Review` |

A versão experimental 0.1 da SDD-0001 pertence ao histórico privado anterior e não foi importada para o snapshot público. O ID foi preservado para manter continuidade documental.
