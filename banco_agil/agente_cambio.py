# Agente de câmbio - para tratar requisições relacionadas a câmbio

from google.adk.agents.llm_agent import Agent, FunctionTool

from .ferramentas_cambio import get_exchange_rate

#Definindo a Tool para obter a cotação de câmbio
exchange_rate = FunctionTool(
    func=get_exchange_rate
)

# Definindo o agente de cambio...
agente_cambio = Agent(
    model='gemini-2.5-flash',
    name='Agente_de_Cambio',
    tools=[exchange_rate],
    instruction=""""
    Você é um especialista em câmbio. Use a ferramenta "exchange_rate" para informar ao cliente qual é a cotação da moeda de origem para a moeda de destino.
    Você deve sempre perguntar ao cliente qual é a moeda de origem e a moeda de destino. Se o cliente não souber o código da moeda (Ex: USD, EUR), ajude-o a descobrir.
    Sempre responda de forma clara e objetiva, fornecendo a cotação atualizada.
    Depois de fornecer a cotação, pergunte se o cliente precisa de mais alguma coisa relacionada a câmbio. Caso contrário, retorne ao agente de triagem. 

    """,
)