import hashlib
import json
from datetime import timezone
from pathlib import Path

from family_violence_steps import build_family_violence_steps
from schemas import FamilyViolenceReviewRecord


REVIEW_RECORD_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "legal_reviews"
    / "family_violence.json"
)

FINGERPRINT_FIELDS = [
    "diligence_id",
    "step",
    "legal_basis",
    "urgent",
    "category",
    "display_group",
    "purpose",
    "applicability_condition",
    "responsible_authority",
    "priority",
    "expected_result",
    "warnings",
    "foundations",
]

SYNTHETIC_REVIEW_CASES = [
    {
        "case_id": "vf_case_physical_injuries",
        "title": "Violencia fisica con lesiones",
        "facts": (
            "La victima refiere que su pareja la golpeo en el rostro y brazos, "
            "causandole hematomas visibles."
        ),
        "expected_active_diligence_ids": [
            "vf_recepcion_entrevista_inicial",
            "vf_medidas_proteccion_urgentes",
            "vf_evaluacion_medico_forense",
            "vf_evaluacion_psicologica_forense",
            "vf_estudio_trabajo_social",
            "vf_consulta_antecedentes_relacionados",
        ],
        "review_focus": "La evaluacion medico-forense debe activarse por lesiones reportadas.",
    },
    {
        "case_id": "vf_case_non_physical",
        "title": "Violencia psicologica y economica sin lesiones",
        "facts": (
            "La pareja controla el dinero, insulta y amenaza de forma reiterada. "
            "No hubo golpes ni lesiones."
        ),
        "expected_inactive_diligence_ids": ["vf_evaluacion_medico_forense"],
        "review_focus": "La ausencia explicita de lesiones no debe activar el peritaje medico.",
    },
    {
        "case_id": "vf_case_death_threat",
        "title": "Amenaza de muerte y evaluacion de riesgo",
        "facts": "La pareja amenazo a la victima con privarla de la vida.",
        "expected_trigger": "Amenaza de muerte reportada como factor de riesgo",
        "review_focus": (
            "La amenaza activa la evaluacion de riesgo, pero no selecciona "
            "automaticamente una medida del articulo 137."
        ),
    },
    {
        "case_id": "vf_case_minors",
        "title": "Personas menores como victimas o testigos",
        "facts": (
            "La victima refiere violencia familiar. Sus hijos menores de 8 y 5 anos "
            "presenciaron los hechos."
        ),
        "expected_active_diligence_ids": ["vf_entrevista_especializada_nna"],
        "review_focus": "La entrevista especializada permanece preliminar hasta contar con fuente.",
    },
    {
        "case_id": "vf_case_explicit_negations",
        "title": "Negacion de lesiones y de presencia de menores",
        "facts": (
            "La victima refiere violencia familiar sin describir lesiones ni personas "
            "menores de edad."
        ),
        "expected_inactive_diligence_ids": [
            "vf_evaluacion_medico_forense",
            "vf_entrevista_especializada_nna",
        ],
        "review_focus": "Las negaciones expresas deben impedir activaciones condicionales.",
    },
    {
        "case_id": "vf_case_witness_interview",
        "title": "Entrevista en calidad de testigo",
        "facts": (
            "Una vecina presencio las agresiones y sera entrevistada en calidad de testigo."
        ),
        "expected_foundation": "CNPP 251, fraccion X",
        "review_focus": (
            "La fraccion X solo corresponde cuando la persona entrevistada tiene "
            "calidad de testigo."
        ),
    },
    {
        "case_id": "vf_case_forensic_vs_therapy",
        "title": "Peritaje psicologico frente a atencion terapeutica",
        "facts": (
            "La victima reporta afectacion emocional por amenazas reiteradas y solicita "
            "apoyo psicologico."
        ),
        "expected_active_diligence_ids": ["vf_evaluacion_psicologica_forense"],
        "review_focus": (
            "El dictamen forense no sustituye intervencion en crisis, terapia ni atencion clinica."
        ),
    },
]


def build_family_violence_review_catalog(articles: list[dict]) -> list[dict]:
    steps = build_family_violence_steps(
        articles,
        (
            "La pareja golpeo y lesiono a la victima, la amenazo con matarla y "
            "sus hijos menores presenciaron los hechos."
        ),
        {"minors_present": True, "violence_type": "fisica", "threats_to_kill": True},
    )
    stored_decisions = _load_stored_decisions()
    catalog = []

    for step in steps:
        fingerprint = calculate_review_fingerprint(step)
        stored = stored_decisions.get(step["diligence_id"])
        is_current = bool(stored and stored.get("fingerprint") == fingerprint)
        status = stored["status"] if is_current else "pending"
        catalog.append(
            {
                **step,
                "review_fingerprint": fingerprint,
                "legal_review_status": status,
                "review_is_current": is_current,
                "review_observations": stored.get("observations", "") if is_current else "",
            }
        )

    return catalog


def calculate_review_fingerprint(step: dict) -> str:
    payload = {field: step.get(field) for field in FINGERPRINT_FIELDS}
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def validate_family_violence_review_record(
    record: FamilyViolenceReviewRecord,
    articles: list[dict],
) -> dict:
    catalog = build_family_violence_review_catalog(articles)
    expected = {
        item["diligence_id"]: item["review_fingerprint"]
        for item in catalog
    }
    seen = set()

    for decision in record.decisions:
        if decision.diligence_id in seen:
            raise ValueError(f"Decision duplicada: {decision.diligence_id}")
        seen.add(decision.diligence_id)

        if decision.diligence_id not in expected:
            raise ValueError(f"Diligencia desconocida: {decision.diligence_id}")
        if decision.fingerprint != expected[decision.diligence_id]:
            raise ValueError(
                f"Huella obsoleta para la diligencia: {decision.diligence_id}"
            )

    missing = sorted(set(expected) - seen)
    if missing:
        raise ValueError(
            "El registro debe incluir una decision para cada diligencia. "
            f"Faltan: {', '.join(missing)}"
        )

    normalized = record.model_dump(mode="json")
    normalized["reviewed_at"] = (
        record.reviewed_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    return normalized


def apply_family_violence_review(steps: list[dict]) -> list[dict]:
    stored_decisions = _load_stored_decisions()
    visible_steps = []

    for step in steps:
        fingerprint = calculate_review_fingerprint(step)
        stored = stored_decisions.get(step["diligence_id"])
        is_current = bool(stored and stored.get("fingerprint") == fingerprint)
        status = stored["status"] if is_current else "pending"

        if status == "rejected":
            continue

        enriched = dict(step)
        enriched["legal_review_status"] = status
        enriched["review_fingerprint"] = fingerprint
        enriched["review_is_current"] = is_current
        if is_current:
            enriched["review_observations"] = stored.get("observations", "")
        visible_steps.append(enriched)

    return visible_steps


def get_family_violence_review_payload(articles: list[dict]) -> dict:
    return {
        "schema_version": 1,
        "crime_type": "violencia_familiar",
        "catalog": build_family_violence_review_catalog(articles),
        "synthetic_cases": SYNTHETIC_REVIEW_CASES,
        "stored_record": _load_review_record(),
    }


def _load_review_record() -> dict:
    try:
        payload = json.loads(REVIEW_RECORD_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {
            "schema_version": 1,
            "crime_type": "violencia_familiar",
            "reviewer_name": "",
            "reviewed_at": None,
            "decisions": [],
        }

    if not isinstance(payload, dict) or not isinstance(payload.get("decisions"), list):
        return {
            "schema_version": 1,
            "crime_type": "violencia_familiar",
            "reviewer_name": "",
            "reviewed_at": None,
            "decisions": [],
        }
    return payload


def _load_stored_decisions() -> dict[str, dict]:
    record = _load_review_record()
    decisions = {}
    for decision in record.get("decisions", []):
        if not isinstance(decision, dict):
            continue
        diligence_id = decision.get("diligence_id")
        if isinstance(diligence_id, str) and diligence_id not in decisions:
            decisions[diligence_id] = decision
    return decisions
