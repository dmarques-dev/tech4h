

def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Acessa a API em frankfurter.app para obter a cotação de câmbio entre duas moedas.

    Argumentos:
        from_currency: A moeda de origem (ex: "USD").
        to_currency: A moeda de destino (ex: "BRL").

    Returns:
        A taxa de câmbio da moeda de origem para a moeda de destino. O seguinte exemplo de formato em JSON é retornado:
        {"amount":1.0,"base":"USD","date":"2025-11-26","rates":{"BRL":5.3763}}
        Onde "rates" contém a taxa de câmbio solicitada.
    """
    import requests
    
    try:
        # Se a moeda de destino não for especificada, atribuir "BRL" por padrão
        if not to_currency:
            to_currency = "BRL"
        
        
        url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP de erro
        data = response.json()
        
        if "rates" in data and to_currency in data["rates"]:
         #  return data["rates"][to_currency]
            rates = data["rates"][to_currency]

            rates = f"{rates:.4f}".replace('.', ',')

            return {
                "status": "success",
                "taxa": rates, 
                "moeda_origem": from_currency,
                "moeda_destino": to_currency,
 #               "data": data.get("date", "N/A"),
            }
        else:
            return {
            "status": "error",
            "mensagem": f"Não foi possível obter a taxa de câmbio de {from_currency} para {to_currency}."
            }

    except requests.exceptions.RequestException as e:
        # Erros de rede
        return {
            "status": "error",
            "mensagem": "Não foi possível conectar ao serviço de câmbio no momento. Por favor, tente novamente mais tarde.",
            "detalhes": str(e)
        }

    except Exception as e:
        # Erros não esperados
        return {
            "status": "error",
            "mensagem": "Ocorreu um erro inesperado ao obter a taxa de câmbio. Por favor, tente novamente mais tarde.",
            "detalhes": str(e)
        }


