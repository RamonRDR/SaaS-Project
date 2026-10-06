# SDD-XXXX - Título da entrega

> Copie este arquivo para criar uma nova Software Design Document. Substitua os placeholders e preserve todas as seções obrigatórias.
>
> Se uma seção não se aplicar, registre **Não aplicável** e a justificativa. Não remova silenciosamente a seção.

## Metadados

- **ID:** SDD-XXXX
- **Título:** <título curto e específico>
- **Status:** Draft
- **Versão:** 0.1
- **Responsável pela especificação:** Product & SDD
- **Responsável humano pela aprovação:** <nome ou papel>
- **Data de criação:** YYYY-MM-DD
- **Última atualização:** YYYY-MM-DD
- **Entrega / issue / PR relacionada:** <referência ou Não aplicável>
- **ADRs relacionados:** <ADR-XXXX ou Não aplicável>
- **SDDs relacionadas:** <SDD-XXXX ou Não aplicável>

### Estados permitidos

- `Draft`: em elaboração;
- `In Review`: pronta para revisão, ainda não aprovada;
- `Approved`: revisão concluída e aprovação humana explicitamente registrada;
- `Superseded`: substituída por outra SDD identificada e já `Approved`.

Uma SDD não pode assumir `Approved` por decisão de um agente de IA.

### Versão da especificação e validade da aprovação

As seções **1 a 24** compõem o conteúdo material da especificação.

Antes de `Approved`:

- qualquer alteração material nas seções 1 a 24 incrementa `Versão`;
- essa alteração invalida automaticamente qualquer parecer de `review-sdd` anterior;
- o status permanece ou retorna para `Draft`;
- a SDD precisa passar novamente por `review-sdd`;
- qualquer aprovação humana anterior deixa de ser válida para a nova versão.

Depois de `Approved`, qualquer mudança material nas seções 1 a 24 também incrementa `Versão`, retorna o status para `Draft`, invalida o parecer e a aprovação anteriores e exige nova revisão e novo gate humano.

As seções 25 e 26 registram histórico, revisão e aprovação. Atualizações puramente de auditoria nessas seções não incrementam a versão se não alterarem o conteúdo material da especificação.

Quando a mudança representar uma nova entrega ou substituir substancialmente a intenção da SDD anterior, o Orquestrador pode exigir uma nova SDD sucessora em vez de nova versão.

## 1. Contexto

Descreva o cenário atual e as informações necessárias para compreender a entrega.

## 2. Problema

Defina o problema que precisa ser resolvido. Evite descrever a solução como se fosse o problema.

## 3. Objetivo

Declare o resultado esperado de forma verificável.

## 4. Escopo

- <item>

## 5. Fora de escopo

- <item>

## 6. Atores e jornadas afetadas

| Ator | Jornada / interação | Impacto |
| --- | --- | --- |
| <ator> | <jornada> | <impacto> |

## 7. Regras de negócio

- **BR-001:** <regra>
- **BR-002:** <regra>

Não registre hipótese como regra confirmada.

## 8. Permissões e multi-tenancy

Documente:

- quem pode executar cada operação;
- como o tenant é determinado;
- quais dados pertencem ao tenant;
- relações cross-tenant proibidas;
- restrições por profissional, quando aplicável;
- testes negativos cross-tenant necessários.

## 9. Impacto no modelo de dados

Documente entidades, campos, relacionamentos, índices, constraints e dados derivados afetados.

## 10. Impacto no contrato da API

Documente endpoints, comandos, eventos, payloads, erros, compatibilidade e risco de breaking change.

## 11. Comportamento esperado no Flutter

Documente telas, estados, responsividade, acessibilidade, loading, empty, success, error e regras que permanecem obrigatoriamente no backend.

## 12. Integrações externas

Documente integrações e provedores afetados.

Fornecedor novo pago, regulado ou sensível exige gate humano.

## 13. Segurança e privacidade

Documente autenticação, autorização, dados sensíveis, validação de entrada, secrets, exposição de dados, riscos de abuso e privacidade.

Mudanças de autenticação, autorização ou estratégia de tenant isolation exigem gate humano e, quando arquiteturais, ADR.

## 14. Observabilidade

Defina logs estruturados, correlation/request ID, eventos, captura de exceções, health checks, métricas, tracing e restrições de dados sensíveis em logs.

## 15. Casos de borda e comportamentos de erro

| ID | Cenário | Comportamento esperado |
| --- | --- | --- |
| EDGE-001 | <cenário> | <resultado> |

## 16. Migration

- **Migration necessária:** Sim / Não
- **Destrutiva:** Sim / Não
- **Descrição:** <detalhes ou Não aplicável>
- **Gate humano necessário:** <sim/não e motivo>

Migration destrutiva exige aprovação humana explícita.

## 17. Estratégia de rollback

Descreva como reverter a alteração. Se não for aplicável ou possível, explique por quê e registre o risco.

## 18. Testes obrigatórios

### Unitários
- <teste>

### Integração
- <teste>

### E2E
- <teste>

### Segurança / autorização / multi-tenancy
- <teste>

### Regressão
- <teste>

## 19. Critérios de aceite

- **AC-001:** <critério verificável>
- **AC-002:** <critério verificável>

Evite critérios subjetivos como “funciona corretamente”.

## 20. Evidências de validação esperadas

- resultados de testes;
- screenshots, quando aplicável;
- respostas de API, quando aplicável;
- evidência de QA;
- parecer de Security;
- parecer de Platform/Observability.

## 21. Dependências

- <dependência>

## 22. Riscos conhecidos

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| <risco> | <impacto> | <mitigação> |

## 23. Dúvidas abertas

Toda dúvida capaz de alterar materialmente comportamento, segurança, arquitetura ou escopo bloqueia a aprovação até resolução.

- <dúvida ou Nenhuma>

## 24. ADRs necessários ou relacionados

- **ADR necessário:** Sim / Não
- **Referências:** <ADR-XXXX ou Não aplicável>
- **Motivo:** <justificativa>

## 25. Histórico de revisão

| Versão | Data | Autor | Alteração |
| --- | --- | --- | --- |
| 0.1 | YYYY-MM-DD | <responsável> | Criação inicial |

## 26. Aprovação

### Revisão

- **Parecer de `review-sdd`:** <Pronta para aprovação / Necessita ajustes / Bloqueada>
- **Versão revisada:** <versão>
- **Pendências bloqueantes:** <Nenhuma / lista>
- **Pendências não bloqueantes:** <Nenhuma / lista>

Somente o parecer `Pronta para aprovação`, com **Nenhuma** pendência bloqueante e `Versão revisada` igual à `Versão` atual, libera o gate humano.

### Gate humano

- **Aprovada:** Sim / Não
- **Versão aprovada:** <versão ou Não aplicável>
- **Responsável humano:** <nome ou papel>
- **Data:** YYYY-MM-DD ou Não aplicável
- **Registro da aprovação:** <referência>

O status só pode ser alterado para `Approved` quando **todas** as condições abaixo forem verdadeiras:

1. o `review-sdd` emitiu `Pronta para aprovação`;
2. não existe pendência bloqueante;
3. `Versão revisada` é exatamente igual à `Versão` atual;
4. `Versão aprovada` é exatamente igual à versão favoravelmente revisada;
5. a aprovação humana foi explicitamente registrada.

Se qualquer condição falhar, a SDD permanece fora de `Approved`.

Se esta SDD substituir outra, a SDD anterior só pode mudar para `Superseded` depois que esta SDD sucessora estiver `Approved`.
