# Catálogo de Skills

Skills são procedimentos reutilizáveis.

Agentes são papéis. Skills são capacidades que esses papéis executam.

Os nomes técnicos das skills permanecem em inglês. O conteúdo e as instruções internas são escritos em português do Brasil.

## Contrato mínimo de uma skill

Toda skill formalizada deve declarar:

- missão;
- quando usar;
- agentes autorizados;
- entradas obrigatórias;
- procedimento;
- outputs esperados;
- limites ou ações que não executa;
- condições de parada;
- gates humanos, quando aplicáveis;
- critério de conclusão.

## Skill Set V1 - núcleo formalizado

### Planejamento e especificação

- `impact-analysis` -> `impact-analysis.md`
- `create-sdd` -> `create-sdd.md`
- `review-sdd` -> `review-sdd.md`
- `create-adr` -> `create-adr.md`
- `review-adr` -> `review-adr.md`

### Segurança

- `review-multitenancy` -> `review-multitenancy.md`
- `review-security` -> `review-security.md`

### Plataforma e observabilidade

- `review-observability` -> `review-observability.md`

### Coordenação de PR e encerramento

- `manage-pr-review-loop` -> `manage-pr-review-loop.md`
- `validate-definition-of-done` -> `validate-definition-of-done.md`
- `update-project-status` -> `update-project-status.md`

## Skills previstas para expansão

### Backend

- `implement-django-feature`
- `design-api-contract`
- `create-migration`
- `write-backend-tests`
- `review-query-performance`

### Frontend

- `implement-flutter-feature`
- `consume-api-contract`
- `build-responsive-ui`
- `write-widget-tests`
- `review-accessibility`

### Qualidade

- `create-test-plan`
- `write-unit-tests`
- `write-integration-tests`
- `write-e2e-tests`
- `validate-acceptance-criteria`
- `produce-test-evidence`

### Segurança complementar

- `review-permissions`
- `threat-model`
- `review-secrets`
- `review-data-exposure`
- `review-sensitive-logging`

### Plataforma

- `dockerize-service`
- `configure-environment`
- `configure-ci`
- `add-health-check`
- `add-structured-logging`
- `configure-sentry`
- `prepare-deployment`

### Encerramento complementar

- `update-architecture-docs`
- `update-changelog`
- `prepare-release`

## Regra de evolução

Uma skill planejada só passa a fazer parte do núcleo formalizado quando possuir contrato próprio neste diretório.

Agentes podem referenciar skills planejadas em seus contratos para responsabilidades futuras, mas workflows ativos não devem depender de uma skill ainda não formalizada sem que o Orquestrador trate essa ausência como dependência de engenharia.
