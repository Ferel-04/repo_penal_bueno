import pytest

from article_map import ARTICLE_MAP, get_mapped_articles
from ingest import parse_all_sources
from legal_rules import (
    build_missing_questions,
    classify_article,
    detect_legal_topics,
)


COMPRENDER_QUESTION = (
    "\u00bfLa v\u00edctima pod\u00eda comprender el significado del hecho y resistirlo?"
)


def test_violencia_familiar_adult_victim_no_menor_topic():
    topics = detect_legal_topics(
        facts="El agresor golpe\u00f3 a la v\u00edctima en el domicilio conyugal.",
        structured_facts={
            "victim_age_group": None,
            "relationship_to_aggressor": "c\u00f3nyuge",
            "violence_detected": True,
            "threat_detected": False,
            "sexual_conduct_detected": False,
            "unconscious_detected": False,
            "unable_to_resist_detected": False,
            "explicit_crime_mentioned": None,
        },
        crime_type="violencia_familiar",
    )
    assert "menor" not in topics


def test_violencia_familiar_child_witnesses_adult_victim_no_menor_topic():
    topics = detect_legal_topics(
        facts=(
            "El agresor golpe\u00f3 a la v\u00edctima. "
            "Sus hijos menores de edad fueron testigos presenciales."
        ),
        structured_facts={
            "victim_age_group": None,
            "relationship_to_aggressor": "c\u00f3nyuge",
            "violence_detected": True,
            "threat_detected": True,
            "sexual_conduct_detected": False,
            "unconscious_detected": False,
            "unable_to_resist_detected": False,
            "explicit_crime_mentioned": None,
        },
        crime_type="violencia_familiar",
    )
    assert "menor" not in topics


def test_violencia_familiar_no_comprender_question():
    questions = build_missing_questions(
        detected_topics=["violencia", "familiar"],
        structured_facts={
            "victim_age_group": "adulto",
            "relationship_to_aggressor": "c\u00f3nyuge",
        },
        crime_type="violencia_familiar",
    )
    assert COMPRENDER_QUESTION not in questions


def test_violacion_missing_comprender_question_when_no_unconscious():
    questions = build_missing_questions(
        detected_topics=["violaci\u00f3n"],
        structured_facts={"victim_age_group": "adulto"},
        crime_type="violacion",
    )
    assert COMPRENDER_QUESTION in questions


def test_violacion_no_comprender_question_when_unconscious_detected():
    questions = build_missing_questions(
        detected_topics=["violaci\u00f3n", "inconsciente"],
        structured_facts={"victim_age_group": "adulto"},
        crime_type="violacion",
    )
    assert COMPRENDER_QUESTION not in questions


def test_cnpp_reasons_correct_for_violencia_familiar():
    articles = parse_all_sources()
    grouped = get_mapped_articles("violencia_familiar", articles)
    procedural = grouped["procedural_foundations"]

    reasons_by_number = {
        a["article_number"]: a["match_reason"]
        for a in procedural
    }

    expected = {
        "109": "Derechos de la v\u00edctima u ofendido en el proceso",
        "131": "Obligaciones del Ministerio P\u00fablico en la investigaci\u00f3n",
        "146": "Supuestos de flagrancia",
        "147": "Detenci\u00f3n en caso de flagrancia",
    }
    for number, reason_prefix in expected.items():
        assert number in reasons_by_number, f"CNPP art. {number} missing"
        assert reasons_by_number[number].startswith(reason_prefix), (
            f"CNPP art. {number}: expected reason starting with '{reason_prefix}', "
            f"got '{reasons_by_number[number]}'"
        )


def test_cnpp_reasons_correct_for_violacion():
    articles = parse_all_sources()
    grouped = get_mapped_articles("violacion", articles)
    procedural = grouped["procedural_foundations"]

    reasons_by_number = {
        a["article_number"]: a["match_reason"]
        for a in procedural
    }

    expected = {
        "109": "Derechos de la v\u00edctima u ofendido en el proceso",
        "131": "Obligaciones del Ministerio P\u00fablico en la investigaci\u00f3n",
        "146": "Supuestos de flagrancia",
        "147": "Detenci\u00f3n en caso de flagrancia",
    }
    for number, reason_prefix in expected.items():
        assert number in reasons_by_number, f"CNPP art. {number} missing"
        assert reasons_by_number[number].startswith(reason_prefix), (
            f"CNPP art. {number}: expected reason starting with '{reason_prefix}', "
            f"got '{reasons_by_number[number]}'"
        )


def test_classify_robo_equiparado_not_violacion_equiparada():
    article = {
        "source_name": "C\u00f3digo Penal para el Estado de Michoac\u00e1n de Ocampo",
        "article_number": "209",
        "title": "",
        "content": "Se equipara al robo y se sancionar\u00e1 con las mismas penas.",
    }
    assert classify_article(article) != "violacion_equiparada"
    assert classify_article(article) == "tipo_penal_base"
