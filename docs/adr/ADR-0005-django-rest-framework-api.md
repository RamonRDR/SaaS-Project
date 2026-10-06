# ADR-0005 - Adotar Django REST Framework para a API REST

## Metadados

- **ID:** ADR-0005
- **Título:** Adotar Django REST Framework para a API REST
- **Status:** Accepted
- **Revisão decisória:** 2
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0001, ADR-0002, ADR-0004, ADR-0008
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

Flutter, site/agendamento e integrações precisam consumir o mesmo backend por uma API REST. A documentação técnica deixou Django REST Framework e Django Ninja como alternativas a decidir antes da camada pública.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- maturidade de autorização e serializers
- ecossistema Django consolidado
- documentação e manutenção de longo prazo
- integração com autenticação
- contrato OpenAPI

## 3. Restrições

- API deve aplicar tenant e permissões no backend
- clientes multiplataforma precisam de contratos estáveis
- breaking changes devem ser explícitos

## 4. Opções consideradas

### Opção A - Django REST Framework

**Descrição**

Usar DRF como camada principal de API REST sobre Django.

**Vantagens**

- ecossistema maduro
- padrões conhecidos de serializers, permissions e pagination
- ampla documentação

**Desvantagens**

- mais boilerplate em alguns casos
- tipagem menos direta que abordagens mais novas

**Riscos**

- viewsets genéricos esconderem regras de domínio se usados sem disciplina

**Impacto operacional / migração**

- API baseada em serializers/views/permissions DRF

### Opção B - Django Ninja

**Descrição**

Usar Django Ninja com forte uso de type hints e schemas.

**Vantagens**

- API concisa
- tipagem e OpenAPI naturais

**Desvantagens**

- ecossistema menor
- menos padrões maduros para algumas necessidades empresariais

**Riscos**

- decisões próprias adicionais para autorização e organização

**Impacto operacional / migração**

- contratos Pydantic/Ninja

### Opção C - GraphQL como interface principal

**Descrição**

Expor schema GraphQL para clientes.

**Vantagens**

- flexibilidade de consulta

**Desvantagens**

- complexidade extra para autorização, caching e operação
- não é requisito atual

**Riscos**

- superfície de consulta mais difícil de governar cedo

**Impacto operacional / migração**

- stack e contratos diferentes da direção REST

## 5. Opção recomendada

- **Opção:** Opção A - Django REST Framework
- **Justificativa:** prioriza maturidade, segurança e manutenibilidade para um SaaS multi-tenant. A pequena economia de boilerplate não supera o valor do ecossistema consolidado nesta fundação.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- padrões claros de permissions/serialização
- integração natural com Django
- contratos REST estáveis para Flutter e integrações

### Negativas / trade-offs aceitos

- mais código estrutural em endpoints simples

### Novas obrigações

- OpenAPI gerável e versionado como evidência de contrato
- permissions backend obrigatórias
- serializers, views e viewsets são adaptadores de transporte e não contêm regras de negócio
- serializers limitam-se a shape, serialização/deserialização e validação sintática/estrutural; disponibilidade, preço, transições de estado e demais decisões de domínio pertencem aos serviços/módulos de domínio
- views/viewsets podem aplicar autenticação, autorização, tenant scoping e coordenação HTTP, mas toda mutação ou decisão de domínio deve delegar para serviço de aplicação/domínio explícito
- breaking changes exigem gate e estratégia de compatibilidade

## 7. Impacto em segurança e multi-tenancy

Permissions devem combinar autenticação, membership, papel e tenant context. Object lookup nunca pode ignorar ADR-0004.

## 8. Impacto em dados e API

A API expõe recursos do domínio sem permitir acesso direto ao banco. A camada DRF traduz HTTP para comandos/consultas de aplicação e traduz resultados para HTTP; não implementa regras de negócio. Paginação, filtros e erros devem ter convenções comuns definidas na fundação.

## 9. Impacto operacional e observabilidade

Latência, status codes, erros e correlation_id devem ser observáveis por endpoint.

## 10. Migração e rollout

A primeira API autenticada do vertical slice já nasce em DRF. Ferramenta concreta de geração OpenAPI pode ser escolhida na implementação sem mudar este ADR, desde que não altere o contrato arquitetural.

## 11. Rollback / reversibilidade

- **Reversível:** Parcialmente
- **Estratégia:** Django Ninja poderia coexistir ou substituir endpoints gradualmente por contrato, mas exigiria ADR sucessor se virar framework principal.
- **Custo ou risco de reversão:** troca ampla de framework depois de muitos endpoints aumenta custo.

## 12. Relação com decisões existentes

- Serve Flutter do ADR-0002 e aplica tenancy/autenticação dos ADRs 0004 e 0008.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Padronizar erros, paginação e contrato |
| Frontend | Favorável | OpenAPI e contratos estáveis |
| Security & Tenant Isolation | Favorável | Permissions e object scoping obrigatórios |
| Platform & Observability | Favorável | Instrumentar endpoints |
| QA & Quality | Favorável | Testes de contrato e autorização |

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
- **Pendências não bloqueantes:** Nenhuma

O parecer técnico é válido somente para a revisão decisória 2.

## 17. Aceite humano

- **Aceito:** Sim
- **Responsável humano:** Responsável do projeto
- **Data:** 2026-10-01
- **Revisão decisória aceita:** 2
- **Registro do aceite:** PR #9, comentário humano imutável [#5933524532](https://github.com/RamonRDR/SaaS-Project/pull/9#issuecomment-5933524532), publicado por `RamonRDR` em 2026-10-01.

As condições de aceite foram satisfeitas para a revisão decisória 2; o ADR está `Accepted`.
