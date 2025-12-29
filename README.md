[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/_wic0ZrM)
# Trabalho Prático

**Laboratórios de Informática**

Licenciatura em Engenharia de Sistemas Informáticos (*regime pós-laboral*) 2025-26

## Grupo  *37*
| #      | Número  | Nome            | 
| -----  | -----   | ----            |
| _A1_   | 29382   | Alexandre Silva |
| _A2_   | 29383   | Pedro Mendes    |


## organização 

|    |    |
| -- | -- |
|[data/](./data/)| dados de entrada |
|[doc/](./doc/)  | relatório em LaTex|
|[ref/](./ref/)  | documentação do código (pdoc)| 
|[src/](./src/)  | código com a implementação da solução desenvolvida |

### executar a aplicação 

**Como executar o Shiny:**
1. Dentro da pasta do projeto, executar o comando:
   ```bash
   shiny run --reload app.py
2. No browser, aceder ao seguinte endereço: http://127.0.0.1:8000/


Como gerar o relatório LaTeX:

1. Através do VSCode, instalar a extensão LaTeX Workshop.

2. Executar o ficheiro `main.tex` que se encontra dentro da pasta ref. Este ficheiro contém todos os dados que serão apresentados no PDF que será gerado.

3. Após a execução, irá ser gerado um ficheiro `main.pdf` na pasta ref.


Como gerar o relatório LaTex:
1 - Através do VSCode, instalar a extensão LaTex Workshop.
2 - Executar o ficheiro ref/main.tex. Este ficheiro contém todos os dados que serão apresentados no pdf que será gerado.
3 - Após a execução, irá ser gerado um ficheiro main.pdf na pasta ref.

Como gerar ficheiros HTML pdoc:
1 - Dentro da pasta do projeto, executar o seguinte comando: pdoc --html app.py src --output-dir docs --force
2 - Na pasta docs, será criado um ficheiro app.html que documenta todo o código que gere o funcionamento do shiny (frontend), e uma pasta src onde existe documentação específica para cada um dos módulos de tratamento dos dados, bem como um ficheiro index.html que compila todas as informações, sendo possível visualizar todos os dados dentro deste ficheiro através da navegação por links.