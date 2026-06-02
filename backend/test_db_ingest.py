from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from db_ingest import get_articles_from_db, ingest_all_sources, ingest_articles
from models import LegalArticle


def test_ingest_articles_uses_temp_sqlite_and_avoids_duplicates(tmp_path, monkeypatch):
    temp_db_path = tmp_path / "test_penal_mvp.db"
    temp_engine = create_engine(
        f"sqlite:///{temp_db_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)

    monkeypatch.setattr("db_ingest.engine", temp_engine)
    Base.metadata.create_all(bind=temp_engine)

    session = TestingSessionLocal()
    try:
        first_insert_count = ingest_articles(db=session)
        second_insert_count = ingest_articles(db=session)
        articles = get_articles_from_db(db=session)
    finally:
        session.close()

    assert first_insert_count == 3
    assert second_insert_count == 0
    assert [article["article_number"] for article in articles] == ["164", "165", "166"]
    assert all(article["content_hash"] for article in articles)
    assert {article["source_version"] for article in articles} == {"2026-05-24"}
    assert {article["last_reform_date"] for article in articles} == {"2026-05-24"}


def test_ingest_all_sources_loads_articles_from_four_mock_sources(tmp_path, monkeypatch):
    temp_db_path = tmp_path / "test_legal_sources.db"
    temp_engine = create_engine(
        f"sqlite:///{temp_db_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)

    monkeypatch.setattr("db_ingest.engine", temp_engine)
    Base.metadata.create_all(bind=temp_engine)

    session = TestingSessionLocal()
    try:
        inserted_count = ingest_all_sources(db=session)
        articles = get_articles_from_db(db=session)
    finally:
        session.close()

    assert inserted_count == 13
    assert len(articles) == 13
    assert {
        article["source_name"]
        for article in articles
    } == {
        "Código Penal para el Estado de Michoacán MOCK",
        "Código Nacional de Procedimientos Penales MOCK",
        "Ley General de Víctimas MOCK",
        "Constitución Política de los Estados Unidos Mexicanos MOCK",
    }
    assert {article["source_version"] for article in articles} == {"2026-05-24"}
    assert {article["last_reform_date"] for article in articles} == {"2026-05-24"}
    assert {article["legal_domain"] for article in articles} == {
        "penal",
        "procesal",
        "victimas",
        "constitucional",
    }


def test_ingest_articles_keeps_history_when_content_changes(tmp_path, monkeypatch):
    temp_db_path = tmp_path / "test_penal_history.db"
    temp_engine = create_engine(
        f"sqlite:///{temp_db_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)

    first_source = tmp_path / "first_version.txt"
    first_source.write_text(
        "Artículo 1. Prueba.\nContenido inicial.",
        encoding="utf-8",
    )
    second_source = tmp_path / "second_version.txt"
    second_source.write_text(
        "Artículo 1. Prueba.\nContenido reformado.",
        encoding="utf-8",
    )

    monkeypatch.setattr("db_ingest.engine", temp_engine)
    Base.metadata.create_all(bind=temp_engine)

    session = TestingSessionLocal()
    try:
        first_insert_count = ingest_articles(first_source, db=session)
        second_insert_count = ingest_articles(second_source, db=session)
        stored_articles = (
            session.query(LegalArticle)
            .filter(LegalArticle.article_number == "1")
            .order_by(LegalArticle.id)
            .all()
        )
    finally:
        session.close()

    assert first_insert_count == 1
    assert second_insert_count == 1
    assert len(stored_articles) == 2
    assert stored_articles[0].is_active is False
    assert stored_articles[1].is_active is True
    assert stored_articles[0].content_hash != stored_articles[1].content_hash
