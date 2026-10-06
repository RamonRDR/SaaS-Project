# ADR-0002 - Adotar Flutter como frontend multiplataforma principal

## Metadados

- **ID:** ADR-0002
- **Título:** Adotar Flutter como frontend multiplataforma principal
- **Status:** Accepted
- **Revisão decisória:** 1
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0005, ADR-0008, ADR-0009
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

O produto precisa oferecer experiência simples no celular, web/PWA e futuramente aplicações nativas, compartilhando o mesmo backend. A documentação funcional prioriza acesso sem instalação para clientes e experiência móvel para a operação; a direção técnica baseline já aponta Flutter como frontend principal.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- reuso de código entre targets
- experiência mobile-first
- capacidade Web/PWA, Android, desktop e iOS
- contratos de API comuns
- redução de múltiplas bases de frontend

## 3. Restrições

- cliente final não deve ser obrigado a instalar aplicativo
- Flutter não pode ser autoridade de regra crítica
- SEO/performance de uma futura superfície pública podem exigir exceção

## 4. Opções consideradas

### Opção A - Flutter como cliente principal multiplataforma

**Descrição**

Usar Flutter para interfaces autenticadas e superfícies web/PWA quando adequado, mantendo uma exceção futura para web pública se houver necessidade comprovada.

**Vantagens**

- alta reutilização
- uma arquitetura de UI principal
- boa cobertura de targets

**Desvantagens**

- SEO web público pode exigir solução específica
- algumas integrações de plataforma demandam adaptações

**Riscos**

- forçar Flutter em uma superfície pública onde métricas provem inadequação

**Impacto operacional / migração**

- pipeline Flutter por target e uma API backend comum

### Opção B - Frontends separados por plataforma

**Descrição**

Manter stacks independentes para web, Android, iOS e desktop.

**Vantagens**

- otimização específica por plataforma

**Desvantagens**

- duplicação de regras de apresentação, testes e equipe
- maior custo de consistência

**Riscos**

- experiências divergentes

**Impacto operacional / migração**

- múltiplas bases e pipelines

### Opção C - Web/PWA em stack web e mobile posterior em outra stack

**Descrição**

Começar com frontend web dedicado e adotar app separado depois.

**Vantagens**

- web pública tradicional mais simples

**Desvantagens**

- segunda stack quando mobile crescer
- menor reuso

**Riscos**

- migração ou duplicação futura

**Impacto operacional / migração**

- duas famílias de frontend

## 5. Opção recomendada

- **Opção:** Opção A - Flutter como cliente principal multiplataforma
- **Justificativa:** atende a direção técnica e o objetivo de experiência mobile-first sem obrigar instalação, pois Web/PWA continua disponível. Uma superfície pública dedicada permanece permitida se SEO ou performance apresentarem evidência concreta.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- base compartilhada entre targets
- componentes e testes reutilizáveis
- mesmo contrato de API

### Negativas / trade-offs aceitos

- necessidade de disciplina responsiva
- possível frontend web público separado no futuro

### Novas obrigações

- design responsivo e acessível
- nenhuma regra crítica exclusiva no cliente
- testes por breakpoints/targets relevantes
- ADR sucessor se uma superfície pública migrar para outra stack

## 7. Impacto em segurança e multi-tenancy

Autorização sempre no backend. Tokens, sessão e armazenamento seguro seguirão ADR-0008; o cliente não define tenant ou permissões por conta própria.

## 8. Impacto em dados e API

Flutter consome a API REST. Modelos locais são representações de transporte/apresentação, não fonte de verdade.

## 9. Impacto operacional e observabilidade

Builds e telemetria de cliente devem ser separados por ambiente. Erros de frontend devem ser correlacionáveis com requisições backend quando possível.

## 10. Migração e rollout

Iniciar pelos targets necessários ao primeiro vertical slice, priorizando Web/PWA e evolução para demais targets conforme roadmap.

## 11. Rollback / reversibilidade

- **Reversível:** Parcialmente
- **Estratégia:** Uma superfície específica pode ser reimplementada sem substituir o backend ou contratos de domínio.
- **Custo ou risco de reversão:** mudar toda a stack de UI depois de ampla adoção aumenta custo; contratos de API estáveis reduzem esse risco.

## 12. Relação com decisões existentes

- Depende do contrato REST do ADR-0005 e da estratégia de autenticação do ADR-0008.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Manter contratos de API independentes do Flutter |
| Frontend | Favorável | Priorizar responsividade e acessibilidade |
| Security & Tenant Isolation | Favorável | Autoridade permanece no backend |
| Platform & Observability | Favorável | Definir builds por ambiente |
| QA & Quality | Favorável | Matriz de targets no roadmap de testes |

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
