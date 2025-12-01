import csv
import os
from dotenv import load_dotenv
from google.adk.tools import ToolContext



#Função para validar CPF
def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    # Rejeita sequências repetidas ===> Para o exercício, vamos suprimir esta verificação para podermos usar CPFs de teste (Ex: 111.111.111-11)
    #if cpf == cpf[0] * 11:
    #    return False

    # Primeiro dígito
    soma = sum(int(d) * peso for d, peso in zip(cpf[:9], range(10, 1, -1)))
    dv1 = (soma * 10) % 11
    dv1 = 0 if dv1 == 10 else dv1

    if dv1 != int(cpf[9]):
    #    print(f"Erro ! CPF {cpf} Digito 1: {dv1}")
        return False

    # Segundo dígito
    soma = sum(int(d) * peso for d, peso in zip(cpf[:10], range(11, 1, -1)))
    dv2 = (soma * 10) % 11
    dv2 = 0 if dv2 == 10 else dv2

    if dv2 != int(cpf[10]):
    #    print(f"Erro ! CPF {cpf} Digito 2: {dv2}")
        return False

    return True

def encerra_sessao(tool_context: ToolContext = None) -> dict:

    if tool_context:
        tool_context.state["user_cpf"] = ""
        tool_context.state["user_limite_credito"] = ""
        tool_context.state["user_score_atual"] = ""
        return {"status": "success", "mensagem": "Informações de contexto apagadas. Encerrando sessão"}

    

async def auth_clientes(cpf: str, data_nascimento: str = None, tool_context: ToolContext = None)  -> dict:
    """
    Verifica no CSV CSV_CLIENTES se existe o CPF e a data de nascimento, e se o par é válido.
    Caso não seja válido, informar falha de autenticação, e que só serão permitidos 3 tentativas.
    Não expor as mensagens de erro de sistema diretamente ao cliente. Somente se for um erro de autenticação.

    Parâmetros:
        cpf (str): CPF a ser buscado.
        data_nascimento (str): Data de nascimento para validar (dd-mm-AAAA).

    Retorna:
        dict: Resultado da verificação.
    """
    
    csv_path = os.getenv("CSV_CLIENTES")

    # Limpar o CPF para garantir que está no formato correto (apenas dígitos)
    cpf = ''.join(filter(str.isdigit, cpf))    

    # Limpar data de nascimento de entrada 
    if data_nascimento:
        data_nascimento = ''.join(filter(str.isdigit, data_nascimento))

    if not csv_path:
        return {"status": "error", "mensagem": "Variável CSV_CLIENTES não definida no .env"}

    try:
        with open(csv_path, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)

            for linha in leitor:

                # Limpar CPF do CSV
                cpf_csv = ''.join(filter(str.isdigit, linha.get("cpf", "")))
    
                if cpf_csv == cpf:


                    # Limpar a data do CSV
                    data_registrada = linha.get("data_nascimento", "")
                    data_registrada_num = ''.join(filter(str.isdigit, data_registrada))

                    #Ler limite de crédito e score atual para gravar em context se necessário no futuro
                    limite_credito = linha.get("limite_credito", "")
                    score_atual = linha.get("score_atual", "")
                

                    if not data_registrada_num:
                        return {
                            "status": "error",
                            "mensagem": "CPF encontrado, mas sem data de nascimento registrada."
                        }

                    # Se usuário informou data, comparar
                    if data_nascimento:
                        if data_registrada_num == data_nascimento:
                            # Grava os dados do cliente autenticado no contexto para outros agentes se necessário

                            if tool_context:
                                tool_context.state["user_cpf"] = cpf
                                tool_context.state["user_limite_credito"] = limite_credito
                                tool_context.state["user_score_atual"] = score_atual    


                            return {
                                "status": "success",
                                "mensagem": "CPF e data de nascimento conferem.",
                                "cpf": cpf,
                                "data_nascimento": data_registrada
                            }
                        else:
                            return { #Somente para fins de debug, retirar variaveis em produção 
                                "status": "error",
                                #"mensagem": f"Falha de autenticação. CPF: {cpf} (enviado) vs {cpf_csv} (registrado), Data Nasc: {data_nascimento} (enviado) vs {data_registrada_num} (registrado)"
                                "mensagem": "Falha de autenticação. CPF ou data de nascimento não conferem."                              
                            }

                    # Se não foi informado data, mas o CPF existe:
                    return {
                        "status": "error",
                        "mensagem": "CPF encontrado sem data de nascimento.",
                        "cpf": cpf
                    }

        return {"status": "error", "mensagem": f"Falha de autenticação. CPF não encontrado. {cpf}"}

    except FileNotFoundError:
        return {"status": "error", "mensagem": "Arquivo de dados não encontrado."}

    except Exception as e:
        return {"status": "error", "mensagem": f"Erro interno ao processar autenticação: {e}"}