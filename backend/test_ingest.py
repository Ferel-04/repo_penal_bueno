from pathlib import Path

import pytest

from ingest import JURISDICTION, SOURCE_NAME, generate_content_hash, parse_all_sources, parse_articles


def test_parse_articles_supports_basic_uppercase_and_bis_patterns(tmp_path: Path):
    legal_text = """
ARTÍCULO 1. Tipo base.
Contenido del primer artículo.

Artículo 2 Bis. Variante bis.
Contenido del artículo bis.

Artículo 3.
Contenido sin título.

Art. 4. Abreviado.
Contenido con encabezado abreviado.

Artículo 5-Bis. Guion bis.
Contenido con bis separado por guion.
"""
    source_file = tmp_path / "mock_code.txt"
    source_file.write_text(legal_text, encoding="utf-8")

    articles = parse_articles(source_file)

    assert len(articles) == 5
    assert articles[0]["article_number"] == "1"
    assert articles[0]["title"] == "Tipo base."
    assert articles[1]["article_number"] == "2 Bis"
    assert articles[1]["title"] == "Variante bis."
    assert articles[2]["article_number"] == "3"
    assert articles[2]["title"] is None
    assert articles[3]["article_number"] == "4"
    assert articles[3]["title"] == "Abreviado."
    assert articles[4]["article_number"] == "5 Bis"
    assert articles[4]["title"] == "Guion bis."

    for article in articles:
        assert article["source_name"] == SOURCE_NAME
        assert article["jurisdiction"] == JURISDICTION
        assert article["is_active"] is True
        assert article["source_type"] == "mock"
        assert article["source_version"] == "mock-v1"
        assert len(article["content_hash"]) == 64
        assert article["hierarchical_path"].endswith(f"Artículo {article['article_number']}")


def test_generate_content_hash_changes_when_content_changes():
    first_hash = generate_content_hash("164", "Violación.", "Contenido inicial.")
    second_hash = generate_content_hash("164", "Violación.", "Contenido reformado.")

    assert first_hash != second_hash
    assert len(first_hash) == 64


def test_parse_all_sources_loads_four_mock_sources():
    articles = parse_all_sources()
    source_names = {article["source_name"] for article in articles}

    assert len(articles) == 13
    assert source_names == {
        "Código Penal para el Estado de Michoacán MOCK",
        "Código Nacional de Procedimientos Penales MOCK",
        "Ley General de Víctimas MOCK",
        "Constitución Política de los Estados Unidos Mexicanos MOCK",
    }


def test_parse_articles_raises_file_not_found_for_missing_file(tmp_path: Path):
    missing_file = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        parse_articles(missing_file)
