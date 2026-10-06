# Sistema de Agentes

Este diretório contém os contratos dos papéis usados no desenvolvimento assistido por IA.

## Princípio central

**Agente é um papel. Skill é uma capacidade.**

O projeto evita criar um agente diferente para cada tarefa pequena. O objetivo é manter poucos papéis estáveis, com responsabilidades claras, apoiados por skills reutilizáveis.

## Agent System V1

| Papel | Arquivo | Responsabilidade principal |
| --- | --- | --- |
| Orchestrator / Tech Lead | `orchestrator.md` | Coordenar fluxo, dependências, gates e handoffs |
| Product & SDD | `product-sdd.md` | Transformar intenção em especificação aprovada |
| Backend | `backend.md` | Domínio, APIs, persistência e backend |
| Frontend | `frontend.md` | Flutter, experiência, responsividade e consumo de API |
| QA & Quality | `qa-quality.md` | Testes, critérios de aceite e evidências |
| Security & Tenant Isolation | `security-tenant-isolation.md` | Segurança, permissões e isolamento entre tenants |
| Platform & Observability | `platform-observability.md` | Ambientes, CI/CD, deploy e observabilidade |
| Docs & Release | `docs-release.md` | Documentação, status e encerramento da entrega |

## Regras de convivência

- o Orquestrador é o ponto de entrada;
- após o início de um PR review loop, o Orquestrador mantém posse operacional do fluxo até `READY_FOR_HUMAN_MERGE` ou até surgir um gate humano/bloqueio terminal;
- cada especialista trabalha apenas dentro do handoff recebido;
- um agente não deve tomar silenciosamente uma decisão pertencente a outro papel;
- mudanças de contrato voltam ao Orquestrador;
- especialistas podem apontar necessidade de outro agente, mas não expandem o próprio escopo por conta própria;
- gates de aprovação humana permanecem humanos;
- SDD, ADR, testes, segurança, observabilidade e documentação fazem parte do processo de engenharia.

## Padrão mínimo de contrato de agente

Cada agente especialista deve declarar:

- missão;
- responsabilidades;
- o que pode fazer;
- o que não pode fazer;
- entradas obrigatórias;
- documentos obrigatórios a ler;
- skills permitidas;
- outputs esperados;
- regras de handoff;
- condições de parada;
- gates de aprovação humana;
- Definition of Done específica.

## Política de linguagem

Os nomes técnicos dos arquivos e identificadores permanecem em inglês.

O conteúdo documental dos contratos de agentes é escrito em português do Brasil, conforme `docs/LANGUAGE_POLICY.md`.
