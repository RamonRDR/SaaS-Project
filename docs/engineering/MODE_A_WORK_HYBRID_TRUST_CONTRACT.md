# Mode A híbrido: contrato de fronteiras de confiança (proposta)

**Status:** contrato candidato, NÃO implementado. **Data:** 2026-10-13. **Referências:** ADR-0015 rev.3, SDD-0002 v0.3, issue #10, PR #11. Nenhum componente descrito neste arquivo concede autorização de operação ou merge.

## 1. Topologia obrigatória

1. **Repositório principal:** `RamonRDR/SaaS-Project`, branch padrão `main`. Ruleset observado `main-protection` ID `25036481`, `active`, `~DEFAULT_BRANCH`, `bypass_actors=[]`, PR obrigatório, resolução de threads e checks `governance`/`secret-scan`. Exige zero aprovações obrigatórias, portanto **NÃO é gate humano de merge**; não substitui isolamento de escrita do agente.
2. **Sandbox de trabalho:** criar um **repositório separado** (nome a definir pelo humano) que contém somente material de trabalho permitido e nenhuma credencial ou token capaz de escrever no principal. Work escreve commits/PRs **somente nesse sandbox**, nunca em `SaaS-Project`. O sandbox não é um fork com acesso a segredos do principal e não deve receber artifacts confidenciais.
3. **Identidade Work:** reconfigurar a conexão GitHub/Work com uma **identidade distinta, com acesso de escrita apenas ao sandbox**. **Revogar a conexão atual do proprietário ao Work para escrita no principal antes de habilitar qualquer tarefa produtiva.** Não basta pedir ao agente para evitar o repo: GitHub UI e permissões efetivas da instalação devem demonstrar ausência de write/admin no principal. Se o conector não suportar tal isolamento, **não ativar a arquitetura híbrida no principal**.
4. **Publicador confiável:** GitHub Actions executado a partir de workflow/script **imutavelmente versionado na `main`** do repositório principal, com permissão mínima `contents:write` limitada à operação de publicação. **Work nunca recebe nem invoca essa credencial**. O publicador lê dados do sandbox como fonte não confiável, sem executar scripts dos candidatos e sem carregar workflows do PR.
5. **CI e reviewer:** testes do candidato sem secrets/credencial escrita; `CODEX-01` independente, ligado ao changeset e contrato trusted da `main`; controles de governança e merge executados no repositório principal.
6. **Operador humano:** conta/identidade que não é delegada ao Work (nem disponibilizada à sua sessão/navegador) inicia os atos `workflow_dispatch` **no principal** para concessão de escopo e autorização final de merge. Essa identidade deve ser comprovadamente distinta da identidade da automação. Nunca confiar apenas no login mostrado em comentário.

## 2. Canal de autorização verificável

**Artefato canônico proposto:** receipt de uma execução `workflow_dispatch` de workflow confiável na `main`, iniciado no GitHub pelo operador humano **cuja credencial não está conectada ao Work**. A leitura autorizadora usa exclusivamente a API GitHub de runs e payload validado da ação confiável; comentários não criam autorização.

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

**MergeGrantReceipt v1:** novo `workflow_dispatch` humano e trusted, **posterior** a `ORCHESTRATOR_READY`, com `pr_number`, `head_sha`, `ready_comment_id`, `ready_created_at`, `decision=APPROVE_MERGE`, `approval_run_id` e `approval_actor`. Workflow reconsulta PR/HEAD, `MERGE_ALLOWED`, CI/review e ordem temporal; só o job trusted converte a decisão em comentário `ORCHESTRATOR_RECORDED_HUMAN_AUTHORIZATION` com provenance do run. Um texto/ACK publicado pelo Work ou comentário do mesmo login não é receipt. O merge principal permanece ação humana válida no GitHub; qualquer automação de merge além desse checkpoint exige aprovação arquitetural nova.

**Verificações negativas:** ator Work tentando disparar workflow no principal, comentário que imita grant, replay de `run_id`, receipt expirado, SHA divergente, execução do workflow por branch PR, ordem temporal inválida e falso `READY` devem falhar sem escrita.

## 3. Pré-escrita do control plane e trusted publisher

- O **Work pode gravar livremente no sandbox isolado**, que não é fonte privilegiada. Nada que ele grave tem efeito no principal até passar pelo publicador confiável.
- O publicador monta o changeset completo `approved_base_sha → sandbox_candidate_sha` e verifica a lista de blobs/paths e os modos antes de criar QUALQUER blob/commit/ref/PR no principal. Caminhos proibidos: `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**`, `docs/PROJECT_STATUS.md`. Aplicar também allowlist explícita do scope grant, no máximo `src/approved-area/**` e `tests/approved-area/**` no piloto.
- Rejeitar diretórios/path traversal/case-fold e normalização ambígua, symlink, submodule, alteração de modo executável, binários, artefatos enormes, patches truncados, arquivo deletado/renomeado fora do escopo e código desconhecido antes de publicar. Usar objetos Git e manifest/digest de árvore completos, não um diff textual truncado. **Nenhum checkout/execução de código do sandbox em job com credencial GitHub de escrita**.
- Ao encontrar qualquer path protegido, rejeitar o **changeset inteiro** e transicionar para `HUMAN_DECISION_REQUIRED` com evidência; nunca publicar commit parcial nem tentar sanitizar automaticamente. Um check de PR sozinho é insuficiente, porque a negação deve ocorrer **antes da escrita**.
- Publicador **não** roda código do candidato e valida `ScopeGrantReceipt`, `operation_key`, owner/fencing, SHA esperado, origem do sandbox e manifest inteiro antes de criar branch `work/<operation_key>` no principal. Revalidar após criar ref/PR. Em transporte ambíguo, consultar o estado real e bloquear reenvio incerto.
- Branch de produto no principal e CI/SECRET/GOV permanecem separados do workflow de publicação e usam revisão vinculada ao HEAD. **Mudanças em control plane só por PR documental/técnico humano próprio**, nunca por esse caminho.

## 4. Exclusão durável e protocolo de checkpoint

**Backend escolhido para o desenho:** **PostgreSQL transacional em infraestrutura a ser autorizada pelo humano** (não é o banco de produção do SaaS). O Work **não recebe credenciais SQL**. Somente o writer trusted, isolado e executado de `main`, escreve o estado. **Não provisionar fornecedor pago, plano ou credenciais sem autorização humana.** Se storage transacional não estiver disponível, M2 permanece read-only e **M3 mutável está BLOQUEADO**; Git ref, issue comments e `concurrency.group` do Actions não substituem CAS.

Esquema mínimo:

```sql
CREATE TABLE work_operations (
  operation_key text PRIMARY KEY,
  source_repo text NOT NULL,
  target_repo text NOT NULL,
  scope_receipt_run_id bigint NOT NULL,
  expected_base_sha char(40) NOT NULL,
  candidate_sha char(40),
  owner_run_id bigint,
  fencing_epoch bigint NOT NULL DEFAULT 0,
  lease_expires_at timestamptz,
  state text NOT NULL,
  published_pr_number bigint,
  published_head_sha char(40),
  updated_at timestamptz NOT NULL DEFAULT now()
);
```

Transições sob **uma transação** `BEGIN → SELECT ... FOR UPDATE → conferir state/receipt/lease → incrementar fencing_epoch se takeover permitido → atualizar owner/lease → COMMIT`. `operation_key` idêntica recebe o mesmo registro e resultados idempotentes. Um writer deve checar seu `fencing_epoch` e owner atual em transação imediatamente antes da publicação; como GitHub e DB não são uma transação distribuída, não há garantia automática exactly-once: serializar a região crítica de publicação **em writer exclusivo real**, testar fencing/lease e, em qualquer intervalo ambíguo entre POST e checkpoint, **bloquear e exigir readback do GitHub antes de qualquer retry**. Jamais promover um lease expirado quando envio anterior possa ter ocorrido ou permanecer em trânsito.

**Teste de concorrência obrigatório antes de M3:** dois runners independentes disputam a mesma `operation_key`, apenas um consegue `CLAIMED/PUBLISHING`, o outro observa o mesmo registro; simular crash antes e depois de commit GitHub, stale epoch, POST de resultado desconhecido, timeout e corrida de 3+ operações. Nenhum segundo PR/commit no principal. A falha desses testes impede piloto mutável.

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
- **M2a: observer e receipts:** implementar em PR revisado na main, testar `workflow_dispatch` humano e emissão/validação de receipts; scanner read-only sem disparar Work automaticamente.
- **M2b: writer serial e publicador:** escolher/autorizar instância PostgreSQL, implementar transações, fencing, verificação pré-escrita e teste de concorrência; nenhum secret no Work. CodeX/GOV/SEC e autorização humana antes do merge técnico.
- **M3: piloto Work sandbox:** só depois de M1/M2a/M2b `PASS`, habilitar task Work sobre sandbox e executar três operações pequenas. Publicador confiável cria PR draft no principal; não merge.
- **M4: negative/security:** duplicata, perda de evento, mutação control plane, stale reviewer, falsa autorização e recuperação de crash; bloquear falhas.
- **M5: decisão humana operacional:** expandir ou desativar; sem assinatura/limites garantidos, sem OpenAI API paga, sem merge automático.
- **M6: PR final/governança:** seguir `AGENTS.md` e `DONE_ALLOWED`, merge principal sempre autorizado por humano em ordem READY → autorização → merge.

A proposta **não foi implementada**. O ruleset da `main` é uma evidência concreta; isolamento de identidade, receipts, publisher e PostgreSQL são requisitos pendentes de execução e testes.
