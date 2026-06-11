from ingest import parse_all_sources
from investigation_steps import get_investigation_steps


BAD_FAMILY_VIOLENCE_REFERENCES = [
    "Art. 154",
    "Art. 206",
    "Art. 264",
    "Art. 271",
    "Protocolo Alba",
]


def get_family_steps(facts: str, structured_facts: dict | None = None) -> list[dict]:
    return get_investigation_steps(
        "violencia_familiar",
        structured_facts=structured_facts,
        articles=parse_all_sources(),
        facts=facts,
    )


def test_all_grounded_family_violence_steps_resolve_their_foundations():
    steps = get_family_steps(
        "El esposo golpeó a la víctima y la amenazó. Sus hijos menores observaron los hechos."
    )
    grounded = [step for step in steps if step["display_group"] == "grounded"]

    assert {step["diligence_id"] for step in grounded} == {
        "vf_recepcion_entrevista_inicial",
        "vf_medidas_proteccion_urgentes",
        "vf_evaluacion_medico_forense",
        "vf_evaluacion_psicologica_forense",
    }
    assert all(step["foundation_status"] == "source_verified" for step in grounded)
    assert all(step["legal_review_status"] == "pending" for step in grounded)
    assert all(step["foundations"] for step in grounded)
    assert all(
        foundation["content_hash"]
        and foundation["source_version"]
        and foundation["source_url"]
        for step in grounded
        for foundation in step["foundations"]
    )


def test_family_violence_steps_do_not_expose_known_bad_references():
    steps = get_family_steps(
        "El esposo golpeó a la víctima y la amenazó con matarla. Hay hijos menores."
    )
    rendered_basis = " ".join(
        step["legal_basis"] or ""
        for step in steps
    )

    assert all(reference not in rendered_basis for reference in BAD_FAMILY_VIOLENCE_REFERENCES)
    assert all("feminicidio" not in step["step"].lower() for step in steps)


def test_preliminary_steps_have_no_legal_basis_or_foundations():
    steps = get_family_steps(
        "La pareja amenazó a la víctima. Sus hijos menores fueron testigos."
    )
    preliminary = [step for step in steps if step["display_group"] == "preliminary"]

    assert {step["diligence_id"] for step in preliminary} == {
        "vf_estudio_trabajo_social",
        "vf_entrevista_especializada_nna",
        "vf_consulta_antecedentes_relacionados",
    }
    assert all(step["legal_basis"] is None for step in preliminary)
    assert all(step["foundations"] == [] for step in preliminary)
    assert all(step["foundation_status"] == "unverified" for step in preliminary)
    assert all(
        any("Sugerencia operativa pendiente" in warning for warning in step["warnings"])
        for step in preliminary
    )


def test_physical_violence_activates_medical_forensic_evaluation():
    steps = get_family_steps(
        "El esposo golpeó a la víctima en el rostro y le causó hematomas."
    )

    assert any(
        step["diligence_id"] == "vf_evaluacion_medico_forense"
        for step in steps
    )


def test_non_physical_family_violence_does_not_activate_medical_evaluation():
    steps = get_family_steps(
        "La pareja controla el dinero, la insulta y la amenaza de manera reiterada."
    )

    assert all(
        step["diligence_id"] != "vf_evaluacion_medico_forense"
        for step in steps
    )


def test_explicit_absence_of_injuries_and_minors_does_not_activate_conditionals():
    steps = get_family_steps(
        "La víctima refiere violencia familiar sin describir lesiones ni personas menores de edad."
    )
    step_ids = {step["diligence_id"] for step in steps}

    assert "vf_evaluacion_medico_forense" not in step_ids
    assert "vf_entrevista_especializada_nna" not in step_ids


def test_death_threat_is_risk_trigger_not_separate_diligence():
    steps = get_family_steps(
        "La pareja amenazó a la víctima con matarla."
    )
    protection = next(
        step
        for step in steps
        if step["diligence_id"] == "vf_medidas_proteccion_urgentes"
    )

    assert "Amenaza de muerte reportada como factor de riesgo" in protection["triggered_by"]
    assert all("feminicidio" not in step["step"].lower() for step in steps)


def test_missing_required_article_degrades_grounded_step_to_preliminary():
    articles_without_137 = [
        article
        for article in parse_all_sources()
        if not (
            article["source_name"] == "Código Nacional de Procedimientos Penales"
            and article["article_number"] == "137"
        )
    ]
    steps = get_investigation_steps(
        "violencia_familiar",
        articles=articles_without_137,
        facts="La pareja amenazó a la víctima.",
    )
    protection = next(
        step
        for step in steps
        if step["diligence_id"] == "vf_medidas_proteccion_urgentes"
    )

    assert protection["display_group"] == "preliminary"
    assert protection["foundation_status"] == "unverified"
    assert protection["legal_basis"] is None
    assert protection["foundations"] == []
    assert any("se degradó a sugerencia preliminar" in warning for warning in protection["warnings"])
