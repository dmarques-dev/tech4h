import csv
import os
from dotenv import load_dotenv
from google.adk.tools import ToolContext



def atualiza_credito_cliente(cpf: str, novo_limite: float) -> dict:
    """
    Atualiza o limite de crédito de um cliente no arquivo clientes.csv.
    
    Args:
        cpf (str): CPF do cliente 
        novo_limite (float): O novo limite a ser gravado.
    
    Returns:
        dict: Resultado da operação com status e mensagem.
    """
    
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
                    # Atualizar o limite de crédito
                    linha['limite_credito'] = f"{novo_limite:.2f}"
                    cliente_encontrado = True
                
                linhas.append(linha)
        
        if not cliente_encontrado:
            return {"status": "error", "mensagem": f"Cliente com CPF {cpf_formatado} não encontrado no arquivo."}
        

        # Reescrever o arquivo com os dados atualizados
        with open(csv_clientes_path, mode='w', encoding='utf-8', newline='') as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=fieldnames)
            escritor.writeheader()
            escritor.writerows(linhas)
        
        return {
            "status": "success",
            "mensagem": f"Limite de crédito atualizado com sucesso para R$ {novo_limite:.2f}.",
            "cpf": cpf_formatado,
            "novo_limite": novo_limite
        }
    
    except FileNotFoundError:
        return {"status": "error", "mensagem": "Arquivo clientes.csv não encontrado."}
    
    except Exception as e:
        return {"status": "error", "mensagem": f"Erro ao atualizar limite de crédito: {str(e)}"}
    


def verificar_limite_credito(tool_context: ToolContext) -> dict:

    """
    Informe o limite de crédito disponível para um cliente com base no CPF.
    Usa as informações armazenadas no contexto do agente para obter o CPF, limite de crédito e score atual.

    Args:
    Somente o conteúdo do ToolContext é necessário.

    Returns:
        str: Mensagem informando o limite de crédito disponível.
    """
   
    # Busca as variáveis no contexto.
    cpf = tool_context.state.get("user_cpf")
    limite_atual = tool_context.state.get("user_limite_credito")
    score = tool_context.state.get("user_score_atual")

    if not cpf:
        return {"status": "error", "mensagem": "CPF do usuário não encontrado no contexto."}
  
    
    return f"O limite de crédito disponível para o CPF {cpf} é R$ {limite_atual}."
                        



def solicitar_aumento_limite(tool_context: ToolContext, novo_limite: float) -> dict:
    """
    Solicita um aumento de limite de crédito para o cliente com base no CPF do contexto.
    Registra a solicitação em um arquivo CSV chamado solicitacoes_aumento_limite.csv.
    Caso o limite solicitado seja maior que o permitido pelo score, informa ao cliente que não é possível e 
    ele pode realizar uma entrevista de crédito. Perguntar se deseja iniciar a entrevista.

    Cado o limite solicitado seja menor ou igual ao permitido pelo score, aprova a solicitação, registra no clientes.csv 
    e informa ao cliente que a solicitação foi concedida, informando o novo limite.

    Args:
    tool_context (ToolContext): Contexto do agente contendo informações do cliente.
        novo_limite (float): O novo limite de crédito solicitado.

    Returns:
        str: Mensagem confirmando a solicitação.
    """

    import datetime

    # Busca as variáveis no contexto.
    cpf = tool_context.state.get("user_cpf")
    limite_atual = tool_context.state.get("user_limite_credito")
    score_atual = tool_context.state.get("user_score_atual")

    csv_solicitacoes_path = os.getenv("CSV_SOLICITACOES_LIMITE")    
    csv_limites_path = os.getenv("CSV_SCORE_LIMITE")
    
    if not cpf:
        return {"status": "error", "mensagem": "CPF do usuário não encontrado no contexto. Fazer autenticação primeiro."}
                
    if not score_atual:
        return {"status": "error", "mensagem": "Score do cliente não encontrado no contexto."}
    
    # Colocar o score atual como inteiro
    try:
        score_cliente = int(score_atual)
    except (ValueError, TypeError):
        return {"status": "error", "mensagem": "Score do cliente inválido."}

    #Verificar se o cliente é elegível a aumento de limite baseado no score
    if not csv_limites_path:
        return {"status": "error", "mensagem": "Variável CSV_SCORE_LIMITE não definida no .env"}

    try:
        with open(csv_limites_path, mode='r', encoding='utf-8') as arquivo:    
            leitor = csv.DictReader(arquivo)

            #Ler todos os registros e encontrar o melhor limite para o score atual
            limite_permitido = None
            melhor_score = -1
            status_pedido = "pendente"
            mensagem_pedido = {}

            for linha in leitor:
                try:
                    score_tabela = int(linha.get("score_target", "0"))
                    limite_tabela = float(linha.get("limite_permitido", "0"))
                    
                    # Verifica se o score da tabela é <= score do cliente
                    # E se é o maior score encontrado até agora (mais próximo do score do cliente)
                    if score_tabela <= score_cliente and score_tabela > melhor_score:
                        melhor_score = score_tabela
                        limite_permitido = limite_tabela
                        
                except (ValueError, TypeError):
                    continue  # Se houver erro, pula para proxima linha
            
            if limite_permitido is None:
                return {
                    "status": "error",
                    "mensagem": f"Não foi possível determinar o limite permitido para o score do cliente. Erro ao processar solicitação: {str(e)}"
                }
            
            # Verificar se o novo limite solicitado excede o permitido
            if novo_limite > limite_permitido:
                status_pedido = "reprovado"
                mensagem_pedido = { 
                    "status": "limite_rejeitado",
                    "mensagem": f"Infelizmente, o limite solicitado de R$ {novo_limite:.2f} excede o limite máximo permitido de R$ {limite_permitido:.2f} baseado no seu score atual ({score_cliente}). Você pode optar por realizar uma entrevista de crédito para tentar aumentar seu limite. Deseja iniciar a entrevista de crédito?",
                    "limite_permitido": limite_permitido,
                    "limite_solicitado": novo_limite
                }
            else:
                status_pedido = "aprovado"
                mensagem_pedido = {
                    "status": "limite_aprovado",
                    "mensagem": f"Parabéns! Sua solicitação de aumento de limite para R$ {novo_limite:.2f} foi aprovada. Seu novo limite de crédito é de R$ {novo_limite:.2f}.",
                    "limite_anterior": limite_atual,
                    "limite_novo": novo_limite
                }
                # Atualiza o credito no arquivo de clientes.
                atualiza_credito_cliente(cpf, novo_limite)

                # Além de reescrever o arquivo, precisa atualizar o contexto lido inicialmente.
                tool_context.state["user_limite_credito"] = novo_limite


            # Registrar solicitação aprovada/rejeitada/pendente no CSV de solicitações
            if csv_solicitacoes_path:
                try:
                    with open(csv_solicitacoes_path, mode='a', encoding='utf-8', newline='') as arquivo_solicitacoes:
                        escritor = csv.writer(arquivo_solicitacoes)
                        
                        # Se o arquivo está vazio, escrever cabeçalho
                        if os.path.getsize(csv_solicitacoes_path) == 0:
                            escritor.writerow(['cpf', 'data_hora_solicitacao', 'limite_atual', 'novo_limite_solicitado', 'status_pedido'])
                        
                        cpf = ''.join(filter(str.isdigit, cpf))
                        cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}/{cpf[9:]}"
                        escritor.writerow([
                            cpf_formatado,
                            datetime.datetime.now().isoformat(),
                            limite_atual,
                            novo_limite,
                            status_pedido
                        ])
                except Exception as e:
                    # Mesmo se falhar o registro, continua com a aprovação
                    pass
            
            return mensagem_pedido
            
    except FileNotFoundError:
        return {"status": "error", "mensagem": "Arquivo de limites por score não encontrado."}
    
    except Exception as e:
        return {"status": "error", "mensagem": f"Erro ao processar solicitação: {str(e)}"}    


