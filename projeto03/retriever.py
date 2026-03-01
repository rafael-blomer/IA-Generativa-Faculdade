import os
import re
import math
import hashlib
from openai import OpenAI
from groq import Groq


def load_conhecimento(path="projeto03/conhecimento/conhecimento.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_conhecimento(
    conhecimento: str, chunk_size: int = 400, overlap: int = 80
) -> list[str]:
    """
    Divide o conhecimento em chunks por seções numeradas.
    Aplica sliding window com overlap para não perder contexto entre seções longas.
    """
    sections = re.split(r"\n(?=\d+\.)", conhecimento)
    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        if len(section) <= chunk_size:
            chunks.append(section)
        else:
            words = section.split()
            window = []
            char_count = 0

            for word in words:
                window.append(word)
                char_count += len(word) + 1

                if char_count >= chunk_size:
                    chunks.append(" ".join(window))
                    overlap_words = window[-(overlap // 6) :]
                    window = overlap_words
                    char_count = sum(len(w) + 1 for w in window)

            if window:
                chunks.append(" ".join(window))

    return chunks


# ---------------------------------------------------------------------------
# ARMAZENAMENTO EM MEMÓRIA
# ---------------------------------------------------------------------------


class VectorStore:
    """Armazena chunks e seus embeddings em memória (lista Python, sem banco externo)."""

    def __init__(self):
        self._store: list[dict] = []  # [{"text": str, "embedding": list[float]}]

    def add_all(self, embedded_chunks: list[dict]) -> None:
        self._store = embedded_chunks
        print(f"[VectorStore] {len(self._store)} vetores armazenados em memória.")

    def get_all(self) -> list[dict]:
        return self._store

    def __len__(self):
        return len(self._store)


# ---------------------------------------------------------------------------
# EMBEDDING LOCAL (usado pelo Groq, que não tem endpoint de embeddings)
# ---------------------------------------------------------------------------


def _embed_text_local(text: str) -> list[float]:
    """
    Gera embedding local via TF-IDF + hashing de tokens.
    Não depende de nenhuma API externa — usado quando o provider é Groq.

    Produz um vetor de 512 dimensões normalizado (norma unitária),
    compatível com cosine similarity.
    """
    tokens = re.findall(r"[a-záàãâéêíóôõúüçñ]+", text.lower())

    freq: dict[int, float] = {}
    for token in tokens:
        idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % 512
        freq[idx] = freq.get(idx, 0.0) + 1.0

    if not freq:
        return [0.0] * 512

    norm = math.sqrt(sum(v * v for v in freq.values()))
    vector = [0.0] * 512
    for idx, val in freq.items():
        vector[idx] = val / norm

    return vector


# ---------------------------------------------------------------------------
# GERAÇÃO DE EMBEDDINGS
# ---------------------------------------------------------------------------


def generate_embeddings(chunks: list[str], client, provider: str) -> list[dict]:
    """
    Gera embeddings para cada chunk.
    - OpenAI → client.embeddings.create (text-embedding-3-small)
    - Groq   → embedding local via TF-IDF + hashing (sem dependência de API externa)
    """
    results = []
    print(f"[Retriever] Gerando embeddings para {len(chunks)} chunks...")

    for i, text in enumerate(chunks):
        if provider == "openai":
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            vector = response.data[0].embedding

        elif provider == "groq":
            vector = _embed_text_local(text)

        results.append({"text": text, "embedding": vector})
        print(f"  → Chunk {i} embedado ({len(vector)} dims)")

    print(f"[Retriever] {len(results)} embeddings prontos.\n")
    return results


# ---------------------------------------------------------------------------
# BUSCA POR SIMILARIDADE (Cosine Similarity)
# ---------------------------------------------------------------------------


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    cos(θ) = (A · B) / (||A|| × ||B||)
    Implementado em Python puro, sem dependências externas.
    """
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


def similarity_search(
    query_embedding: list[float], store: VectorStore, top_k: int = 3
) -> list[dict]:
    """
    Busca os top_k chunks mais similares ao vetor da query.
    Retorna lista de dicts com 'text' e 'score', ordenada por score desc.
    """
    scored = [
        {
            "text": item["text"],
            "score": _cosine_similarity(query_embedding, item["embedding"]),
        }
        for item in store.get_all()
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


# ---------------------------------------------------------------------------
# PIPELINE: build store + embed query
# ---------------------------------------------------------------------------


def build_vector_store(conhecimento: str, client, provider: str) -> VectorStore:
    """Chunkiza → gera embeddings → armazena em memória. Retorna VectorStore pronto."""
    chunks = chunk_conhecimento(conhecimento)
    embedded = generate_embeddings(chunks, client, provider)

    store = VectorStore()
    store.add_all(embedded)
    return store


def embed_query(query: str, client, provider: str) -> list[float]:
    """Gera o embedding de uma query do usuário."""
    if provider == "openai":
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query,
        )
        return response.data[0].embedding

    elif provider == "groq":
        return _embed_text_local(query)
