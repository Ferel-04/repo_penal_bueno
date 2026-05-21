from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from ingest import parse_articles
from legal_rules import classify_article
from models import LegalArticle


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def serialize_article(article: LegalArticle) -> dict:
    return {
        "article_number": article.article_number,
        "title": article.title,
        "content": article.content,
        "source_name": article.source_name,
        "jurisdiction": article.jurisdiction,
        "is_active": article.is_active,
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
    owns_session = db is None
    session = db or SessionLocal()
    inserted_count = 0

    try:
        for article in parsed_articles:
            existing_article = (
                session.query(LegalArticle)
                .filter(
                    LegalArticle.article_number == article["article_number"],
                    LegalArticle.source_name == article["source_name"],
                )
                .first()
            )

            if existing_article:
                continue

            session.add(
                LegalArticle(
                    article_number=article["article_number"],
                    title=article["title"],
                    content=article["content"],
                    source_name=article["source_name"],
                    jurisdiction=article["jurisdiction"],
                    is_active=article["is_active"],
                    applicability_type=classify_article(article),
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


if __name__ == "__main__":
    count = ingest_articles()
    print(f"Artículos insertados: {count}")
