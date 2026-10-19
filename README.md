# $${\color{darkseagreen}Perene}$$
<h3> Soluções ESG para pequenas e médias empresas no setor de varejo alimentar </h3>
<h4><em>Fundamentos de Desenvolvimento de Software</em></h4>

## Sobre o Projeto Perene
O projeto Perene surge da necessidade dos mercados de pequeno e médio porte (no setor varejista supermercadista), evoluírem para não ficar para trás quando se trata das medidas cada vez mais presentes de ESG em suas funções.

## Nossa solução
Propomos um site e aplicativo que possibilita de maneira simples donos ou gerentes de mercados de médio e pequeno porte nas medidas ambientais, sociais e de governança. dentre nossas várias funcionalidades, as que mais se destacam são: consultoria automática, cardápio de empresas alinhadas a ESG.

## $${\color{darkseagreen}Acesso \space ao \space Deploy \space :}$$
A url do nosso projeto já está disponível, acesse o link abaixo e veja nossa plataforma desenvolvida para a implementação de ESG no ramo de varejo alimentar! 
<h4 align="center" target="_blank">https://perene.onrender.com</h4>

---
## ୭  🧷  Como Rodar o Projeto Localmente

### Pré-requisitos

- Python
- Git

### 1. Clonar o repositório

```bash
git clone https://github.com/hellosofi/perene.git
cd perene
```

### 2. Criar e ativar o ambiente virtual

No Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Mac/Linux (Terminal):

```
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto, na mesma pasta do `manage.py`.

Gere uma chave secreta com o comando:

```bash
py -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

No arquivo `.env`, adicione:

```env
SECRET_KEY=cole-sua-chave-gerada-aqui
ENVIRONMENT=development
```

Substitua `cole-sua-chave-gerada-aqui` pela chave gerada no comando anterior.

Para liberar o cadastro de gestor pela página, defina também um código de acesso (quem não souber o código não consegue criar conta de gestor):

```env
GESTOR_CODIGO_CONVITE=escolha-um-codigo-aqui
```

No deploy (Render), adicione essa mesma variável em *Environment*.

### 5. Executar as migrações

```bash
python manage.py migrate
```

### 6. Verificar o projeto

```bash
python manage.py check
```

### 7. Iniciar o servidor

```bash
python manage.py runserver
```

A aplicação ficará disponível em:

http://127.0.0.1:8000/

---
## $${\color{darkseagreen}Entregas}$$

### ⭐┆ Entrega 01

<h4 align="center">𖥸</h4>

<div align="center"><a href="https://grupo-perene.atlassian.net"><img src="https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=Jira&logoColor=white"/></a>

<a href="https://github.com/hellosofi/perene/blob/main/entregas/entrega-01/documento-analise.md"><img src="https://img.shields.io/badge/DOCUMENTO-A?style=for-the-badge&logo=readme&logoColor=darkseagreen&labelColor=33473B&color=darkseagreen"></a>

</div>

![Quadro da Sprint 01 - Jira](./entregas/entrega-01/media/backlog.png)


<br/>

### ⭐┆ Entrega 02

![Quadro da Sprint 02 - Jira](entregas/entrega-01/media/Sprint02.png)

<br/>

![Print Bug Tracker](entregas/entrega-01/media/Print_BugTracker.png)

<br/>

Veja o projeto funcionando: [Acesse o vídeo no Youtube](https://youtu.be/EpsZ5v47rjs)
<br/>
Explicação do código inicial (W.I.P): [Youtube](https://youtu.be/7_4VonwUPlg?si=UQOuGa8QSrvDRjkZ)

### ⭐┆ Entrega 03
<div align="center">

<a href="https://github.com/hellosofi/perene/blob/main/entregas/entrega-03/historias.md"><img src="https://img.shields.io/badge/HIST%C3%93RIAS-A?style=for-the-badge&logo=readme&logoColor=darkseagreen&labelColor=33473B&color=darkseagreen"></a>

</div>

![Quadro da Sprint 03 - Jira](entregas/entrega-03/media/Sprint03.png)

<br/>

![Backlog da Sprint 03](entregas/entrega-03/media/Backlog03.png)

<br/>

---

### $${\color{darkseagreen}Nossa \space equipe \space :}$$

<div align="center">

<!-- <table style="">
  <tr>
    <td align="center"><a href="https://github.com/joaogpedrosa">
      <img style= "width: 115px; height: 115px; display: flex; align-items: center; justify-content: center;" src="https://i.imgur.com/IkLCEzz.jpeg">
      </a>
      <br/>
      João Gustavo
    </td>
    <td align="center"><a href="https://github.com/heykauac">
      <img style= "width: 115px; height: 115px; display: flex; align-items: center; justify-content: center;" src="https://i.imgur.com/IkLCEzz.jpeg">
      </a>
      <br/>
      Kauã Cardoso
    </td>
    <td align="center">
      <a href="https://github.com/lunnaaguiar">
        <img style= "width: 115px; height: 115px; display: flex; align-items: center; justify-content: center;" src="https://i.imgur.com/IkLCEzz.jpeg">
        </a>
        <br/>
        Lunna de A.
      </td> 
    <td align="center">
      <a href="https://github.com/matheuspinheirol">
        <img style= "width: 115px; height: 115px; display: flex; align-items: center; justify-content: center;" src="https://i.imgur.com/IkLCEzz.jpeg">
        </a>
        <br/>
        Matheus P.
      </td>
    <td align="center"><a href="https://github.com/algaerithm">
      <img style= "width: 115px; height: 115px; display: flex; align-items: center; justify-content: center;" src="https://i.imgur.com/IkLCEzz.jpeg">
      </a>
      <br/>
      Nara Melo
    </td>
    <td align="center"><a href="https://github.com/hellosofi">
      <img style= "width: 115px; height: 115px; display: flex; align-items: center; justify-content: center;" src="https://i.imgur.com/IkLCEzz.jpeg">
      </a>
      <br/>
      Sofia Carolina
    </td>
  </tr>
</table> -->


| Nome Completo | E-mail da School |
| :---: | :---: |
| João Gustavo Vieira Fernandes Pedrosa | jgvfp@cesar.school |
| Kauã Cardoso de Melo | kcm2@cesar.school |
| Lunna de Aguiar Mendonça Morelato Moreno | lammm@cesar.school |
| Matheus Pinheiro Laurentino | mpl2@cesar.school |
| Nara de Melo Santos | nms2@cesar.school |
| Sofia Carolina Santos Bezerra | scsb@cesar.school |

</div>
