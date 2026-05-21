import unicodedata


KEYWORD_SEARCH_TERMS = {
    "violación": ["violacion"],
    "familiar": ["ascendiente", "descendiente", "hermano", "tutor", "custodia"],
    "menor": ["menor", "quince años"],
    "violencia": ["violencia"],
    "inconsciente": ["no tenga la capacidad", "no pueda resistirlo"],
    "amenaza": ["violencia moral"],
}


def normalize_text(value: str) -> str:
    value = value.casefold()
    normalized = unicodedata.normalize("NFD", value)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def get_article_search_text(article: dict) -> str:
    return " ".join(
        [
            article.get("article_number") or "",
            article.get("title") or "",
            article.get("content") or "",
        ]
    )


def classify_article(article: dict) -> str:
    article_text = normalize_text(get_article_search_text(article))

    if "agravante" in article_text or "aumentaran" in article_text:
        return "agravante"
    if "equiparada" in article_text:
        return "violacion_equiparada"
    if "violacion" in article_text:
        return "tipo_penal_base"
    return "otro"


def search_local_articles(query: str, articles: list[dict]) -> list[dict]:
    normalized_query = normalize_text(query)
    results = []

    for article in articles:
        if normalized_query in normalize_text(get_article_search_text(article)):
            results.append(
                {
                    "article_number": article["article_number"],
                    "content": article["content"],
                    "source_name": article["source_name"],
                    "classification": classify_article(article),
                    "match_reason": "Coincidencia simple por texto en el artículo.",
                }
            )

    return results


def detect_legal_topics(facts: str) -> list[str]:
    normalized_facts = normalize_text(facts)
    detected_topics = []

    for keyword in KEYWORD_SEARCH_TERMS:
        if normalize_text(keyword) in normalized_facts:
            detected_topics.append(keyword)

    return detected_topics


def summarize_facts(facts: str, max_length: int = 240) -> str:
    clean_facts = " ".join(facts.split())
    if len(clean_facts) <= max_length:
        return clean_facts
    return clean_facts[: max_length - 3].rstrip() + "..."


def build_missing_questions(detected_topics: list[str]) -> list[str]:
    questions = []

    if "violencia" not in detected_topics and "amenaza" not in detected_topics:
        questions.append("¿Se usó violencia física, violencia moral o amenazas?")
    if "menor" not in detected_topics:
        questions.append("¿La víctima era menor de quince años?")
    if "inconsciente" not in detected_topics:
        questions.append("¿La víctima podía comprender el significado del hecho y resistirlo?")
    if "familiar" not in detected_topics:
        questions.append("¿Existe relación familiar, custodia, guarda, educación o autoridad?")

    return questions


def build_candidate_articles(facts: str, articles: list[dict]) -> list[dict]:
    detected_topics = detect_legal_topics(facts)
    search_terms = []

    for topic in detected_topics:
        search_terms.extend(KEYWORD_SEARCH_TERMS[topic])

    if not search_terms:
        search_terms = [facts]

    candidates_by_article = {}
    for term in search_terms:
        for result in search_local_articles(term, articles):
            article_number = result["article_number"]
            candidates_by_article.setdefault(article_number, result)

    return list(candidates_by_article.values())


def analyze_facts_deterministically(facts: str, articles: list[dict]) -> dict:
    detected_topics = detect_legal_topics(facts)

    return {
        "facts_summary": summarize_facts(facts),
        "detected_legal_topics": detected_topics,
        "candidate_articles": build_candidate_articles(facts, articles),
        "missing_questions": build_missing_questions(detected_topics),
        "human_review_required": True,
    }
