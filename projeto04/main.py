import os
import json
import re
from dotenv import load_dotenv
from tools import calcular_idade, converter_temperatura, calcular_imc, gerar_senha, data_atual
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

ARQUIVO_HISTORICO = os.path.join(os.path.dirname(__file__), "historico.json")
LIMITE_MENSAGENS = 10


def get_system_prompt():
    return f"""Você é o Byte, um assistente virtual inteligente, simpático e direto ao ponto.
Seu estilo é descontraído mas profissional — você usa linguagem clara, ocasionalmente informal,
e sempre tenta ser útil com um toque de bom humor. Você é honesto quando não sabe algo.

A data de hoje é {data_atual()}. Use essa informação sempre que o usuário perguntar sobre a data atual.

Quando o usuário pedir para calcular idade, converter temperatura, calcular IMC ou gerar senha,
você DEVE retornar uma linha especial no seguinte formato (antes da sua resposta normal):
  [FUNÇÃO: nome_da_função | parametros em linguagem natural]

Funções disponíveis:
- calcular_idade: quando pedir idade a partir de data de nascimento (ex: "nascido em 1990-05-15")
- converter_temperatura: quando pedir conversão de temperatura (ex: "25 celsius para fahrenheit")
- calcular_imc: quando pedir cálculo de IMC (ex: "peso 70kg altura 1.75")
- gerar_senha: quando pedir geração de senha (ex: "senha de 12 caracteres")

Exemplo de uso:
  Usuário: "Qual minha idade se nasci em 1995-03-20?"
  Você responde: [FUNÇÃO: calcular_idade | data_nascimento=1995-03-20]
  Claro! Deixa eu calcular...
"""


def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_historico(historico):
    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


def limitar_historico(historico):
    if len(historico) > LIMITE_MENSAGENS:
        historico = historico[-LIMITE_MENSAGENS:]
    return historico


def detectar_e_executar_funcao(resposta_llm):
    """Detecta chamada de função na resposta do LLM e executa."""
    padrao = r"\[FUNÇÃO:\s*(\w+)\s*\|(.*?)\]"
    match = re.search(padrao, resposta_llm)

    if not match:
        return None, resposta_llm

    nome_funcao = match.group(1).strip()
    params_str = match.group(2).strip()

    resposta_limpa = re.sub(padrao, "", resposta_llm).strip()

    resultado = None
    try:
        params = dict(p.strip().split("=") for p in params_str.split(",") if "=" in p)

        if nome_funcao == "calcular_idade":
            resultado = calcular_idade(params.get("data_nascimento", ""))
        elif nome_funcao == "converter_temperatura":
            valor = float(params.get("valor", 0))
            escala_origem = params.get("escala_origem", "celsius").lower()
            escala_destino = params.get("escala_destino", "fahrenheit").lower()
            resultado = converter_temperatura(valor, escala_origem, escala_destino)
        elif nome_funcao == "calcular_imc":
            peso = float(params.get("peso", 0))
            altura = float(params.get("altura", 0))
            resultado = calcular_imc(peso, altura)
        elif nome_funcao == "gerar_senha":
            tamanho = int(params.get("tamanho", 12))
            resultado = gerar_senha(tamanho)
    except Exception as e:
        resultado = f"Erro ao executar função: {e}"

    return resultado, resposta_limpa


def chat(historico, pergunta):
    historico.append({"role": "user", "content": pergunta})
    historico = limitar_historico(historico)

    mensagens_com_sistema = [{"role": "system", "content": get_system_prompt()}] + historico

    resposta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=mensagens_com_sistema
    )

    conteudo = resposta.choices[0].message.content
    resultado_funcao, conteudo_limpo = detectar_e_executar_funcao(conteudo)

    if resultado_funcao is not None:
        conteudo_final = f"{conteudo_limpo}\n\n📊 **Resultado:** {resultado_funcao}"
    else:
        conteudo_final = conteudo_limpo

    historico.append({"role": "assistant", "content": conteudo_final})
    salvar_historico(historico)
    return conteudo_final, historico


def main():
    historico = carregar_historico()

    print("=" * 50)
    print("       🤖 Byte — Assistente Virtual")
    print("=" * 50)
    print("Comandos: /limpar para apagar histórico | sair para encerrar")

    if historico:
        print(f"📂 Histórico carregado ({len(historico)} mensagens anteriores)\n")
    else:
        print("💬 Nova conversa iniciada!\n")

    while True:
        try:
            pergunta = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté mais!")
            break

        if not pergunta:
            continue

        if pergunta.lower() in ["sair", "exit", "quit"]:
            print("Byte: Até mais! Foi um prazer conversar 👋")
            break

        if pergunta.lower() == "/limpar":
            historico = []
            salvar_historico(historico)
            print("Byte: Memória da conversa apagada.\n")
            continue

        resposta, historico = chat(historico, pergunta)
        print(f"Byte: {resposta}\n")


if __name__ == "__main__":
    main()