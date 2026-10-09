# Gate de segurança para teste real de CAS entre runners

**Status:** `BLOCKED_EXTERNAL` até existir um repositório descartável separado para o teste com `contents: write`. A branch experimental no projeto principal deve continuar somente com `contents: read`.

## Auditoria no GitHub

- SaaS principal: `RamonRDR/SaaS-Project`, repositório público.
- `main`: `protected=false` na API GitHub no momento da auditoria.
- `experiment/claim-budget-lab`: `protected=false`.
- Rulesets listados pela API: `[]`.
- Endpoint de detalhes de branch protection: a integração retornou `403 Resource not accessible by integration`; não presumir proteções adicionais.
- Workflow atual usa `permissions: contents: read` e já demonstrou 32/32 testes em 2 runners e um coordenador somente leitura, **sem** comprovar writes concorrentes em Git ref.

A permissão `GITHUB_TOKEN` `contents: write` se aplica ao **repositório**, não a um prefixo de branch ou caminho específico. `persist-credentials: false` e guardas no script ajudam, mas **não diminuem o alcance do token**. Colocar token de escrita em workflow executado de branch experimental e `main` sem proteção aumenta desnecessariamente o blast radius.

Fontes oficiais:
- https://docs.github.com/en/actions/concepts/security/github_token
- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

## DE → PARA

| | DE | PARA recomendado |
| --- | --- | --- |
| Permissões | Apenas `contents: read` em `RamonRDR/SaaS-Project` | `contents: write` **somente** em laboratório dedicado, sem secrets de produção |
| Workers | Jobs independentes com artefatos, single-writer simulado | Dois runners escrevendo proposals irmãos na **mesma ref remota** descartável |
| Evidência | Ledger simulado e Git ref testado pela conexão interativa | HTTP nativo de GitHub registrado por worker, SHA, parent, estado remoto após erro/timeout |
| Falhas | `UNKNOWN_AFTER_PERSIST` simulada | Injeção controlada de timeout de resposta, seguida de readback do servidor |
| Reconciliação | Coordenador read-only | Worker vencedor, losers rejeitados; reconciliação por CAS/leitura de nova versão e teto |
| Cleanup | Artefatos expiram em 2 dias | Deletar somente ref `refs/heads/experiment/cas-probe-<run-id>`, verificar 404 e guardar trace |

## Plano do teste privilegiado futuro

1. Criar **repositório público descartável separado**, sugerido `RamonRDR/SaaS-CAS-Lab`. Não conectar segredos de IA/produção, não copiar tokens ou credenciais da aplicação. A ferramenta GitHub disponível nesta conversa **não suporta criar repositórios**, logo requer criação pelo responsável humano na interface GitHub.
2. Copiar apenas o laboratório versionado para o repositório de teste. Não executar workflows de PRs/forks e não receber conteúdo não confiável. Usar gatilho exclusivamente `push` da branch confiável.
3. Provisionar `GITHUB_TOKEN` `contents: write` somente nos jobs `bootstrap`, `worker-alpha`, `worker-beta` e `cleanup` daquele repositório separado. Verificador de resultados permanece `contents: read`. Não usar PAT.
4. Bootstrap cria uma ref efêmera de run-id único sob prefixo `experiment/cas-probe-` apontando para um commit inicial canônico de ledger, sem tocar `main`.
5. Dois runners independentes leem a **mesma revisão inicial** e constroem commits irmãos divergentes, cada um tentando `PATCH /git/refs/heads/experiment/cas-probe-<run-id>` com `force:false`. Não assumir que `force:false` sozinho implementa compare-and-swap por `expected_sha`.
6. Registrar HTTP status real, eventual timeout e SHA de cada commit. Depois de qualquer erro ambíguo, o verificador relê HEAD e objeto do ledger: nunca repetir a mutação sem reconciliação da identidade da operação.
7. Para orçamento, reservar quatro unidades entre seis operações concorrentes. Atualizações derrotadas devem reler o ledger, recalcular o limite e só produzir nova proposta caso continue elegível. Verificar que não existem reservas duplicadas.
8. Testar separadamente um **descendente fast-forward com snapshot obsoleto**. Esta é uma prova crítica: se o GitHub aceitar o descendente apenas por ser fast-forward, teremos demonstrado que `PATCH force:false` não oferece comparação explícita de versão e devemos escolher outro protocolo/caminho atômico.
9. `cleanup` roda `if: always()` e apaga exclusivamente a ref efêmera do próprio run. O resultado do cleanup deve ser verificado; falha deixa gate vermelho e pede intervenção.
10. Guardar artefatos de ambos runners, reconciliação, erros e SHA final, inclusive casos negativos. Se houver discrepância, parar com `HUMAN_DECISION_REQUIRED`; nunca declarar CAS comprovado só porque um teste terminou verde.

## Descoberta adicional já confirmada

GitHub normalmente **não cria novos workflows de `push` quando o push foi feito usando o `GITHUB_TOKEN` da execução**, exceto certos eventos específicos (por exemplo, `workflow_dispatch` e `repository_dispatch`). Isso reduz loops acidentais **mas não substitui** isolar os gatilhos. As atualizações anteriores via **conector externo** dispararam execuções na branch experimental, uma origem diferente de token.

Fonte: https://docs.github.com/en/actions/concepts/security/github_token

## Próximas decisões

**Gate humano pendente:** criação do repositório descartável separado, ou instalação de políticas equivalentes de proteção no SaaS principal com avaliação explícita da abrangência do token. Preferir o primeiro.

`test_privilege_gate.py` valida o contrato proposto em modo simulado, sem conceder escrita. Seu resultado verde não afirma teste real de concorrência de ref remota.

Nenhuma alteração em `main`, PR #2, SDD v1.2, ADR-0014 ou PHASE-0-G é autorizada por este gate.
