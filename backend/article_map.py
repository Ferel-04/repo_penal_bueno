# backend/article_map.py
"""
Mapa curado de artículos relevantes por tipo de delito.
Cada entrada define los artículos exactos a mostrar, agrupados por fuente.

Fuentes disponibles:
- "cpem": Código Penal para el Estado de Michoacán de Ocampo
- "cnpp": Código Nacional de Procedimientos Penales  
- "lgv": Ley General de Víctimas
- "const": Constitución Política de los Estados Unidos Mexicanos

Para cada artículo se define:
- number: número del artículo
- reason: por qué es relevante para este delito (se muestra al MP)
"""

ARTICLE_MAP = {
    "violencia_familiar": {
        "cpem": [
            {"number": "178", "reason": "Tipo penal base: violencia familiar"},
            {"number": "125", "reason": "Lesiones simples (cuando hay golpes)"},
            {"number": "126", "reason": "Lesiones agravadas por relación con víctima"},
            {"number": "131", "reason": "Lesiones calificadas"},
        ],
        "cnpp": [
            {"number": "109", "reason": "Derechos de la víctima u ofendido en el proceso"},
            {"number": "131", "reason": "Obligaciones del Ministerio Público en la investigación"},
            {"number": "137", "reason": "Medidas u Órdenes de Protección — el MP puede ordenarlas de inmediato"},
            {"number": "146", "reason": "Supuestos de flagrancia — cuándo se puede detener sin orden"},
            {"number": "147", "reason": "Detención en caso de flagrancia — procedimiento"},
            {"number": "154", "reason": "Procedencia de medidas cautelares"},
            {"number": "155", "reason": "Tipos de medidas cautelares disponibles"},
            {"number": "167", "reason": "Causas de procedencia para prisión preventiva"},
            {"number": "219", "reason": "Acceso a registros y audiencia inicial"},
        ],
        "lgv": [
            {"number": "7",  "reason": "Derechos generales de las víctimas"},
            {"number": "12", "reason": "Derecho a ser informada del proceso"},
            {"number": "17", "reason": "Derecho a medidas de protección"},
            {"number": "26", "reason": "Derecho a asistencia médica y psicológica"},
            {"number": "27", "reason": "Atención médica y psicológica de emergencia"},
        ],
        "const": [],
    },
    "violacion": {
        "cpem": [
            {"number": "164", "reason": "Tipo penal base: violación"},
            {"number": "165", "reason": "Violación equiparada"},
            {"number": "166", "reason": "Abuso sexual"},
            {"number": "167", "reason": "Abuso sexual de menores de 18 años"},
            {"number": "168", "reason": "Agravantes de violación"},
            {"number": "169", "reason": "Hostigamiento sexual"},
        ],
        "cnpp": [
            {"number": "109", "reason": "Derechos de la víctima u ofendido en el proceso"},
            {"number": "131", "reason": "Obligaciones del Ministerio Público en la investigación"},
            {"number": "146", "reason": "Supuestos de flagrancia — cuándo se puede detener sin orden"},
            {"number": "147", "reason": "Detención en caso de flagrancia — procedimiento"},
            {"number": "154", "reason": "Procedencia de medidas cautelares"},
            {"number": "155", "reason": "Tipos de medidas cautelares disponibles"},
            {"number": "167", "reason": "Causas de procedencia para prisión preventiva"},
            {"number": "219", "reason": "Acceso a registros y audiencia inicial"},
        ],
        "lgv": [
            {"number": "7",  "reason": "Derechos generales de las víctimas"},
            {"number": "12", "reason": "Derecho a ser informada del proceso"},
            {"number": "17", "reason": "Derecho a medidas de protección"},
            {"number": "26", "reason": "Derecho a asistencia médica y psicológica"},
            {"number": "27", "reason": "Atención médica y psicológica de emergencia"},
            {"number": "34", "reason": "Atención médica especializada para víctimas de violencia sexual"},
        ],
        "const": [
            {"number": "20", "reason": "Derechos de la víctima en el proceso penal"},
        ],
    },
    "robo": {
        "cpem": [
            {"number": "199", "reason": "Tipo penal base: robo"},
            {"number": "200", "reason": "Consecuencias jurídicas del robo"},
            {"number": "204", "reason": "Robo calificado grave"},
            {"number": "205", "reason": "Robo calificado"},
            {"number": "206", "reason": "Violencia en el robo"},
            {"number": "209", "reason": "Robo equiparado"},
        ],
        "cnpp": [
            {"number": "109", "reason": "Derechos de la víctima u ofendido en el proceso"},
            {"number": "131", "reason": "Obligaciones del Ministerio Público en la investigación"},
            {"number": "146", "reason": "Supuestos de flagrancia"},
            {"number": "147", "reason": "Detención en caso de flagrancia"},
            {"number": "167", "reason": "Causas de procedencia para prisión preventiva"},
            {"number": "219", "reason": "Acceso a registros y audiencia inicial"},
        ],
        "lgv": [
            {"number": "7",  "reason": "Derechos generales de las víctimas"},
            {"number": "12", "reason": "Derecho a ser informada del proceso"},
        ],
        "const": [],
    },
    "lesiones": {
        "cpem": [
            {"number": "125", "reason": "Lesiones simples"},
            {"number": "126", "reason": "Lesiones agravadas por relación con víctima"},
            {"number": "127", "reason": "Lesiones por condición de género"},
            {"number": "129", "reason": "Lesiones con crueldad o frecuencia contra menor"},
            {"number": "131", "reason": "Lesiones calificadas"},
            {"number": "132", "reason": "Lesiones que se persiguen por querella"},
        ],
        "cnpp": [
            {"number": "109", "reason": "Derechos de la víctima u ofendido en el proceso"},
            {"number": "131", "reason": "Obligaciones del Ministerio Público en la investigación"},
            {"number": "146", "reason": "Supuestos de flagrancia"},
            {"number": "147", "reason": "Detención en caso de flagrancia"},
            {"number": "219", "reason": "Acceso a registros y audiencia inicial"},
        ],
        "lgv": [
            {"number": "7",  "reason": "Derechos generales de las víctimas"},
            {"number": "12", "reason": "Derecho a ser informada del proceso"},
        ],
        "const": [],
    },
    "homicidio": {
        "cpem": [
            {"number": "117", "reason": "Homicidio doloso"},
            {"number": "118", "reason": "Homicidio culposo"},
            {"number": "119", "reason": "Penalidad del homicidio"},
            {"number": "120", "reason": "Feminicidio"},
            {"number": "121", "reason": "Homicidio por razón de preferencia sexual"},
            {"number": "135", "reason": "Calificativas: ventaja, traición, alevosía"},
        ],
        "cnpp": [
            {"number": "109", "reason": "Derechos de la víctima u ofendido en el proceso"},
            {"number": "131", "reason": "Obligaciones del Ministerio Público en la investigación"},
            {"number": "146", "reason": "Supuestos de flagrancia"},
            {"number": "147", "reason": "Detención en caso de flagrancia"},
            {"number": "167", "reason": "Causas de procedencia para prisión preventiva"},
            {"number": "219", "reason": "Acceso a registros y audiencia inicial"},
        ],
        "lgv": [
            {"number": "7",  "reason": "Derechos generales de las víctimas"},
            {"number": "12", "reason": "Derecho a ser informada del proceso"},
        ],
        "const": [],
    },
    "fraude": {
        "cpem": [
            {"number": "217", "reason": "Tipo penal base: fraude"},
            {"number": "218", "reason": "Fraude específico"},
            {"number": "219", "reason": "Fraude por abuso de confianza"},
            {"number": "220", "reason": "Fraude equiparado"},
        ],
        "cnpp": [
            {"number": "109", "reason": "Derechos de la víctima u ofendido en el proceso"},
            {"number": "131", "reason": "Obligaciones del Ministerio Público en la investigación"},
            {"number": "146", "reason": "Supuestos de flagrancia"},
            {"number": "147", "reason": "Detención en caso de flagrancia"},
            {"number": "219", "reason": "Acceso a registros y audiencia inicial"},
        ],
        "lgv": [
            {"number": "7",  "reason": "Derechos generales de las víctimas"},
            {"number": "12", "reason": "Derecho a ser informada del proceso"},
        ],
        "const": [],
    },
    "unknown": {
        "cpem": [],
        "cnpp": [
            {"number": "131", "reason": "Obligaciones del Ministerio Público en la investigación"},
            {"number": "154", "reason": "Procedencia de medidas cautelares"},
            {"number": "219", "reason": "Acceso a registros y audiencia inicial"},
        ],
        "lgv": [
            {"number": "7",  "reason": "Derechos generales de las víctimas"},
            {"number": "12", "reason": "Derecho a ser informada del proceso"},
        ],
        "const": [],
    },
}

SOURCE_KEY_MAP = {
    "michoacan": "cpem",
    "ocampo": "cpem",
    "procedimientos penales": "cnpp",
    "victimas": "lgv",
    "constitucion": "const",
}


def get_source_key(source_name: str) -> str | None:
    import unicodedata
    normalized = unicodedata.normalize("NFD", source_name.lower())
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    for fragment, key in SOURCE_KEY_MAP.items():
        if fragment in normalized:
            return key
    return None


def get_mapped_articles(crime_type: str, all_articles: list[dict]) -> dict:
    """
    Retorna artículos agrupados para el tipo de delito dado,
    obtenidos directamente del corpus cargado por número de artículo.
    
    Returns dict con keys: penal_articles, procedural_foundations,
    victim_rights, constitutional_foundations, human_review_warnings
    """
    from legal_rules import normalize_text, classify_article

    crime_map = ARTICLE_MAP.get(crime_type, ARTICLE_MAP["unknown"])
    
    article_index: dict[tuple[str, str], dict] = {}
    for article in all_articles:
        source_key = get_source_key(article.get("source_name") or "")
        if source_key:
            article_index[(source_key, article["article_number"])] = article

    result = {
        "penal_articles": [],
        "procedural_foundations": [],
        "victim_rights": [],
        "constitutional_foundations": [],
        "human_review_warnings": [],
    }

    source_to_group = {
        "cpem": "penal_articles",
        "cnpp": "procedural_foundations",
        "lgv": "victim_rights",
        "const": "constitutional_foundations",
    }

    for source_key, entries in crime_map.items():
        group = source_to_group.get(source_key)
        if not group:
            continue
        for entry in entries:
            article = article_index.get((source_key, entry["number"]))
            if article:
                enriched = dict(article)
                enriched["match_reason"] = entry["reason"]
                enriched["classification"] = classify_article(article)
                result[group].append(enriched)

    warnings = ["Este análisis es determinista y debe ser revisado por una persona abogada."]
    if result["penal_articles"] and not result["procedural_foundations"]:
        warnings.append("Hay posibles artículos penales sin fundamento procesal relacionado.")
    if result["penal_articles"] and not result["victim_rights"]:
        warnings.append("Hay posibles artículos penales sin derechos de víctima relacionados.")
    result["human_review_warnings"] = warnings

    return result
