# Prompt do executor — início de fase em Modo A

Você está executando uma fase governada pelo Orquestrador em Modo A.

Leia obrigatoriamente, nesta ordem:

1. `AGENTS.md`;
2. `.ai/runtime/MODE_A.md`;
3. `docs/PROJECT_STATUS.md`;
4. `docs/architecture/ARCHITECTURE.md`;
5. ADRs `Accepted` aplicáveis;
6. `docs/specs/SDD-TEMPLATE.md`;
7. `.ai/skills/create-sdd.md`;
8. `.ai/skills/review-sdd.md`.

O identificador da fase e o objetivo são fornecidos pelo workflow.

## Missão desta etapa

Somente preparar a fase para aprovação humana da SDD.

Você deve:

- executar a análise de impacto;
- criar uma SDD completa a partir do template oficial;
- usar um caminho determinístico `docs/specs/<PHASE>.md`;
- revisar a própria SDD conforme `review-sdd`;
- registrar parecer `Pronta para aprovação` somente se não houver pendência bloqueante;
- atualizar `docs/PROJECT_STATUS.md` para refletir a fase como trabalho ativo;
- transicionar o marcador `GOV:<PHASE>:planned` para `GOV:<PHASE>:active` quando ele existir;
- manter fases posteriores em `planned`;
- manter a SDD sem aprovação humana fabricada.

## Proibido nesta etapa

- implementar Django, Flutter ou qualquer código de produto;
- aprovar a SDD em nome do humano;
- criar ou aceitar ADR silenciosamente;
- marcar a fase como concluída;
- alterar escopo material além do objetivo recebido;
- remover ou enfraquecer gates existentes.

Ao terminar, deixe o repositório em estado revisável para o gate humano de aprovação da SDD.
