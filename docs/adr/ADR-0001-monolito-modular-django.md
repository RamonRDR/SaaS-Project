# ADR-0001 - Adotar monólito modular com Django como arquitetura inicial

## Metadados

- **ID:** ADR-0001
- **Título:** Adotar monólito modular com Django como arquitetura inicial
- **Status:** Accepted
- **Revisão decisória:** 1
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0008, ADR-0009
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

O produto precisa suportar agenda, CRM, clientes, profissionais, serviços, financeiro, estoque e integrações sem assumir a complexidade operacional de sistemas distribuídos antes de existir escala que a justifique. A direção baseline já estabelece Django e preferência por monólito modular.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- simplicidade operacional na fase inicial
- fronteiras claras por domínio
- alta testabilidade
- baixo custo de coordenação e deploy
- evolução futura sem impedir extração de módulos

## 3. Restrições

- backend principal em Python/Django
- regras críticas permanecem no backend
- produto nasce multi-tenant
- complexidade só deve crescer quando houver necessidade comprovada

## 4. Opções consideradas

### Opção A - Monólito modular Django

**Descrição**

Uma aplicação Django implantável como uma unidade, organizada por módulos de domínio com fronteiras explícitas.

**Vantagens**

- menor complexidade operacional
- transações locais simples
- debug e testes integrados mais diretos
- boa aderência ao estágio do produto

**Desvantagens**

- exige disciplina para evitar acoplamento entre módulos
- escala de deploy é conjunta

**Riscos**

- o monólito degradar para estrutura sem fronteiras

**Impacto operacional / migração**

- um backend principal e uma pipeline de deploy

### Opção B - Microsserviços desde a fundação

**Descrição**

Separar domínios em serviços independentes desde o início.

**Vantagens**

- isolamento de deploy
- escala independente por serviço

**Desvantagens**

- rede, observabilidade e consistência distribuída mais complexas
- maior custo de desenvolvimento e operação

**Riscos**

- complexidade prematura e contratos distribuídos frágeis

**Impacto operacional / migração**

- múltiplos serviços, pipelines, bancos ou esquemas e observabilidade distribuída

### Opção C - Serviços/serverless por caso de uso

**Descrição**

Dividir funcionalidades em funções ou pequenos serviços independentes.

**Vantagens**

- elasticidade pontual
- deploy isolado de pequenas funções

**Desvantagens**

- fragmenta regras de domínio
- aumenta dependência de infraestrutura e integração

**Riscos**

- regra de negócio espalhada e difícil de rastrear

**Impacto operacional / migração**

- mais componentes e contratos operacionais

## 5. Opção recomendada

- **Opção:** Opção A - Monólito modular Django
- **Justificativa:** preserva simplicidade e transações locais, atende a direção baseline e mantém uma rota de extração futura caso escala ou isolamento operacional justifiquem.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- entrega inicial mais rápida sem sacrificar modularidade
- uma única fonte de regras de domínio
- menor superfície operacional

### Negativas / trade-offs aceitos

- deploy conjunto
- disciplina arquitetural obrigatória para impedir dependências cruzadas indevidas

### Novas obrigações

- módulos separados por domínio
- interfaces internas explícitas quando módulos se comunicarem
- testes de fronteira e regressão
- ADR sucessor antes de extrair um módulo para serviço independente

## 7. Impacto em segurança e multi-tenancy

A arquitetura não reduz a exigência de autorização e isolamento de tenant. Todo módulo que manipule dados de domínio deve receber contexto de tenant validado no backend.

## 8. Impacto em dados e API

Os módulos podem compartilhar a mesma instância PostgreSQL, mantendo ownership lógico das tabelas. A API pública será REST e não deve expor detalhes internos entre módulos.

## 9. Impacto operacional e observabilidade

Um deploy principal simplifica health checks, logs, captura de exceções e rollback. Métricas por módulo/operação devem permitir identificar hotspots antes de qualquer extração.

## 10. Migração e rollout

Começar com projeto Django modular. Extrações futuras exigem métricas, motivação concreta e ADR sucessor.

## 11. Rollback / reversibilidade

- **Reversível:** Parcialmente
- **Estratégia:** Enquanto não houver extração de serviços, módulos podem ser reorganizados internamente preservando contratos.
- **Custo ou risco de reversão:** extrair um módulo depois que houver acoplamento excessivo pode ser caro; por isso as fronteiras precisam existir desde a fundação.

## 12. Relação com decisões existentes

- Define a estrutura na qual os ADRs de dados, tenancy, API, autenticação e observabilidade serão aplicados.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Nenhuma |
| Frontend | Não aplicável diretamente | Consome a API comum |
| Security & Tenant Isolation | Favorável | Preservar tenant context em todos os módulos |
| Platform & Observability | Favorável | Uma unidade de deploy inicialmente |
| QA & Quality | Favorável | Cobrir fronteiras de domínio |

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
