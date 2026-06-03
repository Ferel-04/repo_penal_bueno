import unicodedata

from article_map import get_mapped_articles
from crime_catalog import detect_crime_type
from crime_classifier import classify_crime_type, get_crime_display_name, get_crime_subtype
from investigation_steps import get_investigation_steps


KEYWORD_SEARCH_TERMS = {
    "violación": [
        "violacion",
        "copula",
        "abuso sexual",
        "violacion equiparada",
    ],
    "familiar": ["ascendiente", "descendiente", "tutor", "custodia"],
    "menor": ["menor de quince", "menor de edad", "menor de dieciocho"],
    "violencia": [
        "violencia fisica",
        "violencia psicologica",
        "violencia contra la victima",
        "victima de violencia",
    ],
    "inconsciente": ["no tenga la capacidad", "no pueda resistirlo", "privada de razon"],
    "amenaza": [
        "amenaza a la victima",
        "amenazas graves",
    ],
    "medida de protección": [
        "medida de proteccion",
        "orden de proteccion",
        "medidas de proteccion para la victima",
    ],
    "asesoría jurídica": [
        "asesor juridico de la victima",
        "asesor juridico victimal",
    ],
    "reparación integral": [
        "reparacion integral del dano",
        "reparacion a la victima",
    ],
    "debido proceso": ["debido proceso", "garantias procesales"],
    "audiencia": ["audiencia inicial", "audiencia de formulacion"],
}


def normalize_text(value: str) -> str:
    value = value.casefold()
    normalized = unicodedata.normalize("NFD", value)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def contains_any(value: str, terms: list[str]) -> bool:
    return any(normalize_text(term) in value for term in terms)


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
    legal_domain = normalize_text(article.get("legal_domain") or "")
    applicability_type = normalize_text(article.get("applicability_type") or "")

    if "codigo nacional de procedimientos penales" in source_name:
        return "fundamento_procesal"
    if "ley general de victimas" in source_name:
        return "derecho_victima"
    if "constitucion" in source_name:
        return "fundamento_constitucional"

    if "codigo penal" in source_name:
        if applicability_type in {"agravante", "violacion_equiparada",
                                   "tipo_penal_base", "fundamento_procesal",
                                   "derecho_victima", "fundamento_constitucional"}:
            return applicability_type
        content = normalize_text(article.get("content") or "")
        if "se equipara" in content and "violacion" in content:
            return "violacion_equiparada"
        if "se equipara" in content and "robo" in content:
            return "tipo_penal_base"
        if "violencia familiar" in article_text:
            return "tipo_penal_base"
        if any(t in content for t in ["agravante", "se aumentara", "se aumentaran"]):
            return "agravante"
        if "violacion" in content:
            return "tipo_penal_base"
        if "lesiones" in content or "dano en la salud" in content:
            return "tipo_penal_base"
        if "homicidio" in content or "privar de la vida" in content:
            return "tipo_penal_base"
        if "robo" in content or "apoderamiento" in content:
            return "tipo_penal_base"
        return "otro"

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


def detect_topics_from_text(facts: str, crime_type: str) -> list[str]:
    from crime_catalog import get_crime_catalog_entry

    normalized = normalize_text(facts)
    entry = get_crime_catalog_entry(crime_type)
    topics = []

    if crime_type == "violacion":
        topics.append("violación")

    violence_keywords = [
        "golpe",
        "golpeo",
        "golpeó",
        "agredió",
        "agredio",
        "ataco",
        "atacó",
        "empujo",
        "empujó",
        "forcejeo",
        "sometio",
        "sometió",
        "lesiono",
        "lesionó",
        "hiero",
        "hirió",
        "golpiza",
    ]
    if contains_any(normalized, violence_keywords):
        topics.append("violencia")

    threat_keywords = [
        "amenaza",
        "amenazo",
        "amenazó",
        "amenazan",
        "matar",
        "lastimar",
        "dano",
        "daño",
    ]
    if contains_any(normalized, threat_keywords):
        topics.append("amenaza")

    return topics


def detect_legal_topics(
    facts: str,
    structured_facts: dict | None = None,
    crime_type: str = "unknown",
) -> list[str]:
    normalized_facts = normalize_text(facts)
    detected_topics = []

    for keyword in KEYWORD_SEARCH_TERMS:
        if normalize_text(keyword) in normalized_facts:
            detected_topics.append(keyword)

    for topic in topics_from_structured_facts(structured_facts, crime_type):
        if topic not in detected_topics:
            detected_topics.append(topic)

    if structured_facts is None:
        for topic in detect_topics_from_text(facts, crime_type):
            if topic not in detected_topics:
                detected_topics.append(topic)

    detected_topics = apply_structured_topic_overrides(detected_topics, structured_facts)

    if crime_type == "violencia_familiar" and "menor" in detected_topics:
        sf = structured_facts or {}
        victim_age = normalize_text(sf.get("victim_age_group") or "")
        if "menor" not in victim_age and "nina" not in victim_age and "nino" not in victim_age:
            detected_topics = [t for t in detected_topics if t != "menor"]

    return detected_topics


def apply_structured_topic_overrides(
    detected_topics: list[str],
    structured_facts: dict | None,
) -> list[str]:
    if not structured_facts:
        return detected_topics

    victim_age_group = normalize_text(structured_facts.get("victim_age_group") or "")
    relationship = normalize_text(structured_facts.get("relationship_to_aggressor") or "")
    filtered_topics = list(detected_topics)

    if victim_age_group == "adulto" and "menor" in filtered_topics:
        filtered_topics.remove("menor")
    if relationship.startswith("sin relacion") and "familiar" in filtered_topics:
        filtered_topics.remove("familiar")

    return filtered_topics


def topics_from_structured_facts(
    structured_facts: dict | None,
    crime_type: str = "unknown",
) -> list[str]:
    if not structured_facts:
        return []

    topics = []
    explicit_crime = normalize_text(structured_facts.get("explicit_crime_mentioned") or "")
    victim_age_group = normalize_text(structured_facts.get("victim_age_group") or "")
    relationship = normalize_text(structured_facts.get("relationship_to_aggressor") or "")

    if structured_facts.get("sexual_conduct_detected") or "violacion" in explicit_crime:
        topics.append("violación")
    if "menor" in victim_age_group or "nina" in victim_age_group or "nino" in victim_age_group:
        topics.append("menor")
    if relationship and not relationship.startswith("sin relacion"):
        topics.append("familiar")
    if structured_facts.get("violence_detected"):
        topics.append("violencia")
    if structured_facts.get("threat_detected"):
        topics.append("amenaza")
    if structured_facts.get("unconscious_detected") or structured_facts.get("unable_to_resist_detected"):
        topics.append("inconsciente")

    valid_topics_by_crime = {
        "violacion": {"violación", "menor", "familiar", "violencia", "amenaza", "inconsciente"},
        "robo": {"violencia", "amenaza"},
        "lesiones": {"violencia", "amenaza"},
        "homicidio": {"violencia", "amenaza"},
        "violencia_familiar": {"violencia", "amenaza", "familiar", "menor"},
        "fraude": set(),
        "unknown": {"violación", "menor", "familiar", "violencia", "amenaza", "inconsciente"},
    }

    valid_topics = valid_topics_by_crime.get(crime_type, valid_topics_by_crime["unknown"])
    filtered_topics = [topic for topic in topics if topic in valid_topics]

    return filtered_topics


def summarize_facts(facts: str, max_length: int = 240) -> str:
    clean_facts = " ".join(facts.split())
    if len(clean_facts) <= max_length:
        return clean_facts
    return clean_facts[: max_length - 3].rstrip() + "..."


def build_missing_questions(
    detected_topics: list[str],
    structured_facts: dict | None = None,
    crime_type: str = "unknown",
) -> list[str]:
    questions = []
    victim_age_group = normalize_text((structured_facts or {}).get("victim_age_group") or "")
    relationship = normalize_text((structured_facts or {}).get("relationship_to_aggressor") or "")

    if "violencia" not in detected_topics and "amenaza" not in detected_topics:
        questions.append("¿Se usó violencia física, violencia moral o amenazas?")
    if "menor" not in detected_topics and not victim_age_group:
        questions.append("¿La víctima era menor de quince años?")
    if crime_type in {"violacion", "unknown"}:
        if "inconsciente" not in detected_topics:
            questions.append(
                "¿La víctima podía comprender el significado del hecho y resistirlo?"
            )
    if "familiar" not in detected_topics and not relationship:
        questions.append("¿Existe relación familiar, custodia, guarda, educación o autoridad?")

    return questions


def build_candidate_articles(
    facts: str,
    articles: list[dict],
    detected_topics: list[str] | None = None,
    crime_type: str = "unknown",
) -> list[dict]:
    grouped = get_mapped_articles(crime_type, articles)
    flat_list = []
    for group_key in ("penal_articles", "procedural_foundations", "victim_rights", "constitutional_foundations"):
        flat_list.extend(grouped.get(group_key, []))
    return flat_list


def group_candidate_articles(
    candidate_articles: list[dict],
    crime_type: str = "unknown",
) -> dict:
    grouped = {
        "penal_articles": [],
        "procedural_foundations": [],
        "victim_rights": [],
        "constitutional_foundations": [],
        "human_review_warnings": [],
    }
    for article in candidate_articles:
        classification = article.get("classification", "otro")
        if classification in {"tipo_penal_base", "agravante", "violacion_equiparada", "otro"}:
            source_name = normalize_text(article.get("source_name") or "")
            if "codigo penal" in source_name:
                grouped["penal_articles"].append(article)
            elif "codigo nacional" in source_name:
                grouped["procedural_foundations"].append(article)
            elif "victimas" in source_name:
                grouped["victim_rights"].append(article)
            elif "constitucion" in source_name:
                grouped["constitutional_foundations"].append(article)
        elif classification == "fundamento_procesal":
            grouped["procedural_foundations"].append(article)
        elif classification == "derecho_victima":
            grouped["victim_rights"].append(article)
        elif classification == "fundamento_constitucional":
            grouped["constitutional_foundations"].append(article)

    grouped["human_review_warnings"] = [
        "Este análisis es determinista y debe ser revisado por una persona abogada.",
    ]
    if grouped["penal_articles"] and not grouped["procedural_foundations"]:
        grouped["human_review_warnings"].append("Hay posibles artículos penales sin fundamento procesal relacionado.")
    if grouped["penal_articles"] and not grouped["victim_rights"]:
        grouped["human_review_warnings"].append("Hay posibles artículos penales sin derechos de víctima relacionados.")
    return grouped


def analyze_facts_deterministically(
    facts: str,
    articles: list[dict],
    structured_facts: dict | None = None,
    analysis_engine: str = "deterministic_fallback",
    crime_type: str | None = None,
) -> dict:
    if crime_type is None:
        crime_type = classify_crime_type(facts, structured_facts)
    
    crime_subtype = get_crime_subtype(crime_type, structured_facts)
    crime_display_name = get_crime_display_name(crime_type)
    investigation_steps = get_investigation_steps(crime_type, structured_facts)
    
    detected_topics = detect_legal_topics(facts, structured_facts, crime_type)

    return {
        "facts_summary": summarize_facts(facts),
        "detected_legal_topics": detected_topics,
        "structured_facts": structured_facts,
        "candidate_articles": get_mapped_articles(crime_type, articles),
        "missing_questions": build_missing_questions(detected_topics, structured_facts, crime_type),
        "human_review_required": True,
        "analysis_engine": analysis_engine,
        "legal_assignment_engine": "deterministic_rules",
        "detected_crime_type": crime_type,
        "crime_subtype": crime_subtype,
        "crime_display_name": crime_display_name,
        "investigation_steps": investigation_steps,
    }
