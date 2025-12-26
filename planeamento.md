# Trabalho Prático

**Laboratórios de Informática**

Licenciatura em Engenharia de Sistemas Informáticos (*regime pós-laboral*) 2025-26

## grupo  *37*
| #      | Número  | Nome |
| -----  | -----   | ---- |
| _A1_   | 29382   | Alexandre Silva  |
| _A2_   | 29383    | Pedro Mendes  |


## Planeamento

### Semana 1 - [17.nov a 21.nov] 

- [x] Distribuíção de tarefas
- [x] Análise do ficheiro PS2 para compreensão do formato
- [x] Estruturação inicial do projeto


| #      | Branch  | Descrição da Tarefa |
| -----  | ------  | ---- |
| _A1_   | feature/validacao-ps2   | Validar dados retornados por uma lista de dicionários  |
| _A2_   | feature/leitura-ps2    | Abordargem inicial à leitura de um único ficheiro ps2, bem como a organização dos dados numa lista de dicionários |

### observações / decisões  
Análise inicial do ficheiro para proceder à identificação de cada campo (Perceber a lógica da estrutura).


## Semana 2 - [24.nov a 28.nov] 

- [x] Implementação da leitura de ficheiros .ps2 presentes na pasta `data`
- [x] validar se conteúdo do ficheiro respeita a formatação ps2
- [x] validar nifs e IBANs 

| #      | Branch  | Descrição da Tarefa |
| -----  | -----   | ---- |
| _A1_   | feature/validacao-ps2   | Validar dados expecíficos retornados por uma lista de dicionários (NIF, IBAN) |
| _A2_   | feature/leitura-ps2    | Leitura de um único ficheiro ps2, bem como a organização dos dados numa lista de dicionários |

### observações / decisões  
A Branch de feature/leitura-ps2 retorna a lista de dicionários com o NIB devidamente formatado como IBAN (PT50). Para verificar se o IBAN é válido recorremos às regras da norma ISO 7064 (módulo 97-10), que respeita as normas internacionais, para validar qualquer código IBAN.
Já o campo NIF recorremos ao cálculo do módulo 11, a fase crítica do algoritmo reside na soma ponderada, onde cada um dos oito dígitos iniciais do NIF é multiplicado por um fator de ponderação específico. Estes 'pesos' são atribuídos de forma sequencial e decrescente: o primeiro dígito é multiplicado por 9, o segundo por 8, continuando esta lógica até ao oitavo dígito, que é multiplicado por 2. Desta forma podemos determinar se o NIF é válido, calculando o resto da divisão da soma total por 11. Se o resto for 0 ou 1, o dígito de controlo (9.º algarismo) deve ser 0; caso contrário, o dígito de controlo deve corresponder à diferença entre 11 e o resto obtido.


## Semana 3 - [01.dez a 05.dez] 

- [x] Validação dos restantes campos retornados
- [x] Blindagem das validações (prevenir erros de código) 
- [x] Introdução ao Pandas

| #      | Branch  | Descrição da Tarefa |
| -----  | -----   | ---- |
| _A1_   | feature/validacao-ps2   | Validar dados retornados por uma lista de dicionários e blindagem de código|
| _A2_   | feature/leitura-ps2    | Formatação dos dados extraidos em tabelas com recurso à biblioteca Pandas ||

### observações / decisões  
Foi feito um estudo para compreender o conceito da biblioteca Pandas, sendo esta uma das mais famosas do Python.
O Pandas é o Cérebro (Back-end): Faz o trabalho "sujo" e pesado. Lê o ficheiro e prepara a tabela final.


## Semana 4 - [08.dez a 12.dez] 

- [x] Implementar uma variável pública ao validar campos de cada ficheiro
- [x] Leitura de múltiplos ficheiros em simultâneo 

| #      | Branch  | Descrição da Tarefa |
| -----  | -----   | ---- |
| _A1_   | feature/validacao-ps2 | implementação de variável global |
| _A2_   | feature/leitura-varios-ps2 | Leitura de vários ficheiros e retornar em tabelas com recurso à biblioteca Pandas|

### observações / decisões  
Implementação de uma variável global no código validacao-ps2 para validar se o ficheiro completo é válido ou não, se for válido avança para a leitura dos ficheiros, caso não seja válido salta logo fora.

## Semana 5 - [15.dez a 19.dez] 

- [x] Introdução ao Shiny
- [x] Implementação do Pandas com o Shiny para consultar dados
- [x] Construção do relatório e atualização do ficheiro planeamento


| #      | Branch  | Descrição da Tarefa |
| -----  | -----   | ---- |
| _A1_   | feature/validacao-ps2 | Construção do relatório e atualização do ficheiro planeamento |
| _A2_   | feature/shiny  | Implementação Shiny e integração do Pandas com o Shiny para consultar dados |

### observações / decisões  
Feito um estudo da biblioteca Shiny para implementação no trabalho prático, com o intuito de consultar dados finais já validados.

## Semana 6 - [22.dez a 29.dez] 

- [x] Desenvolvimento da dashboard em Shiny
- [x] Criação de ficheiros válidos
- [x] Construção do relatório e atualização do ficheiro planeamento

| #      | Branch  | Descrição da Tarefa |
| -----  | -----   | ---- |
| _A1_   | feature/validacao-ps2 | Criação de ficheiros válidos, documentação de código, variável tipo lista para apresentar ficheiros inválidos,  desenvolvimento do relatório |
| _A2_   | feature/shiny  | Desenvolvimento da dashboard em Shiny para consultar os dados, documentação de código, desenvolvimento do relatório |

### observações / decisões  
Os ficheiros inválidos devem aparecem listados pelo nome do ficheiro, não sendo carregados para a dashboard.