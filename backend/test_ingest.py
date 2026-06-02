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


def test_parse_articles_supports_basic_uppercase_bis_and_ordinal_patterns(tmp_path: Path):
    legal_text = """
ART\u00cdCULO 1. Tipo base.
Contenido del primer articulo.

Articulo 2 Bis. Variante bis.
Contenido del articulo bis.

Articulo 3.
Contenido sin titulo.

Art. 4. Abreviado.
Contenido con encabezado abreviado.

Articulo 5-Bis. Guion bis.
Contenido con bis separado por guion.

Articulo 1o. Ordinal.
Contenido con ordinal.
"""
    source_file = tmp_path / "mock_code.txt"
    source_file.write_text(legal_text, encoding="utf-8")

    articles = parse_articles(source_file)

    assert len(articles) == 6
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
    assert articles[5]["article_number"] == "1o"
    assert articles[5]["title"] == "Ordinal."

    for article in articles:
        assert article["source_name"] == SOURCE_NAME
        assert article["jurisdiction"] == JURISDICTION
        assert article["is_active"] is True
        assert article["source_type"] == "mock"
        assert article["source_version"] == "mock-v1"
        assert len(article["content_hash"]) == 64
        assert article["hierarchical_path"].endswith(article["article_number"])


def test_generate_content_hash_changes_when_content_changes():
    first_hash = generate_content_hash("164", "Violacion.", "Contenido inicial.")
    second_hash = generate_content_hash("164", "Violacion.", "Contenido reformado.")

    assert first_hash != second_hash
    assert len(first_hash) == 64


def test_parse_all_sources_loads_real_federal_sources():
    articles = parse_all_sources()
    source_names = {article["source_name"] for article in articles}

    assert len(articles) > 800
    assert {
        "C\u00f3digo Nacional de Procedimientos Penales",
        "Ley General de V\u00edctimas",
        "Constituci\u00f3n Pol\u00edtica de los Estados Unidos Mexicanos",
    }.issubset(source_names)
    assert any("MOCK" in source_name for source_name in source_names)
    assert {article["source_version"] for article in articles} == {
        "2026-05-24",
        "2025-11-28",
        "2024-04-01",
        "2026-05-06",
    }
    assert {article["last_reform_date"] for article in articles} == {
        "2026-05-24",
        "2025-11-28",
        "2024-04-01",
        "2026-05-06",
    }
    assert {article["source_type"] for article in articles} == {
        "official_text_manual_load",
        "official_pdf_extract",
    }
    assert {article["legal_domain"] for article in articles} == {
        "penal",
        "procesal",
        "victimas",
        "constitucional",
    }


def test_load_source_metadata_reads_metadata_json():
    metadata = load_source_metadata(
        "backend/data/legal_sources/federal/cnpp/2025-11-28.txt"
    )

    assert metadata["source_name"] == "C\u00f3digo Nacional de Procedimientos Penales"
    assert metadata["jurisdiction"] == "Federal"
    assert metadata["source_type"] == "official_pdf_extract"
    assert metadata["source_version"] == "2025-11-28"
    assert metadata["last_reform_date"] == "2025-11-28"
    assert metadata["legal_domain"] == "procesal"


def test_parse_all_sources_raises_clear_error_when_metadata_is_missing(tmp_path: Path):
    source_dir = tmp_path / "legal_sources"
    source_file = source_dir / "federal" / "missing_metadata_source" / "2026-05-24.txt"
    source_file.parent.mkdir(parents=True)
    source_file.write_text("Articulo 1. Prueba.\nContenido.", encoding="utf-8")

    with pytest.raises(MissingMetadataError, match="Falta metadata.json"):
        parse_all_sources(source_dir)


def test_parse_articles_raises_file_not_found_for_missing_file(tmp_path: Path):
    missing_file = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        parse_articles(missing_file)
