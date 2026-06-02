import hashlib
import json
import re
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"
LEGAL_SOURCES_DIR = DATA_DIR / "legal_sources"
LEGACY_CPEM_PATH = DATA_DIR / "cpem_mock.txt"
DEFAULT_DATA_PATH = LEGAL_SOURCES_DIR / "michoacan" / "codigo_penal" / "2026-05-24.txt"

SOURCE_NAME = "Código Penal para el Estado de Michoacán MOCK"
JURISDICTION = "Michoacán"
SOURCE_TYPE = "mock"
SOURCE_URL = None
SOURCE_VERSION = "mock-v1"
LAST_REFORM_DATE = None
LEGAL_DOMAIN = "penal"

REQUIRED_METADATA_FIELDS = {
    "source_name",
    "jurisdiction",
    "source_type",
    "source_url",
    "source_version",
    "last_reform_date",
    "legal_domain",
}

SOURCE_METADATA_BY_FILE = {
    "cpem_mock.txt": {
        "source_name": SOURCE_NAME,
        "source_type": SOURCE_TYPE,
        "jurisdiction": JURISDICTION,
        "source_version": SOURCE_VERSION,
        "source_url": SOURCE_URL,
        "last_reform_date": LAST_REFORM_DATE,
        "legal_domain": LEGAL_DOMAIN,
    },
    "cnpp_mock.txt": {
        "source_name": "Código Nacional de Procedimientos Penales MOCK",
        "source_type": "mock",
        "jurisdiction": "Federal",
        "source_version": "mock-v1",
        "source_url": None,
        "last_reform_date": None,
        "legal_domain": "procesal",
    },
    "lgv_mock.txt": {
        "source_name": "Ley General de Víctimas MOCK",
        "source_type": "mock",
        "jurisdiction": "Federal",
        "source_version": "mock-v1",
        "source_url": None,
        "last_reform_date": None,
        "legal_domain": "victimas",
    },
    "constitucion_mock.txt": {
        "source_name": "Constitución Política de los Estados Unidos Mexicanos MOCK",
        "source_type": "mock",
        "jurisdiction": "Federal",
        "source_version": "mock-v1",
        "source_url": None,
        "last_reform_date": None,
        "legal_domain": "constitucional",
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


class MissingMetadataError(FileNotFoundError):
    pass


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


def load_source_metadata(filepath: str | Path, source_root: str | Path = LEGAL_SOURCES_DIR) -> dict:
    path = Path(filepath)
    metadata_path = path.parent / "metadata.json"

    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        validate_metadata(metadata, metadata_path)
        return metadata

    source_root = Path(source_root)
    if is_legacy_flat_source(path, source_root):
        return SOURCE_METADATA_BY_FILE[path.name]

    if is_inside(path, source_root):
        raise MissingMetadataError(f"Falta metadata.json para la fuente legal: {path}")

    return SOURCE_METADATA_BY_FILE["cpem_mock.txt"]


def validate_metadata(metadata: dict, metadata_path: Path) -> None:
    missing_fields = sorted(REQUIRED_METADATA_FIELDS - set(metadata))
    if missing_fields:
        missing_text = ", ".join(missing_fields)
        raise ValueError(f"metadata.json incompleto en {metadata_path}: faltan {missing_text}")


def is_legacy_flat_source(path: Path, source_root: Path) -> bool:
    return path.parent.resolve() == source_root.resolve() and path.name in SOURCE_METADATA_BY_FILE


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def build_hierarchical_path(article_number: str, metadata: dict) -> str:
    return " > ".join(
        [
            metadata["jurisdiction"],
            metadata["source_name"],
            f"Artículo {article_number}",
        ]
    )


def parse_articles(
    filepath: str | Path = DEFAULT_DATA_PATH,
    source_root: str | Path = LEGAL_SOURCES_DIR,
) -> list[dict]:
    """Parse legal articles from one plain text source."""
    path = Path(filepath)
    if not path.exists() and path == DEFAULT_DATA_PATH and LEGACY_CPEM_PATH.exists():
        path = LEGACY_CPEM_PATH
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    metadata = load_source_metadata(path, source_root)
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
            "legal_domain": metadata["legal_domain"],
            "content_hash": generate_content_hash(article_number, title, body),
            "hierarchical_path": build_hierarchical_path(article_number, metadata),
        }
        articles.append(article)

    return articles


def parse_source(source_filename: str, source_dir: str | Path = LEGAL_SOURCES_DIR) -> list[dict]:
    return parse_articles(Path(source_dir) / source_filename, source_root=source_dir)


def find_versioned_source_files(source_dir: str | Path = LEGAL_SOURCES_DIR) -> list[Path]:
    source_path = Path(source_dir)
    return sorted(
        file_path
        for file_path in source_path.rglob("*.txt")
        if (file_path.parent / "metadata.json").exists()
    )


def find_legacy_source_files(source_dir: str | Path = LEGAL_SOURCES_DIR) -> list[Path]:
    source_path = Path(source_dir)
    ordered_paths = [
        source_path / filename
        for filename in SOURCE_LOAD_ORDER
        if (source_path / filename).exists()
    ]
    extra_paths = sorted(
        file_path
        for file_path in source_path.glob("*.txt")
        if file_path.name not in SOURCE_LOAD_ORDER
    )
    return ordered_paths + extra_paths


def find_missing_metadata_source_files(source_dir: str | Path = LEGAL_SOURCES_DIR) -> list[Path]:
    source_path = Path(source_dir)
    return sorted(
        file_path
        for file_path in source_path.rglob("*.txt")
        if file_path.parent != source_path and not (file_path.parent / "metadata.json").exists()
    )


def parse_all_sources(source_dir: str | Path = LEGAL_SOURCES_DIR) -> list[dict]:
    source_path = Path(source_dir)
    articles = []
    versioned_files = find_versioned_source_files(source_path)
    missing_metadata_files = find_missing_metadata_source_files(source_path)

    if missing_metadata_files:
        raise MissingMetadataError(
            f"Falta metadata.json para la fuente legal: {missing_metadata_files[0]}"
        )

    if versioned_files:
        for file_path in versioned_files:
            articles.extend(parse_articles(file_path, source_root=source_path))
        return articles

    for file_path in find_legacy_source_files(source_path):
        articles.extend(parse_articles(file_path, source_root=source_path))

    return articles


def parse_legal_text(filepath: str | Path = DEFAULT_DATA_PATH) -> list[dict]:
    """Backward-compatible alias for older local scripts."""
    return parse_articles(filepath)


if __name__ == "__main__":
    print(json.dumps(parse_all_sources(), indent=2, ensure_ascii=False))
