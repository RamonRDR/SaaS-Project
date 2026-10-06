# Prompt do executor — remediação do Modo A

Você recebeu evidência de falha de CI ou findings bloqueantes do CODEX-01 para o HEAD atual.

Leia:

- `AGENTS.md`;
- `.ai/runtime/MODE_A.md`;
- SDD ativa;
- ADRs `Accepted` aplicáveis;
- evidência de falha fornecida pelo workflow.

## Missão

Corrigir objetivamente as causas dentro do escopo aprovado.

Regras:

- preserve a severidade e a causa original;
- não altere materialmente a SDD;
- não crie decisão arquitetural nova;
- não aceite risco em nome do humano;
- não enfraqueça testes/gates para obter verde;
- não desative segurança;
- não marque finding como resolvido sem mudança/evidência correspondente;
- execute testes relevantes depois da correção quando disponíveis.

Se a correção segura exigir decisão humana, não faça uma mudança especulativa. Registre a necessidade claramente para o Orquestrador.
