import json
from dotenv import load_dotenv
from llm_client import LLMClient
from retriever import (
    load_conhecimento,
    build_vector_store,
    embed_query,
    similarity_search,
)
from validator import validate_injection, SAFE_REFUSAL
from prompt import build_system_prompt, build_user_prompt

load_dotenv()


def main():
    provider = input("Escolha o provedor (openai/groq): ").strip().lower()
    client = LLMClient(provider=provider)

    # ------------------------------------------------------------------
    # PARTE 1 — Embeddings: carrega, chunkiza, gera vetores, salva em memória
    # ------------------------------------------------------------------
    print("\n[Main] Carregando e indexando conhecimento...\n")
    conhecimento = load_conhecimento()
    store = build_vector_store(conhecimento, client.client, provider)
    print(f"[Main] Pronto. {len(store)} chunks indexados.\n")

    system_prompt = build_system_prompt()

    while True:
        query = input("Digite sua pergunta (ou 'sair' para encerrar): ").strip()
        if query.lower() == "sair":
            break

        # ------------------------------------------------------------------
        # PARTE 2 — Proteção: detecta prompt injection antes de qualquer coisa
        # ------------------------------------------------------------------
        if validate_injection(query):
            print(f"\nAssistente: {SAFE_REFUSAL}\n")
            continue

        # ------------------------------------------------------------------
        # PARTE 1 — Embeddings: embed da query + busca por similaridade
        # ------------------------------------------------------------------
        query_embedding = embed_query(query, client.client, provider)
        retrieved_chunks = similarity_search(query_embedding, store, top_k=3)

        for i, chunk in enumerate(retrieved_chunks, 1):
            print(f"  [{i}] score={chunk['score']:.4f} | '{chunk['text'][:70]}...'")

        user_prompt = build_user_prompt(query, retrieved_chunks)
        response_text = client.generate_text(system_prompt, user_prompt)

        try:
            data = json.loads(response_text)
            if "status" not in data:
                raise ValueError("Campo 'status' obrigatório")
            print(f"\nAssistente: {data['resposta']}\n")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Erro de validação: {e}")


if __name__ == "__main__":
    main()
