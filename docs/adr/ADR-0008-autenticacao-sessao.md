# ADR-0008 - Adotar autenticação Django com access token curto e refresh rotativo

## Metadados

- **ID:** ADR-0008
- **Título:** Adotar autenticação Django com access token curto e refresh rotativo
- **Status:** Accepted
- **Revisão decisória:** 2
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0002, ADR-0004, ADR-0005
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

O mesmo backend atenderá Flutter Web/PWA, mobile e desktop. O sistema precisa autenticar usuários e validar memberships/roles por tenant sem confiar em contexto enviado isoladamente pelo cliente. A fonte atual exige que autenticação e autorização permaneçam no backend, mas não define o mecanismo de sessão.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- clientes multiplataforma
- revogação e expiração
- segurança em browser e dispositivos nativos
- integração natural com Django/DRF
- separação entre identidade e tenant

## 3. Restrições

- senhas nunca em texto puro
- tenant e permissões são validados no backend
- secrets não entram no repositório
- mudanças de autenticação exigem gate humano

## 4. Opções consideradas

### Opção A - Access token curto + refresh rotativo

**Descrição**

Django autentica a identidade; a API usa access token de curta duração e refresh credential rotativo/revogável. Armazenamento do refresh segue mecanismo seguro por plataforma.

**Vantagens**

- bom ajuste a Flutter multiplataforma
- access token reduz estado por request
- permite revogação via refresh/session registry

**Desvantagens**

- maior cuidado com rotação, revogação e storage
- browser exige proteção CSRF quando refresh usar cookie

**Riscos**

- armazenamento inseguro de refresh token ou rotação incorreta

**Impacto operacional / migração**

- endpoints de login/refresh/logout, registro de sessões e políticas de expiração

### Opção B - Session cookie Django para todos os clientes

**Descrição**

Usar sessão server-side e cookie como mecanismo universal.

**Vantagens**

- modelo maduro e simples no browser
- revogação central

**Desvantagens**

- ergonomia menos comum em clientes nativos
- CSRF/cookies precisam de cuidado cross-platform

**Riscos**

- configuração de cookies inadequada

**Impacto operacional / migração**

- session store e cookie jar em todos os targets

### Opção C - Provedor externo de identidade desde a fundação

**Descrição**

Delegar autenticação a serviço OIDC/SaaS.

**Vantagens**

- recursos avançados de identidade prontos

**Desvantagens**

- custo/lock-in e dependência externa antes da necessidade

**Riscos**

- complexidade de integração e disponibilidade de terceiro

**Impacto operacional / migração**

- provedor externo vira dependência crítica

## 5. Opção recomendada

- **Opção:** Opção A - Access token curto + refresh rotativo
- **Justificativa:** equilibra clientes Flutter multiplataforma com controle de sessão no backend. A identidade é autenticada por Django e tenant/membership continua sendo decisão server-side em cada operação relevante.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- adequado a web e clientes nativos
- access tokens limitam janela de exposição
- logout/revogação podem invalidar refresh

### Negativas / trade-offs aceitos

- implementação de rotação e revogação precisa ser rigorosa
- mais casos de segurança para testar

### Novas obrigações

- access token de curta duração
- refresh token é de uso único: cada rotação invalida atomicamente o predecessor e emite o sucessor dentro da mesma operação transacional
- cada refresh pertence a uma família/sessão identificável e revogável
- tentativa de reutilizar refresh já consumido, rotacionado ou revogado é tratada como comprometimento: a família/sessão inteira é revogada e nova autenticação é obrigatória
- rotação concorrente deve garantir que apenas uma tentativa possa consumir o refresh atual; tentativas subsequentes entram na política de detecção de reuso
- access tokens carregam identificador de sessão/família e requisições autenticadas devem rejeitar sessão marcada como revogada, permitindo contenção imediata após detecção de reuso
- browser armazena refresh em cookie Secure, HttpOnly e política SameSite adequada; não usar localStorage para credencial de longa duração
- clientes nativos usam armazenamento seguro do sistema operacional
- proteção CSRF onde cookies autenticam endpoint
- password hashing padrão seguro do Django
- rate limiting/abuse protection quando superfície pública evoluir
- membership e role revalidados no backend

## 7. Impacto em segurança e multi-tenancy

Token não é autoridade suficiente para escolher tenant arbitrário. Toda operação valida membership ativa e permissões. Claims podem otimizar contexto, mas nunca substituem checagem server-side para decisões sensíveis.

Refresh tokens são credenciais de uso único. O backend mantém estado suficiente para rotação atômica, detecção de reuso e revogação da família/sessão comprometida. Um refresh reapresentado depois de consumido nunca gera novo token.

## 8. Impacto em dados e API

API DRF exige autenticação nos recursos privados. O registro de sessão/família e o estado de refresh precisam suportar consumo único, rotação atômica, revogação e detecção de reuso. Tokens brutos não devem ser persistidos quando um identificador/hash seguro for suficiente.

## 9. Impacto operacional e observabilidade

Auditar login, logout, falhas, rotações, detecções de reuso e revogações sem registrar senhas ou tokens. Reuso de refresh gera evento de segurança e revogação da sessão/família. Alertas de abuso podem ser adicionados conforme exposição pública.

## 10. Migração e rollout

Implementar a base no primeiro vertical slice autenticado. SSO/social login ficam fora de escopo inicial e podem ser adicionados sem substituir o modelo de autorização.

## 11. Rollback / reversibilidade

- **Reversível:** Parcialmente
- **Estratégia:** Mecanismo de token pode ser substituído por sessão/OIDC via ADR sucessor preservando usuários e memberships.
- **Custo ou risco de reversão:** mudança afeta todos os clientes; contratos de autenticação devem ser isolados da lógica de domínio.

## 12. Relação com decisões existentes

- Usa DRF do ADR-0005 e governa contexto que habilita tenancy do ADR-0004.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Implementar rotação/revogação com testes |
| Frontend | Favorável | Storage seguro específico por plataforma |
| Security & Tenant Isolation | Favorável | CSRF, expiração, revogação e membership obrigatórios |
| Platform & Observability | Favorável | Auditoria sem secrets |
| QA & Quality | Favorável | Testar roubo/reuso de refresh e autorização negativa |

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
- **Pendências não bloqueantes:** Tempos exatos de expiração serão definidos na SDD/implementação de autenticação e podem ser ajustados sem mudar a decisão arquitetural.

O parecer técnico é válido somente para a revisão decisória 2.

## 17. Aceite humano

- **Aceito:** Sim
- **Responsável humano:** Responsável do projeto
- **Data:** 2026-10-01
- **Revisão decisória aceita:** 2
- **Registro do aceite:** aceite humano histórico registrado por `RamonRDR` em 2026-10-01; a evidência operacional original permanece no histórico privado anterior e não foi importada para este snapshot público.

As condições de aceite foram satisfeitas para a revisão decisória 2; o ADR está `Accepted`.
