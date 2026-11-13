# Como contribuir com o Perene

## Boas-vindas

Obrigado por querer ajudar o **Perene**, um sistema web de soluções ESG para pequenas e médias empresas do varejo alimentar. Ele ajuda o mercado a enxergar o estoque, perceber o que está perto de vencer e organizar a equipe, para reduzir o desperdício.

Este guia mostra como configurar o projeto, onde mexer, como enviar suas mudanças e como pedir ajuda. Você não precisa ser expert: correções de texto, testes e melhorias pequenas também são muito bem-vindas.

## Índice

- [Antes de começar](#antes-de-começar)
- [Como configurar o ambiente](#como-configurar-o-ambiente)
- [Como o projeto é organizado](#como-o-projeto-é-organizado)
- [Como enviar uma mudança](#como-enviar-uma-mudança)
- [Como reportar um bug](#como-reportar-um-bug)
- [Como corrigir um bug](#como-corrigir-um-bug)
- [Como sugerir uma melhoria](#como-sugerir-uma-melhoria)
- [Testes](#testes)
- [Convenções de código e de commits](#convenções-de-código-e-de-commits)
- [Segurança](#segurança)
- [Código de conduta](#código-de-conduta)
- [Reconhecimento](#reconhecimento)
- [Quem mantém o projeto](#quem-mantém-o-projeto)
- [Onde pedir ajuda](#onde-pedir-ajuda)

## Antes de começar

Links úteis:

| O quê | Onde |
|---|---|
| Código-fonte | <https://github.com/hellosofi/perene> |
| Site publicado | <https://perene.onrender.com> |
| Backlog e sprints (Jira) | <https://grupo-perene.atlassian.net> |
| Descrição do projeto e instalação | [README.md](https://github.com/hellosofi/perene#fundamentos-de-desenvolvimento-de-software) |
| Documento de análise (Entrega 01) | [documento-analise.md](entregas/entrega-01/documento-analise.md) |
| Histórias de usuário (Entrega 03) | [historias.md](entregas/entrega-03/historias.md) |
| Guia dos testes | [TESTES.md](TESTES.md) |

Se você quer pegar uma tarefa, olhe o backlog no Jira ou as [issues abertas](https://github.com/hellosofi/perene/issues) e avise o grupo antes de começar, para duas pessoas não fazerem a mesma coisa.

## Como configurar o ambiente

O passo a passo completo está no [README](https://github.com/hellosofi/perene#fundamentos-de-desenvolvimento-de-software). Em resumo, na pasta do projeto (onde fica o `manage.py`):

```bash
git clone https://github.com/hellosofi/perene.git
cd perene

# Windows (PowerShell)
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Mac / Linux
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Crie um arquivo `.env` na mesma pasta do `manage.py`:

```env
SECRET_KEY=cole-uma-chave-gerada-aqui
ENVIRONMENT=development
GESTOR_CODIGO_CONVITE=escolha-um-codigo-aqui
```

- `ENVIRONMENT=development` faz o projeto usar o banco SQLite local, sem precisar de banco online.
- `GESTOR_CODIGO_CONVITE` é o código exigido para cadastrar um gestor pela página. Sem ele, o cadastro de gestor fica desativado.
- O comando para gerar uma `SECRET_KEY` está no README.

Depois:

```bash
python manage.py migrate
python manage.py check
python manage.py runserver
```

Abra <http://127.0.0.1:8000/>. Para testar um **funcionário**, cadastre um gestor primeiro (ele cria o mercado) e use o código de convite do mercado, que aparece na tela Equipe.

## Como o projeto é organizado

```
perene/
├── projeto/          configurações do Django (settings.py, urls.py)
├── perene/           login, cadastro, mercados, perfis, notificações, página inicial
├── estoque/          produtos, lotes e a tela de inventário
├── funcionarios/     tela de equipe e tarefas (só para gestores)
├── entregas/         documentos e imagens das entregas da disciplina
├── design/           materiais de design
├── requirements.txt  dependências
├── build.sh          comandos do deploy no Render
└── TESTES.md         guia dos testes
```

Cada app tem seus próprios `models.py`, `views.py`, `urls.py`, `templates/` e `static/`. Os testes ficam em `tests.py` e `tests_selenium.py` dentro de cada app.

## Como enviar uma mudança

1. **Atualize a `main`** e crie uma branch a partir dela. Use um nome curto que diga o que você vai fazer, por exemplo `feature/filtro-por-lote` ou `fix/mensagem-de-erro-do-login` (ou a sua branch pessoal, como o grupo já faz).
   ```bash
   git switch main
   git pull
   git switch -c fix/mensagem-de-erro-do-login
   ```
2. **Faça a mudança** e rode os testes (veja [Testes](#testes)).
3. **Faça commits pequenos e claros** (veja [Convenções](#convenções-de-código-e-de-commits)).
4. **Envie a branch** e abra um **Pull Request** para a `main`:
   ```bash
   git push -u origin fix/mensagem-de-erro-do-login
   ```
5. **Descreva o Pull Request**: o que mudou, por que mudou e, se mexeu em tela, anexe um print.
6. **Peça revisão** de pelo menos uma pessoa do grupo. Ninguém junta o próprio Pull Request sem revisão.

Checklist antes de abrir o Pull Request:

- [ ] `python manage.py check` sem erros
- [ ] `python manage.py makemigrations --check` sem mudanças pendentes (se você mexeu em `models.py`, inclua a migration no commit)
- [ ] `python manage.py test --exclude-tag=selenium` passando
- [ ] Testes novos para o que você criou ou corrigiu
- [ ] Nenhum arquivo secreto no commit (veja [Segurança](#segurança))

Costumamos responder aos Pull Requests em até **3 dias úteis**. Se passar disso, pode cobrar no grupo.

## Como reportar um bug

Antes de abrir, procure nas [issues](https://github.com/hellosofi/perene/issues) e no bug tracker do Jira se alguém já reportou. Se não, abra uma nova issue com este modelo:

```markdown
**O que aconteceu**
Descreva o problema em uma ou duas frases.

**Como reproduzir**
1. Entre como (gestor / funcionário)
2. Vá para ...
3. Clique em ...
4. Veja o erro

**O que era esperado**
O que deveria ter acontecido.

**Prints ou mensagem de erro**
Cole aqui (se for erro do Django, copie o final do terminal).

**Ambiente**
- Local ou site publicado (https://perene.onrender.com)
- Navegador e sistema operacional
```

Quanto mais passos claros, mais rápido alguém consegue consertar.

## Como corrigir um bug

1. Comente na issue que você vai assumir (para evitar trabalho repetido).
2. Escreva **primeiro um teste que falha** reproduzindo o bug. Isso garante que ele não volta.
3. Corrija o código até o teste passar.
4. Siga o fluxo de [Como enviar uma mudança](#como-enviar-uma-mudança) e cite a issue no Pull Request (por exemplo, `Corrige #12`).

Correções pequenas e focadas são melhores que mudanças grandes misturando vários assuntos.

## Como sugerir uma melhoria

Abra uma issue com o modelo abaixo. Se a ideia nasceu de uma história de usuário, cite qual (veja [historias.md](https://github.com/hellosofi/perene/blob/main/entregas/entrega-03/historias.md).

```markdown
**Qual problema isso resolve**
Quem sente essa dor e em que momento do dia a dia do mercado.

**Como imagina a solução**
Descreva, com um rascunho de tela se puder.

**Alternativas pensadas**
O que mais poderia resolver.

**Para quem**
Gestor, funcionário ou os dois.
```

Antes, confira se a ideia já está no backlog do Jira. Sugestões grandes são conversadas no grupo antes de virarem tarefa.

## Testes

Os testes ficam dentro de cada app:

| Local | O que tem |
|---|---|
| `perene/tests.py` | Login, cadastro, mercados, perfis, permissões e notificações |
| `estoque/tests.py` | Regras de lote e validade, formulários e telas do estoque |
| `funcionarios/tests.py` | Tela de equipe e tarefas |
| `*/tests_selenium.py` | Testes de sistema, que abrem o navegador |
| `perene/fabricas.py` | Funções para criar dados de teste (mercado, gestor, produto, lote...) |

Para rodar tudo, menos os que abrem o navegador:

```bash
python manage.py test --exclude-tag=selenium
```

Mais comandos (rodar um app, uma classe, cobertura e Selenium) estão no [TESTES.md](TESTES.md).

Regras para escrever testes:

- Um assunto por teste, com nome que diz o comportamento: `test_funcionario_nao_abre_a_equipe`.
- Sem `if` nem `for` dentro do teste.
- Crie os dados com as funções de `perene/fabricas.py` e não dependa de dados de outros testes.
- Para datas, congele o dia com `mock` (veja `SituacaoLoteValoresLimiteTests`) em vez de depender da data de hoje.

## Convenções de código e de commits

**Código**

- Python seguindo a [PEP 8](https://peps.python.org/pep-0008/): 4 espaços, linhas curtas, sem imports sobrando.
- Nomes em português, como no resto do projeto: funções e variáveis em `snake_case` (`lista_produtos`), classes em `CamelCase` (`CadastroGestorForm`).
- Regras de validação ficam em `forms.py`, regras de negócio nos `models.py` e as `views.py` só orquestram.
- Telas do estoque ficam em `estoque/templates/estoque/` e o CSS em `static/css/`, reaproveitando as classes já existentes antes de criar novas.
- Textos para o usuário em português do Brasil.

**Regras importantes deste projeto**

- **Cada mercado só vê os próprios dados.** Toda consulta a produtos, lotes, equipe, tarefas ou notificações precisa filtrar pelo mercado do usuário (`mercado_do_usuario(request.user)`). Nunca busque um objeto só pelo `id`.
- **Proteja as telas.** Use `@login_required` em toda tela interna e `@gestor_required` nas que são só de gestores.
- **Não confie no que vem do formulário** para definir mercado, produto ou permissões. Quem decide isso é o servidor.

**Commits**

- Em português, no presente, começando com um verbo: `adiciona`, `corrige`, `atualiza`, `remove`.
- Primeira linha com até 72 caracteres, dizendo **o que** mudou.
- Um assunto por commit.
- Se houver, cite o card do Jira ou a issue (`#12`) no fim da mensagem.

```text
corrige filtro de lotes vencidos no estoque (#12)
adiciona validação de quantidade negativa no registro de lote
atualiza README com o código de convite do gestor
```

## Segurança

- **Nunca** coloque no commit o `.env`, o `db.sqlite3`, a pasta `venv`/`.venv` ou a pasta `staticfiles` (já estão no `.gitignore`). Confira o `git status` antes de commitar.
- Se uma senha, chave ou `DATABASE_URL` for enviada por engano, avise o grupo na hora: ela precisa ser trocada.
- Se achar uma falha de segurança, **não abra issue pública**. Avise um mantenedor diretamente (contatos na seção "Nossa equipe" do [README](README.md)).

## Código de conduta

Queremos um espaço respeitoso para todas as pessoas. Ao participar, você se compromete a:

- tratar todo mundo com respeito e gentileza, sem preconceito ou assédio de nenhum tipo;
- dar e receber feedback com cuidado, focando no código e não na pessoa;
- aceitar que existem níveis diferentes de experiência e ajudar quem está começando.

Comportamentos desrespeitosos podem levar à remoção de comentários, issues ou contribuições. Nos guiamos pelo [Contributor Covenant](https://www.contributor-covenant.org/pt-br/version/2/1/code_of_conduct/).

## Reconhecimento

Toda contribuição conta, de uma vírgula corrigida a uma funcionalidade nova. Quem contribui aparece na seção "Nossa equipe" do [README](https://github.com/hellosofi/perene#colordarkseagreennossa-space-equipe-space-) e no histórico do GitHub.

## Quem mantém o projeto

O Perene é feito por estudantes da CESAR School, na disciplina de Fundamentos de Desenvolvimento de Software:

João Gustavo Vieira Fernandes Pedrosa, Kauã Cardoso de Melo, Lunna de Aguiar Mendonça Morelato Moreno, Matheus Pinheiro Laurentino, Nara de Melo Santos, Sofia Carolina Santos Bezerra, Sabrina Rayanne, Nadla Gabriele, Maria Clara, Beatriz Aciolli e Guilherme Lôbo.

Os e-mails de contato estão no [README](README.md).

## Onde pedir ajuda

- **Dúvida sobre o código ou o projeto:** abra uma [issue](https://github.com/hellosofi/perene/issues) com a etiqueta de dúvida ou pergunte no grupo da equipe.
- **Dúvida sobre as tarefas e o backlog:** [Jira do grupo](https://grupo-perene.atlassian.net).
- **Entender o código:** veja os vídeos de explicação linkados na seção Entregas do [README](README.md).
- **Algo não funcionou na instalação:** mande a mensagem de erro completa na issue ou no grupo, que a gente ajuda.
