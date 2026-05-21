from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from db_ingest import get_articles_from_db, ingest_articles


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
