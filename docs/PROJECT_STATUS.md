# Status do Projeto

## Projeto

SaaS Project — nome técnico temporário de uma plataforma SaaS multi-tenant para negócios de serviços.

## Fase atual

**Fase 0 — Fundação de Engenharia**

## Estado de governança automatizada

O bloco abaixo é reservado ao enforcement de CI.

<!-- GOV:PROJECT_STATUS:BEGIN -->
<!-- GOV:PHASE-0-F:completed -->
<!-- GOV:PHASE-0-G:planned -->
<!-- GOV:PROJECT_STATUS:END -->

## Estado atual

- repositório público iniciado a partir de snapshot de engenharia sanitizado;
- histórico operacional privado e experimentos descartados não fazem parte deste Git público;
- branch padrão: `main`;
- Phase 0A — fundação do repositório: concluída;
- Phase 0B — Agent System V1: concluída;
- Phase 0C — Skill System V1: concluída;
- Phase 0D — templates e lifecycle de SDD/ADR: concluída;
- Phase 0E — baseline arquitetural ADR-0001 a ADR-0010: concluída;
- Phase 0F — Definition of Done e gates de CI: concluída;
- Mode A interativo: operacional;
- runtime unattended anterior: experimento encerrado e não importado para o repositório público;
- novo runtime unattended: em redesenho para execução 100% cloud-native;
- backend de produto: não iniciado;
- frontend de produto: não iniciado;
- PHASE-0-G permanece planejada até a conclusão do novo runtime unattended.

## Baseline arquitetural vigente

- monólito modular em Django;
- Django REST Framework para API;
- Flutter como frontend multiplataforma;
- PostgreSQL como banco transacional;
- Docker para ambientes;
- n8n restrito a automações e integrações, fora das regras centrais de domínio;
- estratégia multi-tenant com isolamento explícito;
- autenticação e sessão definidas por ADR;
- observabilidade desde a fundação;
- CI/CD e política de merge definidas por ADR-0010;
- desenvolvimento orientado por SDD e ADR;
- revisão técnica e gates humanos para decisões materiais.

## Próximo marco

Redesenhar e validar o **runtime unattended do Mode A** com as seguintes premissas:

1. execução 100% online;
2. zero dependência de máquina local;
3. GitHub Actions no critical path da orquestração;
4. Codex como executor/reviewer de IA em jobs controlados;
5. fail-closed, idempotência, provenance e anti-loop;
6. merge principal sempre sujeito a autorização humana explícita;
7. validação E2E antes de liberar PHASE-0-G.

A especificação e a decisão arquitetural do novo runtime serão versionadas em uma nova SDD/ADR antes da implementação.

## Política pública

Este repositório é uma vitrine técnica e, ao mesmo tempo, o repositório de engenharia do projeto.

Não devem ser versionados:

- credenciais, tokens, chaves ou arquivos `.env`;
- dados pessoais ou dados de clientes;
- URLs de sessão privadas;
- logs operacionais sensíveis;
- artefatos locais;
- conteúdo copiado de fontes privadas sem autorização.

Consulte `SECURITY.md` e `CONTRIBUTING.md`.
