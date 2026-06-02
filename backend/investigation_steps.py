from crime_catalog import get_investigation_steps_for_crime


def get_investigation_steps(
    crime_type: str,
    structured_facts: dict | None = None,
    include_conditionals: bool = True,
) -> list[dict]:
    steps = get_investigation_steps_for_crime(crime_type, structured_facts)

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
    if any(kw in text_lower for kw in ["medida de protección", "cautelar", "orden de protección"]):
        return "cautelar"
    if any(kw in text_lower for kw in ["inspección", "levantamiento", "visita"]):
        return "inspeccion"

    return "diligencia"
