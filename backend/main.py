from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db_ingest import get_articles_from_db
from family_violence_review import (
    get_family_violence_review_payload,
    validate_family_violence_review_record,
)
from ingest import parse_all_sources
from legal_rules import analyze_facts_deterministically, search_local_articles
from local_llm import extract_facts_with_local_llm
from schemas import FactInput, FamilyViolenceReviewRecord, SearchInput


app = FastAPI(title="MVP Asistente Penal Michoacán")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https://[a-zA-Z0-9-]+\.vercel\.app",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_articles() -> list[dict]:
    try:
        db_articles = get_articles_from_db()
        if db_articles:
            has_mock = any("MOCK" in (a.get("source_name") or "") for a in db_articles)
            if not has_mock:
                return db_articles
    except Exception:
        pass

    try:
        return parse_all_sources()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/")
def read_root():
    return {
        "message": "API Backend Activa - MVP Penal Michoacán",
        "endpoints": ["/articles", "/search", "/analyze"],
    }


@app.get("/articles")
def get_articles():
    articles = load_articles()
    return {
        "total_articles": len(articles),
        "articles": articles,
    }


@app.post("/search")
def search_articles(input_data: SearchInput):
    query = input_data.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="El campo query no puede estar vacío.")

    results = search_local_articles(query, load_articles())

    return {
        "query": query,
        "total_results": len(results),
        "results": results,
    }


@app.post("/analyze")
def analyze_facts(input_data: FactInput):
    facts = input_data.facts.strip()
    if not facts:
        raise HTTPException(status_code=400, detail="El campo facts no puede estar vacío.")

    structured_facts = extract_facts_with_local_llm(facts)
    analysis_engine = "local_llm" if structured_facts else "deterministic_fallback"

    return analyze_facts_deterministically(
        facts,
        load_articles(),
        structured_facts=structured_facts,
        analysis_engine=analysis_engine,
        crime_type=input_data.crime_type,
    )


@app.get("/review/family-violence")
def get_family_violence_review():
    return get_family_violence_review_payload(load_articles())


@app.post("/review/family-violence/validate")
def validate_family_violence_review(input_data: FamilyViolenceReviewRecord):
    try:
        normalized = validate_family_violence_review_record(
            input_data,
            load_articles(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "valid": True,
        "record": normalized,
    }


@app.post("/api/analyze")
def analyze_facts_legacy(input_data: FactInput):
    return {
        "status": "success",
        "mock_result": "Simulación de encuadre.",
    }
