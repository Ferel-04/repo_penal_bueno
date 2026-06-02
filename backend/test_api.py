import pytest
from fastapi import HTTPException

import main
from ingest import parse_all_sources
from schemas import FactInput, SearchInput


def setup_function():
    main.load_articles = parse_all_sources
    main.extract_facts_with_local_llm = lambda facts: None


def test_articles_endpoint_returns_real_federal_sources():
    payload = main.get_articles()

    assert payload["total_articles"] > 800

    source_names = {article["source_name"] for article in payload["articles"]}
    assert "C\u00f3digo Nacional de Procedimientos Penales" in source_names
    assert "Ley General de V\u00edctimas" in source_names
    assert "Constituci\u00f3n Pol\u00edtica de los Estados Unidos Mexicanos" in source_names
    assert any("MOCK" in source_name for source_name in source_names)
    assert all(article["content_hash"] for article in payload["articles"])
    assert all("source_version" in article for article in payload["articles"])
    assert all("last_reform_date" in article for article in payload["articles"])


def test_search_endpoint_finds_text_matches_and_classifies_penal_results():
    payload = main.search_articles(SearchInput(query="violaci\u00f3n"))

    assert payload["query"] == "violaci\u00f3n"
    assert payload["total_results"] >= 3
    assert all(result["content_hash"] for result in payload["results"])
    assert all("source_version" in result for result in payload["results"])
    assert all("last_reform_date" in result for result in payload["results"])

    penal_classifications = {
        result["article_number"]: result["classification"]
        for result in payload["results"]
        if "C\u00f3digo Penal" in result["source_name"]
    }
    assert penal_classifications["164"] == "tipo_penal_base"
    assert penal_classifications["165"] == "violacion_equiparada"
    assert penal_classifications["166"] == "agravante"


def test_search_endpoint_finds_cnpp_articles():
    payload = main.search_articles(SearchInput(query="entrevista"))

    assert payload["total_results"] >= 1
    assert any(
        result["classification"] == "fundamento_procesal"
        and result["source_name"] == "C\u00f3digo Nacional de Procedimientos Penales"
        for result in payload["results"]
    )


def test_search_endpoint_finds_lgv_articles():
    payload = main.search_articles(SearchInput(query="reparaci\u00f3n integral"))

    assert payload["total_results"] >= 1
    assert any(
        result["classification"] == "derecho_victima"
        and result["source_name"] == "Ley General de V\u00edctimas"
        for result in payload["results"]
    )


def test_search_endpoint_rejects_empty_query():
    with pytest.raises(HTTPException) as exc_info:
        main.search_articles(SearchInput(query="   "))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "El campo query no puede estar vac\u00edo."


def test_analyze_endpoint_detects_topics_and_returns_grouped_candidates():
    payload = main.analyze_facts(
        FactInput(
            facts=(
                "La v\u00edctima menor fue amenazada con violencia y existe una posible "
                "relaci\u00f3n familiar."
            )
        )
    )

    assert payload["human_review_required"] is True
    assert payload["analysis_engine"] == "deterministic_fallback"
    assert payload["structured_facts"] is None
    assert payload["legal_assignment_engine"] == "deterministic_rules"
    assert payload["detected_legal_topics"] == ["familiar", "menor", "violencia", "amenaza"]
    assert payload["facts_summary"].startswith("La v\u00edctima menor")
    assert payload["missing_questions"] == [
        "\u00bfLa v\u00edctima pod\u00eda comprender el significado del hecho y resistirlo?"
    ]

    candidates = payload["candidate_articles"]
    assert "penal_articles" in candidates
    assert "procedural_foundations" in candidates
    assert "victim_rights" in candidates
    assert "constitutional_foundations" in candidates
    assert "human_review_warnings" in candidates

    article_numbers = {
        article["article_number"]
        for article in candidates["penal_articles"]
    }
    assert {"164", "165", "166"}.issubset(article_numbers)


def test_analyze_with_violacion_returns_penal_articles_and_victim_rights():
    payload = main.analyze_facts(
        FactInput(facts="Hechos posiblemente relacionados con violaci\u00f3n contra una v\u00edctima.")
    )

    candidates = payload["candidate_articles"]
    assert candidates["penal_articles"]
    assert candidates["victim_rights"]


def test_analyze_with_medida_de_proteccion_returns_procedural_foundations():
    payload = main.analyze_facts(
        FactInput(facts="Se requiere medida de protecci\u00f3n urgente para la v\u00edctima.")
    )

    candidates = payload["candidate_articles"]
    assert candidates["procedural_foundations"]
    assert any(
        article["classification"] == "fundamento_procesal"
        for article in candidates["procedural_foundations"]
    )


def test_analyze_uses_local_llm_when_structured_facts_are_valid():
    main.extract_facts_with_local_llm = lambda facts: {
        "sexual_conduct_detected": True,
        "victim_age_group": "menor",
        "relationship_to_aggressor": None,
        "violence_detected": True,
        "threat_detected": False,
        "unconscious_detected": False,
        "unable_to_resist_detected": False,
        "explicit_crime_mentioned": None,
    }

    payload = main.analyze_facts(FactInput(facts="Relato sin palabras legales expl\u00edcitas."))

    assert payload["analysis_engine"] == "local_llm"
    assert payload["structured_facts"]["sexual_conduct_detected"] is True
    assert payload["legal_assignment_engine"] == "deterministic_rules"
    assert "violaci\u00f3n" in payload["detected_legal_topics"]
    assert "menor" in payload["detected_legal_topics"]
    assert payload["candidate_articles"]["penal_articles"]


def test_analyze_does_not_ask_age_or_family_when_structured_as_adult_no_family():
    main.extract_facts_with_local_llm = lambda facts: {
        "sexual_conduct_detected": True,
        "victim_age_group": "adulto",
        "relationship_to_aggressor": "sin relaci\u00f3n familiar",
        "violence_detected": True,
        "threat_detected": True,
        "unconscious_detected": False,
        "unable_to_resist_detected": False,
        "explicit_crime_mentioned": None,
    }

    payload = main.analyze_facts(
        FactInput(
            facts=(
                "La v\u00edctima tiene 21 a\u00f1os y no hay relaci\u00f3n familiar con el agresor. "
                "Refiere actos sexuales, violencia y amenazas."
            )
        )
    )

    assert "familiar" not in payload["detected_legal_topics"]
    assert "menor" not in payload["detected_legal_topics"]
    assert "\u00bfLa v\u00edctima era menor de quince a\u00f1os?" not in payload["missing_questions"]
    assert (
        "\u00bfExiste relaci\u00f3n familiar, custodia, guarda, educaci\u00f3n o autoridad?"
        not in payload["missing_questions"]
    )


def test_analyze_endpoint_rejects_empty_facts():
    with pytest.raises(HTTPException) as exc_info:
        main.analyze_facts(FactInput(facts=""))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "El campo facts no puede estar vac\u00edo."
