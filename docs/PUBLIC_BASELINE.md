# Baseline pública do projeto

## Objetivo

Este repositório público foi iniciado em 2026-10-06 a partir de um **snapshot sanitizado** da fundação de engenharia do projeto.

O histórico operacional anterior permanece privado e não foi importado para este Git público.

## O que foi preservado

Foram preservados os artefatos técnicos vigentes anteriores aos experimentos de runtime unattended descartados:

- contratos de agentes e skills;
- Mode A interativo;
- templates e lifecycle de SDD/ADR;
- ADR-0001 a ADR-0010;
- arquitetura baseline;
- Definition of Done;
- gates de CI;
- scripts e testes de governança.

## O que não foi importado

Por decisão deliberada de sanitização e clareza pública, não foram importados:

- commits históricos privados;
- pull requests e comentários privados anteriores;
- logs antigos do GitHub Actions;
- referências de sessões de ferramentas;
- metadados pessoais de commits antigos;
- experimentos descartados de runtime unattended;
- evidências operacionais antigas que dependiam dos PRs privados.

## Integridade das decisões

Os ADRs 0001–0010 foram migrados mantendo **inalterado o conteúdo decisório** de suas revisões aceitas.

Somente metadados de auditoria que apontavam para PRs privados foram substituídos por uma declaração explícita de que a evidência operacional original permanece no histórico privado anterior.

## Histórico público

A partir deste snapshot, novas SDDs, ADRs, issues, PRs, reviews, CI e decisões relevantes são registradas diretamente neste repositório público.

## Segurança

A publicação do repositório não autoriza a exposição de:

- secrets ou credenciais;
- dados pessoais ou de clientes;
- URLs de sessões privadas;
- logs sensíveis;
- artefatos locais.

Consulte `SECURITY.md`.
