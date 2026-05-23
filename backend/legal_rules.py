import unicodedata


KEYWORD_SEARCH_TERMS = {
    "violación": [
        "violacion",
        "victima",
        "asesoria juridica",
        "reparacion integral",
        "derechos humanos",
    ],
    "familiar": ["ascendiente", "descendiente", "hermano", "tutor", "custodia"],
    "menor": ["menor", "quince años"],
    "violencia": ["violencia"],
    "inconsciente": ["no tenga la capacidad", "no pueda resistirlo"],
    "amenaza": ["violencia moral"],
    "medida de protección": [
        "medida de proteccion",
        "medidas de proteccion",
        "medidas cautelares",
    ],
    "audiencia": ["audiencia"],
    "asesoría jurídica": ["asesoria juridica"],
    "reparación integral": ["reparacion integral"],
    "debido proceso": ["debido proceso"],
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
            article.get("source_name") or "",
        ]
    )


def classify_article(article: dict) -> str:
    source_name = normalize_text(article.get("source_name") or "")
    article_text = normalize_text(get_article_search_text(article))

    if "codigo nacional de procedimientos penales" in source_name:
        return "fundamento_procesal"
    if "ley general de victimas" in source_name:
        return "derecho_victima"
    if "constitucion" in source_name:
        return "fundamento_constitucional"
    if "codigo penal" in source_name:
        if "agravante" in article_text or "aumentaran" in article_text:
            return "agravante"
        if "equiparada" in article_text:
            return "violacion_equiparada"
        if "violacion" in article_text:
            return "tipo_penal_base"

    if "agravante" in article_text or "aumentaran" in article_text:
        return "agravante"
    if "equiparada" in article_text:
        return "violacion_equiparada"
    if "violacion" in article_text:
        return "tipo_penal_base"
    return "otro"


def build_search_result(article: dict, match_reason: str) -> dict:
    return {
        "article_number": article["article_number"],
        "content": article["content"],
        "source_name": article["source_name"],
        "content_hash": article.get("content_hash"),
        "source_version": article.get("source_version"),
        "last_reform_date": article.get("last_reform_date"),
        "classification": classify_article(article),
        "match_reason": match_reason,
    }


def search_local_articles(query: str, articles: list[dict]) -> list[dict]:
    normalized_query = normalize_text(query)
    results = []

    for article in articles:
        if normalized_query in normalize_text(get_article_search_text(article)):
            results.append(
                build_search_result(
                    article,
                    "Coincidencia simple por texto en el artículo.",
                )
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

    candidates_by_key = {}
    for term in search_terms:
        for result in search_local_articles(term, articles):
            candidate_key = (
                result["source_name"],
                result["article_number"],
                result.get("content_hash"),
            )
            candidates_by_key.setdefault(candidate_key, result)

    return list(candidates_by_key.values())


def group_candidate_articles(candidate_articles: list[dict]) -> dict:
    grouped_articles = {
        "penal_articles": [],
        "procedural_foundations": [],
        "victim_rights": [],
        "constitutional_foundations": [],
        "human_review_warnings": [],
    }

    for article in candidate_articles:
        classification = article["classification"]

        if classification in {"tipo_penal_base", "agravante", "violacion_equiparada"}:
            grouped_articles["penal_articles"].append(article)
        elif classification == "fundamento_procesal":
            grouped_articles["procedural_foundations"].append(article)
        elif classification == "derecho_victima":
            grouped_articles["victim_rights"].append(article)
        elif classification == "fundamento_constitucional":
            grouped_articles["constitutional_foundations"].append(article)

    grouped_articles["human_review_warnings"] = build_human_review_warnings(grouped_articles)
    return grouped_articles


def build_human_review_warnings(grouped_articles: dict) -> list[str]:
    warnings = [
        "Este análisis es determinista y debe ser revisado por una persona abogada.",
    ]

    if grouped_articles["penal_articles"] and not grouped_articles["procedural_foundations"]:
        warnings.append("Hay posibles artículos penales sin fundamento procesal relacionado.")
    if grouped_articles["penal_articles"] and not grouped_articles["victim_rights"]:
        warnings.append("Hay posibles artículos penales sin derechos de víctima relacionados.")

    return warnings


def analyze_facts_deterministically(facts: str, articles: list[dict]) -> dict:
    detected_topics = detect_legal_topics(facts)
    candidate_articles = build_candidate_articles(facts, articles)

    return {
        "facts_summary": summarize_facts(facts),
        "detected_legal_topics": detected_topics,
        "candidate_articles": group_candidate_articles(candidate_articles),
        "missing_questions": build_missing_questions(detected_topics),
        "human_review_required": True,
    }
