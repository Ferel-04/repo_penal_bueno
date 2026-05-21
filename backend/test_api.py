from fastapi.testclient import TestClient

import main
from ingest import parse_articles


client = TestClient(main.app)


def setup_function():
    main.load_articles = parse_articles


def test_articles_endpoint_returns_mock_articles():
    response = client.get("/articles")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_articles"] == 3
    assert [article["article_number"] for article in payload["articles"]] == ["164", "165", "166"]


def test_search_endpoint_finds_text_matches_and_classifies_results():
    response = client.post("/search", json={"query": "violación"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "violación"
    assert payload["total_results"] == 3

    classifications = {
        result["article_number"]: result["classification"]
        for result in payload["results"]
    }
    assert classifications["164"] == "tipo_penal_base"
    assert classifications["165"] == "violacion_equiparada"
    assert classifications["166"] == "agravante"


def test_search_endpoint_rejects_empty_query():
    response = client.post("/search", json={"query": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "El campo query no puede estar vacío."


def test_analyze_endpoint_detects_topics_and_returns_candidates():
    response = client.post(
        "/analyze",
        json={
            "facts": (
                "La víctima menor fue amenazada con violencia y existe una posible "
                "relación familiar."
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["human_review_required"] is True
    assert payload["detected_legal_topics"] == ["familiar", "menor", "violencia", "amenaza"]
    assert payload["facts_summary"].startswith("La víctima menor")
    assert payload["missing_questions"] == [
        "¿La víctima podía comprender el significado del hecho y resistirlo?"
    ]

    article_numbers = {
        article["article_number"]
        for article in payload["candidate_articles"]
    }
    assert {"164", "165", "166"}.issubset(article_numbers)


def test_analyze_endpoint_rejects_empty_facts():
    response = client.post("/analyze", json={"facts": ""})

    assert response.status_code == 400
    assert response.json()["detail"] == "El campo facts no puede estar vacío."
