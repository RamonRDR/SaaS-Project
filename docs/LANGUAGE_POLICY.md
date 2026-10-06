# Política de Linguagem

## Objetivo

Manter o código alinhado às convenções internacionais de desenvolvimento e, ao mesmo tempo, tornar a documentação natural para a equipe e o mercado inicial brasileiro.

## Regra principal

**Código em inglês. Documentação e explicações em português do Brasil.**

## Deve ficar em inglês

- nomes de funções;
- nomes de métodos;
- nomes de classes;
- nomes de variáveis;
- nomes de módulos e packages;
- nomes de eventos;
- identificadores de banco e entidades técnicas, salvo decisão específica de modelagem;
- nomes de endpoints e contratos internos quando tratados como identificadores técnicos;
- nomes de diretórios e arquivos estruturais do repositório;
- nomes das skills e dos agentes em arquivos técnicos.

Exemplo:

```python
def get_available_slots(
    professional_id: UUID,
    service_id: UUID,
    target_date: date,
    tenant_id: UUID,
) -> list[AvailableSlot]:
    """
    Retorna os horários disponíveis para um profissional e serviço.

    Considera duração do serviço, buffer entre atendimentos,
    compromissos existentes e isolamento do estabelecimento.

    O tenant_id é obrigatório para impedir acesso cruzado entre tenants.
    """
```

## Deve ficar em português do Brasil

- README;
- SDDs;
- ADRs;
- documentação de arquitetura;
- documentação de segurança;
- documentação de observabilidade;
- roadmap;
- PROJECT_STATUS;
- conteúdo dos arquivos de agentes e skills;
- critérios de aceite;
- evidências de teste;
- comentários;
- docstrings;
- mensagens explicativas voltadas à manutenção do projeto.

## Comentários

Comentários devem explicar **por que** algo existe, especialmente quando houver:

- regra de negócio não óbvia;
- proteção contra condição de corrida;
- decisão de segurança;
- workaround;
- limitação externa;
- decisão arquitetural relevante.

Bom exemplo:

```python
# Revalidamos a disponibilidade dentro da transação porque dois clientes
# podem tentar reservar o mesmo horário quase simultaneamente.
```

Evitar:

```python
# Percorre os horários
for slot in slots:
    ...
```

## Termos técnicos

Termos consolidados podem permanecer em inglês quando a tradução piorar a clareza, por exemplo:

- tenant
- endpoint
- middleware
- rollback
- health check
- staging
- CI/CD
- pull request
- commit
- merge
- deploy
- tracing
- logging

## Interface do produto

O produto será inicialmente voltado ao mercado brasileiro. A interface inicial será pt-BR, sem impedir internacionalização futura.

## Evolução

Se o produto passar a operar internacionalmente ou a equipe ganhar integrantes que não falem português, esta política poderá ser revisada por ADR.
