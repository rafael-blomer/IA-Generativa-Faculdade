from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")


def gerar_resposta(prompt, temperature):
    resposta = client.responses.create(
        model="openai/gpt-oss-20b",
        temperature=temperature,
        input=prompt
    )

    return resposta.output_text