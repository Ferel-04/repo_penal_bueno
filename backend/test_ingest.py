from pathlib import Path

import pytest

from ingest import JURISDICTION, SOURCE_NAME, parse_articles


def test_parse_articles_supports_basic_uppercase_and_bis_patterns(tmp_path: Path):
    legal_text = """
ARTÍCULO 1. Tipo base.
Contenido del primer artículo.

Artículo 2 Bis. Variante bis.
Contenido del artículo bis.

Artículo 3.
Contenido sin título.
"""
    source_file = tmp_path / "mock_code.txt"
    source_file.write_text(legal_text, encoding="utf-8")

    articles = parse_articles(source_file)

    assert len(articles) == 3
    assert articles[0]["article_number"] == "1"
    assert articles[0]["title"] == "Tipo base."
    assert articles[1]["article_number"] == "2 Bis"
    assert articles[1]["title"] == "Variante bis."
    assert articles[2]["article_number"] == "3"
    assert articles[2]["title"] is None

    for article in articles:
        assert article["source_name"] == SOURCE_NAME
        assert article["jurisdiction"] == JURISDICTION
        assert article["is_active"] is True


def test_parse_articles_raises_file_not_found_for_missing_file(tmp_path: Path):
    missing_file = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        parse_articles(missing_file)
