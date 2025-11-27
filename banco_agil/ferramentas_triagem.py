import csv
import os
from dotenv import load_dotenv


def validar_cpf(cpf: str) -> bool:
    """
    Verifica se um CPF é válido. Usando apenas regras básicas de validação para demonstração.
    Requer também que o CPF seja passado com pelo menos 11 digitos numéricos (em str).
    """
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # 1. Checa se tem 11 dígitos (Válido)
    if len(cpf) != 11:
        return False
        
    # 2. Lógica de cálculo básico de validade (multiplo de 11)
    soma_digitos = sum(int(d) for d in cpf)

    if soma_digitos % 11 != 0:
        return False
    else:
        return True 
    

def auth_clientes(cpf: str, data_nascimento: str = None) -> dict:
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

                    if not data_registrada_num:
                        return {
                            "status": "error",
                            "mensagem": "CPF encontrado, mas sem data de nascimento registrada."
                        }

                    # Se usuário informou data, comparar
                    if data_nascimento:
                        if data_registrada_num == data_nascimento:
                            return {
                                "status": "success",
                                "mensagem": "CPF e data de nascimento conferem.",
                                "cpf": cpf,
                                "data_nascimento": data_registrada
                            }
                        else:
                            return { #Somente para fins de debug, retirar variaveis em produção ###VERIFICAR PARA PRODUÇÃO###
                                "status": "error",
                                "mensagem": f"Falha de autenticação. CPF: {cpf} (enviado) vs {cpf_csv} (registrado), Data Nasc: {data_nascimento} (enviado) vs {data_registrada_num} (registrado)"
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