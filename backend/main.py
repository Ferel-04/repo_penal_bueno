from fastapi import FastAPI, HTTPException

from db_ingest import get_articles_from_db
from ingest import parse_articles
from legal_rules import analyze_facts_deterministically, search_local_articles
from schemas import FactInput, SearchInput


app = FastAPI(title="MVP Asistente Penal Michoacán")


def load_articles() -> list[dict]:
    try:
        db_articles = get_articles_from_db()
        if db_articles:
            return db_articles
    except Exception:
        pass

    try:
        return parse_articles()
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

    return analyze_facts_deterministically(facts, load_articles())


@app.post("/api/analyze")
def analyze_facts_legacy(input_data: FactInput):
    return {
        "status": "success",
        "mock_result": "Simulación de encuadre.",
    }
