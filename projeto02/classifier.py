from llm_client import gerar_resposta
from validator import parse_json, validar_categoria, fallback

CATEGORIAS = ["Suporte", "Vendas", "Financeiro", "Geral"]

def classificar_mensagem(mensagem, temperature=0.2):
    prompt = f"""
        Você é um classificador.
        Classifique a mensagem abaixo em UMA das categorias permitidas.

        Categorias permitidas:
        {', '.join(CATEGORIAS)}

        Regras:
        - Responda SOMENTE com JSON válido
        - Não inclua texto fora do JSON
        - Não invente categorias

        Formato esperado:
        {{
         "categoria": "Suporte | Vendas | Financeiro | Geral"
        }}

        Mensagem: "{mensagem}"
    """

    resposta_llm = gerar_resposta(prompt, temperature)

    dados = parse_json(resposta_llm)

    if not validar_categoria(dados):
        return fallback()

    return dados