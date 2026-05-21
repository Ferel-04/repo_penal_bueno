import re
from pathlib import Path


SOURCE_NAME = "Código Penal para el Estado de Michoacán MOCK"
JURISDICTION = "Michoacán"
DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "cpem_mock.txt"


ARTICLE_PATTERN = re.compile(
    r"(?im)^[^\S\r\n]*art[ií]culo[^\S\r\n]+(\d+(?:[^\S\r\n]+bis)?)[^\S\r\n]*\.[^\S\r\n]*(.*?)[^\S\r\n]*$"
)


def parse_articles(filepath: str | Path = DEFAULT_DATA_PATH) -> list[dict]:
    """Parse legal articles from a plain text file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    text = path.read_text(encoding="utf-8")
    matches = list(ARTICLE_PATTERN.finditer(text))
    articles = []

    for index, match in enumerate(matches):
        content_start = match.end()
        content_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)

        article_number = " ".join(match.group(1).title().split())
        title = match.group(2).strip() or None
        body = text[content_start:content_end].strip()

        article = {
            "article_number": article_number,
            "title": title,
            "content": body,
            "source_name": SOURCE_NAME,
            "jurisdiction": JURISDICTION,
            "is_active": True,
        }
        articles.append(article)

    return articles


def parse_legal_text(filepath: str | Path = DEFAULT_DATA_PATH) -> list[dict]:
    """Backward-compatible alias for older local scripts."""
    return parse_articles(filepath)


if __name__ == "__main__":
    import json

    print(json.dumps(parse_articles(), indent=2, ensure_ascii=False))
