import json
import urllib.error

import local_llm


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_extract_facts_with_local_llm_returns_validated_json(monkeypatch):
    ollama_payload = {
        "message": {
            "content": json.dumps(
                {
                    "sexual_conduct_detected": True,
                    "victim_age_group": "menor",
                    "relationship_to_aggressor": "familiar",
                    "violence_detected": True,
                    "threat_detected": False,
                    "unconscious_detected": False,
                    "unable_to_resist_detected": True,
                    "explicit_crime_mentioned": "violación",
                }
            )
        }
    }

    def fake_urlopen(request, timeout):
        return FakeResponse(ollama_payload)

    monkeypatch.setattr(local_llm.urllib.request, "urlopen", fake_urlopen)

    extraction = local_llm.extract_facts_with_local_llm("hechos")

    assert extraction == {
        "sexual_conduct_detected": True,
        "victim_age_group": "menor",
        "relationship_to_aggressor": "familiar",
        "violence_detected": True,
        "threat_detected": False,
        "unconscious_detected": False,
        "unable_to_resist_detected": True,
        "explicit_crime_mentioned": "violación",
    }


def test_extract_facts_with_local_llm_ignores_invalid_json(monkeypatch):
    def fake_urlopen(request, timeout):
        return FakeResponse({"message": {"content": "no es json"}})

    monkeypatch.setattr(local_llm.urllib.request, "urlopen", fake_urlopen)

    assert local_llm.extract_facts_with_local_llm("hechos") is None


def test_extract_facts_with_local_llm_ignores_invalid_schema(monkeypatch):
    ollama_payload = {
        "message": {
            "content": json.dumps(
                {
                    "sexual_conduct_detected": "yes",
                    "victim_age_group": "menor",
                    "relationship_to_aggressor": None,
                    "violence_detected": False,
                    "threat_detected": False,
                    "unconscious_detected": False,
                    "unable_to_resist_detected": False,
                    "explicit_crime_mentioned": None,
                    "invented_legal_conclusion": "Artículo inventado",
                }
            )
        }
    }

    def fake_urlopen(request, timeout):
        return FakeResponse(ollama_payload)

    monkeypatch.setattr(local_llm.urllib.request, "urlopen", fake_urlopen)

    assert local_llm.extract_facts_with_local_llm("hechos") is None


def test_extract_facts_with_local_llm_returns_none_when_ollama_fails(monkeypatch):
    def fake_urlopen(request, timeout):
        raise urllib.error.URLError("Ollama no disponible")

    monkeypatch.setattr(local_llm.urllib.request, "urlopen", fake_urlopen)

    assert local_llm.extract_facts_with_local_llm("hechos") is None


def test_extract_facts_with_local_llm_normalizes_common_null_strings(monkeypatch):
    ollama_payload = {
        "message": {
            "content": json.dumps(
                {
                    "sexual_conduct_detected": False,
                    "victim_age_group": "unknown",
                    "relationship_to_aggressor": "false",
                    "violence_detected": True,
                    "threat_detected": False,
                    "unconscious_detected": False,
                    "unable_to_resist_detected": False,
                    "explicit_crime_mentioned": False,
                }
            )
        }
    }

    def fake_urlopen(request, timeout):
        return FakeResponse(ollama_payload)

    monkeypatch.setattr(local_llm.urllib.request, "urlopen", fake_urlopen)

    extraction = local_llm.extract_facts_with_local_llm("hechos")

    assert extraction["victim_age_group"] is None
    assert extraction["relationship_to_aggressor"] is None
    assert extraction["explicit_crime_mentioned"] is None
    assert extraction["violence_detected"] is True


def test_deterministic_guardrails_correct_obvious_llm_misses():
    extraction = {
        "sexual_conduct_detected": False,
        "victim_age_group": None,
        "relationship_to_aggressor": None,
        "violence_detected": False,
        "threat_detected": False,
        "unconscious_detected": False,
        "unable_to_resist_detected": False,
        "explicit_crime_mentioned": None,
    }

    guarded = local_llm.apply_deterministic_fact_guardrails(
        (
            "La víctima tiene 21 años y no hay relación familiar con el agresor. "
            "Refiere actos de naturaleza sexual, violencia física y amenazas."
        ),
        extraction,
    )

    assert guarded["sexual_conduct_detected"] is True
    assert guarded["victim_age_group"] == "adulto"
    assert guarded["relationship_to_aggressor"] == "sin relación familiar"
    assert guarded["violence_detected"] is True
    assert guarded["threat_detected"] is True


def test_guardrails_do_not_assign_child_witness_age_to_direct_victim():
    extraction = {
        "sexual_conduct_detected": False,
        "victim_age_group": "menor de quince a\u00f1os",
        "relationship_to_aggressor": None,
        "violence_detected": True,
        "threat_detected": True,
        "unconscious_detected": False,
        "unable_to_resist_detected": False,
        "explicit_crime_mentioned": "No se mencion\u00f3 un crimen explicito.",
    }

    guarded = local_llm.apply_deterministic_fact_guardrails(
        (
            "El agresor golpe\u00f3 a la v\u00edctima, su c\u00f3nyuge, en el domicilio conyugal. "
            "Sus dos hijos menores de edad, de 8 y 5 a\u00f1os respectivamente, fueron "
            "testigos presenciales de las agresiones."
        ),
        extraction,
    )

    assert guarded["victim_age_group"] is None
    assert guarded["relationship_to_aggressor"] == "c\u00f3nyuge"
    assert guarded["explicit_crime_mentioned"] is None
