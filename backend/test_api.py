import pytest
from fastapi import HTTPException

import local_llm
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
    assert penal_classifications["168"] == "agravante"


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
    assert len(article_numbers) == 0

    procedural_numbers = {
        article["article_number"]
        for article in candidates["procedural_foundations"]
    }
    assert {"131", "154", "219"}.issubset(procedural_numbers)

    victim_numbers = {
        article["article_number"]
        for article in candidates["victim_rights"]
    }
    assert {"7", "12"}.issubset(victim_numbers)


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


def test_analyze_returns_crime_type_and_investigation_steps():
    payload = main.analyze_facts(
        FactInput(
            facts="El sujeto asaltó a la víctima con violencia física y le robó su cartera."
        )
    )

    assert payload["detected_crime_type"] == "robo"
    assert payload["crime_display_name"] == "Robo"
    assert len(payload["investigation_steps"]) >= 3
    assert all(
        "step" in step and "legal_basis" in step and "urgent" in step and "category" in step
        for step in payload["investigation_steps"]
    )
    assert any(step["urgent"] is True for step in payload["investigation_steps"])
    assert payload["crime_subtype"] is None or isinstance(payload["crime_subtype"], str)


def test_analyze_fraude_does_not_return_violencia_topic():
    payload = main.analyze_facts(
        FactInput(
            facts="La víctima fue defraudada cuando le entregó dinero mediante pagarés y nunca lo pagó."
        )
    )

    assert payload["detected_crime_type"] == "fraude"
    assert "violencia" not in payload["detected_legal_topics"]


def test_analyze_explicit_crime_type_overrides_detection():
    payload = main.analyze_facts(
        FactInput(facts="Texto genérico sin palabras clave de delito.", crime_type="homicidio")
    )

    assert payload["detected_crime_type"] == "homicidio"
    assert payload["crime_display_name"] == "Homicidio"
    assert len(payload["investigation_steps"]) >= 3


def test_analyze_spousal_repeated_violence_returns_family_violence_article():
    raw_extraction = {
        "sexual_conduct_detected": False,
        "victim_age_group": "menor de quince a\u00f1os",
        "relationship_to_aggressor": None,
        "violence_detected": True,
        "threat_detected": True,
        "unconscious_detected": False,
        "unable_to_resist_detected": False,
        "explicit_crime_mentioned": "No se mencion\u00f3 un crimen explicito.",
    }
    main.extract_facts_with_local_llm = (
        lambda facts: local_llm.apply_deterministic_fact_guardrails(facts, raw_extraction)
    )

    facts = (
        "El d\u00eda 15 de mayo de 2025, el C. Juan P\u00e9rez Garc\u00eda lleg\u00f3 en estado de "
        "ebriedad al domicilio conyugal. Agredi\u00f3 f\u00edsicamente a la v\u00edctima, su "
        "c\u00f3nyuge, con golpes en el rostro y brazos, caus\u00e1ndole hematomas visibles. "
        "El agresor amenaz\u00f3 a la v\u00edctima con privarla de la vida. Los hechos no son "
        "aislados; lleva dos a\u00f1os ejerciendo violencia f\u00edsica y psicol\u00f3gica de "
        "manera reiterada contra la v\u00edctima y contra sus dos hijos menores de edad, "
        "de 8 y 5 a\u00f1os, quienes han sido testigos presenciales."
    )

    payload = main.analyze_facts(FactInput(facts=facts))
    penal_articles = payload["candidate_articles"]["penal_articles"]

    assert payload["detected_crime_type"] == "violencia_familiar"
    assert payload["structured_facts"]["victim_age_group"] is None
    assert payload["structured_facts"]["relationship_to_aggressor"] == "c\u00f3nyuge"
    penal_numbers = [article["article_number"] for article in penal_articles]
    assert "178" in penal_numbers
    assert {"178", "125", "126", "131"}.issubset(set(penal_numbers))
    assert all(article["article_number"] != "164" for article in penal_articles)
