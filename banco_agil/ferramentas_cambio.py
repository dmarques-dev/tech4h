
def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Acessa a API aberta em frankfurter.app para obter a cotação de câmbio entre duas moedas.

    Argumentos:
        from_currency: A moeda de origem (ex: "USD").
        to_currency: A moeda de destino (ex: "BRL").

    Returns:
        A taxa de câmbio da moeda de origem para a moeda de destino. O seguinte formato em JSON é retornado:
        {"amount":1.0,"base":"USD","date":"2025-11-26","rates":{"BRL":5.3763}}
        Onde "rates" contém a taxa de câmbio solicitada.
    """
    import requests
    
    # Se a moeda de destino não for especificada, atribuir "BRL" por padrão
    if not to_currency:
        to_currency = "BRL"
    
     
    url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
    response = requests.get(url)
    response.raise_for_status()  # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
    data = response.json()
    
    if "rates" in data and to_currency in data["rates"]:
        return data["rates"][to_currency]
    else:
        raise ValueError(f"Não foi possível obter a taxa de câmbio para {from_currency} para {to_currency}.")


from . import agente_cambio # Importa Agente de cambio definido no agente_cambio.py
def rotear_para_agente_cambio(mensagem_cliente: str) -> str:
    """
    Encaminha a conversa do cliente para o Agente de Câmbio para 
    obter informações sobre limite.
    
    Args:
        mensagem_cliente: A pergunta original do cliente sobre câmbio.
        
    Returns:
        A resposta final gerada pelo Agente de Câmbio.
    """

    try:
        response = agente_cambio.run(message=mensagem_cliente)
        return f"Resposta do Agente de Crédito: {response.text}"
    except Exception as e:
        return f"Erro ao rotear: {e}"