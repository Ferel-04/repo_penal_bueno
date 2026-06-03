import unicodedata

from crime_catalog import (
    CRIME_CATALOG,
    detect_crime_type,
    get_active_subtypes,
)


def normalize_alias(value: str) -> str:
    value = value.casefold()
    normalized = unicodedata.normalize("NFD", value)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def classify_crime_type(
    facts: str,
    structured_facts: dict | None = None,
) -> str:
    crime_aliases = {
        "violacion": "violacion",
        "abuso sexual": "violacion",
        "robo": "robo",
        "asalto": "robo",
        "hurto": "robo",
        "lesiones": "lesiones",
        "golpes": "lesiones",
        "lesion": "lesiones",
        "homicidio": "homicidio",
        "asesinato": "homicidio",
        "feminicidio": "homicidio",
        "violencia familiar": "violencia_familiar",
        "violencia domestica": "violencia_familiar",
        "fraude": "fraude",
        "estafa": "fraude",
        "defraudacion": "fraude",
    }

    if structured_facts:
        explicit_crime = structured_facts.get("explicit_crime_mentioned")
        if explicit_crime and isinstance(explicit_crime, str):
            explicit_crime_lower = normalize_alias(explicit_crime).strip()
            if explicit_crime_lower in crime_aliases:
                return crime_aliases[explicit_crime_lower]

    detected_type = detect_crime_type(facts)
    if structured_facts and detected_type in {"unknown", "lesiones"}:
        violence_detected = structured_facts.get("violence_detected")
        relationship = structured_facts.get("relationship_to_aggressor")
        if violence_detected is True and relationship and isinstance(relationship, str) and relationship.strip():
            return "violencia_familiar"

    if detected_type != "unknown":
        return detected_type

    if structured_facts:
        violence_detected = structured_facts.get("violence_detected")
        relationship = structured_facts.get("relationship_to_aggressor")
        if violence_detected is True and relationship and isinstance(relationship, str) and relationship.strip():
            return "violencia_familiar"

        sexual_conduct_detected = structured_facts.get("sexual_conduct_detected")
        if sexual_conduct_detected is True:
            return "violacion"

    return "unknown"


def get_crime_display_name(crime_type: str) -> str:
    crime_entry = CRIME_CATALOG.get(crime_type)
    if not crime_entry:
        return "Delito no clasificado"
    return crime_entry.get("display_name", "Delito no clasificado")


def get_crime_subtype(
    crime_type: str,
    structured_facts: dict | None,
) -> str | None:
    if not structured_facts:
        return None

    active_subtypes = get_active_subtypes(crime_type, structured_facts)
    if not active_subtypes:
        return None

    return active_subtypes[-1]["key"]
