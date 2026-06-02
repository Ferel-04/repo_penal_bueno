from pathlib import Path

import pytest

from ingest import (
    JURISDICTION,
    SOURCE_NAME,
    MissingMetadataError,
    generate_content_hash,
    load_source_metadata,
    parse_all_sources,
    parse_articles,
)


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
    assert {article["source_version"] for article in articles} == {"2026-05-24"}
    assert {article["last_reform_date"] for article in articles} == {"2026-05-24"}
    assert {article["source_type"] for article in articles} == {"official_text_manual_load"}
    assert {article["legal_domain"] for article in articles} == {
        "penal",
        "procesal",
        "victimas",
        "constitucional",
    }


def test_load_source_metadata_reads_metadata_json():
    metadata = load_source_metadata(
        "backend/data/legal_sources/federal/cnpp/2026-05-24.txt"
    )

    assert metadata["source_name"] == "Código Nacional de Procedimientos Penales MOCK"
    assert metadata["jurisdiction"] == "Federal"
    assert metadata["source_type"] == "official_text_manual_load"
    assert metadata["source_version"] == "2026-05-24"
    assert metadata["last_reform_date"] == "2026-05-24"
    assert metadata["legal_domain"] == "procesal"


def test_parse_all_sources_raises_clear_error_when_metadata_is_missing(tmp_path: Path):
    source_dir = tmp_path / "legal_sources"
    source_file = source_dir / "federal" / "missing_metadata_source" / "2026-05-24.txt"
    source_file.parent.mkdir(parents=True)
    source_file.write_text("Artículo 1. Prueba.\nContenido.", encoding="utf-8")

    with pytest.raises(MissingMetadataError, match="Falta metadata.json"):
        parse_all_sources(source_dir)


def test_parse_articles_raises_file_not_found_for_missing_file(tmp_path: Path):
    missing_file = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        parse_articles(missing_file)
