# Skill `review-observability`

## Missão

Verificar se uma alteração pode ser operada, diagnosticada e investigada com sinais suficientes sem expor dados indevidos.

## Quando usar

Usar em features ou mudanças que introduzam comportamento operacional relevante, integrações, jobs, APIs, falhas externas ou novos caminhos críticos.

## Agentes autorizados

- Platform & Observability.

Security & Tenant Isolation participa quando houver risco de logging sensível.

## Entradas obrigatórias

- SDD;
- fluxo técnico;
- erros esperados;
- dependências externas;
- requisitos de negócio relevantes;
- implementação candidata quando existir.

## Procedimento

1. identificar eventos relevantes;
2. verificar logging estruturado;
3. verificar correlation/request ID;
4. revisar níveis de log;
5. revisar ausência de dados sensíveis;
6. verificar tratamento e captura de exceções;
7. verificar health checks quando aplicável;
8. avaliar necessidade de métricas;
9. avaliar necessidade de tracing;
10. verificar sinais para falhas de integração;
11. verificar sinais para jobs e processamento assíncrono;
12. registrar lacunas operacionais.

## Outputs esperados

- parecer de observabilidade;
- eventos/logs necessários;
- necessidade de health checks, métricas ou tracing;
- riscos de logging sensível;
- pendências operacionais.

## Não faz

- não adiciona dado sensível aos logs para facilitar debug;
- não introduz fornecedor externo sem gate aplicável;
- não substitui revisão de segurança.

## Condições de parada

Parar quando:

- uma falha crítica não puder ser diagnosticada;
- logging exigir exposição indevida;
- novo provedor pago, regulado ou sensível for necessário sem aprovação.

## Gates humanos

Novo provedor externo pago, regulado ou sensível exige aprovação humana.

## Critério de conclusão

A skill termina quando o comportamento relevante possui sinais operacionais suficientes e seguros.
