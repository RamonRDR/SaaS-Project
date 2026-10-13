# Mode A híbrido: contrato de fronteiras de confiança (proposta)

**Status:** contrato candidato, NÃO implementado. **Data:** 2026-10-13. **Referências:** ADR-0015 rev.4, SDD-0002 v0.4, issue #10, PR #11. Nenhum componente descrito neste arquivo concede autorização de operação ou merge.

## 1. Topologia obrigatória

1. **Repositório principal:** `RamonRDR/SaaS-Project`, branch padrão `main`. Ruleset observado `main-protection` ID `25036481`, `active`, `~DEFAULT_BRANCH`, `bypass_actors=[]`, PR obrigatório, resolução de threads e checks `governance`/`secret-scan`. Exige zero aprovações obrigatórias, portanto **NÃO é gate humano de merge**; não substitui isolamento de escrita do agente.
2. **Sandbox de trabalho:** criar um **repositório separado** (nome a definir pelo humano) que contém somente material de trabalho permitido e nenhuma credencial ou token capaz de escrever no principal. Work escreve commits/PRs **somente nesse sandbox**, nunca em `SaaS-Project`. O sandbox não é um fork com acesso a segredos do principal e não deve receber artifacts confidenciais.
3. **Identidade Work:** reconfigurar a conexão GitHub/Work com uma **identidade distinta, com acesso de escrita apenas ao sandbox**. **Revogar a conexão atual do proprietário ao Work para escrita no principal antes de habilitar qualquer tarefa produtiva.** Não basta pedir ao agente para evitar o repo: GitHub UI e permissões efetivas da instalação devem demonstrar ausência de write/admin no principal. Se o conector não suportar tal isolamento, **não ativar a arquitetura híbrida no principal**.
4. **Publicador confiável:** GitHub Actions executado a partir de workflow/script **imutavelmente versionado na `main`** do repositório principal, com permissão mínima `contents:write` limitada à operação de publicação. **Work nunca recebe nem invoca essa credencial**. O publicador lê dados do sandbox como fonte não confiável, sem executar scripts dos candidatos e sem carregar workflows do PR.
5. **CI e reviewer:** testes do candidato sem secrets/credencial escrita; `CODEX-01` independente, ligado ao changeset e contrato trusted da `main`; controles de governança e merge executados no repositório principal.
6. **Operador humano:** identidade GitHub não delegada ao Work concede somente **escopo de execução reversível** por `workflow_dispatch` no principal. **Autorização de merge permanece exclusivamente nos dois canais existentes do AGENTS.md, regra 31:** comentário manual `HUMAN_MERGE_AUTHORIZATION` do responsável após READY, no mesmo PR/HEAD; ou decisão explícita no canal interativo do Orquestrador, que ele apenas registra com `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`. Workflow GitHub **não pode emitir** o segundo marcador.

## 2. Canal de autorização verificável

**Artefato canônico de ESCOPO apenas:** `ScopeGrantReceipt v1`, derivado de execução `workflow_dispatch` confiável na `main` por operador humano cuja credencial não está conectada ao Work. A API GitHub de runs e os dados de controle do job trusted validam origem, limite, validade e escopo; comentários não criam concessões de trabalho. Este receipt **não concede permissão de merge**.

**ScopeGrantReceipt v1** (dados de controle persistidos por job trusted, associados ao `run_id` da aprovação humana):

```json
{
  "schema_version": 1,
  "decision_type": "SCOPE_GRANT",
  "repository": "RamonRDR/SaaS-Project",
  "scope_id": "approved-scope-id",
  "allowed_paths": ["src/approved-area/**", "tests/approved-area/**"],
  "base_commit_sha": "<40-hex>",
  "operation_family": "DOCUMENTED_SMALL_CHANGE",
  "sandbox_repo": "<sandbox-repo-id>",
  "max_operations": 1,
  "expires_at_utc": "<RFC3339>",
  "approval_run_id": "<trusted-workflow-run-id>",
  "approval_actor": "<human-only-actor>",
  "trusted_main_workflow_sha": "<40-hex>"
}
```

**Validação fail-closed:** consultar metadados atuais da execução, `event=workflow_dispatch`, `head_branch=main`, workflow exato aprovado da `main`, ator em allowlist humana mantida fora do sandbox, sem poder ser usado pelo Work; comparar `sha` e contract revision do workflow, campos canônicos, destino/escopo/base/tempo/cota. Se não houver evidência de execução humana independente ou o artefato divergir, `HUMAN_DECISION_REQUIRED`. Uma concessão pode cobrir operações reversíveis delimitadas dentro do prazo, sem microautorizações para cada teste.

**MERGE-01: nenhum novo canal de aprovação.** Após `ORCHESTRATOR_READY` e a comprovação de `MERGE_ALLOWED` no mesmo PR/HEAD, a autorização de merge segue **exatamente** o AGENTS.md, regra 31:

- **Canal A, legado e preferencial neste piloto:** o responsável humano publica manualmente `HUMAN_MERGE_AUTHORIZATION` no PR/HEAD vigente, **depois de READY**. O verificador trusted consulta via API GitHub o comentário e seu timestamp, PR/HEAD/ator permitido, valida `ready.created_at < authorization_record.created_at < merged_at` após o merge e confirma que a identidade do Work não possui escrita/comentário autorizado no repositório principal. Conteúdo de comentário do sandbox/Work nunca é válido.
- **Canal B, interativo existente:** quando a decisão explícita ocorre no **canal interativo do Orquestrador, fora do GitHub**, e pode ser comprovada, o próprio Orquestrador apenas registra `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`, indicando sua autoria delegada e que está registrando decisão humana anterior. **`workflow_dispatch` não é esse canal** e nunca cria este marcador.

Qualquer aprovação proveniente de `workflow_dispatch`, texto de agente, receipt de escopo, comentário falso ou ausência de provenance válida falha fechado. Se for desejado no futuro autorizar merge por um terceiro canal GitHub, isso exige **alteração formal prévia do AGENTS.md/CI_GATES.md com aprovação humana específica**, fora deste PR.

**Verificações negativas:** ator Work tentando disparar workflow de escopo no principal, comentário imitando `HUMAN_MERGE_AUTHORIZATION`, `workflow_dispatch` tentando publicar `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION`, replay de `run_id`, receipt expirado, SHA divergente, execução por branch PR, autorização anterior a READY e falso READY devem falhar. A possibilidade de o Work ainda possuir qualquer permissão de comentário/escrita no principal bloqueia o piloto.

## 3. Pré-escrita do control plane e trusted publisher

- O **Work pode gravar livremente no sandbox isolado**, que não é fonte privilegiada. Nada que ele grave tem efeito no principal até passar pelo publicador confiável.
- O publicador monta o changeset completo `approved_base_sha → sandbox_candidate_sha` e verifica a lista de blobs/paths e os modos antes de criar QUALQUER blob/commit/ref/PR no principal. Caminhos proibidos: `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**`, `docs/PROJECT_STATUS.md`. Aplicar também allowlist explícita do scope grant, no máximo `src/approved-area/**` e `tests/approved-area/**` no piloto.
- Rejeitar diretórios/path traversal/case-fold e normalização ambígua, symlink, submodule, alteração de modo executável, binários, artefatos enormes, patches truncados, arquivo deletado/renomeado fora do escopo e código desconhecido antes de publicar. Usar objetos Git e manifest/digest de árvore completos, não um diff textual truncado. **Nenhum checkout/execução de código do sandbox em job com credencial GitHub de escrita**.
- Ao encontrar qualquer path protegido, rejeitar o **changeset inteiro** e transicionar para `HUMAN_DECISION_REQUIRED` com evidência; nunca publicar commit parcial nem tentar sanitizar automaticamente. Um check de PR sozinho é insuficiente, porque a negação deve ocorrer **antes da escrita**.
- Publicador **não** roda código do candidato e valida `ScopeGrantReceipt`, `operation_key`, owner/fencing, SHA esperado, origem do sandbox e manifest inteiro antes de criar branch `work/<operation_key>` no principal. Revalidar após criar ref/PR. Em transporte ambíguo, consultar o estado real e bloquear reenvio incerto.
- Branch de produto no principal e CI/SECRET/GOV permanecem separados do workflow de publicação e usam revisão vinculada ao HEAD. **Mudanças em control plane só por PR documental/técnico humano próprio**, nunca por esse caminho.

## 4. Exclusão durável e protocolo de checkpoint

**Backend escolhido para o desenho:** **PostgreSQL transacional em infraestrutura a ser autorizada pelo humano** (não é o banco de produção do SaaS). O Work **não recebe credenciais SQL**. Somente o writer trusted, isolado e executado de `main`, escreve o estado. **Não provisionar fornecedor pago, plano ou credenciais sem autorização humana.** Se storage transacional não estiver disponível, M2 permanece read-only e **M3 mutável está BLOQUEADO**; Git ref, issue comments e `concurrency.group` do Actions não substituem CAS.

Esquema mínimo **com cota por concessão**, não somente por operação:

```sql
CREATE TABLE scope_receipts (
  scope_receipt_run_id bigint PRIMARY KEY,
  grant_digest char(64) NOT NULL,
  max_operations integer NOT NULL CHECK (max_operations > 0),
  consumed_operations integer NOT NULL DEFAULT 0,
  expires_at timestamptz NOT NULL,
  state text NOT NULL CHECK (state IN ('ACTIVE', 'REVOKED', 'EXPIRED')),
  CHECK (consumed_operations >= 0 AND consumed_operations <= max_operations)
);

CREATE TABLE work_operations (
  operation_key text PRIMARY KEY,
  source_repo text NOT NULL,
  target_repo text NOT NULL,
  scope_receipt_run_id bigint NOT NULL
    REFERENCES scope_receipts(scope_receipt_run_id),
  expected_base_sha char(40) NOT NULL,
  candidate_sha char(40),
  owner_run_id bigint,
  fencing_epoch bigint NOT NULL DEFAULT 0,
  lease_expires_at timestamptz,
  state text NOT NULL,
  published_pr_number bigint,
  published_head_sha char(40),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (scope_receipt_run_id, operation_key)
);
```

**Protocolo de consumo:** somente o trusted writer da `main` pode registrar operações. Em **uma transação PostgreSQL**, executar `BEGIN → SELECT scope_receipts ... FOR UPDATE → validar assinatura/digest, expiração, estado e cota → verificar/reconciliar operation_key existente → se operação nova e consumed_operations < max_operations, incrementar consumed_operations e inserir work_operations → COMMIT`. **Sempre bloquear primeiro a linha `scope_receipts`, depois a linha da operação**, em ordem determinística, evitando deadlocks e corridas entre operations distintas. `operation_key` existente com o mesmo receipt é reentrada idempotente sem novo consumo; operação diferente com o mesmo `scope_receipt_run_id` compete pelo contador **compartilhado**, ainda que tenha `authorized_attempt` distinto. Para o piloto, `max_operations=1` e nenhum segundo `operation_key` pode ser admitido com o mesmo grant.

**Reserva conservadora:** o contador é consumido ao admitir a operação, antes de qualquer publicação. **Não liberar nem reembolsar automaticamente** cota após timeout, crash, lease expirado, falha de CI ou ACK GitHub incerto. Se a operação definitivamente não publicou e houver necessidade de reembolso, exigir decisão humana e transação auditável separada com prova negativa; no piloto, preferir emitir uma nova concessão. Expiração/revogação impede **novas** operações; efeitos de operação já admitida permanecem sujeitos ao escopo original, revogação e parada segura.

**Exclusão por operação:** sob o grant já consumido, uma transação `SELECT work_operations ... FOR UPDATE` valida owner/lease/`fencing_epoch` para o writer exclusivo. O owner revalida o epoch atual antes da publicação. Como GitHub e PostgreSQL não fazem commit atômico distribuído, não alegar exactly-once: falha entre POST e checkpoint exige **parar e reconsultar o GitHub** para identificar eventual commit/ref/PR antes de qualquer tentativa. Não promover lease expirado quando existe POST em voo ou resultado ambíguo.

**Provas obrigatórias antes de M3:**
1. Dois runners disputam a **mesma** `operation_key`, no máximo um publica.
2. Dois runners usam o **mesmo receipt `max_operations=1` com `operation_key` DIFERENTES**, e apenas um consegue reservar, o outro falha sem publicar. Repetir com tentativas distintas no identificador.
3. Reentrada da mesma operação não consome uma segunda unidade.
4. Crash antes/depois do POST, ACK desconhecido, lease/epoch stale, receipt revogado/expirado, 3+ operações e replay não produzem um segundo PR/commit; operação ambígua permanece bloqueada até readback confiável.

**Sem Postgres autorizado, implementado e esses testes verdes: M2 permanece read-only, M3 mutável BLOQUEADO.**

## 5. Evidência CODEX-01 e contrato trusted

`CODEX-01` é uma revisão **independente do Work**, com evidência imutável para:

```text
repo, pr, base_ref, base_tip_sha, merge_base_sha, head_sha,
payload_digest = SHA256(manifest completo do diff merge-base -> HEAD),
trusted_review_contract_digest = SHA256(closure completa do reviewer
na main: workflow, prompt, schema, parser, policies, modelo,
parâmetros e dependências executadas),
main_source_commit_sha, review_context_fingerprint
```

`review_context_fingerprint = SHA256(canon(repo,pr,base_ref,merge_base_sha,head_sha,payload_digest,trusted_review_contract_digest))`. **Antes de READY**, reconsultar árvores completas e reviewer trusted atual; qualquer divergência de `merge_base_sha`, `payload_digest` ou `trusted_review_contract_digest` invalida `clean`, ainda que `head_sha` seja igual. Mudança isolada do `base_tip_sha` sem alterar o fingerprint ainda exige revalidar CI/mergeability. Sem snapshot completo/contrato trusted, falhar fechado. Não iniciar segunda inferência de API paga para resolver divergência: piloto é zero API paga, e revisão indisponível → `BLOCKED_EXTERNAL`.

## 6. Marcos de ativação

- **M0: documento:** revisão e decisão humanas para ADR/SDD, sem criar credenciais ou runtime.
- **M1: identidade e trust boundary:** responsável revoga conexão Work com escrita em `SaaS-Project`, configura identidade Work separada apenas no sandbox, verifica negativas de acesso, confirma ruleset principal e canal humano-only. Sem prova, não prosseguir.
- **M2a: observer e ScopeGrantReceipt:** implementar somente grants de escopo por `workflow_dispatch` trusted, e comprovar que não produzem autorização de merge; merge mantém os dois canais do AGENTS.md. Scanner read-only sem disparar Work automaticamente.
- **M2b: writer serial e publicador:** escolher/autorizar PostgreSQL, implementar **bloqueio da linha do receipt, consumo de cota entre operation_keys distintas**, lock de operação/fencing, publicação pré-verificada e testes cruzados. Nenhum secret no Work. CODEX/GOV/SEC e autorização humana existente antes de qualquer merge.
- **M3: piloto Work sandbox:** só depois de M1/M2a/M2b `PASS`, habilitar task Work sobre sandbox e executar três operações pequenas. Publicador confiável cria PR draft no principal; não merge.
- **M4: negative/security:** duplicata, perda de evento, mutação control plane, stale reviewer, falsa autorização e recuperação de crash; bloquear falhas.
- **M5: decisão humana operacional:** expandir ou desativar; sem assinatura/limites garantidos, sem OpenAI API paga, sem merge automático.
- **M6: PR final/governança:** seguir `AGENTS.md` e `DONE_ALLOWED`, merge principal sempre autorizado por humano em ordem READY → autorização → merge.

A proposta **não foi implementada**. O ruleset da `main` é uma evidência concreta; isolamento de identidade, receipts, publisher e PostgreSQL são requisitos pendentes de execução e testes.
