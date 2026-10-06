# ADR-0010 - Adotar GitHub Actions, PR obrigatório e squash merge como política de CI/CD

## Metadados

- **ID:** ADR-0010
- **Título:** Adotar GitHub Actions, PR obrigatório e squash merge como política de CI/CD
- **Status:** Accepted
- **Revisão decisória:** 1
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0006, ADR-0009
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

O repositório é privado no GitHub e a governança já exige PR, Codex Review no HEAD final, gates de qualidade e validação antes de merge. Ainda falta formalizar o mecanismo de CI/CD e a política de merge.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- automação próxima ao repositório
- rastreabilidade entre commit, checks e deploy
- main estável
- feedback rápido
- enforcement progressivo de gates

## 3. Restrições

- Codex Review é obrigatório em todo PR
- checks obrigatórios falhando bloqueiam merge
- branch protection técnica pode depender do plano disponível
- staging antecede produção em mudanças relevantes

## 4. Opções consideradas

### Opção A - GitHub Actions + PR + squash merge

**Descrição**

Usar workflows GitHub Actions para CI/CD, branches curtas, PR obrigatório e squash merge na main.

**Vantagens**

- integração nativa com repositório
- histórico da main limpo
- boa rastreabilidade

**Desvantagens**

- dependência operacional do GitHub Actions

**Riscos**

- gates apenas documentais enquanto branch protection não puder ser tecnicamente habilitada

**Impacto operacional / migração**

- workflows versionados no repositório e checks por PR

### Opção B - CI externo

**Descrição**

Usar outro provedor para pipelines e deploy.

**Vantagens**

- recursos especializados possíveis

**Desvantagens**

- mais credenciais, integração e superfícies externas sem necessidade atual

**Riscos**

- complexidade operacional

**Impacto operacional / migração**

- serviço adicional crítico

### Opção C - Processo manual inicialmente

**Descrição**

Executar testes/build/deploy manualmente.

**Vantagens**

- nenhuma configuração inicial

**Desvantagens**

- inconsistência e baixa rastreabilidade

**Riscos**

- merge com validação esquecida

**Impacto operacional / migração**

- dependência de disciplina humana

## 5. Opção recomendada

- **Opção:** Opção A - GitHub Actions + PR + squash merge
- **Justificativa:** alinha o pipeline ao GitHub já adotado, automatiza a Definition of Done e mantém histórico de main simples. Onde a proteção técnica não estiver disponível, a governança processual continua obrigatória até poder ser automatizada.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- checks reproduzíveis em todo PR
- audit trail de CI e deploy
- squash reduz ruído de commits intermediários

### Negativas / trade-offs aceitos

- configuração inicial de workflows
- dependência do serviço GitHub Actions

### Novas obrigações

- formatter/lint/type checking
- testes backend e Flutter conforme existirem
- validação de migrations
- dependency/security scan
- secret scan
- build
- Codex Review do HEAD final
- nenhum commit mutável após review final antes do PRE_MERGE
- deploy de staging para validação quando aplicável
- produção com aprovação adequada
- main sem desenvolvimento direto

## 7. Impacto em segurança e multi-tenancy

Secrets de CI usam mecanismos seguros do GitHub/ambiente. Workflows de PR externo, quando existirem, não recebem secrets privilegiados por padrão.

## 8. Impacto em dados e API

Sem impacto direto nos contratos. Migrations e breaking changes têm gates adicionais conforme AGENTS.md.

## 9. Impacto operacional e observabilidade

Pipelines produzem evidência de checks e artefatos. Deploy deve ser rastreável ao commit/imagem e integrado à observabilidade.

## 10. Migração e rollout

Criar workflows à medida que backend/frontend forem bootstrapados. A política de PR e Codex já vigora antes da automação completa.

## 11. Rollback / reversibilidade

- **Reversível:** Sim
- **Estratégia:** Outro provedor CI pode substituir Actions mantendo os mesmos gates definidos neste ADR.
- **Custo ou risco de reversão:** baixo se gates forem descritos por resultado esperado e não por detalhes proprietários.

## 12. Relação com decisões existentes

- Automatiza controles relacionados aos ambientes do ADR-0006 e observabilidade do ADR-0009.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Adicionar checks quando bootstrap existir |
| Frontend | Favorável | Adicionar Flutter analyze/test/build |
| Security & Tenant Isolation | Favorável | Secret/dependency/security scans |
| Platform & Observability | Favorável | GitHub Actions como baseline |
| QA & Quality | Favorável | Gates reproduzíveis antes do merge |

## 14. Riscos não resolvidos

- Nenhum risco bloqueante identificado na revisão decisória 1.

## 15. Histórico de revisão

| Data | Responsável | Ação | Resultado |
| --- | --- | --- | --- |
| 2026-10-01 | Product & SDD | Proposta inicial | Proposed |
| 2026-10-01 | Orchestrator / Tech Lead | Revisão técnica da revisão decisória 1 | Pronto para aceite humano |
| 2026-10-01 | Responsável do projeto | Aceite humano explícito da revisão decisória 1 | Accepted |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pronto para aceite humano
- **Revisão decisória revisada:** 1
- **Revisor:** Orchestrator / Tech Lead
- **Data:** 2026-10-01
- **Pendências bloqueantes:** Nenhuma
- **Pendências não bloqueantes:** A proteção automática de branch continua condicionada às capacidades do plano do repositório; enquanto indisponível, a regra permanece operacional e auditável por PR.

O parecer técnico é válido somente para a revisão decisória 1.

## 17. Aceite humano

- **Aceito:** Sim
- **Responsável humano:** Responsável do projeto
- **Data:** 2026-10-01
- **Revisão decisória aceita:** 1
- **Registro do aceite:** aceite humano histórico registrado por `RamonRDR` em 2026-10-01; a evidência operacional original permanece no histórico privado anterior e não foi importada para este snapshot público.

As condições de aceite foram satisfeitas para a revisão decisória 1; o ADR está `Accepted`.
