# ADR-0009 - Adotar baseline de observabilidade desde o primeiro vertical slice

## Metadados

- **ID:** ADR-0009
- **Título:** Adotar baseline de observabilidade desde o primeiro vertical slice
- **Status:** Accepted
- **Revisão decisória:** 2
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0001, ADR-0006, ADR-0007, ADR-0010
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

O projeto define observabilidade como parte da feature, não tarefa posterior. O primeiro vertical slice precisa de logs estruturados, correlation/request IDs, health checks, captura centralizada de exceções e auditoria separada de logs técnicos.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- diagnóstico de falhas
- rastreabilidade de integrações
- segurança de logs
- operação de staging/produção
- evolução incremental para métricas e tracing

## 3. Restrições

- dados sensíveis não aparecem em logs
- auditoria de negócio é separada de logs técnicos
- tenant_id/user_id só quando seguro e aplicável
- não introduzir stack operacional excessiva cedo

## 4. Opções consideradas

### Opção A - Baseline estruturado incremental

**Descrição**

JSON/structured logging, request/correlation ID, health checks, captura centralizada de exceções e trilha de auditoria; métricas/tracing crescem com necessidade.

**Vantagens**

- alto valor com baixo overhead
- boa base para Django, n8n e provedores

**Desvantagens**

- não entrega tracing distribuído completo no dia 1

**Riscos**

- adiar métricas importantes por tempo demais

**Impacto operacional / migração**

- instrumentação mínima obrigatória em todo módulo novo

### Opção B - Apenas logs locais no início

**Descrição**

Usar logs simples e adicionar observabilidade depois.

**Vantagens**

- menor configuração inicial

**Desvantagens**

- diagnóstico fraco em staging/produção
- difícil correlacionar integrações

**Riscos**

- incidentes sem evidência

**Impacto operacional / migração**

- retrabalho posterior

### Opção C - Stack completa de métricas/tracing desde o início

**Descrição**

Implantar observabilidade distribuída completa antes do vertical slice.

**Vantagens**

- visibilidade máxima

**Desvantagens**

- complexidade e custo prematuros

**Riscos**

- infraestrutura dominar a fundação

**Impacto operacional / migração**

- coletores, storage, dashboards e alertas avançados

## 5. Opção recomendada

- **Opção:** Opção A - Baseline estruturado incremental
- **Justificativa:** cumpre os requisitos não negociáveis sem introduzir uma plataforma de observabilidade maior que o próprio produto.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- diagnóstico desde staging
- correlação entre backend e integrações
- evidência para QA e segurança

### Negativas / trade-offs aceitos

- métricas/tracing completos não estarão presentes inicialmente

### Novas obrigações

- logs estruturados
- request_id/correlation_id
- tratamento centralizado de exceções
- health endpoint
- captura de erro em Sentry ou equivalente
- política de logs por allowlist: somente campos operacionais previamente aprovados podem ser emitidos
- tokens, refresh tokens, senhas, secrets, Authorization headers, cookies, credenciais e conteúdo sensível de payload nunca podem ser registrados em logs técnicos
- identificadores operacionais permitidos devem ser mínimos e preferencialmente opacos; tenant_id/user_id só entram quando aprovados no schema de logging e sem dados pessoais associados
- eventos de negócio que exijam identidade ou contexto sensível pertencem à trilha de auditoria protegida, com minimização e controle de acesso
- auditoria de negócio separada
- definição explícita de novos sinais em cada SDD

## 7. Impacto em segurança e multi-tenancy

Logs técnicos seguem allowlist, não denylist. É proibido registrar tokens de acesso ou refresh, senhas, secrets, cabeçalhos de autorização, cookies, credenciais e conteúdo sensível de request/response, sem exceção genérica de diagnóstico.

A allowlist operacional pode conter, quando previamente aprovada: request_id, correlation_id, ambiente, módulo, operação, rota, método, status code, duração e identificadores internos opacos de tenant/usuário estritamente necessários. Nome, e-mail, telefone, conteúdo de mensagem e outros dados pessoais não entram automaticamente nessa allowlist.

Eventos de negócio que exijam contexto adicional devem ser registrados na trilha de auditoria protegida, com minimização, controle de acesso e retenção apropriada.

## 8. Impacto em dados e API

Erros da API têm correlation ID rastreável sem expor stack interna nem ecoar conteúdo sensível. Auditoria de ações relevantes referencia identidades e entidades de forma minimizada e controlada.

## 9. Impacto operacional e observabilidade

Health checks, erro centralizado e logs são obrigatórios desde o primeiro ambiente executável. Métricas e tracing entram progressivamente com sinais e SLOs reais.

## 10. Migração e rollout

Instrumentação baseline acompanha o bootstrap Django e o primeiro vertical slice.

## 11. Rollback / reversibilidade

- **Reversível:** Sim
- **Estratégia:** Ferramenta de captura centralizada pode ser trocada mantendo contratos de logging/correlation.
- **Custo ou risco de reversão:** baixo se a aplicação não acoplar regra de negócio ao fornecedor de observabilidade.

## 12. Relação com decisões existentes

- Complementa Docker/ambientes do ADR-0006, n8n do ADR-0007 e gates do ADR-0010.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Structured logging e error handler |
| Frontend | Favorável | Captura de erros de cliente quando aplicável |
| Security & Tenant Isolation | Favorável | Redação de dados sensíveis |
| Platform & Observability | Favorável | Baseline incremental |
| QA & Quality | Favorável | Evidência de falhas correlacionável |

## 14. Riscos não resolvidos

- Nenhum risco bloqueante identificado na revisão decisória 2.

## 15. Histórico de revisão

| Data | Responsável | Ação | Resultado |
| --- | --- | --- | --- |
| 2026-10-01 | Product & SDD | Proposta inicial | Proposed |
| 2026-10-01 | Orchestrator / Tech Lead | Revisão técnica da revisão decisória 1 | Parecer invalidado por alteração material posterior |
| 2026-10-01 | Product & SDD | Ajustes materiais após Codex Review | Revisão decisória 2 |
| 2026-10-01 | Orchestrator / Tech Lead | Revisão técnica da revisão decisória 2 | Pronto para aceite humano |
| 2026-10-01 | Responsável do projeto | Aceite humano explícito da revisão decisória 2 | Accepted |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pronto para aceite humano
- **Revisão decisória revisada:** 2
- **Revisor:** Orchestrator / Tech Lead
- **Data:** 2026-10-01
- **Pendências bloqueantes:** Nenhuma
- **Pendências não bloqueantes:** Fornecedor concreto de captura de erros permanece substituível; Sentry é opção inicial, não lock-in arquitetural.

O parecer técnico é válido somente para a revisão decisória 2.

## 17. Aceite humano

- **Aceito:** Sim
- **Responsável humano:** Responsável do projeto
- **Data:** 2026-10-01
- **Revisão decisória aceita:** 2
- **Registro do aceite:** aceite humano histórico registrado por `RamonRDR` em 2026-10-01; a evidência operacional original permanece no histórico privado anterior e não foi importada para este snapshot público.

As condições de aceite foram satisfeitas para a revisão decisória 2; o ADR está `Accepted`.
