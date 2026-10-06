# ADR-0006 - Adotar Docker no backend e separar Development, Staging e Production

## Metadados

- **ID:** ADR-0006
- **Título:** Adotar Docker no backend e separar Development, Staging e Production
- **Status:** Accepted
- **Revisão decisória:** 2
- **Data de criação:** 2026-10-01
- **Última atualização:** 2026-10-01
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead
- **Responsável humano pelo aceite:** Responsável do projeto
- **SDDs relacionadas:** Não aplicável — decisão de fundação anterior às SDDs de feature.
- **ADRs relacionados:** ADR-0001, ADR-0003, ADR-0009, ADR-0010
- **PR / issue relacionada:** branch `foundation/phase-0e-initial-adrs`

### Estados permitidos

- `Proposed`: em elaboração ou revisão;
- `Accepted`: revisão técnica favorável, nenhuma pendência bloqueante e aceite humano explícito;
- `Rejected`: proposta rejeitada, preservada para histórico;
- `Superseded`: substituída por ADR posterior já aceito;
- `Deprecated`: decisão anteriormente válida que deixou de ser recomendada.

Nenhum agente de IA pode alterar sozinho o status para `Accepted`.

## 1. Contexto

O projeto precisa reduzir dependência do provedor de hospedagem e manter ambientes reproduzíveis. A direção técnica exige Docker, configuração por ambiente e separação de Development, Staging e Production.

A proposta parte das direções registradas no repositório e nos documentos mestres do projeto. Onde a fonte define apenas uma direção baseline, a escolha abaixo é uma recomendação arquitetural sujeita a aceite humano.

## 2. Drivers da decisão

- reprodutibilidade
- portabilidade de hosting
- paridade entre ambientes
- rollback previsível
- isolamento de credenciais e bancos

## 3. Restrições

- segredos não entram no Git
- bancos e credenciais são separados por ambiente
- staging deve permitir validação antes de produção

## 4. Opções consideradas

### Opção A - Docker backend + Compose local + hosting gerenciado de containers

**Descrição**

Empacotar backend e serviços auxiliares necessários em containers, usando Compose para desenvolvimento quando adequado.

**Vantagens**

- portabilidade
- setup reproduzível
- boa transição entre local e cloud

**Desvantagens**

- exige manutenção de imagens e arquivos de container

**Riscos**

- imagem divergente entre ambientes se tags não forem imutáveis

**Impacto operacional / migração**

- build de imagem como artefato de deploy

### Opção B - Deploy direto no runtime do provedor

**Descrição**

Instalar dependências diretamente no ambiente gerenciado sem container próprio.

**Vantagens**

- setup inicial simples

**Desvantagens**

- maior acoplamento ao provedor
- menor paridade local

**Riscos**

- diferenças de runtime e migração mais difícil

**Impacto operacional / migração**

- pipelines específicos do host

### Opção C - Kubernetes desde o início

**Descrição**

Usar orquestração Kubernetes para todos os ambientes.

**Vantagens**

- alto controle e escalabilidade

**Desvantagens**

- complexidade operacional excessiva nesta fase

**Riscos**

- fundação consumida por infraestrutura antes do produto

**Impacto operacional / migração**

- cluster, manifests, ingress, secrets e observabilidade adicionais

## 5. Opção recomendada

- **Opção:** Opção A - Docker backend + Compose local + hosting gerenciado de containers
- **Justificativa:** entrega portabilidade e paridade sem introduzir a complexidade de Kubernetes.

Esta seção registra recomendação técnica, não aceite humano.

## 6. Consequências

### Positivas

- mesmo artefato de backend entre staging e produção
- rollback por imagem
- menor lock-in

### Negativas / trade-offs aceitos

- tempo de build e manutenção de Dockerfiles

### Novas obrigações

- imagens reproduzíveis e com versões
- configuração via ambiente
- secrets fora da imagem
- banco/credenciais separados
- migrations como etapa controlada de deploy
- mudanças de schema que precisem coexistir com a imagem anterior usam estratégia expand/contract por padrão; quando isso não for possível, a promoção exige plano de down migration ou restauração testado
- migrations destrutivas continuam exigindo aprovação humana explícita antes da promoção
- staging antes de produção em mudanças relevantes

## 7. Impacto em segurança e multi-tenancy

Imagens não contêm secrets. Usuários/processos devem usar menor privilégio quando aplicável. Credenciais externas são separadas por ambiente.

## 8. Impacto em dados e API

Não muda contratos de domínio. Cada ambiente possui banco independente e endpoints próprios.

## 9. Impacto operacional e observabilidade

Health checks e logs em stdout/estrutura compatível com coleta. Artefato de deploy precisa ser rastreável ao commit.

## 10. Migração e rollout

Containerizar backend na fundação; adicionar serviços auxiliares ao Compose somente quando existirem.

## 11. Rollback / reversibilidade

- **Reversível:** Parcialmente
- **Estratégia:** Reimplantar a imagem anterior somente quando o schema pós-migration permanecer compatível. Para mudanças incompatíveis, usar expand/contract ou executar um plano previamente testado de down migration/restauração antes de considerar o rollback disponível.
- **Custo ou risco de reversão:** migrations incompatíveis ou destrutivas podem impedir rollback simples da aplicação. A promoção deve comprovar compatibilidade com a imagem anterior ou evidência de restauração/down migration testada; migrations destrutivas continuam sujeitas a gate humano.

## 12. Relação com decisões existentes

- Viabiliza deploy do ADR-0001 e gates do ADR-0010.

Nenhum ADR vigente será marcado como `Superseded` antes de um sucessor atingir `Accepted`.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Favorável | Health e configuração por ambiente |
| Frontend | Parcialmente aplicável | Flutter mantém toolchain própria por target |
| Security & Tenant Isolation | Favorável | Secrets separados por ambiente |
| Platform & Observability | Favorável | Artefatos imutáveis e health checks |
| QA & Quality | Favorável | Staging deve reproduzir comportamento de produção |

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
