from google.adk.tools import ToolContext

# Estabelecendo os pesos para cálculo de score
peso_renda = 30
peso_emprego = {
    "formal": 300,
    "autônomo": 200,
    "autonomo": 200, 
    "desempregado": 0
}

peso_dependentes = {
    0: 100,
    1: 80,
    2: 60,
    "3+": 30
}

peso_dividas = {
    "sim": -100,
    "não": 100,
    "nao": 100
}

def calcular_score(renda_mensal: str, tipo_emprego: str, despesas_mensais: str, dependentes: str, tem_dividas: str, tool_context: ToolContext = None ) -> dict:
    """
    Calcula o score de crédito baseado nas informações financeiras do cliente.
    
    Args:
        renda_mensal (str): Renda mensal do cliente
        tipo_emprego (str): Tipo de emprego (formal, autônomo, desempregado)
        despesas_mensais (str): Despesas mensais fixas
        dependentes (str): Número de dependentes (0, 1, 2, 3+)
        tem_dividas (str): Se possui dívidas ativas (sim/não)
    
    Returns:
        dict: Resultado do cálculo do score com status e mensagem.
    """
    try:
        renda = float(renda_mensal)
        despesas = float(despesas_mensais)
        tipo_emp = tipo_emprego.lower()

        # Processar dependentes
        try:
            deps = int(dependentes)
        except:
            deps = "3+"

        dividas = tem_dividas.lower()

        # Calcular score
        score = (
            (renda / (despesas + 1)) * peso_renda +
            peso_emprego.get(tipo_emp, 0) +
            peso_dependentes.get(deps, 0) +
            peso_dividas.get(dividas, 0)
        )

        score_final = round(score)

        return {
            "status": "success",
            "score": score_final,
            "mensagem": f"Score de crédito calculado: {score_final}"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "mensagem": f"Erro ao calcular score: {str(e)}"
        }

def atualizar_score_cliente(cpf: str, novo_score: int, tool_context: ToolContext = None) -> dict:
    """
    Atualiza o score do cliente no arquivo clientes.csv.
    
    Args:
        cpf (str): CPF do cliente 
        novo_score (int): O novo score a ser gravado.
    
    Returns:
        dict: Resultado da operação com status e mensagem.
    """
    import csv
    import os
    
    csv_clientes_path = os.getenv("CSV_CLIENTES")
    
    if not csv_clientes_path:
        return {"status": "error", "mensagem": "Variável CSV_CLIENTES não definida no .env"}
    
    # Limpar o CPF 
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    # Formatar o CPF para o padrão do arquivo
    cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}/{cpf_limpo[9:]}"
    
    try:
        # Ler todas as linhas do arquivo
        linhas = []
        cliente_encontrado = False
        
        with open(csv_clientes_path, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            fieldnames = leitor.fieldnames
            
            for linha in leitor:
                # Limpar o CPF da linha para comparação
                cpf_linha_limpo = ''.join(filter(str.isdigit, linha.get("cpf", "")))
                
                if cpf_linha_limpo == cpf_limpo:
                    # Atualizar o score atual
                    linha['score_atual'] = str(int(novo_score))
                    cliente_encontrado = True
                
                linhas.append(linha)
        
        if not cliente_encontrado:
            return {"status": "error", "mensagem": f"Cliente com CPF {cpf_formatado} não encontrado no arquivo."}
        
        # Reescrever o arquivo com os dados atualizados
        with open(csv_clientes_path, mode='w', encoding='utf-8', newline='') as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=fieldnames)
            escritor.writeheader()
            escritor.writerows(linhas)
        
        tool_context.state["user_score_atual"] = novo_score 
 

        return {
            "status": "success",
            "mensagem": f"Score de crédito atualizado com sucesso para {novo_score:.2f}.",
            "cpf": cpf_formatado,
            "novo_score": novo_score
        }
    
    except FileNotFoundError:
        return {"status": "error", "mensagem": "Arquivo clientes.csv não encontrado."}
    
    except Exception as e:
        return {"status": "error", "mensagem": f"Erro ao atualizar score de crédito: {str(e)}"}