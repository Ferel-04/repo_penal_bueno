import pytest
from fastapi import HTTPException

import main
from ingest import parse_all_sources
from schemas import FactInput, SearchInput


def setup_function():
    main.load_articles = parse_all_sources


def test_articles_endpoint_returns_all_mock_sources():
    payload = main.get_articles()

    assert payload["total_articles"] == 13

    source_names = {article["source_name"] for article in payload["articles"]}
    assert "Código Penal para el Estado de Michoacán MOCK" in source_names
    assert "Código Nacional de Procedimientos Penales MOCK" in source_names
    assert "Ley General de Víctimas MOCK" in source_names
    assert "Constitución Política de los Estados Unidos Mexicanos MOCK" in source_names
    assert all(article["content_hash"] for article in payload["articles"])
    assert all("source_version" in article for article in payload["articles"])
    assert all("last_reform_date" in article for article in payload["articles"])


def test_search_endpoint_finds_text_matches_and_classifies_penal_results():
    payload = main.search_articles(SearchInput(query="violación"))

    assert payload["query"] == "violación"
    assert payload["total_results"] == 3
    assert all(result["content_hash"] for result in payload["results"])
    assert all("source_version" in result for result in payload["results"])
    assert all("last_reform_date" in result for result in payload["results"])

    classifications = {
        result["article_number"]: result["classification"]
        for result in payload["results"]
    }
    assert classifications["164"] == "tipo_penal_base"
    assert classifications["165"] == "violacion_equiparada"
    assert classifications["166"] == "agravante"


def test_search_endpoint_finds_cnpp_articles():
    payload = main.search_articles(SearchInput(query="entrevista"))

    assert payload["total_results"] >= 1
    assert any(
        result["classification"] == "fundamento_procesal"
        and result["source_name"] == "Código Nacional de Procedimientos Penales MOCK"
        for result in payload["results"]
    )


def test_search_endpoint_finds_lgv_articles():
    payload = main.search_articles(SearchInput(query="reparación integral"))

    assert payload["total_results"] >= 1
    assert any(
        result["classification"] == "derecho_victima"
        and result["source_name"] == "Ley General de Víctimas MOCK"
        for result in payload["results"]
    )


def test_search_endpoint_rejects_empty_query():
    with pytest.raises(HTTPException) as exc_info:
        main.search_articles(SearchInput(query="   "))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "El campo query no puede estar vacío."


def test_analyze_endpoint_detects_topics_and_returns_grouped_candidates():
    payload = main.analyze_facts(
        FactInput(
            facts=(
                "La víctima menor fue amenazada con violencia y existe una posible "
                "relación familiar."
            )
        )
    )

    assert payload["human_review_required"] is True
    assert payload["detected_legal_topics"] == ["familiar", "menor", "violencia", "amenaza"]
    assert payload["facts_summary"].startswith("La víctima menor")
    assert payload["missing_questions"] == [
        "¿La víctima podía comprender el significado del hecho y resistirlo?"
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
        FactInput(facts="Hechos posiblemente relacionados con violación contra una víctima.")
    )

    candidates = payload["candidate_articles"]
    assert candidates["penal_articles"]
    assert candidates["victim_rights"]


def test_analyze_with_medida_de_proteccion_returns_procedural_foundations():
    payload = main.analyze_facts(
        FactInput(facts="Se requiere medida de protección urgente para la víctima.")
    )

    candidates = payload["candidate_articles"]
    assert candidates["procedural_foundations"]
    assert any(
        article["classification"] == "fundamento_procesal"
        for article in candidates["procedural_foundations"]
    )


def test_analyze_endpoint_rejects_empty_facts():
    with pytest.raises(HTTPException) as exc_info:
        main.analyze_facts(FactInput(facts=""))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "El campo facts no puede estar vacío."
