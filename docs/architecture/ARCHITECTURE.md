# Arquitetura

**Status: Baseline aprovada**

Esta baseline consolida as decisões arquiteturais aceitas na PHASE-0-E. Os ADRs individuais permanecem como fonte de verdade para contexto, alternativas, trade-offs e consequências.

## Baseline aceita

- **ADR-0001:** monólito modular com Django como arquitetura inicial;
- **ADR-0002:** Flutter como frontend multiplataforma principal, com Web/PWA para acesso sem instalação e possibilidade de superfície web pública específica se SEO ou performance justificarem nova decisão;
- **ADR-0003:** PostgreSQL como banco transacional e fonte persistente, preservando portabilidade entre provedores;
- **ADR-0004:** multi-tenancy em banco e schema compartilhados, com tenant explícito e contexto autorizado obrigatório em toda operação;
- **ADR-0005:** Django REST Framework como camada principal da API REST, mantendo regras de domínio fora de serializers, views e viewsets;
- **ADR-0006:** Docker no backend, com ambientes Development, Staging e Production separados e rollback condicionado à compatibilidade de migrations;
- **ADR-0007:** n8n restrito à orquestração de automações e integrações, sem atuar como backend paralelo nem acessar diretamente o banco do produto;
- **ADR-0008:** autenticação Django com access token curto e refresh token de uso único, rotativo, revogável e protegido contra reuso;
- **ADR-0009:** observabilidade desde o primeiro vertical slice, com logs estruturados por allowlist, correlation/request IDs, health checks, captura centralizada de exceções e auditoria de negócio separada;
- **ADR-0010:** GitHub Actions como baseline de CI/CD, pull request obrigatório, squash merge e Codex Review válido somente para o HEAD final.

## Princípios resultantes

- o estabelecimento/workspace é a fronteira principal de isolamento;
- regras críticas de negócio pertencem ao backend;
- PostgreSQL é a fonte de verdade dos dados do produto;
- Flutter, n8n e provedores externos não são autoridades finais de regra de domínio;
- nenhuma operação deve confiar em tenant enviado apenas pelo cliente;
- segurança, testes, observabilidade e documentação fazem parte da entrega;
- complexidade arquitetural deve crescer somente quando requisitos ou métricas justificarem;
- mudanças materiais nessas decisões exigem ADR sucessor conforme o lifecycle oficial.

## Relação com implementação

Esta baseline autoriza o planejamento das próximas etapas de fundação, mas não substitui SDD, Definition of Done, gates de CI ou aprovação humana exigidos pelo repositório.

A implementação tecnológica continua condicionada aos marcos subsequentes definidos em `docs/PROJECT_STATUS.md`.

## Política de linguagem

A documentação arquitetural deve ser escrita em português do Brasil.

Identificadores técnicos, exemplos de código, nomes de classes, funções, módulos e contratos técnicos permanecem em inglês.
