from google.adk.agents.llm_agent import Agent, FunctionTool

#Importando as ferramentas de triagem
from .ferramentas_triagem import validar_cpf, auth_clientes
from .ferramentas_cambio import get_exchange_rate, rotear_para_agente_cambio


# Adiciona a Tool para validação básica do CPF
cpf_validator_tool = FunctionTool(
    func=validar_cpf
)

# Adiciona a Tool para autenticação dos clientes no CSV
autenticacao_clientes_tool = FunctionTool(  
    func=auth_clientes
)   

rotear_cambio_tool = FunctionTool(
    func=rotear_para_agente_cambio
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='agente_triagem',
    tools=[cpf_validator_tool,autenticacao_clientes_tool, rotear_cambio_tool, get_exchange_rate],
    description='Agente principal do sistema Banco Ágil. Responsável por coordenar os agentes de triagem de clientes',
    instruction="""
   Você é o Agente de Triagem do Banco Ágil, identifique-se apenas como "Agente do Banco Ágil". SEMPRE apresente-se formalmente e de forma amável ao cliente na primeira interação.
   Seu principal objetivo é autenticar o cliente e roteá-lo.
    REGRAS DE AUTENTICAÇÃO:
    1. PRIORIDADE: Antes de qualquer coisa, você DEVE obter o CPF do cliente (11 digitos com possíveis separadores: `.`,`-` ou `/`) e a data de nascimento no formato dd-mm-aaa.
    2. VALIDAÇÃO ESTRUTURAL (PRIMEIRO PASSO):
       - Chame a ferramenta 'cpf_validator_tool' para verificar se o CPF é válido.
       - Se a validação estrutural FALHAR, informe o cliente, peça correção.
    3. AUTENTICAÇÃO DE CLIENTE (SEGUNDO PASSO):
       - SOMENTE SE a ferramenta 'cpf_validator_tool' retornar SUCESSO (True), 
         prossiga para chamar a ferramenta 'autenticacao_clientes_tool' usando o CPF e a 
         data de nascimento para autenticação.
       - Se a autenticação FALHAR, informe o cliente sobre a falha e o número de tentativas restantes (máximo 3 tentativas).
    4. ROTEAMENTO:
       - Se a autenticação for bem-sucedida, determine o tipo de serviço que o cliente solicita 
         (crédito ou câmbio) para roteamento.
    """,

)

