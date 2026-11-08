# Testes automatizados do Perene

## Como rodar

Na pasta do `manage.py`, com o venv ativado e o `.env` configurado (`ENVIRONMENT=development`):

```bash
# testes rápidos (unidade + integração): ~2 segundos, não abrem navegador
python manage.py test --exclude-tag=selenium

# só um app, uma classe ou um teste
python manage.py test estoque
python manage.py test perene.tests.CadastroGestorFormTests
python manage.py test estoque.tests.SituacaoLoteValoresLimiteTests.test_vence_hoje_fica_atencao_e_nao_critico

# testes de sistema (abrem o Chrome; precisam de internet na 1ª vez para baixar o driver)
python manage.py test --tag=selenium
SELENIUM_HEADLESS=1 python manage.py test --tag=selenium     # sem abrir a janela (Mac/Linux)
$env:SELENIUM_HEADLESS=1; python manage.py test --tag=selenium   # PowerShell
```

## Cobertura

```bash
pip install coverage
coverage run --source=perene,estoque,funcionarios manage.py test --exclude-tag=selenium
coverage report -m --omit="*/migrations/*,*/tests*.py,*/fabricas.py,*/selenium_base.py"
```

## Como está organizado (pirâmide de testes)

| Tipo | Onde | O que verifica |
|---|---|---|
| Unidade | `tests.py` de cada app | Regras dos modelos, formulários, permissões e utilitários, isoladas das telas |
| Integração | `tests.py` de cada app | Views com banco de dados: login, cadastro, estoque, equipe, isolamento entre mercados |
| Sistema (E2E) | `tests_selenium.py` | Fluxos completos num navegador real |

Arquivos de apoio:

- `perene/fabricas.py`: funções para criar mercado, gestor, funcionário, produto, lote... (evita repetição nos testes) e a classe `BaseTeste`, que usa um hash de senha rápido.
- `perene/selenium_base.py`: o `BaseTestCase` do modelo da disciplina, com métodos de apoio (`abrir`, `preencher`, `clicar`, `entrar_como_gestor`...).

## Boas práticas aplicadas (FIRST)

- **Rápidos**: hash de senha leve e banco de teste em memória.
- **Independentes**: cada teste cria os próprios dados, sem depender de ordem.
- **Determinísticos**: a data é congelada com `mock` nos testes de limite de validade.
- **Auto-verificáveis**: cada teste termina em `assert`.
- Testes **lineares** (sem `if`/`for`) e com um único assunto cada, com nome que descreve o comportamento.

## Como adicionar um teste novo

1. Escolha o tipo: regra isolada (unidade), tela com banco (integração) ou fluxo completo (sistema).
2. Crie os dados com as funções de `perene/fabricas.py`.
3. Dê um nome que diga o comportamento esperado: `test_funcionario_nao_abre_a_equipe`.
4. Rode só aquele teste, veja falhar de propósito (quebrando o código) e depois passar.
