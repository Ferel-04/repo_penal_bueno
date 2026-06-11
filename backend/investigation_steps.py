from crime_catalog import get_investigation_steps_for_crime
from family_violence_review import apply_family_violence_review
from family_violence_steps import build_family_violence_steps


def get_investigation_steps(
    crime_type: str,
    structured_facts: dict | None = None,
    include_conditionals: bool = True,
    articles: list[dict] | None = None,
    facts: str = "",
) -> list[dict]:
    if crime_type == "violencia_familiar":
        return apply_family_violence_review(
            build_family_violence_steps(
                articles or [],
                facts,
                structured_facts,
                include_conditionals=include_conditionals,
            )
        )

    steps = [
        dict(step)
        for step in get_investigation_steps_for_crime(crime_type, structured_facts)
    ]

    if not include_conditionals:
        steps = [step for step in steps if step.get("applies_when") == "always"]

    for step in steps:
        step["category"] = _infer_category(step.get("step", ""))

    return steps


def _infer_category(step_text: str) -> str:
    text_lower = step_text.lower()

    if any(kw in text_lower for kw in ["entrevista", "testigo", "declaración"]):
        return "testimonio"
    if any(kw in text_lower for kw in ["certificado médico", "pericial", "dictamen", "necropsia"]):
        return "pericial"
    if any(kw in text_lower for kw in ["cámara", "documento", "contrato", "estado de cuenta", "imagen"]):
        return "documental"
    if any(
        kw in text_lower
        for kw in [
            "medida de protección",
            "medidas de protección",
            "cautelar",
            "orden de protección",
        ]
    ):
        return "cautelar"
    if any(kw in text_lower for kw in ["inspección", "levantamiento", "visita"]):
        return "inspeccion"

    return "diligencia"
