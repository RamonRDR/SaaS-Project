# ADR-0007 - Limitar n8n à orquestração de automações e integrações

## Metadados

- **ID:** ADR-0007
- **Título:** Limitar n8n à orquestração de automações e integrações
- **Status:** Accepted
- **Revisão decisória:** 1
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0001, ADR-0004, ADR-0005, ADR-0009
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

WhatsApp, e-mail, Google Calendar, lembretes e outras integrações precisam de workflows. Os documentos do projeto estabelecem a regra: o SaaS decide, o n8n orquestra e os canais entregam.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- centralização das regras de negócio
- reprocessamento de integrações
- facilidade de trocar canais/provedores
- auditabilidade
- evitar backend paralelo em low-code

## 3. Restrições

- n8n não é fonte de verdade
- regras críticas pertencem ao Django
- integrações devem respeitar tenant, autenticação e idempotência

## 4. Opções consideradas

### Opção A - n8n como orquestrador via API

**Descrição**

n8n recebe eventos/tarefas, chama contratos Django e provedores externos, sem decidir regra crítica nem escrever diretamente no banco do produto.

**Vantagens**

- separação clara de responsabilidades
- workflows visuais para integrações
- domínio testável no backend

**Desvantagens**

- depende de contratos de API internos estáveis

**Riscos**

- workflow tentar replicar regra de domínio por conveniência

**Impacto operacional / migração**

- credenciais de serviço, APIs internas e observabilidade correlacionada

### Opção B - n8n com regras de domínio e acesso direto ao banco

**Descrição**

Workflows decidem disponibilidade, preço, tenant ou manutenção e alteram PostgreSQL diretamente.

**Vantagens**

- prototipagem rápida

**Desvantagens**

- duplica regras
- contorna autorização e testes
- acoplamento ao schema

**Riscos**

- inconsistência e vazamento cross-tenant

**Impacto operacional / migração**

- backend paralelo difícil de governar

### Opção C - Não usar n8n

**Descrição**

Implementar jobs e integrações somente em código Django/workers.

**Vantagens**

- uma stack de código

**Desvantagens**

- mais código operacional para integrações simples
- perde ferramenta já prevista

**Riscos**

- reinventar orquestração

**Impacto operacional / migração**

- jobs e conectores próprios

## 5. Opção recomendada

- **Opção:** Opção A - n8n como orquestrador via API
- **Justificativa:** mantém domínio e autorização no Django, usando n8n onde ele agrega valor: fluxo, retry, agenda e conexão com canais.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- troca de provedor mais simples
- regras críticas testáveis em Python
- workflows externos mais visíveis

### Negativas / trade-offs aceitos

- necessidade de contratos de integração explícitos
- dois planos de observabilidade, Django e n8n

### Novas obrigações

- n8n não acessa banco do produto diretamente
- toda ação de domínio passa por API/serviço autorizado
- operações reprocessáveis devem ser idempotentes
- correlation_id atravessa workflow quando possível
- credenciais separadas por ambiente
- erros/retries precisam de política explícita

## 7. Impacto em segurança e multi-tenancy

n8n usa credenciais de serviço com menor privilégio. Tenant context deve ser autenticado/validado pelo backend, nunca aceito como autoridade apenas do workflow.

## 8. Impacto em dados e API

Google Calendar e canais externos são projeções/integrações; PostgreSQL continua fonte do produto. Contratos internos devem evitar dependência do schema físico.

## 9. Impacto operacional e observabilidade

Monitorar falhas, retries e duração de workflows. Correlacionar execução externa com logs Django e provedor.

## 10. Migração e rollout

Introduzir n8n apenas quando surgir o primeiro workflow externo real. Não criar automações vazias na fundação.

## 11. Rollback / reversibilidade

- **Reversível:** Sim
- **Estratégia:** Um workflow pode ser desativado e substituído por job/backend mantendo os mesmos contratos.
- **Custo ou risco de reversão:** baixo se regra de domínio permanecer fora do n8n.

## 12. Relação com decisões existentes

- Depende das APIs do ADR-0005 e da observabilidade do ADR-0009.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Contratos internos explícitos |
| Frontend | Não aplicável diretamente | Nenhuma |
| Security & Tenant Isolation | Favorável | Credenciais e tenant validados no backend |
| Platform & Observability | Favorável | Correlation, retries e alertas |
| QA & Quality | Favorável | Testes de idempotência e falhas de integração |

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
- **Registro do aceite:** aceite humano histórico registrado por `RamonRDR` em 2026-10-01; a evidência operacional original permanece no histórico privado anterior e não foi importada para este snapshot público.

As condições de aceite foram satisfeitas para a revisão decisória 1; o ADR está `Accepted`.
