# ADR-0004 - Adotar multi-tenancy por banco e schema compartilhados com tenant explícito

## Metadados

- **ID:** ADR-0004
- **Título:** Adotar multi-tenancy por banco e schema compartilhados com tenant explícito
- **Status:** Accepted
- **Revisão decisória:** 1
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0001, ADR-0003, ADR-0008
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

O estabelecimento/workspace é a fronteira principal de isolamento. Clientes são únicos dentro do estabelecimento, profissionais possuem agendas próprias e nenhuma operação pode atravessar tenants sem autorização explícita. A estratégia concreta precisava ser decidida antes da modelagem definitiva.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- isolamento forte de dados
- simplicidade operacional inicial
- baixo custo por tenant
- consultas e migrations uniformes
- testabilidade sistemática contra acesso cross-tenant

## 3. Restrições

- nenhum tenant informado apenas pelo cliente pode ser confiado
- toda operação de domínio precisa de contexto autorizado de tenant
- falha cross-tenant é crítica
- produto começa como monólito modular em PostgreSQL

## 4. Opções consideradas

### Opção A - Banco e schema compartilhados com tenant_id

**Descrição**

Todos os dados pertencentes ao estabelecimento carregam relação explícita com tenant; o backend deriva/valida o tenant a partir da autenticação e membership.

**Vantagens**

- operação simples
- migrations únicas
- baixo custo por tenant
- boa aderência ao estágio inicial

**Desvantagens**

- isolamento depende de disciplina consistente em toda consulta
- índices e constraints precisam considerar tenant

**Riscos**

- consulta sem escopo causar vazamento cross-tenant

**Impacto operacional / migração**

- convenções obrigatórias de model/query/service e testes negativos

### Opção B - Schema por tenant

**Descrição**

Cada tenant utiliza schema PostgreSQL separado.

**Vantagens**

- isolamento lógico adicional

**Desvantagens**

- migrations e operação ficam mais complexas
- crescimento do número de schemas

**Riscos**

- drift e manutenção operacional

**Impacto operacional / migração**

- tooling específico de tenancy e migrations por schema

### Opção C - Banco por tenant

**Descrição**

Cada estabelecimento possui database próprio.

**Vantagens**

- isolamento físico forte
- backup/restauração por tenant

**Desvantagens**

- alto custo operacional e de conexões
- complexidade de provisioning e analytics

**Riscos**

- overhead desproporcional ao mercado inicial

**Impacto operacional / migração**

- orquestração e observabilidade multi-database

## 5. Opção recomendada

- **Opção:** Opção A - Banco e schema compartilhados com tenant_id
- **Justificativa:** oferece a melhor relação entre isolamento governado e simplicidade nesta fase, desde que tenant context, constraints e testes cross-tenant sejam obrigatórios em toda a arquitetura.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- baixo custo operacional
- migrations e observabilidade centralizadas
- fácil criação de novos tenants

### Negativas / trade-offs aceitos

- um erro de scoping pode ter alto impacto
- exige convenções de código e testes não opcionais

### Novas obrigações

- todo model tenant-owned possui referência explícita ao tenant
- tenant é derivado/validado no backend a partir da identidade e membership
- queries e serviços recebem/impõem tenant context
- uniqueness e índices incluem tenant quando a regra for por estabelecimento
- relações cross-tenant são rejeitadas
- testes sempre incluem Tenant A e Tenant B
- jobs, cache, uploads e auditoria preservam tenant context

## 7. Impacto em segurança e multi-tenancy

Esta é uma decisão de segurança. Nunca confiar em tenant_id recebido isoladamente do frontend. A autorização deve validar membership e permissões. PostgreSQL RLS pode ser avaliado futuramente como defesa adicional, mas não substitui o scoping da aplicação sem ADR sucessor.

## 8. Impacto em dados e API

IDs podem ser globais, mas nenhum endpoint pode resolver recurso somente por ID sem também aplicar tenant context autorizado. Dados globais, se existirem, precisam ser explicitamente classificados como não tenant-owned.

## 9. Impacto operacional e observabilidade

Logs podem incluir tenant_id somente quando seguro. Métricas e jobs devem permitir diagnóstico por tenant sem expor dados sensíveis.

## 10. Migração e rollout

Os primeiros models persistentes já devem nascer com o padrão de tenant ownership. Não haverá retrofit posterior como estratégia padrão.

## 11. Rollback / reversibilidade

- **Reversível:** Parcialmente
- **Estratégia:** Migrar para schema ou banco por tenant exigiria projeto de migração dedicado e ADR sucessor.
- **Custo ou risco de reversão:** mudança futura de estratégia é cara, por isso os limites de tenant precisam estar explícitos desde a primeira migration.

## 12. Relação com decisões existentes

- Apoia-se no PostgreSQL do ADR-0003 e na autenticação/membership do ADR-0008.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Criar abstrações de scoping sem esconder contexto |
| Frontend | Favorável | Nunca tratar tenant enviado pelo cliente como autoridade |
| Security & Tenant Isolation | Favorável | Testes cross-tenant obrigatórios |
| Platform & Observability | Favorável | Jobs/cache/logs precisam carregar contexto |
| QA & Quality | Favorável | Tenant A/Tenant B em cenários negativos |

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
- **Pendências não bloqueantes:** Nenhuma

O parecer técnico é válido somente para a revisão decisória 1.

## 17. Aceite humano

- **Aceito:** Sim
- **Responsável humano:** Responsável do projeto
- **Data:** 2026-10-01
- **Revisão decisória aceita:** 1
- **Registro do aceite:** PR #9, comentário humano imutável [#5933524532](https://github.com/RamonRDR/SaaS-Project/pull/9#issuecomment-5933524532), publicado por `RamonRDR` em 2026-10-01.

As condições de aceite foram satisfeitas para a revisão decisória 1; o ADR está `Accepted`.
