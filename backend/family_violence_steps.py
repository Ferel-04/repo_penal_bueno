import re
import unicodedata

from article_map import get_source_key


PRELIMINARY_WARNING = (
    "Sugerencia operativa pendiente de fuente específica y validación jurídica."
)

FAMILY_VIOLENCE_STEP_DEFINITIONS = [
    {
        "diligence_id": "vf_recepcion_entrevista_inicial",
        "step": "Recibir la denuncia y realizar entrevista inicial",
        "legal_basis": "Arts. 109, 131, 217 y 251, fracción X, CNPP",
        "urgent": True,
        "category": "testimonio",
        "display_group": "grounded",
        "purpose": (
            "Documentar el relato, identificar necesidades inmediatas y dejar un registro "
            "íntegro de la actuación inicial."
        ),
        "applicability_condition": "Aplica al inicio de la investigación.",
        "responsible_authority": "Ministerio Público y Policía bajo su conducción",
        "priority": "inmediata",
        "expected_result": (
            "Denuncia recibida y registro separado de la entrevista con fecha, hora, "
            "intervinientes y resultados relevantes."
        ),
        "warnings": [
            (
                "El artículo 251, fracción X, se invoca únicamente cuando la entrevista "
                "se practique en calidad de testigo."
            ),
            "Debe evitarse la repetición innecesaria del relato y la revictimización.",
        ],
        "foundation_specs": [
            {
                "source_key": "cnpp",
                "article_number": "109",
                "fractions": ["II", "III", "VI", "XVIII", "XXVI"],
                "foundation_type": "victim_right",
                "reason": "Reconoce derechos de acceso, atención, trato digno y protección.",
            },
            {
                "source_key": "cnpp",
                "article_number": "131",
                "fractions": ["II", "III", "V", "XXIII"],
                "foundation_type": "procedural_basis",
                "reason": "Obliga al Ministerio Público a recibir la denuncia y conducir la investigación.",
            },
            {
                "source_key": "cnpp",
                "article_number": "217",
                "fractions": [],
                "foundation_type": "record_requirement",
                "reason": "Exige registrar cada actuación de investigación de forma completa e íntegra.",
            },
            {
                "source_key": "cnpp",
                "article_number": "251",
                "fractions": ["X"],
                "foundation_type": "procedural_basis",
                "reason": "Prevé la entrevista de testigos sin autorización judicial previa.",
            },
        ],
        "trigger_builder": "initial_interview",
        "activation": "always",
    },
    {
        "diligence_id": "vf_medidas_proteccion_urgentes",
        "step": "Evaluar y, en su caso, ordenar medidas de protección urgentes",
        "legal_basis": "Art. 137 CNPP — Medidas u órdenes de protección",
        "urgent": True,
        "category": "cautelar",
        "display_group": "grounded",
        "purpose": (
            "Valorar el riesgo inmediato y, si es inminente, reducir la posibilidad "
            "de nuevas agresiones mediante medidas idóneas y motivadas."
        ),
        "applicability_condition": (
            "Procede cuando el Ministerio Público estime que el imputado representa "
            "un riesgo inminente para la seguridad de la víctima u ofendido."
        ),
        "responsible_authority": "Ministerio Público",
        "priority": "inmediata",
        "expected_result": (
            "Acuerdo fundado y motivado que identifique el riesgo, seleccione las "
            "medidas idóneas y deje constancia de su notificación y ejecución."
        ),
        "warnings": [
            (
                "La narración activa una valoración urgente; no acredita por sí sola "
                "el riesgo inminente exigido por el artículo 137."
            ),
            (
                "Las fracciones I, II y III requieren audiencia judicial dentro de "
                "los cinco días siguientes a su imposición."
            ),
            (
                "Las amenazas de muerte son un factor de riesgo, no fundamento automático "
                "para imponer una medida concreta."
            ),
        ],
        "foundation_specs": [
            {
                "source_key": "cnpp",
                "article_number": "137",
                "fractions": ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"],
                "foundation_type": "procedural_basis",
                "reason": (
                    "Faculta al Ministerio Público para ordenar medidas de protección "
                    "fundadas y motivadas ante un riesgo inminente."
                ),
            }
        ],
        "trigger_builder": "risk",
        "activation": "always",
    },
    {
        "diligence_id": "vf_evaluacion_medico_forense",
        "step": "Disponer evaluación médico-forense de las lesiones",
        "legal_basis": "Art. 272 CNPP; arts. 8 y 34 LGV",
        "urgent": True,
        "category": "pericial",
        "display_group": "grounded",
        "purpose": (
            "Documentar lesiones, mecanismo probable, temporalidad y consecuencias "
            "relevantes para la investigación."
        ),
        "applicability_condition": (
            "Aplica cuando el relato o los hechos estructurados reportan golpes, lesiones "
            "u otra violencia física."
        ),
        "responsible_authority": "Ministerio Público, Policía y personal pericial médico",
        "priority": "inmediata",
        "expected_result": (
            "Dictamen médico-forense con hallazgos, metodología, conclusiones y registro "
            "de los indicios examinados."
        ),
        "warnings": [
            (
                "Los artículos 8 y 34 de la LGV sustentan derechos de atención médica; "
                "no sustituyen el fundamento procesal del peritaje."
            ),
            "La atención clínica urgente no debe retrasarse por la práctica pericial.",
        ],
        "foundation_specs": [
            {
                "source_key": "cnpp",
                "article_number": "272",
                "fractions": [],
                "foundation_type": "procedural_basis",
                "reason": "Permite disponer los peritajes necesarios para investigar el hecho.",
            },
            {
                "source_key": "lgv",
                "article_number": "8",
                "fractions": [],
                "foundation_type": "victim_right",
                "reason": "Reconoce ayuda médica y psicológica inmediata y especializada.",
            },
            {
                "source_key": "lgv",
                "article_number": "34",
                "fractions": ["I"],
                "foundation_type": "victim_right",
                "reason": "Reconoce atención médica y psicológica gratuita por lesiones y trauma.",
            },
        ],
        "trigger_builder": "physical_injury",
        "activation": "physical_injury",
    },
    {
        "diligence_id": "vf_evaluacion_psicologica_forense",
        "step": "Disponer evaluación psicológica forense",
        "legal_basis": "Art. 272 CNPP",
        "urgent": True,
        "category": "pericial",
        "display_group": "grounded",
        "purpose": (
            "Valorar afectaciones psicológicas relacionadas con los hechos y aportar "
            "hallazgos periciales a la investigación."
        ),
        "applicability_condition": (
            "Aplica cuando la naturaleza de los hechos amerite una evaluación pericial "
            "psicológica pertinente y proporcional."
        ),
        "responsible_authority": "Ministerio Público y personal pericial en psicología",
        "priority": "alta",
        "expected_result": (
            "Dictamen psicológico forense con metodología, hallazgos, limitaciones y conclusiones."
        ),
        "warnings": [
            (
                "La evaluación psicológica forense no sustituye atención psicológica, "
                "intervención en crisis ni tratamiento terapéutico."
            ),
            "Debe evitarse la repetición innecesaria del relato y la revictimización.",
        ],
        "foundation_specs": [
            {
                "source_key": "cnpp",
                "article_number": "272",
                "fractions": [],
                "foundation_type": "procedural_basis",
                "reason": "Permite disponer los peritajes necesarios para investigar el hecho.",
            }
        ],
        "trigger_builder": "psychological",
        "activation": "always",
    },
    {
        "diligence_id": "vf_estudio_trabajo_social",
        "step": "Valorar la pertinencia de un estudio de trabajo social",
        "legal_basis": None,
        "urgent": False,
        "category": "pericial",
        "display_group": "preliminary",
        "purpose": (
            "Explorar contexto familiar, redes de apoyo y condiciones del entorno cuando "
            "sea útil para orientar la investigación o la atención."
        ),
        "applicability_condition": "Aplicación sujeta a pertinencia y validación jurídica.",
        "responsible_authority": "Por determinar conforme a la institución competente",
        "priority": "por determinar",
        "expected_result": "Producto técnico por definir conforme a una fuente y protocolo aplicables.",
        "warnings": [PRELIMINARY_WARNING],
        "foundation_specs": [],
        "trigger_builder": "context",
        "activation": "always",
    },
    {
        "diligence_id": "vf_entrevista_especializada_nna",
        "step": "Valorar entrevista especializada a niñas, niños o adolescentes",
        "legal_basis": None,
        "urgent": False,
        "category": "testimonio",
        "display_group": "preliminary",
        "purpose": (
            "Preservar información relevante de personas menores de edad con técnicas "
            "adecuadas a su edad y evitando revictimización."
        ),
        "applicability_condition": (
            "Aplica únicamente cuando el relato identifica niñas, niños o adolescentes "
            "como víctimas o posibles testigos."
        ),
        "responsible_authority": "Por determinar conforme a la institución competente",
        "priority": "por determinar",
        "expected_result": "Actuación especializada definida por la fuente y protocolo aplicables.",
        "warnings": [PRELIMINARY_WARNING],
        "foundation_specs": [],
        "trigger_builder": "minors",
        "activation": "minors_present",
    },
    {
        "diligence_id": "vf_consulta_antecedentes_relacionados",
        "step": "Valorar consulta de denuncias o antecedentes relacionados",
        "legal_basis": None,
        "urgent": False,
        "category": "documental",
        "display_group": "preliminary",
        "purpose": (
            "Identificar posibles antecedentes relacionados que ayuden a contextualizar "
            "el riesgo y orientar líneas de investigación."
        ),
        "applicability_condition": "Aplicación sujeta a pertinencia, competencia y acceso legal.",
        "responsible_authority": "Por determinar conforme a la institución competente",
        "priority": "media",
        "expected_result": "Constancia de consulta lícita y de los antecedentes pertinentes encontrados.",
        "warnings": [PRELIMINARY_WARNING],
        "foundation_specs": [],
        "trigger_builder": "history",
        "activation": "always",
    },
]


def build_family_violence_steps(
    articles: list[dict],
    facts: str,
    structured_facts: dict | None,
    include_conditionals: bool = True,
) -> list[dict]:
    context = _build_context(facts, structured_facts)
    steps = []

    for definition in FAMILY_VIOLENCE_STEP_DEFINITIONS:
        if not _is_active(definition["activation"], context):
            if include_conditionals:
                continue
            continue

        step = {
            key: value
            for key, value in definition.items()
            if key not in {"foundation_specs", "trigger_builder", "activation"}
        }
        step["foundation_status"] = (
            "source_verified" if step["display_group"] == "grounded" else "unverified"
        )
        step["legal_review_status"] = "pending"
        step["triggered_by"] = _build_triggers(definition["trigger_builder"], context)
        step["foundations"] = _resolve_foundations(
            articles,
            definition["foundation_specs"],
        )

        if step["display_group"] == "grounded" and len(step["foundations"]) != len(
            definition["foundation_specs"]
        ):
            step["display_group"] = "preliminary"
            step["foundation_status"] = "unverified"
            step["legal_basis"] = None
            step["warnings"] = [
                *step["warnings"],
                (
                    "No se resolvieron todos los fundamentos requeridos contra el corpus "
                    "activo; la diligencia se degradó a sugerencia preliminar."
                ),
            ]

        steps.append(step)

    return steps


def _resolve_foundations(articles: list[dict], specs: list[dict]) -> list[dict]:
    resolved = []
    for spec in specs:
        article = next(
            (
                item
                for item in articles
                if get_source_key(item.get("source_name") or "") == spec["source_key"]
                and item.get("article_number") == spec["article_number"]
            ),
            None,
        )
        if not article:
            continue

        resolved.append(
            {
                "source_name": article["source_name"],
                "article_number": article["article_number"],
                "fractions": list(spec["fractions"]),
                "foundation_type": spec["foundation_type"],
                "reason": spec["reason"],
                "source_version": article.get("source_version"),
                "last_reform_date": article.get("last_reform_date"),
                "source_url": article.get("source_url"),
                "content_hash": article.get("content_hash"),
            }
        )
    return resolved


def _build_context(facts: str, structured_facts: dict | None) -> dict:
    normalized = _normalize(facts)
    structured = structured_facts or {}
    physical_signal_text = _remove_phrases(
        normalized,
        [
            "sin describir lesiones",
            "sin lesiones",
            "no presenta lesiones",
            "no presento lesiones",
            "no hubo golpes",
            "sin golpes",
            "sin violencia fisica",
        ],
    )
    minor_signal_text = _remove_phrases(
        normalized,
        [
            "ni personas menores de edad",
            "sin personas menores de edad",
            "sin menores de edad",
            "sin menores",
            "no hay menores de edad",
            "no hay menores",
            "no se mencionan menores",
        ],
    )

    physical_terms = [
        "violencia fisica",
        "golpe",
        "golpeo",
        "lesion",
        "hematoma",
        "moreton",
        "herida",
        "fractura",
        "empujo",
        "patada",
        "punetazo",
        "objeto contundente",
    ]
    minor_patterns = [
        r"\bhij[oa]s?\s+menores?\b",
        r"\bmenores?\s+(?:de edad|testigos?|victimas?)\b",
        r"\bnin[oa]s?\b",
        r"\badolescentes?\b",
    ]

    relationship = structured.get("relationship_to_aggressor")
    physical_injury = (
        _normalize(str(structured.get("violence_type") or "")) == "fisica"
        or bool(structured.get("injury_type"))
        or any(term in physical_signal_text for term in physical_terms)
    )
    minors_present = bool(structured.get("minors_present")) or any(
        re.search(pattern, minor_signal_text) for pattern in minor_patterns
    )
    threat_to_kill = bool(structured.get("threats_to_kill")) or any(
        term in normalized
        for term in (
            "amenaza de muerte",
            "amenazo con mat",
            "amenaza con mat",
            "privar de la vida",
            "matarla",
            "matarlo",
        )
    )
    generic_threat = bool(structured.get("threat_detected")) or "amenaza" in normalized

    return {
        "facts": facts,
        "normalized": normalized,
        "relationship": relationship,
        "physical_injury": physical_injury,
        "minors_present": minors_present,
        "threat_to_kill": threat_to_kill,
        "generic_threat": generic_threat,
    }


def _is_active(activation: str, context: dict) -> bool:
    if activation == "always":
        return True
    return bool(context.get(activation))


def _build_triggers(trigger_builder: str, context: dict) -> list[str]:
    triggers = ["Posible contexto de violencia familiar"]

    relationship = context.get("relationship")
    if isinstance(relationship, str) and relationship.strip():
        triggers.append(f"Relación reportada con la persona agresora: {relationship.strip()}")
    elif any(
        term in context["normalized"]
        for term in ("conyuge", "esposo", "esposa", "pareja", "concubino", "concubina")
    ):
        triggers.append("Relación familiar o de pareja descrita en el relato")

    if trigger_builder == "initial_interview":
        triggers.append("Relato presentado para análisis inicial")
    elif trigger_builder == "risk":
        if context["physical_injury"]:
            triggers.append("Violencia física o lesiones reportadas")
        if context["generic_threat"]:
            triggers.append("Amenazas reportadas")
        if context["threat_to_kill"]:
            triggers.append("Amenaza de muerte reportada como factor de riesgo")
        if context["minors_present"]:
            triggers.append("Presencia de niñas, niños o adolescentes reportada")
    elif trigger_builder == "physical_injury":
        triggers.append("Golpes, lesiones o violencia física reportados")
    elif trigger_builder == "psychological":
        if context["generic_threat"]:
            triggers.append("Amenazas reportadas")
        else:
            triggers.append("Posible afectación psicológica asociada al relato")
    elif trigger_builder == "minors":
        triggers.append("Niñas, niños o adolescentes identificados en el relato")
    elif trigger_builder == "history":
        triggers.append("Necesidad de contextualizar posibles hechos previos relacionados")
    elif trigger_builder == "context":
        triggers.append("Necesidad potencial de documentar el contexto familiar y social")

    return triggers


def _normalize(value: str) -> str:
    value = value.casefold()
    normalized = unicodedata.normalize("NFD", value)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def _remove_phrases(value: str, phrases: list[str]) -> str:
    for phrase in phrases:
        value = value.replace(phrase, " ")
    return value
