from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from ingest import generate_content_hash, parse_all_sources, parse_articles
from legal_rules import classify_article
from models import LegalArticle


TRACEABILITY_COLUMNS = {
    "source_type": "TEXT NOT NULL DEFAULT 'mock'",
    "source_url": "TEXT",
    "source_version": "TEXT",
    "last_reform_date": "TEXT",
    "legal_domain": "TEXT",
    "content_hash": "TEXT",
    "hierarchical_path": "TEXT",
}


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_schema()


def _ensure_sqlite_schema() -> None:
    with engine.begin() as connection:
        existing_columns = _get_table_columns(connection)

        for column_name, column_definition in TRACEABILITY_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE legal_articles ADD COLUMN {column_name} {column_definition}")
                )

        _backfill_content_hashes(connection)

        if _has_legacy_article_source_unique_constraint(connection):
            _rebuild_legal_articles_table(connection)


def _get_table_columns(connection) -> set[str]:
    rows = connection.execute(text("PRAGMA table_info(legal_articles)")).mappings().all()
    return {row["name"] for row in rows}


def _backfill_content_hashes(connection) -> None:
    rows = (
        connection.execute(
            text(
                """
                SELECT id, article_number, title, content
                FROM legal_articles
                WHERE content_hash IS NULL OR content_hash = ''
                """
            )
        )
        .mappings()
        .all()
    )

    for row in rows:
        content_hash = generate_content_hash(
            row["article_number"],
            row["title"],
            row["content"],
        )
        connection.execute(
            text("UPDATE legal_articles SET content_hash = :content_hash WHERE id = :id"),
            {"content_hash": content_hash, "id": row["id"]},
        )


def _has_legacy_article_source_unique_constraint(connection) -> bool:
    indexes = connection.execute(text("PRAGMA index_list(legal_articles)")).mappings().all()

    for index in indexes:
        if not index["unique"]:
            continue

        index_columns = (
            connection.execute(text(f"PRAGMA index_info({index['name']})"))
            .mappings()
            .all()
        )
        column_names = [column["name"] for column in index_columns]
        if column_names == ["article_number", "source_name"]:
            return True

    return False


def _rebuild_legal_articles_table(connection) -> None:
    connection.execute(text("ALTER TABLE legal_articles RENAME TO legal_articles_old"))
    _drop_named_indexes(connection, "legal_articles_old")
    Base.metadata.create_all(bind=connection)

    connection.execute(
        text(
            """
            INSERT INTO legal_articles (
                id,
                article_number,
                title,
                content,
                source_name,
                jurisdiction,
                is_active,
                applicability_type,
                source_type,
                source_url,
                source_version,
                last_reform_date,
                legal_domain,
                content_hash,
                hierarchical_path,
                created_at
            )
            SELECT
                id,
                article_number,
                title,
                content,
                source_name,
                jurisdiction,
                is_active,
                applicability_type,
                source_type,
                source_url,
                source_version,
                last_reform_date,
                legal_domain,
                content_hash,
                hierarchical_path,
                created_at
            FROM legal_articles_old
            """
        )
    )
    connection.execute(text("DROP TABLE legal_articles_old"))


def _drop_named_indexes(connection, table_name: str) -> None:
    indexes = connection.execute(text(f"PRAGMA index_list({table_name})")).mappings().all()

    for index in indexes:
        index_name = index["name"]
        if index_name.startswith("sqlite_autoindex"):
            continue
        connection.execute(text(f"DROP INDEX IF EXISTS {index_name}"))


def serialize_article(article: LegalArticle) -> dict:
    return {
        "article_number": article.article_number,
        "title": article.title,
        "content": article.content,
        "source_name": article.source_name,
        "jurisdiction": article.jurisdiction,
        "is_active": article.is_active,
        "source_type": article.source_type,
        "source_url": article.source_url,
        "source_version": article.source_version,
        "last_reform_date": article.last_reform_date,
        "legal_domain": article.legal_domain,
        "content_hash": article.content_hash,
        "hierarchical_path": article.hierarchical_path,
    }


def get_articles_from_db(db: Session | None = None) -> list[dict]:
    create_tables()
    owns_session = db is None
    session = db or SessionLocal()

    try:
        articles = (
            session.query(LegalArticle)
            .filter(LegalArticle.is_active.is_(True))
            .order_by(LegalArticle.id)
            .all()
        )
        return [serialize_article(article) for article in articles]
    finally:
        if owns_session:
            session.close()


def ingest_articles(filepath: str | Path | None = None, db: Session | None = None) -> int:
    create_tables()
    parsed_articles = parse_articles(filepath) if filepath else parse_articles()
    return ingest_parsed_articles(parsed_articles, db=db)


def ingest_all_sources(db: Session | None = None) -> int:
    create_tables()
    return ingest_parsed_articles(parse_all_sources(), db=db)


def ingest_parsed_articles(parsed_articles: list[dict], db: Session | None = None) -> int:
    owns_session = db is None
    session = db or SessionLocal()
    inserted_count = 0

    try:
        for article in parsed_articles:
            exact_article = (
                session.query(LegalArticle)
                .filter(
                    LegalArticle.source_name == article["source_name"],
                    LegalArticle.article_number == article["article_number"],
                    LegalArticle.content_hash == article["content_hash"],
                )
                .first()
            )

            if exact_article:
                active_articles = get_active_articles_for_source_article(session, article)
                for active_article in active_articles:
                    if active_article.id != exact_article.id:
                        active_article.is_active = False

                exact_article.is_active = True
                apply_article_metadata(exact_article, article)
                continue

            active_articles = get_active_articles_for_source_article(session, article)

            for active_article in active_articles:
                active_article.is_active = False

            session.add(
                LegalArticle(
                    article_number=article["article_number"],
                    title=article["title"],
                    content=article["content"],
                    source_name=article["source_name"],
                    jurisdiction=article["jurisdiction"],
                    is_active=article["is_active"],
                    applicability_type=classify_article(article),
                    source_type=article["source_type"],
                    source_url=article["source_url"],
                    source_version=article["source_version"],
                    last_reform_date=article["last_reform_date"],
                    legal_domain=article.get("legal_domain"),
                    content_hash=article["content_hash"],
                    hierarchical_path=article["hierarchical_path"],
                )
            )
            inserted_count += 1

        session.commit()
        return inserted_count
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        if owns_session:
            session.close()


def get_active_articles_for_source_article(session: Session, article: dict) -> list[LegalArticle]:
    return (
        session.query(LegalArticle)
        .filter(
            LegalArticle.source_name == article["source_name"],
            LegalArticle.article_number == article["article_number"],
            LegalArticle.is_active.is_(True),
        )
        .all()
    )


def apply_article_metadata(stored_article: LegalArticle, parsed_article: dict) -> None:
    stored_article.title = parsed_article["title"]
    stored_article.content = parsed_article["content"]
    stored_article.jurisdiction = parsed_article["jurisdiction"]
    stored_article.source_type = parsed_article["source_type"]
    stored_article.source_url = parsed_article["source_url"]
    stored_article.source_version = parsed_article["source_version"]
    stored_article.last_reform_date = parsed_article["last_reform_date"]
    stored_article.legal_domain = parsed_article.get("legal_domain")
    stored_article.hierarchical_path = parsed_article["hierarchical_path"]


if __name__ == "__main__":
    count = ingest_all_sources()
    print(f"Artículos insertados: {count}")
