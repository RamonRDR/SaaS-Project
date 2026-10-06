# Prompt do executor — CODEX-01 do Modo A

Faça uma revisão somente leitura do HEAD atual em relação à base do PR.

Leia:

- `AGENTS.md`;
- `.ai/runtime/MODE_A.md`;
- SDD ativa;
- ADRs `Accepted` aplicáveis;
- `docs/engineering/DEFINITION_OF_DONE.md`;
- `docs/engineering/CI_GATES.md`;
- contrato congelado de review disponível no PR quando fornecido pelo workflow.

Avalie apenas problemas concretos que possam bloquear o contrato atual.

Classifique como finding bloqueante somente:

- P0: risco crítico/imediato;
- P1: risco alto, bypass de gate, segurança, autorização, privacidade, integridade ou arquitetura obrigatória;
- P2: defeito material de correção, consistência, confiabilidade ou governança que precise ser resolvido antes do merge.

Não transforme em bloqueio:

- preferência de estilo;
- hardening sem defeito concreto;
- ampliação de escopo;
- redesign opcional;
- melhoria futura que não viola o contrato aprovado.

Esses itens devem ir para `follow_ups`.

A saída deve seguir exatamente o schema fornecido pelo workflow.
