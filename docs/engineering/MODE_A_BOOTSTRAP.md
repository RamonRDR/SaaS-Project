# Mode A Unattended: bootstrap seguro

## Escopo desta entrega

Primeiro incremento da Issue #1, conforme SDD-0001 v1.6 **Approved** e ADR-0014 rev.5 **Accepted**.

Este incremento introduz um workflow para diagnósticos da branch confiável `main`, um validador puro de contexto de evento e uma suíte de testes negativos. O dispatcher é apenas um **stub read-only**. Não existe ainda executor unattended funcional nem reconciliação do estado atual do GitHub.

## Entradas

- `pull_request` e `push`: executam apenas compilação e testes, sem segredos e com `contents:read`.
- `workflow_dispatch`: execução de diagnóstico solicitada explicitamente, opcionalmente com dica de número do PR.
- `repository_dispatch` (`mode_a_wakeup`): wake-up como dado não confiável, nunca uma autorização.
- `schedule` de seis em seis horas: executa diagnóstico sem mutações. **Não drena filas** nem prossegue PRs.

O job de diagnóstico faz checkout explícito da `main` e rejeita referência/repositório inesperados. O payload do evento é apenas uma indicação de contexto. Não há leitura de PRs, publicação de comentários, edição de arquivos, uso de credenciais de IA, gastos ou merge.

## Resultados e segurança

- `MODE_A_BOOTSTRAP_ONLY`: contrato mínimo válido; continua em `NOT_ACTIVATED`.
- `MODE_A_BOOTSTRAP_REJECTED`: evento/contexto inválido, falha fechada.
- `reconciled=false`, `writes_enabled=false` e `paid_inference_enabled=false` em todo resultado válido.
- Nenhum resultado do bootstrap representa `ORCHESTRATOR_STATE_V2`, `CODEX-01` clean ou `READY_FOR_HUMAN_MERGE`.

Logs contêm somente o diagnóstico estruturado e código de erro permitido. O arquivo do evento não é executado ou impresso.

## Testes

`python3 -m unittest discover -s .github/scripts -p 'test_mode_a_bootstrap.py' -v`

Os testes abrangem contexto de fork, ref incorreta, ação desconhecida, injeção em número do PR, divergência de inputs e payload inválido/grande. O job `bootstrap-tests` é a evidência de TEST-01 para este incremento.

## Dependências e próximos incrementos

Ainda são necessários, em PRs próprios, intake durável `PENDING`, reconciler de PR/HEAD, state machine V2 com provenance, Single-Writer Global/ledger íntegro com teste CAS-Lab, Budget Broker, Trusted Publisher separado, CODEX-01 independente e canaries E2E.

**Não configurar `OPENAI_API_KEY`, não ativar dispatch pago e não declarar `PHASE-0-G` concluída nesta entrega.** A ativação financeira depende de limites e preços positivos aprovados pelo humano e das provas de segurança/concorrência estipuladas na SDD/ADR.

Rollback: desabilitar o workflow `Mode A Bootstrap`. O Mode A interativo e os Governance Gates existentes permanecem independentes.
