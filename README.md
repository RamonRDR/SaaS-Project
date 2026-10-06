# SaaS Project

> Engineering foundation for a multi-tenant SaaS platform, built with spec-driven development, architecture governance, automated quality gates, and AI-assisted engineering.

## Overview

This repository contains the engineering foundation of a multi-tenant SaaS for service businesses.

The project is intentionally being built from the foundation up, with emphasis on:

- **Spec-Driven Development (SDD)**
- **Architecture Decision Records (ADR)**
- **AI-assisted software engineering**
- **deterministic CI/CD and quality gates**
- **security and tenant isolation by design**
- **observable, testable and reviewable delivery workflows**

Planned application stack:

- **Django / Django REST Framework**
- **Flutter**
- **PostgreSQL**
- **Docker**
- **n8n**
- **GitHub Actions**

## Engineering focus

This repository also works as a practical engineering portfolio. It demonstrates how I structure software delivery around explicit specifications, architecture decisions, automated review loops, security gates, and human approval only where a real product or risk decision is required.

The current milestone is the redesign of the unattended orchestration runtime to run **100% in the cloud**, with **zero local runtime dependency**.

## Current phase

**Phase 0 — Engineering Foundation**

Completed foundation areas include:

- repository and language conventions;
- specialist AI agent contracts;
- reusable engineering skills;
- SDD and ADR governance;
- baseline architecture decisions;
- Definition of Done and CI governance;
- interactive Mode A orchestration.

The next milestone is a production-ready unattended Mode A runtime based on cloud-native GitHub automation.

## Repository structure

```text
.ai/              AI agent, skill and runtime contracts
.github/          CI workflows, governance gates and scripts
backend/          Django backend
frontend/         Flutter frontend
automations/      n8n and automation assets
infrastructure/   infrastructure and deployment assets
docs/             architecture, SDD, ADR and engineering documentation
tests/            cross-cutting test assets
```

## Language policy

The project uses a hybrid language policy:

- source-code identifiers: **English**
- technical documentation: **Brazilian Portuguese**
- code comments and docstrings: **Brazilian Portuguese**
- established technical terms may remain in English

See `docs/LANGUAGE_POLICY.md`.

## Public repository note

This repository starts from a **sanitized engineering snapshot**. Private operational history, discarded experiments, and superseded repository metadata are intentionally not part of this public Git history.

## Português

Este repositório contém a fundação de engenharia de uma plataforma SaaS multi-tenant para negócios de serviços.

O projeto é desenvolvido com SDD, ADRs, agentes de IA especializados, gates automatizados de qualidade e segurança, CI/CD e uma arquitetura orientada a decisões auditáveis. A fase atual concentra-se no redesenho do runtime unattended para uma solução 100% em nuvem, sem dependência de execução local.

---

**Maintainer:** Ramon Rodriguez  
**GitHub:** [@RamonRDR](https://github.com/RamonRDR)
