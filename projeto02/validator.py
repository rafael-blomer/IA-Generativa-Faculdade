import json

CATEGORIAS_PERMITIDAS = {"Suporte", "Vendas", "Financeiro", "Geral"}

def parse_json(resposta_llm: str):
    try:
        return json.loads(resposta_llm)
    except json.JSONDecodeError:
        return None


def validar_categoria(dados: dict):
    if not dados or "categoria" not in dados:
        return False

    return dados["categoria"] in CATEGORIAS_PERMITIDAS


def fallback():
    return {
        "categoria": "Geral",
        "fallback": True
    }