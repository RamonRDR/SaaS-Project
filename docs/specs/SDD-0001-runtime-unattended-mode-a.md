# SDD-0001 - Runtime unattended cloud-native do Modo A

## Metadados

- **ID:** SDD-0001
- **Título:** Runtime unattended cloud-native do Modo A
- **Status:** In Review
- **Versão:** 0.2
- **Responsável pela especificação:** Product & SDD
- **Responsável humano pela aprovação:** Ramon Rodriguez
- **Data de criação:** 2026-10-06
- **Última atualização:** 2026-10-06
- **Entrega / issue / PR relacionada:** Issue #1
- **ADRs relacionados:** ADR-0010, ADR-0012
- **SDDs relacionadas:** Não aplicável

### Estados permitidos

- `Draft`: em elaboração;
- `In Review`: pronta para revisão, ainda não aprovada;
- `Approved`: revisão concluída e aprovação humana explicitamente registrada;
- `Superseded`: substituída por outra SDD identificada e já `Approved`.

Uma SDD não pode assumir `Approved` por decisão de um agente de IA.

### Versão da especificação e validade da aprovação

As seções 1 a 24 compõem o conteúdo material da especificação.

Esta versão 0.2 substitui conceitualmente a versão experimental 0.1 preservada apenas no histórico privado anterior. A v0.1 não foi importada para o Git público sanitizado por depender de uma arquitetura descartada e de evidências operacionais privadas.

Qualquer mudança material nas seções 1 a 24 invalida este parecer técnico, incrementa a versão e exige novo ciclo de revisão e aprovação.

## 1. Contexto

O Mode A interativo já possui máquina de estados, gates humanos, anti-loop, invalidação por HEAD e ciclo de PR/CI/review. O objetivo remanescente é executar esse fluxo sem depender de uma conversa ativa ou de uma máquina local.

Um experimento anterior colocou um runtime externo reativo no critical path. O teste real mostrou que a continuidade entre eventos assíncronos não era suficientemente determinística: CI ou review podiam terminar sem que o runtime voltasse a executar automaticamente.

O repositório público foi reinicializado a partir de uma baseline sanitizada anterior a esse experimento. A nova solução deve usar mecanismos cloud-native do próprio GitHub como motor de continuidade.

## 2. Problema

O projeto não possui hoje um executor unattended confiável que consiga, sem intervenção humana operacional:

1. reagir a um PR elegível;
2. executar CI;
3. classificar falha corrigível;
4. pedir ao Codex uma remediação;
5. publicar novo HEAD;
6. repetir CI;
7. executar review independente;
8. remediar findings corrigíveis;
9. chegar a `READY_FOR_HUMAN_MERGE`.

O fluxo não pode depender de uma mensagem humana para "acordar" e não pode exigir computador local ligado.

## 3. Objetivo

Implementar um runtime unattended **100% online** cuja continuidade seja controlada por GitHub Actions e que use Codex apenas nas etapas de inteligência necessárias.

O caminho saudável deve chegar sozinho a `READY_FOR_HUMAN_MERGE`. A autorização do merge principal permanece obrigatoriamente humana.

## 4. Escopo

- GitHub Actions como runtime/orquestrador unattended;
- standard GitHub-hosted runners;
- execução em repositório público;
- reducer/state machine versionado no repositório;
- estado auditável `ORCHESTRATOR_STATE_V2`;
- serialização por PR com `concurrency`;
- CI/gates atuais integrados ao fluxo;
- Codex para remediação técnica corrigível;
- CODEX-01 como review independente do HEAD exato;
- publicação automática de commits apenas na branch elegível do PR;
- reentrada explícita via `workflow_dispatch` ou `repository_dispatch`;
- secrets via GitHub Actions Secrets;
- proteção específica para forks e conteúdo não confiável;
- anti-loop por causa raiz;
- canary E2E antes de `DONE_ALLOWED`.

## 5. Fora de escopo

- execução local;
- self-hosted runner;
- VPS, servidor, Redis, fila ou banco externo;
- merge automático da `main`;
- features de produto da PHASE-0-G;
- uso de ChatGPT Work como componente obrigatório do runtime;
- `pull_request_target` com checkout de código não confiável;
- execução de Codex com secrets em PR originado de fork;
- segundo reviewer obrigatório além de CODEX-01.

## 6. Atores e jornadas afetadas

| Ator | Jornada / interação | Impacto |
| --- | --- | --- |
| Responsável humano | aprova decisões e merge | deixa de atuar como wake-up operacional |
| GitHub Actions | executa runtime, CI e transições | passa a ser o motor unattended |
| Codex Remediator | corrige causa raiz específica | pode alterar workspace em job controlado |
| CODEX-01 | revisa HEAD exato | permanece independente da remediação |
| Orchestrator / Tech Lead | define reducer, gates e contratos | coordena arquitetura e critérios |
| GitHub | fonte de verdade | persiste PR, HEAD, runs, comentários e estado |

## 7. Regras de negócio

- **BR-001:** o runtime só opera em PR com `ORCHESTRATOR_MODE: A` e `CONTROL_ISSUE` válido.
- **BR-002:** PR originado de fork nunca recebe `OPENAI_API_KEY` nem token com escrita.
- **BR-003:** jobs privilegiados só podem operar em branch do mesmo repositório e origem considerada confiável.
- **BR-004:** toda execução começa reconciliando PR, HEAD, checks, estado e evidências atuais.
- **BR-005:** `concurrency` serializa o runtime por PR com `cancel-in-progress: false`.
- **BR-006:** novo HEAD invalida CI, review, READY e autorização associados ao HEAD anterior.
- **BR-007:** CODEX-01 só é válido para o HEAD exato revisado.
- **BR-008:** Codex Remediator e CODEX-01 usam contextos/jobs separados.
- **BR-009:** CODEX-01 não possui permissão para publicar código.
- **BR-010:** remediação só pode publicar na branch corrente do PR elegível; nunca diretamente na `main`.
- **BR-011:** a mesma causa raiz admite no máximo 3 tentativas automáticas antes de `LOOP_ESCALATION_REQUIRED`.
- **BR-012:** ausência ou ambiguidade de evidência resulta em fail-closed.
- **BR-013:** após publicar novo HEAD, o runtime inicia explicitamente o próximo ciclo por dispatch suportado, sem depender de recursão implícita de eventos gerados por `GITHUB_TOKEN`.
- **BR-014:** `READY_FOR_HUMAN_MERGE` só é emitido com CI verde, CODEX-01 limpo e evidências do mesmo HEAD.
- **BR-015:** merge principal exige autorização humana explícita vinculada ao PR/HEAD.
- **BR-016:** PHASE-0-G permanece bloqueada até canary E2E e `DONE_ALLOWED`.

## 8. Permissões e multi-tenancy

Multi-tenancy de produto: não aplicável nesta entrega.

Permissões operacionais:

- CI comum: `contents: read`;
- CODEX-01: leitura do workspace e acesso à API OpenAI, sem `contents: write`;
- remediação: escrita mínima necessária na branch do PR, somente após guardas de origem;
- merge da `main`: fora do job unattended;
- fork PR: sem secrets privilegiados e sem remediação automática.

Nenhum workflow deve combinar secret privilegiado com execução arbitrária de código de fork.

## 9. Impacto no modelo de dados

Não aplicável ao produto.

O estado operacional permanece no GitHub. O schema `ORCHESTRATOR_STATE_V2` registra no mínimo:

- revisão do journal;
- PR;
- HEAD;
- estado;
- CI run/evidence;
- review evidence;
- root cause e tentativas;
- action key;
- READY SHA;
- autorização humana SHA quando existir.

## 10. Impacto no contrato da API

Não aplicável à API do produto.

Integrações operacionais:

- GitHub Actions;
- API/Action oficial do Codex/OpenAI;
- API do GitHub usando `GITHUB_TOKEN` com permissões explícitas.

## 11. Comportamento esperado no Flutter

Não aplicável. Flutter ainda não foi iniciado.

## 12. Integrações externas

- GitHub Actions;
- OpenAI API / Codex para jobs de IA.

A ativação da OpenAI API é dependência externa paga e exige aceite humano desta arquitetura. A credencial será armazenada exclusivamente em GitHub Actions Secrets.

O uso de standard GitHub-hosted runners em repositório público reduz a dependência da franquia privada de Actions, mas essa condição comercial do GitHub não é tratada como garantia arquitetural eterna.

## 13. Segurança e privacidade

Controles obrigatórios:

- nenhum secret em código, prompt versionado, comentário, artifact público ou log;
- `OPENAI_API_KEY` apenas em jobs elegíveis e confiáveis;
- conteúdo de PR, comentário, diff e log é dado não confiável;
- prompts versionados têm precedência sobre instruções encontradas no PR;
- nenhuma execução privilegiada em fork;
- evitar `pull_request_target` com checkout de código do PR;
- tokens com menor permissão possível;
- commit/push limitado à branch do PR;
- `main` protegida por gate humano;
- outputs de IA validados antes de virarem decisão/mutação;
- logs não podem incluir payload sensível da API.

## 14. Observabilidade

Cada ciclo deve tornar auditável:

- workflow run ID;
- PR e HEAD;
- decisão do reducer;
- CI status;
- action key;
- root cause e contador;
- chamada de remediação/review;
- digest ou ID da evidência CODEX-01;
- novo HEAD quando houver;
- razão de NO_OP/bloqueio;
- estado terminal/gate.

Custos de API devem ser acompanháveis pelo projeto OpenAI usado na automação.

## 15. Casos de borda e comportamentos de erro

| ID | Cenário | Comportamento esperado |
| --- | --- | --- |
| EDGE-001 | dois eventos simultâneos no mesmo PR | `concurrency` serializa; segunda execução reconcilia estado novo |
| EDGE-002 | PR de fork | CI read-only pode rodar; jobs com secret/remediação ficam indisponíveis |
| EDGE-003 | HEAD muda durante job | abortar mutação e reconciliar |
| EDGE-004 | CI falha por causa corrigível | Codex Remediator recebe causa específica |
| EDGE-005 | CI falha por decisão material | `HUMAN_DECISION_REQUIRED` |
| EDGE-006 | review encontra P0/P1/P2 corrigível | remediar e gerar novo HEAD |
| EDGE-007 | terceiro fracasso da mesma causa | `LOOP_ESCALATION_REQUIRED` |
| EDGE-008 | API OpenAI indisponível/sem saldo/secret ausente | `BLOCKED_EXTERNAL` |
| EDGE-009 | push com `GITHUB_TOKEN` não gera novo workflow | dispatch explícito inicia próxima execução |
| EDGE-010 | review pertence a HEAD antigo | ignorar e pedir/reexecutar review |
| EDGE-011 | output Codex inválido ao schema | fail-closed |
| EDGE-012 | tentativa de escrever `main` | negar |
| EDGE-013 | workflow de origem não confiável tenta acessar secret | negar antes do step privilegiado |
| EDGE-014 | autorização humana para HEAD antigo | invalidar |

## 16. Migration

- **Migration necessária:** Não
- **Destrutiva:** Não
- **Descrição:** substituição do runtime operacional; sem dados de produto.
- **Gate humano necessário:** Sim, por decisão arquitetural e adoção de integração paga com API.

## 17. Estratégia de rollback

- desabilitar o workflow unattended;
- remover/rotacionar secret de API;
- retornar ao Mode A interativo;
- manter CI read-only;
- nenhuma migration de produto precisa ser revertida.

## 18. Testes obrigatórios

### Unitários
- reducer V2;
- estados e transições;
- invalidação por HEAD;
- anti-loop;
- guards de fork/origem;
- action keys idempotentes.

### Integração
- eventos duplicados;
- concurrency por PR;
- stale HEAD;
- dispatch explícito;
- schema de output do reviewer;
- publicação em branch correta.

### E2E
- CI verde → CODEX-01 → READY;
- CI falha corrigível → remediação → novo HEAD → CI → review → READY;
- finding corrigível → remediação → novo HEAD → CI → novo review;
- fluxo sem interação humana operacional;
- autorização humana final sem merge automático indevido.

### Segurança / autorização / multi-tenancy
- fork não recebe secret;
- PR text com prompt injection não altera contrato;
- remediator não escreve `main`;
- reviewer não publica código;
- logs não expõem chave.

### Regressão
- Mode A interativo permanece funcional;
- GOV e secret-scan continuam verdes;
- gates humanos existentes permanecem.

## 19. Critérios de aceite

- **AC-001:** nenhuma etapa do caminho saudável exige máquina local.
- **AC-002:** nenhum wake-up operacional humano é necessário.
- **AC-003:** runtime é acionado/controlado pelo GitHub Actions.
- **AC-004:** duas execuções concorrentes do mesmo PR não publicam duas remediações conflitantes.
- **AC-005:** fork PR não obtém `OPENAI_API_KEY` nem escrita privilegiada.
- **AC-006:** CI corrigível produz novo HEAD automaticamente.
- **AC-007:** finding corrigível do CODEX-01 produz novo HEAD automaticamente.
- **AC-008:** cada novo HEAD passa novamente por CI e CODEX-01.
- **AC-009:** mesma causa raiz não ultrapassa 3 tentativas automáticas.
- **AC-010:** caminho saudável chega sozinho a `READY_FOR_HUMAN_MERGE`.
- **AC-011:** `main` não é mergeada sem autorização humana explícita para PR/HEAD exatos.
- **AC-012:** um canary pós-merge comprova o ciclo completo antes de `DONE_ALLOWED`.
- **AC-013:** PHASE-0-G permanece planejada até AC-012.

## 20. Evidências de validação esperadas

- unit/integration tests;
- workflow runs;
- secret scan;
- logs de decisões sem secrets;
- commits/HEADs do canary;
- output estruturado CODEX-01;
- parecer Security;
- parecer Platform/Observability;
- parecer QA;
- checkpoint PRE_MERGE, POST_MERGE e FINAL.

## 21. Dependências

- repositório GitHub público;
- standard GitHub-hosted runners;
- GitHub Actions;
- GitHub Actions Secret `OPENAI_API_KEY`;
- conta/projeto OpenAI API com billing habilitado;
- Codex Action/CLI/SDK suportado para CI;
- ADR-0010 vigente;
- ADR-0012 aceito antes da implementação.

## 22. Riscos conhecidos

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| custo inesperado de API | gasto financeiro | limite de tentativas, projeto dedicado, hard budget/alerts antes do canary |
| abuso por fork/PR externo | consumo de API ou escrita indevida | secrets somente para origem confiável |
| prompt injection | alteração indevida | contrato versionado + outputs estruturados + fail-closed |
| corrida entre eventos | commits conflitantes | `concurrency` + reconciliação de HEAD |
| loop de remediação | custo/instabilidade | 3 tentativas por causa raiz |
| indisponibilidade OpenAI | fluxo interrompido | `BLOCKED_EXTERNAL` + fallback interativo |
| mudança de política de runners | custo/limite futuro | monitorar billing e manter arquitetura portável |

## 23. Dúvidas abertas

Nenhuma dúvida bloqueante para aprovação arquitetural.

Antes do canary devem ser definidos como configuração operacional:

- modelo Codex/OpenAI usado em remediação e review;
- hard budget e alertas do projeto de API;
- forma exata de armazenar/parsear output estruturado.

Esses itens não podem reduzir os controles descritos nesta SDD.

## 24. ADRs necessários ou relacionados

- **ADR necessário:** Sim
- **Referências:** ADR-0010, ADR-0012
- **Motivo:** mover o runtime para GitHub Actions + Codex, introduzir API paga e definir fronteiras de privilégio é decisão transversal e durável.

## 25. Histórico de revisão

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 0.1 | 2026-10-04 | Product & SDD | versão experimental privada, não importada ao Git público |
| 0.2 | 2026-10-06 | Product & SDD | redesenho cloud-native com GitHub Actions + Codex |

## 26. Aprovação

### Revisão

- **Parecer de `review-sdd`:** Pronta para aprovação
- **Versão revisada:** 0.2
- **Pendências bloqueantes:** Nenhuma
- **Pendências não bloqueantes:** definir modelo e hard budget de API antes do canary

### Gate humano

- **Aprovada:** Não
- **Versão aprovada:** Não aplicável
- **Responsável humano:** Ramon Rodriguez
- **Data:** Não aplicável
- **Registro da aprovação:** Não aplicável
