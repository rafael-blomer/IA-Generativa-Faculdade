import re


# ---------------------------------------------------------------------------
# CAMADA 1 — HEURÍSTICA (regex + keywords)
# ---------------------------------------------------------------------------

_INJECTION_PATTERNS = [
    r"(me\s+diga|revele?|mostre?|exiba|imprima?|repita?|escreva?)\s.*(system\s*prompt|instru[cç][aã]o|contexto\s+interno|prompt\s+base|configura[cç][aã]o)",
    r"(qual|quais)\s+(é|são|foi|foram|seria|seriam)?\s*(a|as|o|os|sua|suas)?\s*(system\s*prompt|instru[cç][aã]o\s+inicial|prompt\s+original)",
    r"ignore\s+(todas?\s+as?\s+)?(instru[cç][õo]es|regras|comandos|restri[cç][õo]es)",
    r"(forget|ignore|disregard|bypass|override)\s+(your\s+)?(previous\s+)?(instructions?|rules?|guidelines?|constraints?|system)",
    r"agora\s+(voc[eê]\s+[eé]|aja\s+como|comporte.se\s+como|finja\s+ser)",
    r"(novo|diferente)\s+(papel|role|persona|personagem|modo|comportamento)",
    r"(print|output|display|show|tell\s+me)\s+(your\s+)?(system\s*prompt|hidden\s+instructions?|context|internal)",
    r"jailbreak",
    r"DAN\s*(mode|modo)?",
    r"modo?\s+DAN",
    r"(estava|era|finja|simule?|pretend)\s+(que\s+)?(voc[eê]\s+)?(n[aã]o\s+tem|sem)\s+(restri[cç][õo]es|limites|regras|filtros)",
    r"prompt\s+injection",
    r"(revele?|exponha?|mostre?)\s+(seu|seus|suas?)\s+(dados?\s+internos?|configura[cç][õo]es?|sistema|instruç[õo]es?)",
    r"o\s+que\s+(est[aá]\s+escrito|diz|consta|tem)\s+(na|na\s+sua|em\s+sua)\s+system\s*prompt",
    r"(repita?|copie?|transcreva?)\s+(tudo\s+)?(o\s+que\s+)?(est[aá]\s+)?(acima|antes|anterior|no\s+contexto)",
    r"translate\s+your\s+(instructions?|system\s*prompt)",
    r"(act|behave)\s+as\s+(if\s+you\s+(are|have\s+no)|a\s+different)",
]

_COMPILED_PATTERNS = [
    re.compile(p, re.IGNORECASE | re.UNICODE) for p in _INJECTION_PATTERNS
]

_HIGH_RISK_KEYWORDS = {
    "system prompt",
    "systemprompt",
    "system_prompt",
    "instrução inicial",
    "instrucao inicial",
    "prompt original",
    "prompt base",
    "ignore instructions",
    "ignore your instructions",
    "ignore as instruções",
    "ignore suas instruções",
    "jailbreak",
    "dan mode",
    "modo dan",
    "prompt injection",
}

# Resposta segura — não vaza nenhuma informação interna
SAFE_REFUSAL = (
    "⚠️ Não consigo processar essa solicitação. "
    "Posso te ajudar com dúvidas sobre reembolsos, prazos e políticas da loja. "
    "Como posso te ajudar?"
)


def validate_injection(query: str) -> bool:
    """
    Verifica se a mensagem é uma tentativa de prompt injection.

    Retorna True se for injeção (bloquear), False se for mensagem legítima.

    Estratégia:
      - Camada 1: keywords de alto risco (sem custo)
      - Camada 2: regex patterns (sem custo)
    """
    query_lower = query.lower()

    # Camada 1 — keywords diretas
    for kw in _HIGH_RISK_KEYWORDS:
        if kw in query_lower:
            print(f"[Validator] ⛔ Injeção detectada (keyword): '{query[:80]}'")
            return True

    # Camada 2 — regex patterns
    for pattern in _COMPILED_PATTERNS:
        if pattern.search(query):
            print(f"[Validator] ⛔ Injeção detectada (regex): '{query[:80]}'")
            return True

    return False
