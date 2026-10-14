# Mode A: plano de piloto Work sandbox → promoção humana

**Atualização:** 2026-10-14. **Status:** planejamento documental da opção A, ainda sem aceite ADR/SDD e sem implementação do piloto. **Rastreabilidade:** issue #10 (decisão humana), issue #8 (canaries), PR #11.  
**Contratos propostos:** ADR-0015 rev.6 `Proposed` e SDD-0002 v0.6 `In Review`.  
**Vigentes:** ADR-0014 rev.5 `Accepted`, SDD-0001 v1.6 `Approved`, `AGENTS.md`, `CI_GATES.md`.

## 1. Objetivo e limites

Demonstrar utilidade de desenvolvimento Work sem API paga nem exposição de escrita do `RamonRDR/SaaS-Project`. Work atua **só em sandbox**, produz PR draft; humano examina diff completo, transporta **manualmente** mudança pequena por GitHub web para branch/PR principal; CI, Codex e autorização de merge continuam. **Não prometer unattended completo**: a promoção é um gate humano consciente.

A escolha da opção A foi aprovada como direção em 14/10/2026, não como aceite da ADR, aprovação da SDD, ativação Work, gasto ou autorização de merge.

## 2. Evidências existentes e suas limitações

| Canary | Evidência | Não demonstra |
| --- | --- | --- |
| C1 wake-up | [Issue #8](https://github.com/RamonRDR/SaaS-Project/issues/8), ACK em PR #6 | Garantia de entrega e isolamento de credenciais |
| C2 desenvolvimento | PR #7 draft, CI verde | Restrição da conexão Work a sandbox |
| C3 correção | PR #9 draft, CI vermelho → verde | Transporte humano e review Codex final do principal |

Essas tarefas experimentais estão desativadas e não são runtime habilitado para o piloto novo.

## 3. Pré-requisitos de confiança (fail-closed)

- **Sandbox:** humano escolhe/revisa repositório segregado, sem secrets; `RamonRDR/SaaS-CAS-Lab` é candidato existente **não aprovado automaticamente**.
- **Conexão Work:** conferir e retirar alcance de escrita/comentário/admin no principal, auditar permissões de instalação e testar acesso negativo antes de habilitar task. Uma conexão owner GitHub com acesso amplo **não atende**. Se não for possível restringir, M2 bloqueado.
- **Principal:** ruleset `main-protection` ID 25036481 ativo; exigir PR, `governance`, `secret-scan`, resolver threads e gates de CODEX-01, READY, MERGE-01; 0 approvals obrigatórios não substitui autorização humana.
- **Promover:** um humano avalia candidato e reescreve/copia **manual e conscientemente** patch pequeno para branch/PR principal pela interface GitHub. Nenhum token/importador autônomo, PostgreSQL, claim ou `PUBLISH_INTENT`.
- **Denylist:** `.github/**`, `.ai/**`, `AGENTS.md`, `SECURITY.md`, `docs/engineering/**`, `docs/specs/**`, `docs/adr/**` e `docs/PROJECT_STATUS.md`. Se patch candidato tocar qualquer caminho proibido, **rejeitar inteiro**, sem promoção parcial.
- **Gates do PR principal:** diff/manifests e SHAs registrados, CI e CODEX-01 vinculados ao HEAD real do principal **após último commit**, MERGE-01 somente com autorização humana posterior.

## 4. Roadmap por gates

| Marco | Entrega | Gate de saída |
| --- | --- | --- |
| M0 Documentação | ADR rev.6, SDD v0.6, plano/contrato e índices no PR #11 DRAFT | GOV/SEC, Codex diagnóstico, pareceres formais e **aceite/aprovação documental humanos separados**, sem merge implícito |
| M1 Isolamento | Humano avalia sandbox, limita conexão Work e confirma acesso negativo ao principal | Security: evidência de permissões e ausência de secrets; falha → `HUMAN_DECISION_REQUIRED` |
| M2 Canary Work sandbox | Um item reversível e pequeno, PR draft e CI sandbox | Sem alterações principal; eventos/CI/quota observados com logs e estados |
| M3 Promoção humana | Humano valida manifesto, recria patch no principal por GitHub web e abre PR draft próprio | Dados de ambos PRs registrados, allowlist e denylist verificadas, nenhum importador automático |
| M4 Revisão e decisão | GOV/SEC/testes/CODEX-01 do HEAD principal, READY, MERGE-01 por humano | Gate humano final, sem merge automático nem antecipar `PHASE-0-G` |
| F Futuro opcional | Estudo de publicador/autonomia de promoção | **Nova ADR/SDD e PoC de credenciais/revogação** com aprovação específica, fora de A |

Uma falha de isolamento ou de transporte seguro não cria licença para reintroduzir o publicador autônomo das versões anteriores.

## 5. Rastreabilidade DE/PARA da governança

| Contrato vigente / proposta anterior | No piloto A |
| --- | --- |
| ADR-0014 / SDD-0001 com Budget Broker pago | Permanecem vigentes historicamente; **não ativar API paga** |
| Work mesmo-repo nos canaries | Substituir por sandbox separado com identidade efetivamente restrita |
| Publicador GitHub automático do PR #11 revs.3–5 | **Fora do escopo**; nenhum token principal delegado a Work/importador |
| PostgreSQL, `ScopeGrantReceipt` e `PUBLISH_INTENT` | **Não implementar/contratar** no piloto |
| Control plane denylist `AGENTS.md` regra 40 | Rejeitar **candidato inteiro antes da promoção humana** |
| CODEX-01 após HEAD final | Preservar, **sobre PR principal**, não evidência do sandbox |
| READY → autorização → merge | Preservar conforme `AGENTS.md` regra 31, sem autorização implícita pela opção A |
| Observador read-only | Permitido depois de PR técnico/revisão próprios, sem fingir gatilho Work |
| Anti-loop `WRITER_CAPABILITY_REVOCATION` | Escalado; eliminado do envelope, **não aceito como risco residual** |
| `PHASE-0-G`, PRs #4/#6/#7/#9 | Preservados em seus estados; nenhum merge/fechamento automático |

## 6. Matriz de testes

| Teste | Entrada | Saída obrigatória |
| --- | --- | --- |
| T01 | Permissões Work ainda incluem escrita principal | Bloquear M2, sem task ativa |
| T02 | Candidato altera `.github/**` ou control plane | Rejeitar patch **inteiro**, não promover |
| T03 | Texto malicioso em comentário/evento | Ignorar instrução; reconsultar estado |
| T04 | Bot ou wake-up duplicado | Sem duplicar operação lógica, ou escalar |
| T05 | Quota ou evento não entregue | `BLOCKED_EXTERNAL`, humano retoma sem API paga |
| T06 | Humano promove patch pequeno via web | Dois PRs/HEADs/diffs documentados, alterações permitidas |
| T07 | HEAD sandbox mudou depois de validado | Invalidar aceite candidato, reavaliar |
| T08 | PR principal tem diff diferente | Rever no principal e só usar suas evidências |
| T09 | CI principal vermelho/ausente | Sem READY e sem merge |
| T10 | CODEX-01 ausente ou anterior a último commit | Sem READY, pedir review do HEAD final |
| T11 | Work tenta comentar/escrever no principal | Permissão negativa comprovada; se conseguir, bloquear piloto |
| T12 | Merge sem autorização humana posterior | Impedir, conforme governança MERGE-01 |
| T13 | Solicitação de publisher/DB/API paga | Fora do escopo, nova decisão humana |
| T14 | Falha idêntica reaparece três vezes | `LOOP_ESCALATION_REQUIRED` |
| T15 | GitHub web não permite transporte íntegro | `HUMAN_DECISION_REQUIRED`; não automatizar silenciosamente |

Não chamar os testes de PASS com base na existência desta tabela.

## 7. Indicadores

Medir tempo de wake-up, CI do sandbox, tentativas, taxa de patches rejeitados, tempo/esforço de promoção humana, divergências de diff/HEAD, CI e CODEX principal, bloqueios/quota. Nenhum SLA, frequência de eventos ou disponibilidade da ferramenta é assumido.

## 8. Responsabilidades humanas

- Aceitar ADR rev.6 e aprovar SDD v0.6 **separadamente**, após pareceres.
- Escolher sandbox, conferir permissões GitHub/Work, autorizar/habilitar canary específico e desligar em falhas.
- Conferir diff completo do candidato, executar transferência **manual** no GitHub e abrir PR principal.
- Validar READY e autorizar cada merge no mesmo PR/HEAD, nunca consentimento genérico.
- Não contratar serviço nem alterar governança principal por inferência.

## 9. Estado e próximos gates

- **Concluído:** aprovação humana da **direção A** para documentação, três canaries históricos, ruleset principal ativo.
- **Em revisão:** PR #11 documental, ADR-0015 rev.6 `Proposed` e SDD-0002 v0.6 `In Review`. Review Codex do novo HEAD ainda precisa ser solicitado/concluído.
- **Não concluído:** avaliação do sandbox, restrição Work, task canary nova, patch promovido, CI/Codex de PR piloto principal, aceite documental, merge.
- **Bloqueio:** se a conexão Work não puder excluir escrita no principal, o piloto A não pode ser ativado. Nenhum custo ou API paga.
- **Próximo passo:** CI documental → revisão Codex → pareceres formais → decisão humana separada sobre ADR/SDD → somente depois M1/M2.

O projeto não considera `PHASE-0-G` concluída e não altera `docs/PROJECT_STATUS.md` ou `AGENTS.md` nesta entrega.
