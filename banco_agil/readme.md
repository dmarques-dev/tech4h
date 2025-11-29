# Desafio Técnico: Agente Bancário Inteligente

## Visão geral do projeto
O projeto chamado "Banco Ágil" visa demonstrar a construção de um agente de inteligência artificial, seguindo os requisitos principais do exercício, construindo:

- Agente de Triagem: Autentica o cliente e direciona para o agente apropriado.
- Agente de Crédito: Informa sobre limites de crédito e processa solicitações de aumento de limite.
- Agente de Entrevista de Crédito: Conduz uma entrevista financeira para atualizar o score de crédito.
- Agente de Câmbio: Realiza consulta de cotação de moedas.


## Estrutura do projeto

```
banco_agil/ 
|---dados/ #Possui as informações sobre a "base de dados" dos clientes
|---.env-example #Variáveis de ambiente, necessário popular com chaves de API e renomear para ".env"
|---agent.py  #Agente principal, também chamado de "Agente de triagem"
|---ferramentas_triagem.py   #Ferramentas (funções em python) do agente de triagem
|---agente_cambio.py  #Agente de câmbio, responsável pela tratativa de conversão de moedas
|---ferramentas_cambio.py   #Ferramentas (funções em python) do agente de câmbio
|---agente_credito.py   #Agente de crédito - Responsável por informar limites do cliente e processar solicitações de aumento de limite
|---ferramentas_credito.py   #Ferramentas (funções em python) do agente de crédito
|---agemte_entrevista.py   #Agente de entrevista - Responsável por conduzir uma entrevista financeira para atualizar o score de crédito

```

## Tecnogia e Ferramentas

### Framework Google ADK
Escolhido por ser modular, utilizar linguagem Python e compatível com diversos tipos de LLMs (inclusive Ollama), e atender à requisição de Multi-agents e Workfloe agent.

### Linguagem Python
Escolhida por ser de natureza de alto nível (acelerando o desenvolvimento), ser uma das com robusta presença no ADK e de maior suporte na comunidade. 

## Arquitetura
A arquitetura desenvolvida contempla agentes Coordenados usando o ADK (Agent Development Kit) do Google, com um Agente de Triagem (Root Agent) que roteia a conversa para um Agente de Câmbio, um Agente de Crédito e um Agente de entrevistas. 

(INSERIR IMAGEM)


## Escolhas técnicas

### Front-end
Como Front-end, um html com Javascript foi utilizado para acessar os agentes em Python. 
Para efeitos de desenvolvimento, usou-se a interface http, diretamente no localhost na porta 8000, uma funcionalidade do ADK que facilita a visão do fluxo de mensagens. 

### LLM
Para fins de teste, a API do Google (gemini-2.5-flash) free tier foi utilizada. 
Além de possuir um free-tier, o LLM foi escolhido principalmente pela sua compatibilidade, integração nativa, e o ecossistema oferecido pelo Google. 



### APIs
Demais APIs utilizadas:
- API em frankfurter.app para obter a cotação de câmbio sem a necessidade de cadastro ou token



# Funcionalidades implementadas
1 - O Agente de triagem é o responsável pela primeira interação, ele é responsável por questionar o CPF e a data de nascimento do cliente do banco
1.1 - Ele valida o CPF antes de buscar na "base de dados" para minimizar os recursos de sistema (BD). Neste ponto, para efeitos de teste, serão validados CPFs de acordo com as regras oficiais, EXCETO os dígitos contínuos para efeitos do exercício proposto. Esta parte do código está comentada para habilitação futura.



#Todo
## Desafios enfrentados e como foram resolvidos.
## Escolhas técnicas e justificativas.
## Tutorial de execução e testes.

