# Skill `review-security`

## Missão

Executar uma revisão de segurança orientada ao risco sobre uma alteração antes do merge ou release.

## Quando usar

Usar quando houver impacto em autenticação, autorização, tenant isolation, dados sensíveis, APIs públicas, uploads, integrações externas, secrets, logging ou superfícies de abuso.

## Agentes autorizados

- Security & Tenant Isolation.

## Entradas obrigatórias

- SDD;
- diff ou desenho técnico;
- contratos afetados;
- fluxo de dados;
- controles de autenticação e autorização;
- estratégia de tenant isolation aplicável;
- integrações externas;
- requisitos de logging.

## Procedimento

1. identificar ativos e dados envolvidos;
2. revisar autenticação;
3. revisar autorização;
4. revisar tenant isolation;
5. revisar exposição de dados;
6. revisar validação de entrada;
7. revisar tratamento de secrets;
8. revisar logging sensível;
9. revisar uploads e conteúdo externo quando aplicável;
10. revisar abuso, enumeração e escalada de privilégio;
11. revisar dependências e provedores;
12. identificar mudanças de arquitetura de autenticação ou autorização;
13. identificar mudanças de estratégia de tenant isolation;
14. identificar nova categoria de dado sensível;
15. identificar provedor externo pago, regulado ou sensível;
16. registrar achados por impacto;
17. definir mitigação, testes e gates necessários.

## Outputs esperados

- parecer de segurança;
- achados classificados;
- mitigações requeridas;
- testes de segurança;
- gates humanos identificados;
- bloqueios explícitos.

## Não faz

- não aceita risco relevante em nome do humano;
- não transforma ausência de evidência em aprovação;
- não substitui `review-multitenancy` quando houver impacto de tenant;
- não autoriza mudança de autenticação, autorização ou tenant isolation.

## Condições de parada

Parar e devolver ao Orquestrador quando:

- houver risco crítico ou alto sem mitigação;
- houver secret exposto;
- existir bypass de autorização;
- o fluxo de dados sensíveis estiver indefinido;
- a arquitetura de autenticação ou autorização mudar e a aprovação humana obrigatória ainda estiver pendente;
- a estratégia de tenant isolation mudar e a aprovação humana obrigatória ainda estiver pendente;
- for introduzido provedor externo pago, regulado ou sensível sem aprovação;
- for criada nova categoria de dado sensível e a aprovação humana obrigatória ainda estiver pendente.

## Gates humanos

Exigem aprovação humana explícita:

- aceitação de risco relevante;
- mudança de arquitetura de autenticação ou autorização;
- mudança de estratégia de tenant isolation;
- introdução de provedor externo pago, regulado ou sensível;
- armazenamento de nova categoria de dado sensível;
- exceção temporária a controle de segurança.

## Critério de conclusão

A skill termina quando os riscos aplicáveis foram avaliados, todos os gates humanos necessários foram satisfeitos e registrados, e não há bloqueio de segurança sem tratamento.

Uma mudança de autenticação, autorização ou tenant isolation já aprovada pode prosseguir na revisão; a existência da mudança, por si só, não mantém a skill permanentemente bloqueada.
