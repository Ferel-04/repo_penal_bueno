from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UniqueConstraint, func

from database import Base


class LegalArticle(Base):
    __tablename__ = "legal_articles"
    __table_args__ = (
        UniqueConstraint(
            "source_name",
            "article_number",
            "content_hash",
            name="uq_legal_articles_source_article_hash",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    article_number = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    source_name = Column(String, nullable=False, index=True)
    jurisdiction = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    applicability_type = Column(String, nullable=False, default="otro")
    source_type = Column(String, nullable=False, default="mock")
    source_url = Column(String, nullable=True)
    source_version = Column(String, nullable=True)
    last_reform_date = Column(String, nullable=True)
    content_hash = Column(String, nullable=False, index=True)
    hierarchical_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
