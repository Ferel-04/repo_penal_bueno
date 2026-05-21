from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UniqueConstraint, func

from database import Base


class LegalArticle(Base):
    __tablename__ = "legal_articles"
    __table_args__ = (
        UniqueConstraint("article_number", "source_name", name="uq_legal_articles_article_source"),
    )

    id = Column(Integer, primary_key=True, index=True)
    article_number = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    source_name = Column(String, nullable=False, index=True)
    jurisdiction = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    applicability_type = Column(String, nullable=False, default="otro")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
