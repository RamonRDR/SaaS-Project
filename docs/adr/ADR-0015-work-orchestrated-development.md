# ADR-0015 - Desenvolvimento orquestrado pelo Work com enforcement no GitHub

## Metadados

- **ID:** ADR-0015
- **Título:** Desenvolvimento orquestrado pelo Work com enforcement no GitHub
- **Status:** Proposed
- **Revisão decisória:** 3
- **Data de criação:** 2026-10-13
- **Última atualização:** 2026-10-13
- **Responsável pela proposta documental:** Product & SDD
- **Revisor técnico:** Orchestrator / Tech Lead (pendente de parecer formal)
- **Responsável humano pelo aceite:** responsável pelo repositório
- **SDDs relacionadas:** SDD-0002 v0.3 (candidata); SDD-0001 v1.6 (Approved, vigente)
- **ADRs relacionadas:** ADR-0014 rev.5 (Accepted, vigente); ADR-0010 (Accepted); ADR-0013 rev.1 (Superseded)
- **PR / issue relacionada:** Issues #1, #8 e #10; PRs experimentais #7 e #9; pareceres rev.1 no PR #11

### Estados permitidos e validade

`Proposed` (atual), `Accepted`, `Rejected`, `Superseded`, `Deprecated`. Somente parecer formal `Pronto para aceite humano` sobre a revisão decisória vigente, sem bloqueantes, seguido de aceite humano explícito, permite `Accepted`. As seções 1 a 14 são decisões materiais; alteração exige nova revisão e novo parecer. **A autorização de 13/10/2026 foi para elaborar esta proposta, NÃO seu aceite.**

## 1. Contexto

O contrato atual, SDD-0001 v1.6 e ADR-0014 rev.5, exige GitHub Actions como executor unattended, Budget Broker, claim universal e consumo programático de IA controlado. O proprietário deseja autonomia de desenvolvimento online dentro do ChatGPT Plus, sem contratar ou usar a OpenAI API. Em 13/10/2026 três canaries do ChatGPT Work conectado ao GitHub demonstraram: (i) evento → comentário ACK idempotente; (ii) evento → código/branch/PR → CI → relatório; (iii) evento → teste intencionalmente vermelho → correção → CI verde → relatório. A issue #8 conserva os SHAs e logs. Nenhum dos testes comprovou garantia de entrega de eventos, disponibilidade ilimitada ou enforcement contra alterações privilegiadas.

A SDD-0001 v1.6 **exclui o Work como componente obrigatório**, logo uma mudança arquitetural não pode ser feita por prompt, comentário ou ajuste silencioso. Esta ADR é proposta sucessora **do mecanismo de execução de IA do ADR-0014**, não aprovação retroativa da migração nem eliminação dos controles que continuam pertinentes.

## 2. Drivers da decisão

- Autonomia operacional verificável entre gatilhos, CI e checkpoints humanos.
- **Zero OpenAI API paga** no caminho proposto; respeitar limites do ChatGPT Work/Codex e parar ao atingir quota.
- Trust boundary de repositório público: PRs, forks, diffs, comentários, logs e instruções de terceiros são dados não confiáveis.
- CI/GitHub como autoridade independente para gates, HEAD, integridade e trilha de auditoria.
- Preservação de `CODEX-01` independente e autorização humana final de merge.
- Redução de complexidade de ledger financeiro/claim pago no modo sem API; não remover guardas de segurança de forma tácita.
- Retomada idempotente, controle de concorrência, custo operacional observável, reversibilidade.

## 3. Restrições não negociáveis

1. `main` protegida; **nenhum merge principal sem `ORCHESTRATOR_READY`, `MERGE_ALLOWED` e autorização humana posterior vinculada ao mesmo PR/HEAD**.
2. SDD-0001 v1.6 e ADR-0014 rev.5 permanecem vigentes até os gates de sucessão. Não reescrever decisões aceitas.
3. **Work não recebe acesso de escrita ao repositório principal.** A opção B passa a exigir sandbox separado, conexão GitHub com identidade segregada e sem escrita/admin em `RamonRDR/SaaS-Project`; o publicador confiável da `main` recebe somente candidatos não confiáveis e os valida **antes** de publicar. Se a segregação efetiva não for possível, bloquear o piloto.
4. **Um comentário GitHub NÃO comprova ação humana.** Escopo e merge exigem `ScopeGrantReceipt v1` / `MergeGrantReceipt v1` derivados de `workflow_dispatch` confiável na `main`, iniciado por identidade humana **não delegada ao Work**, com run ID, workflow e HEAD trusted, alvo, versão, expiração e comparação readback. Merge exige receipt posterior ao `ORCHESTRATOR_READY`; somente um job trusted pode registrar `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`.
5. Alterações em `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/specs/**`, `docs/adr/**`, `docs/engineering/**` e `docs/PROJECT_STATUS.md` são **control plane**, fora da remediação autônoma. Mudanças documentais como este PR seguem review e aprovação humanos.
6. **Sem `OPENAI_API_KEY`**, sem endpoint de inferência de IA paga, sem purchase/upgrade automático, sem fallback de cobrança. Uso de Work/Codex está sujeito ao plano e seus limites, que não equivalem a SLA nem API contratada.
7. `CODEX-01` independente revisa HEAD final e mudanças vinculadas por `merge_base_sha`, `payload_digest`, `trusted_review_contract_digest` completo da `main` e `review_context_fingerprint`; revalidar os três antes de READY, mesmo sem mudança de HEAD. Evidência divergente fica inválida, e piloto nunca usa API paga.
8. Nenhum gate pode ser marcado `PASS`, `READY` ou `DONE` por texto de agente sem evidências reconsultadas.
9. Proposta não autoriza ativação de tarefa unattended principal nem de workflows operacionais; `PHASE-0-G` continua planejada.

## 4. Opções consideradas

### A. Preservar Actions-only + Codex API/Budget Broker (estado vigente)

**Descrição:** dispatcher confiável da `main`, intake `PENDING`, reconciler, claim universal, writer financeiro e inferência controlada em jobs.

**Vantagens:** controle determinístico do ciclo e da contabilidade, compatibilidade direta com a SDD-0001 v1.6, arquitetura independente do serviço Work.

**Desvantagens:** implantação e verificação de ledger/claim/cota financeira complexas, pressupõe uma rota de inferência programática faturável que o usuário não autorizou.

**Riscos:** consumo monetário não autorizado caso ativada sem gates; loops técnicos de capacidade e evolução lenta.

**Impacto operacional / migração:** manter sem ativar componentes pagos; PR #4 em `LOOP_ESCALATION_REQUIRED` e PR #6 draft.

### B. Work como executor de desenvolvimento + Actions como enforcement (recomendada para piloto)

**Descrição:** tarefa Work de escopo explícito reage a eventos GitHub **somente no sandbox separado**, onde publica candidatos sem privilégios sobre o principal. GitHub Actions da `main`, com writer trusted e exclusão durável PostgreSQL, verifica manifests/paths **antes** de qualquer commit no principal, depois publica branch e PR draft. Actions valida CI/governança, CODEX-01 independente revisa fingerprint do HEAD e humano autoriza merge com receipt independente.

**Vantagens:** fluxo curto já comprovado em 3 canaries, nenhum contrato de OpenAI API paga necessário para gerar código, libera desenvolvimento de produto mais cedo.

**Desvantagens:** dependência da disponibilidade/quotas do Work, capacidades de triggers e permissões de conector sujeitas a alteração, ausência de garantia transacional para entrega de eventos.

**Riscos:** prompts não criam isolamento técnico; um conector de escrita pode alcançar outros paths ou a `main`. Na primeira consulta, o repositório não tinha ruleset; **posteriormente foi criado e verificado** `main-protection` ID 25036481, ativo, sem bypass, exigindo PR e checks. Mesmo assim, o Work conectado à identidade do proprietário ainda representa um risco de escrita no principal e de autorização forjada. O desenho exige **identidade distinta limitada ao sandbox**; sem teste de isolamento, piloto bloqueado. Coalescência e limitações podem deixar estados pendentes. O GitHub Actions **não controla a execução interna do Work**.

**Impacto operacional / migração:** nova SDD/ADR, conexão Work segregada com permissão apenas no sandbox, `ScopeGrantReceipt` e `MergeGrantReceipt` via ação humana trusted, publicador read-only sobre candidato + writer restrito ao principal, PostgreSQL transacional com fencing e canaries negativos. Sem M1/M2b aprovados, piloto mutável proibido.

### C. Work como autoridade completa, com merge/CI autodeclarados (rejeitada)

**Descrição:** confiar em comentários do Work para considerar gates aprovados e autorizar merge.

**Vantagens:** aparente menor latência.

**Desvantagens:** nenhuma separação real entre execução, revisão e autorização.

**Riscos:** autoaprovação, prompt injection, bypass de control plane, review desatualizado, alteração irreversível não autorizada.

**Impacto operacional / migração:** incompatível com AGENTS.md e CI_GATES.md; não implementar.

## 5. Opção recomendada

- **Opção:** B, **piloto supervisionado**, sujeito a gates ainda pendentes.
- **Justificativa:** único caminho com execução de IA já demonstrada sem integrar API paga, preservando Github Actions como fonte independente de evidência. A recomendação **não** considera as três provas suficientes para produção.
- **Limite de confiança:** Work somente poderá escrever no sandbox, jamais no principal; seus candidatos serão importados exclusivamente pelo publisher trusted sob escopo verificável. A conexão atual do proprietário ainda exige revogação/segregação antes do piloto. Qualquer comentário, inclusive sob o login do proprietário, é insuficiente para aprovar escopo, risco ou merge. Contratos externos não comprovados impõem `BLOCKED_EXTERNAL` / `HUMAN_DECISION_REQUIRED`.

## 6. Consequências

### Positivas
- Autonomia de escrita, correção e acompanhamento assíncrono com histórico demonstrado.
- Eliminação do caminho de cobrança via OpenAI API no piloto.
- Continuam CI, CODEX-01, AGENTS.md e merge humano.

### Negativas / trade-offs ainda não aceitos para produção
- Ausência de SLA de Work ou contrato de entrega exatamente uma vez.
- Possibilidade de bloqueio por quota, desconexão, permissão ou aprovador.
- Rate limit do GitHub e limite de eventos do Work não são equivalentes a fila durável.
- Caminho de fork e mudanças privilegiadas exigem fluxo separado, não-autônomo.

### Novas obrigações
- Recorte humano de escopo, state machine audível, eventos idempotentes e backlog verificável.
- Auditoria de paths e evidência do SHA/GitHub antes de qualquer transição.
- Reconciler read-only que nunca anuncia progresso falso nem tenta acordar Work sem suporte comprovado.
- Métricas de latência, retries, pending, quota, bloqueios e revisão final.

## 7. Impacto em segurança e multi-tenancy

Apenas engenharia; nenhum dado tenant-owned é manipulado. **Trust boundary escolhido:** conexão Work com escrita no sandbox **sem capacidade de escrita/admin no principal**, após revogação do vínculo existente do proprietário; `main` possui ruleset ativo `main-protection` ID 25036481, branch padrão, sem bypass e com checks `governance`/`secret-scan`, mas zero aprovações obrigatórias. Proteção da branch **não substitui** autorização humana independente nem validação pré-escrita. Publicador trusted da `main` é o **único** caminho de importação: examina manifest completo, allowlist, denylist do control plane, modos e base SHA antes de qualquer escrita. Falta de isolamento ou patch proibido bloqueia e exige `HUMAN_DECISION_REQUIRED`. Contrato vinculante: `docs/engineering/MODE_A_WORK_HYBRID_TRUST_CONTRACT.md`.

## 8. Impacto em dados e API

- **Banco do SaaS:** não aplicável; sem migration de produto.
- **GitHub:** PR, receipts de `workflow_dispatch` trusted, checks/status por SHA, publicador em `main` e comentários de auditoria; comentários não são autorização nem CAS.
- **Work:** assinaturas de eventos dependem de configuração e franquia; conexão com identidade isolada apenas no sandbox. GitHub Actions não tem garantia de acordá-lo após evento perdido.
- **OpenAI API paga:** ausente. O ledger financeiro e claim da ADR-0014 ficam **inativos, não apagados**, até sucessão formal e definição do modo de fallback.
- **Estado durable/exclusão:** PostgreSQL **transacional** escolhido para o desenho, sem fornecedor/instância aprovada ou provisionada. `UNIQUE(operation_key)`, `SELECT FOR UPDATE`, `fencing_epoch`, lease e readback ambíguo; somente writer trusted recebe credencial. Git refs e Actions concurrency NÃO substituem exclusão. Sem DB/serialização testada, só observador read-only e **nenhum** piloto mutável.
- Alterações de schemas existentes exigiriam versionamento explícito e outra revisão técnica.

## 9. Impacto operacional e observabilidade

**Autorização versus wake-up:** o canal escolhido é `workflow_dispatch` humano-only na `main` do principal, com receipts `ScopeGrantReceipt v1` e `MergeGrantReceipt v1`; a identidade humana não fica conectada ao Work. Apenas trusted job transforma autorização posterior ao READY em `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`. O comentário GitHub é somente sinal não confiável. **Leitura e retomada:** um scanner trusted e read-only pode identificar uma operação pendente; se não houver wake-up automatizado suportado, só um operador humano religará/acionará a tarefa. Não declarar auto-healing por haver scanner.

Eventos essenciais: `TASK_OBSERVED`, `WORK_PENDING`, `CI_PENDING`, `CI_FAILED`, `CI_PASSED`, `WAITING_CODEX`, `READY_FOR_HUMAN_MERGE`, `BLOCKED_EXTERNAL`, `LOOP_ESCALATION_REQUIRED`, `HUMAN_DECISION_REQUIRED`. Evidências devem identificar `repo`, `pr`, `head_sha`, `source`, `control_issue`, timestamp e resultado de cada gate. Logs e comentários excluem secrets, tokens, dados de clientes e payload não confiável. Observador GitHub read-only verifica pendências em vez de inferir que a tarefa executou. Tempo limite e escalada são definidos na SDD-0002 e na implantação.

## 10. Migração e rollout

0. Registrar esta ADR `Proposed` e SDD-0002 `In Review`; distinguir revisão/aprovação do **desenho** de autorização posterior da **operação**. Para aceitar desenho, devem estar decididos: canal confiável de autorização, perímetro de escrita, modo de bloqueio sem permissões e limites de retomada. Provas de CI/Work e segurança implantada só serão produzidas nos marcos técnicos depois da aprovação documental, antes da ativação. Obter review formal `review-adr`/`review-sdd` e, só depois, aceite/aprovação humanos.
1. Verificar configurações atuais de Work/GitHub, permissões, quotas do plano e branch protection, sem ativar tarefa principal.
2. Criar observador read-only e receipts humanos trusted na `main`, com prova de isolamento da identidade Work em sandbox separado.
3. Implementar publicador trusted + PostgreSQL transacional (writer/lease/fencing), testes de concorrência e negativa de control plane **antes de qualquer escrita no principal**. Sem storage autorizado e comprovado, bloquear piloto mutável.
4. Executar canaries de perda de evento, duplicata, HEAD stale, reviewer fingerprint alterado, injection, concorrência e autorização forjada; depois piloto de desenvolvimento **no sandbox**, com publicador no principal e `ORCHESTRATOR_MODE: NONE`; sem merge.
5. Somente após evidência e novo gate humano avaliar ativação operacional do Mode A para PRs reais, preservando CODEX-01 e merge humano.

Nenhuma fase presume autosserviço de criação de tarefa Work por GitHub Actions.

## 11. Rollback / reversibilidade

- **Reversível:** parcialmente. Desativar tarefa Work e reconciliação de escrita; não há rollback de comentários/commits já publicados automaticamente.
- Preservar PRs e logs, deixar branches de experimento em draft, bloquear mutações e continuar com revisão manual/CI read-only.
- O contrato Actions-only aprovado permanece referência durante a transição. Não ativar fallback pago automaticamente.

## 12. Relação com decisões existentes

- **ADR-0014 rev.5 (`Accepted`):** decisão atual sobre intake, claim e Budget Broker. Esta ADR-0015 é candidata sucessora **apenas do modo operacional unattended**, e especifica que as partes pagas não podem ser ativadas na rota proposta; a revisão de escopo da sucessão requer decisão humana. ADR-0014 **não** muda de estado enquanto ADR-0015 não alcançar `Accepted`.
- **ADR-0010 (`Accepted`):** governa CI, PR e autorização humana de merge; permanece em vigor.
- **SDD-0001 v1.6 (`Approved`):** contrato operacional atual até eventual aprovação da SDD-0002; não reescrever nem considerar automaticamente `Superseded`.
- **AGENTS.md / CI_GATES.md:** gates obrigatórios preservados; alterações futuras seguem PR separado e aprovação humana.

## 13. Pareceres dos especialistas impactados

| Especialista | Parecer | Pendências |
| --- | --- | --- |
| Backend | Pendente de revisão formal | Não há mudança no backend de produto |
| Frontend | Não aplicável ao piloto | Nenhum frontend alterado |
| Security & Tenant Isolation | **Pendente, bloqueante** | Provar denylist externa, permissões, prompt injection, forks e proteção da main |
| Platform & Observability | **Pendente, bloqueante** | Recuperação sem wake-up, métricas, limites e reconciliação |
| QA & Quality | **Pendente, bloqueante** | Matriz E2E negativa, CODEX-01 independente, não regressão |

A tabela não simula pareceres executados; somente os identifica para revisão.

## 14. Riscos não resolvidos

- **R1 (implantação bloqueada):** `main` agora tem ruleset ativo ID 25036481, porém a identidade atual usada pelo Work ainda pode ter acesso amplo. Separação escolhida: **remover escrita do Work no principal e usar credencial segregada/sandbox**; isso ainda exige configuração e teste humano de permissões.
- **R2:** evento Work perdido/coalescido ou tarefa pausada/excesso de franquia: backlog observado read-only, operador humano responsável pela retomada se não houver API/gatilho comprovado; não assumir auto-resume.
- **R3:** CODEX-01 e receipts humanos estão especificados no contrato, mas não implementados/testados; work login/issue comments continuam sem prova de origem humana.
- **R4:** latência e quotas Work não verificadas para a carga prevista; nenhum SLA assumido. Uma instância PostgreSQL ainda precisa de aprovação de fornecedor/infra, sem custo contratado por esta proposta.
- **R5:** publisher/DB com writer único e fencing definidos para a arquitetura, mas sem instância aprovada, implementação ou teste de duas execuções; `M3` bloqueado até M2b `PASS`.
- **R6:** migração do contrato financeiro existente para arquitetura sem API precisa de matriz de BR/EDGE/AC, sem apagar invariantes de gasto.
- **R7:** especificação incompleta de fluxos de fork. Bloquear mutação automática em fork.

**Critério de aceite da ADR:** o mecanismo de autorização e o perímetro de isolamento devem estar arquiteturalmente decididos e revistos por Security/Platform/QA; riscos que dependem de implementação podem permanecer como *gates de ativação*, desde que haja plano testável e regra fail-closed. Não antecipar evidência de implantação. Risco crítico de desenho não resolvido bloqueia `Accepted`; falha na implantação bloqueia **ativação**, mesmo após aceite documental.

## 15. Histórico de revisão

| Data | Responsável | Ação | Resultado |
| --- | --- | --- | --- |
| 2026-10-13 | Product & SDD | Proposta inicial após 3 canaries e autorização para elaborar | Proposed rev.1 |
| 2026-10-13 | Orchestrator / Tech Lead | Ajustes materiais após review-adr rev.1 (permissões, provenance humano, separação de gates) | Proposed rev.2 |
| 2026-10-13 | Orchestrator / Tech Lead | Rev.3: trust boundary de sandbox, receipts humanos, publisher pré-escrita, PostgreSQL/fencing e fingerprint CODEX-01 | Proposed rev.3 |

## 16. Revisão técnica

- **Parecer de `review-adr`:** Pendente, não executado.
- **Revisão decisória revisada:** Não aplicável.
- **Revisor:** Orchestrator / Tech Lead (a designar no fluxo de review).
- **Data:** Não aplicável.
- **Pendências bloqueantes:** pareceres especializados independentes e verificação do desenho da rev.3 (inclusive custo/autorizações para identidade segregada e PostgreSQL); isolamento real e canaries permanecem gates de **ativação**, não alegações de sucesso.
- **Pendências não bloqueantes:** Ajustes editoriais após revisão.

O texto não declara `Pronto para aceite humano` sem parecer verificável.

## 17. Aceite humano

- **Aceito:** Não.
- **Responsável humano:** Responsável pelo repositório.
- **Data:** Não aplicável.
- **Revisão decisória aceita:** Não aplicável.
- **Registro do aceite:** Não aplicável.

A autorização humana para **elaboração** não substitui revisão/aceite da ADR. Até o aceite, ADR-0014 rev.5 continua `Accepted`.
