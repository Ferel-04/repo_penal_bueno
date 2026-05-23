import hashlib
import re
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"
LEGAL_SOURCES_DIR = DATA_DIR / "legal_sources"
LEGACY_CPEM_PATH = DATA_DIR / "cpem_mock.txt"
DEFAULT_DATA_PATH = LEGAL_SOURCES_DIR / "cpem_mock.txt"

SOURCE_NAME = "Código Penal para el Estado de Michoacán MOCK"
JURISDICTION = "Michoacán"
SOURCE_TYPE = "mock"
SOURCE_URL = None
SOURCE_VERSION = "mock-v1"
LAST_REFORM_DATE = None

SOURCE_METADATA_BY_FILE = {
    "cpem_mock.txt": {
        "source_name": SOURCE_NAME,
        "source_type": SOURCE_TYPE,
        "jurisdiction": JURISDICTION,
        "source_version": SOURCE_VERSION,
        "source_url": SOURCE_URL,
        "last_reform_date": LAST_REFORM_DATE,
    },
    "cnpp_mock.txt": {
        "source_name": "Código Nacional de Procedimientos Penales MOCK",
        "source_type": "mock",
        "jurisdiction": "Federal",
        "source_version": "mock-v1",
        "source_url": None,
        "last_reform_date": None,
    },
    "lgv_mock.txt": {
        "source_name": "Ley General de Víctimas MOCK",
        "source_type": "mock",
        "jurisdiction": "Federal",
        "source_version": "mock-v1",
        "source_url": None,
        "last_reform_date": None,
    },
    "constitucion_mock.txt": {
        "source_name": "Constitución Política de los Estados Unidos Mexicanos MOCK",
        "source_type": "mock",
        "jurisdiction": "Federal",
        "source_version": "mock-v1",
        "source_url": None,
        "last_reform_date": None,
    },
}
SOURCE_LOAD_ORDER = [
    "cpem_mock.txt",
    "cnpp_mock.txt",
    "lgv_mock.txt",
    "constitucion_mock.txt",
]

ARTICLE_PATTERN = re.compile(
    r"(?im)^[^\S\r\n]*(?:art(?:[ií]culo)?\.?)\s+"
    r"(\d+(?:[^\S\r\n]*(?:-| )[^\S\r\n]*bis)?)"
    r"[^\S\r\n]*(?:\.[^\S\r\n]*(.*?))?[^\S\r\n]*$"
)
HEADING_PATTERN = re.compile(
    r"(?im)^[^\S\r\n]*(LIBRO|T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N)[^\r\n]*$"
)


def normalize_article_number(value: str) -> str:
    value = re.sub(r"\s*-\s*", " ", value)
    return " ".join(value.title().split())


def generate_content_hash(article_number: str, title: str | None, content: str) -> str:
    canonical_text = "\n".join(
        [
            article_number.strip(),
            (title or "").strip(),
            "\n".join(line.strip() for line in content.strip().splitlines()),
        ]
    )
    return hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()


def get_source_metadata(filepath: str | Path) -> dict:
    path = Path(filepath)
    return SOURCE_METADATA_BY_FILE.get(
        path.name,
        SOURCE_METADATA_BY_FILE["cpem_mock.txt"],
    )


def build_hierarchical_path(
    text: str,
    article_start: int,
    article_number: str,
    source_name: str,
) -> str:
    headings_by_type = {}

    for heading in HEADING_PATTERN.finditer(text[:article_start]):
        heading_type = heading.group(1).casefold()
        headings_by_type[heading_type] = " ".join(heading.group(0).split())

    headings = list(headings_by_type.values())
    return " > ".join([source_name, *headings, f"Artículo {article_number}"])


def parse_articles(filepath: str | Path = DEFAULT_DATA_PATH) -> list[dict]:
    """Parse legal articles from one plain text source."""
    path = Path(filepath)
    if not path.exists() and path == DEFAULT_DATA_PATH and LEGACY_CPEM_PATH.exists():
        path = LEGACY_CPEM_PATH
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    metadata = get_source_metadata(path)
    text = path.read_text(encoding="utf-8")
    matches = list(ARTICLE_PATTERN.finditer(text))
    articles = []

    for index, match in enumerate(matches):
        content_start = match.end()
        content_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)

        article_number = normalize_article_number(match.group(1))
        title = match.group(2).strip() or None
        body = text[content_start:content_end].strip()

        article = {
            "article_number": article_number,
            "title": title,
            "content": body,
            "source_name": metadata["source_name"],
            "jurisdiction": metadata["jurisdiction"],
            "is_active": True,
            "source_type": metadata["source_type"],
            "source_url": metadata["source_url"],
            "source_version": metadata["source_version"],
            "last_reform_date": metadata["last_reform_date"],
            "content_hash": generate_content_hash(article_number, title, body),
            "hierarchical_path": build_hierarchical_path(
                text,
                match.start(),
                article_number,
                metadata["source_name"],
            ),
        }
        articles.append(article)

    return articles


def parse_source(source_filename: str, source_dir: str | Path = LEGAL_SOURCES_DIR) -> list[dict]:
    return parse_articles(Path(source_dir) / source_filename)


def parse_all_sources(source_dir: str | Path = LEGAL_SOURCES_DIR) -> list[dict]:
    source_path = Path(source_dir)
    articles = []

    for filename in SOURCE_LOAD_ORDER:
        file_path = source_path / filename
        if file_path.exists():
            articles.extend(parse_articles(file_path))

    for file_path in sorted(source_path.glob("*.txt")):
        if file_path.name not in SOURCE_LOAD_ORDER:
            articles.extend(parse_articles(file_path))

    return articles


def parse_legal_text(filepath: str | Path = DEFAULT_DATA_PATH) -> list[dict]:
    """Backward-compatible alias for older local scripts."""
    return parse_articles(filepath)


if __name__ == "__main__":
    import json

    print(json.dumps(parse_all_sources(), indent=2, ensure_ascii=False))
