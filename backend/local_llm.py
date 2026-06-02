import json
import os
import re
import unicodedata
import urllib.error
import urllib.request
from typing import Optional

from pydantic import BaseModel, ConfigDict, StrictBool, ValidationError, field_validator


OLLAMA_CHAT_URL = os.getenv("OLLAMA_CHAT_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "12.0"))

LOCAL_FACT_EXTRACTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "sexual_conduct_detected",
        "victim_age_group",
        "relationship_to_aggressor",
        "violence_detected",
        "threat_detected",
        "unconscious_detected",
        "unable_to_resist_detected",
        "explicit_crime_mentioned",
    ],
    "properties": {
        "sexual_conduct_detected": {"type": "boolean"},
        "victim_age_group": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "relationship_to_aggressor": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "violence_detected": {"type": "boolean"},
        "threat_detected": {"type": "boolean"},
        "unconscious_detected": {"type": "boolean"},
        "unable_to_resist_detected": {"type": "boolean"},
        "explicit_crime_mentioned": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    },
}


class LocalFactExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sexual_conduct_detected: StrictBool
    victim_age_group: Optional[str]
    relationship_to_aggressor: Optional[str]
    violence_detected: StrictBool
    threat_detected: StrictBool
    unconscious_detected: StrictBool
    unable_to_resist_detected: StrictBool
    explicit_crime_mentioned: Optional[str]

    @field_validator(
        "victim_age_group",
        "relationship_to_aggressor",
        "explicit_crime_mentioned",
        mode="before",
    )
    @classmethod
    def normalize_empty_values(cls, value):
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        normalized_value = normalize_text(value).strip(" .")
        if isinstance(value, str) and normalized_value in {
            "",
            "false",
            "no",
            "none",
            "null",
            "unknown",
            "desconocido",
            "desconocida",
            "no mencionado",
            "no mencionada",
            "no se menciono",
            "no se menciona",
            "no especificado",
            "no especificada",
        }:
            return None
        return value


def extract_facts_with_local_llm(facts: str) -> dict | None:
    """Return structured facts from local Ollama, or None on any failure."""
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "think": False,
        "format": LOCAL_FACT_EXTRACTION_SCHEMA,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Eres un extractor local de hechos, no un abogado. No hagas análisis jurídico. "
                    "No elijas artículos. No inventes leyes. No generes conclusiones. "
                    "Devuelve solo JSON válido. Si un dato no aparece explícitamente, usa false o null. "
                    "No infieras edad, relación ni conducta sexual. explicit_crime_mentioned debe ser "
                    "un string con el delito mencionado explícitamente o null, nunca booleano."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Extrae únicamente estos campos: sexual_conduct_detected, victim_age_group, "
                    "relationship_to_aggressor, violence_detected, threat_detected, "
                    "unconscious_detected, unable_to_resist_detected, explicit_crime_mentioned.\n\n"
                    f"Texto:\n{facts}"
                ),
            },
        ],
        "options": {
            "temperature": 0,
            "num_predict": 240,
        },
    }

    try:
        request = urllib.request.Request(
            OLLAMA_CHAT_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError):
        return None

    content = response_payload.get("message", {}).get("content")
    if not isinstance(content, str):
        return None

    json_text = extract_json_object(content)
    if json_text is None:
        return None

    try:
        raw_extraction = json.loads(json_text)
        extraction = LocalFactExtraction.model_validate(raw_extraction)
    except (json.JSONDecodeError, ValidationError):
        return None

    return apply_deterministic_fact_guardrails(facts, extraction.model_dump())


def apply_deterministic_fact_guardrails(facts: str, extraction: dict) -> dict:
    normalized_facts = normalize_text(facts)
    guarded = dict(extraction)

    age_group = detect_age_group(normalized_facts)
    if age_group:
        guarded["victim_age_group"] = age_group

    relationship = detect_relationship_to_aggressor(normalized_facts)
    if relationship:
        guarded["relationship_to_aggressor"] = relationship

    if contains_any(
        normalized_facts,
        [
            "conducta sexual",
            "acto sexual",
            "actos de naturaleza sexual",
            "copula",
            "violacion",
            "abuso sexual",
            "sin su consentimiento",
        ],
    ):
        guarded["sexual_conduct_detected"] = True

    physical_violence_terms = [
        "violencia",
        "fuerza fisica",
        "sujeto de los brazos",
        "empujo",
        "golpeo",
        "golpe",
        "forcejeo",
        "sometio",
        "ataco",
        "agredio",
        "jalon",
    ]

    if contains_any(normalized_facts, physical_violence_terms):
        guarded["violence_detected"] = True

    if contains_any(
        normalized_facts,
        [
            "amenaza",
            "amenazo",
            "amenazada",
            "amenazado",
            "si gritaba",
            "lastimar",
            "hacer dano",
            "hacer daño",
        ],
    ):
        guarded["threat_detected"] = True

    if contains_any(
        normalized_facts,
        ["inconsciente", "desmayada", "desmayado", "dormida", "dormido", "sedada", "sedado"],
    ):
        guarded["unconscious_detected"] = True

    if contains_any(
        normalized_facts,
        [
            "no pudo resistir",
            "no podia resistir",
            "no pudo resistirse",
            "no podia resistirse",
            "incapaz de resistir",
            "sin poder resistir",
        ],
    ):
        guarded["unable_to_resist_detected"] = True

    explicit_crime = detect_explicit_crime(normalized_facts)
    if explicit_crime:
        guarded["explicit_crime_mentioned"] = explicit_crime

    return guarded


def normalize_text(value: str) -> str:
    value = value.casefold()
    normalized = unicodedata.normalize("NFD", value)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def contains_any(value: str, terms: list[str]) -> bool:
    return any(normalize_text(term) in value for term in terms)


def detect_age_group(normalized_facts: str) -> str | None:
    age_match = re.search(r"\b(\d{1,2})\s+anos\b", normalized_facts)
    if age_match:
        age = int(age_match.group(1))
        if age < 15:
            return "menor de quince años"
        if age < 18:
            return "menor de edad"
        return "adulto"

    if contains_any(normalized_facts, ["menor de quince", "menor de 15", "14 anos", "13 anos"]):
        return "menor de quince años"
    if contains_any(normalized_facts, ["menor de edad", "victima menor", "adolescente", "nina", "nino"]):
        return "menor de edad"
    if contains_any(normalized_facts, ["mayor de edad", "persona adulta"]):
        return "adulto"

    return None


def detect_relationship_to_aggressor(normalized_facts: str) -> str | None:
    if contains_any(
        normalized_facts,
        [
            "no hay relacion familiar",
            "sin relacion familiar",
            "no existe relacion familiar",
            "no tiene relacion familiar",
        ],
    ):
        return "sin relación familiar"

    family_terms = {
        "padre": "padre",
        "madre": "madre",
        "hermano": "hermano",
        "tio": "tío",
        "abuelo": "abuelo",
        "tutor": "tutor",
        "pareja": "pareja",
        "ex pareja": "ex pareja",
        "custodia": "custodia",
    }
    for term, label in family_terms.items():
        if term in normalized_facts:
            return label

    return None


def detect_explicit_crime(normalized_facts: str) -> str | None:
    if "violacion" in normalized_facts:
        return "violación"
    if "abuso sexual" in normalized_facts:
        return "abuso sexual"
    if "hostigamiento sexual" in normalized_facts:
        return "hostigamiento sexual"
    return None


def extract_json_object(value: str) -> str | None:
    start = value.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for index, char in enumerate(value[start:], start=start):
        if in_string:
            if escape_next:
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return value[start : index + 1]

    return None
