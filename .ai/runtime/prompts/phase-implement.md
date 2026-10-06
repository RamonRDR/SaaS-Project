# Prompt do executor — implementação de fase em Modo A

Você está retomando uma fase governada após aprovação humana da SDD.

Leia obrigatoriamente:

1. `AGENTS.md`;
2. `.ai/runtime/MODE_A.md`;
3. `docs/PROJECT_STATUS.md`;
4. a SDD ativa em `docs/specs/<PHASE>.md`;
5. todos os ADRs `Accepted` relacionados;
6. `docs/engineering/DEFINITION_OF_DONE.md`;
7. `docs/engineering/CI_GATES.md`;
8. agentes e skills relevantes.

## Missão desta etapa

Implementar integralmente o escopo aprovado da SDD até o ponto em que o pull request possa entrar no review loop.

Você deve:

- registrar na SDD a evidência da aprovação humana fornecida pelo workflow, sem afirmar que o comentário foi digitado no GitHub pelo humano;
- implementar somente o escopo aprovado;
- acionar conceitualmente os especialistas aplicáveis de Backend, Frontend, QA, Security/Tenant Isolation, Platform/Observability e Docs/Release;
- criar ou atualizar testes;
- criar um entrypoint executável `.github/scripts/run_ci.sh` para os checks técnicos locais da entrega;
- materializar os gates técnicos que se tornarem aplicáveis;
- manter documentação consistente;
- executar os testes/checks disponíveis no ambiente;
- não marcar a fase como `completed` no PR principal.

## Paradas obrigatórias

Não improvise quando a implementação exigir:

- ADR novo ou alteração material de ADR `Accepted`;
- mudança material da SDD;
- migration destrutiva;
- breaking change inevitável;
- decisão sensível de autenticação, autorização ou tenant isolation;
- fornecedor externo pago/regulado/sensível;
- operação irreversível;
- aceitação de risco.

Nesses casos, preserve o repositório em estado coerente e registre claramente a decisão pendente em vez de inventar uma solução.
