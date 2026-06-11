import json

import pytest

import family_violence_review
from family_violence_review import (
    apply_family_violence_review,
    build_family_violence_review_catalog,
    get_family_violence_review_payload,
    validate_family_violence_review_record,
)
from ingest import parse_all_sources
from investigation_steps import get_investigation_steps
from schemas import FamilyViolenceReviewRecord


def build_record(
    catalog: list[dict],
    statuses: dict[str, str] | None = None,
) -> FamilyViolenceReviewRecord:
    statuses = statuses or {}
    return FamilyViolenceReviewRecord.model_validate(
        {
            "schema_version": 1,
            "crime_type": "violencia_familiar",
            "reviewer_name": "Lic. Persona Revisora",
            "reviewed_at": "2026-06-09T18:00:00-06:00",
            "decisions": [
                {
                    "diligence_id": item["diligence_id"],
                    "fingerprint": item["review_fingerprint"],
                    "status": statuses.get(item["diligence_id"], "pending"),
                    "observations": "",
                }
                for item in catalog
            ],
        }
    )


def write_record(path, record: FamilyViolenceReviewRecord):
    path.write_text(
        json.dumps(record.model_dump(mode="json"), ensure_ascii=False),
        encoding="utf-8",
    )


def test_review_payload_contains_full_catalog_and_synthetic_cases():
    payload = get_family_violence_review_payload(parse_all_sources())

    assert len(payload["catalog"]) == 7
    assert len(payload["synthetic_cases"]) == 7
    assert all(item["legal_review_status"] == "pending" for item in payload["catalog"])
    assert all(len(item["review_fingerprint"]) == 64 for item in payload["catalog"])
    assert {
        item["case_id"] for item in payload["synthetic_cases"]
    } == {
        "vf_case_physical_injuries",
        "vf_case_non_physical",
        "vf_case_death_threat",
        "vf_case_minors",
        "vf_case_explicit_negations",
        "vf_case_witness_interview",
        "vf_case_forensic_vs_therapy",
    }


def test_complete_review_record_is_normalized():
    articles = parse_all_sources()
    catalog = build_family_violence_review_catalog(articles)
    record = build_record(
        catalog,
        {"vf_medidas_proteccion_urgentes": "approved"},
    )

    normalized = validate_family_violence_review_record(record, articles)

    assert normalized["reviewer_name"] == "Lic. Persona Revisora"
    assert normalized["reviewed_at"] == "2026-06-10T00:00:00Z"
    assert len(normalized["decisions"]) == 7


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda decisions: decisions[0].update(
                {"diligence_id": "vf_diligencia_inexistente"}
            ),
            "Diligencia desconocida",
        ),
        (
            lambda decisions: decisions[0].update({"fingerprint": "0" * 64}),
            "Huella obsoleta",
        ),
        (
            lambda decisions: decisions.append(decisions[0].copy()),
            "Decision duplicada",
        ),
        (
            lambda decisions: decisions.pop(),
            "Faltan",
        ),
    ],
)
def test_review_validation_rejects_invalid_decisions(mutation, message):
    articles = parse_all_sources()
    catalog = build_family_violence_review_catalog(articles)
    payload = build_record(catalog).model_dump(mode="json")
    mutation(payload["decisions"])
    record = FamilyViolenceReviewRecord.model_validate(payload)

    with pytest.raises(ValueError, match=message):
        validate_family_violence_review_record(record, articles)


def test_current_approved_pending_and_rejected_decisions_are_applied(
    tmp_path,
    monkeypatch,
):
    articles = parse_all_sources()
    catalog = build_family_violence_review_catalog(articles)
    record = build_record(
        catalog,
        {
            "vf_recepcion_entrevista_inicial": "approved",
            "vf_medidas_proteccion_urgentes": "rejected",
        },
    )
    review_path = tmp_path / "family_violence.json"
    write_record(review_path, record)
    monkeypatch.setattr(family_violence_review, "REVIEW_RECORD_PATH", review_path)

    steps = get_investigation_steps(
        "violencia_familiar",
        articles=articles,
        facts="La pareja amenazo a la victima.",
    )
    by_id = {step["diligence_id"]: step for step in steps}

    assert by_id["vf_recepcion_entrevista_inicial"]["legal_review_status"] == "approved"
    assert "vf_medidas_proteccion_urgentes" not in by_id
    assert by_id["vf_evaluacion_psicologica_forense"]["legal_review_status"] == "pending"
    assert by_id["vf_estudio_trabajo_social"]["display_group"] == "preliminary"


def test_changed_diligence_invalidates_a_previous_approval(tmp_path, monkeypatch):
    articles = parse_all_sources()
    catalog = build_family_violence_review_catalog(articles)
    record = build_record(
        catalog,
        {"vf_recepcion_entrevista_inicial": "approved"},
    )
    review_path = tmp_path / "family_violence.json"
    write_record(review_path, record)
    monkeypatch.setattr(family_violence_review, "REVIEW_RECORD_PATH", review_path)

    changed = dict(catalog[0])
    changed["expected_result"] = "Resultado modificado despues del dictamen."
    result = apply_family_violence_review([changed])

    assert result[0]["legal_review_status"] == "pending"
    assert result[0]["review_is_current"] is False
