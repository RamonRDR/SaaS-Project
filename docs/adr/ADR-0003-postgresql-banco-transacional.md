# ADR-0003 - Adotar PostgreSQL como banco transacional e fonte persistente do produto

## Metadados

- **ID:** ADR-0003
- **Título:** Adotar PostgreSQL como banco transacional e fonte persistente do produto
- **Status:** Accepted
- **Revisão decisória:** 2
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0001, ADR-0004, ADR-0006
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

Clientes, serviços, agendamentos, histórico, CRM, financeiro e configurações exigem integridade transacional e consultas relacionais. A direção técnica define PostgreSQL como fonte persistente e permite serviço gerenciado, inclusive Supabase, sem acoplamento desnecessário ao provedor.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- integridade transacional
- relacionamentos fortes
- migrations versionadas
- suporte maduro no Django
- portabilidade entre provedores

## 3. Restrições

- Google Calendar não é banco principal
- n8n não deve escrever regra de domínio diretamente
- provider de hospedagem não deve se tornar requisito de domínio

## 4. Opções consideradas

### Opção A - PostgreSQL

**Descrição**

Banco relacional PostgreSQL como fonte persistente transacional.

**Vantagens**

- transações e constraints robustas
- excelente suporte Django
- recursos maduros de indexação e JSON quando necessário

**Desvantagens**

- exige desenho de índices e operação de backup

**Riscos**

- queries mal desenhadas em escala

**Impacto operacional / migração**

- migrations Django, backups e monitoramento PostgreSQL

### Opção B - MySQL/MariaDB

**Descrição**

Banco relacional alternativo.

**Vantagens**

- maturidade e ampla oferta gerenciada

**Desvantagens**

- menos aderente à direção já estabelecida
- mudança sem benefício claro nesta fase

**Riscos**

- custo de troca sem necessidade

**Impacto operacional / migração**

- stack de persistência diferente

### Opção C - Banco documental como fonte principal

**Descrição**

Persistência principal em banco orientado a documentos.

**Vantagens**

- flexibilidade de esquema

**Desvantagens**

- pior ajuste para integridade e relações centrais do domínio
- migrations lógicas mais difíceis

**Riscos**

- consistência transferida para aplicação

**Impacto operacional / migração**

- reformulação de modelagem e acesso a dados

## 5. Opção recomendada

- **Opção:** Opção A - PostgreSQL
- **Justificativa:** é a direção baseline, combina com o modelo relacional do produto e reduz risco de integridade em agenda, memberships, CRM e financeiro.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- constraints no banco complementam validação da aplicação
- portabilidade entre provedores PostgreSQL
- boa base para relatórios operacionais

### Negativas / trade-offs aceitos

- necessidade de backups, tuning e migrations cuidadosas

### Novas obrigações

- migrations versionadas
- backups e restauração antes de operação comercial relevante
- índices revisados
- qualquer extensão fora do núcleo do PostgreSQL exige, antes da adoção, pelo menos uma destas garantias: disponibilidade comprovada em todos os provedores e planos oficialmente suportados pelo projeto; fallback portável e testado; ou ADR específico que aceite explicitamente o lock-in e defina estratégia de migração/rollback
- a portabilidade declarada neste ADR não pode depender apenas de a extensão ser open source

## 7. Impacto em segurança e multi-tenancy

Credenciais separadas por ambiente, menor privilégio, conexões seguras e isolamento de tenant conforme ADR-0004. Dados sensíveis não devem aparecer em logs.

## 8. Impacto em dados e API

PostgreSQL é a fonte de verdade dos dados do produto. APIs e integrações acessam dados por serviços Django, não por acesso externo direto.

## 9. Impacto operacional e observabilidade

Serviço gerenciado é permitido. Health, pool/conexões, espaço, latência e backups devem ser observáveis.

## 10. Migração e rollout

Criar banco por ambiente e migrations Django desde o primeiro modelo persistente.

## 11. Rollback / reversibilidade

- **Reversível:** Parcialmente
- **Estratégia:** Provedores PostgreSQL podem ser trocados por backup/restore e configuração somente quando recursos e extensões utilizados tiverem compatibilidade comprovada no destino ou fallback portável previamente testado.
- **Custo ou risco de reversão:** trocar o motor de banco seria caro; trocar apenas o provedor deve permanecer viável.

## 12. Relação com decisões existentes

- É a base de persistência do monólito do ADR-0001 e da tenancy do ADR-0004.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Nenhuma |
| Frontend | Não aplicável | Sem acesso direto ao banco |
| Security & Tenant Isolation | Favorável | Aplicar escopo tenant e menor privilégio |
| Platform & Observability | Favorável | Backups e métricas obrigatórios |
| QA & Quality | Favorável | Testes de migrations e integração |

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
- **Registro do aceite:** aceite humano histórico registrado por `RamonRDR` em 2026-10-01; a evidência operacional original permanece no histórico privado anterior e não foi importada para este snapshot público.

As condições de aceite foram satisfeitas para a revisão decisória 2; o ADR está `Accepted`.
