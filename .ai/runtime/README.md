# Runtime de autonomia

Este diretório contém contratos e artefatos do runtime do Orquestrador.

## Modo disponível

- `MODE_A.md`: autonomia operacional alta com gates humanos materiais.

## Piloto atual

O piloto usa a conversa ativa do Orquestrador com o conector do GitHub como executor.

Isso significa que o Orquestrador pode realizar em sequência branch, documentação, implementação, PR, CI, Codex, remediação, merge e finalização enquanto a execução estiver ativa, pausando apenas nos estados humanos definidos no contrato.

Não existe promessa de execução em background no piloto interativo.

## Evolução futura

Os prompts e o schema deste diretório são preparados para um executor unattended, como GitHub Actions + Codex GitHub Action, sem mudar o contrato de governança.
