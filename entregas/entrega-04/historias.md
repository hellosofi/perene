![Capa](../entrega-03/media/github-header-banner.png)

<!-- # Histórias de usuário -->

<h1 align="center">História 7: Como gestor, quero cadastrar meu mercado ao criar minha conta, para que os dados da minha empresa fiquem separados dos de outros mercados.</h1>

### Critérios de aceitação:

- [x] O cadastro de gestor deve pedir o nome e a cidade do mercado;

- [x] Ao concluir o cadastro, o sistema cria o mercado e o liga à conta do gestor;

- [x] O sistema não permite concluir o cadastro sem o nome do mercado.

### Cenários de Validação (BDD)
_Cenário 1: Cadastrar gestor com mercado_

```gherkin
Dado que o gestor acessou a página de cadastro com um código de acesso válido.

Quando preencher seus dados e o nome do mercado e confirmar.

Então o sistema deve criar a conta e o mercado e ligar o gestor a esse mercado.
```

_Cenário 2: Cadastro sem nome do mercado_

```gherkin
Dado que o gestor está preenchendo o cadastro.

Quando tentar confirmar sem informar o nome do mercado.

Então o sistema deve impedir o cadastro e informar que o campo é obrigatório.
```
---

<h1 align="center">História 8: Como funcionário, quero me cadastrar no mercado em que trabalho, para acessar as informações da minha equipe.</h1>

### Critérios de aceitação:

- [x] Cada mercado tem um código próprio, que o gestor vê no sistema;

- [x] O cadastro de funcionário deve pedir esse código;

- [x] O funcionário fica ligado ao mercado do código informado;

- [x] O sistema recusa códigos que não pertencem a nenhum mercado.

### Cenários de Validação (BDD)
_Cenário 1: Cadastrar funcionário com código válido_

```gherkin
Dado que existe um mercado cadastrado com um código próprio.

Quando o funcionário se cadastrar informando esse código.

Então o sistema deve criar a conta e ligar o funcionário a esse mercado.
```

_Cenário 2: Código de mercado inválido_

```gherkin
Dado que o funcionário está preenchendo o cadastro.

Quando informar um código que não pertence a nenhum mercado.

Então o sistema deve impedir o cadastro e informar que o código é inválido.
```
---

<h1 align="center">História 9: Como usuário, quero ver apenas os dados do meu mercado, para que as informações da minha empresa fiquem privadas.</h1>

### Critérios de aceitação:

- [x] Produtos, tarefas, funcionários e notificações pertencem a um mercado;

- [x] Todas as listagens mostram apenas os registros do mercado do usuário logado;

- [x] Novos registros são ligados automaticamente ao mercado do usuário;

- [x] Um usuário não consegue acessar registros de outro mercado, nem digitando o endereço direto no navegador.

### Cenários de Validação (BDD)
_Cenário 1: Listar apenas dados do próprio mercado_

```gherkin
Dado que existem produtos cadastrados no mercado A e no mercado B.

Quando um usuário do mercado A acessar o estoque.

Então o sistema deve exibir apenas os produtos do mercado A.
```

_Cenário 2: Tentar acessar registro de outro mercado_

```gherkin
Dado que existe um produto cadastrado no mercado B.

Quando um usuário do mercado A tentar acessar esse produto pelo endereço.

Então o sistema deve negar o acesso.
```
---

<h1 align="center">História 10: Como gestor, quero que os funcionários acessem apenas estoque e tarefas, para proteger as funções de gestão.</h1>

### Critérios de aceitação:

- [x] Funcionários acessam apenas as páginas de estoque, tarefas e notificações;

- [x] Gestores acessam todas as páginas;

- [x] O menu mostra apenas as opções permitidas para cada perfil;

- [x] Um funcionário que acessar uma página restrita pelo endereço recebe uma mensagem de acesso negado.

### Cenários de Validação (BDD)
_Cenário 1: Funcionário acessa página restrita_

```gherkin
Dado que um funcionário está logado no sistema.

Quando tentar acessar a página de gestão da equipe.

Então o sistema deve negar o acesso e exibir uma mensagem informando a restrição.
```

_Cenário 2: Menu conforme o perfil_

```gherkin
Dado que um funcionário está logado no sistema.

Quando visualizar o menu de navegação.

Então o sistema deve exibir apenas as opções de estoque, tarefas e notificações.
```
---

<h1 align="center">História 11: Como funcionário, quero registrar os lotes de cada produto com validade, quantidade e local, para controlar o estoque com precisão.</h1>

### Critérios de aceitação:

- [x] Um produto pode ter vários lotes;

- [x] Cada lote tem quantidade, data de validade, local de armazenamento e observação;

- [x] A quantidade total do produto é a soma de seus lotes;

- [x] O sistema não aceita quantidade negativa.

### Cenários de Validação (BDD)
_Cenário 1: Registrar novo lote_

```gherkin
Dado que existe um produto cadastrado no estoque.

Quando o funcionário registrar um lote com quantidade, validade e local.

Então o sistema deve salvar o lote e atualizar a quantidade total do produto.
```

_Cenário 2: Quantidade inválida_

```gherkin
Dado que o funcionário está registrando um lote.

Quando informar uma quantidade negativa.

Então o sistema deve impedir o registro e informar que a quantidade é inválida.
```
---

<h1 align="center">História 12: Como gestor, quero que a situação de cada lote seja calculada automaticamente, para identificar riscos sem precisar conferir item por item.</h1>

### Critérios de aceitação:

- [x] Verde: lote dentro da validade e estoque acima do mínimo;

- [x] Amarelo: lote que vence nos próximos 7 dias ou estoque abaixo do mínimo;

- [x] Vermelho: lote vencido ou marcado como avariado;

- [x] O prazo de alerta e o estoque mínimo podem ser definidos por produto;

- [x] Ao ficar amarelo ou vermelho, o lote gera uma notificação para o gestor.

### Cenários de Validação (BDD)
_Cenário 1: Lote próximo do vencimento_

```gherkin
Dado que existe um lote com validade daqui a 3 dias.

Quando o gestor acessar o estoque.

Então o sistema deve exibir o lote com a etiqueta amarela e uma notificação de vencimento próximo.
```

_Cenário 2: Lote vencido_

```gherkin
Dado que existe um lote com a data de validade já passada.

Quando o gestor acessar o estoque.

Então o sistema deve exibir o lote com a etiqueta vermelha.
```
