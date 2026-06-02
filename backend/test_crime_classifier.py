from crime_classifier import (
    classify_crime_type,
    get_crime_display_name,
    get_crime_subtype,
)


def test_classify_explicit_crime_mentioned_violacion():
    structured = {"explicit_crime_mentioned": "violación"}
    assert classify_crime_type("hechos diversos", structured) == "violacion"


def test_classify_robo_from_text():
    facts = "El sujeto le robo su celular a la victima en la via publica."
    assert classify_crime_type(facts) == "robo"


def test_classify_fraude_from_text():
    facts = "La persona fue victima de fraude cuando le dieron dinero y nunca lo devolvieron."
    assert classify_crime_type(facts) == "fraude"


def test_classify_violencia_familiar_by_inference():
    facts = "La victima acudio a la fiscalia a presentar una queja."
    structured = {
        "violence_detected": True,
        "relationship_to_aggressor": "esposo",
    }
    assert classify_crime_type(facts, structured) == "violencia_familiar"


def test_classify_violacion_by_sexual_conduct():
    facts = "La victima acudio a presentar una queja ante la autoridad."
    structured = {"sexual_conduct_detected": True}
    assert classify_crime_type(facts, structured) == "violacion"


def test_classify_unknown_when_no_crime():
    facts = "La persona acudio a realizar un tramite administrativo."
    assert classify_crime_type(facts) == "unknown"


def test_display_name_robo():
    assert get_crime_display_name("robo") == "Robo"


def test_display_name_unknown_key():
    assert get_crime_display_name("nonexistent_crime") == "Delito no clasificado"


def test_subtype_robo_con_violencia():
    assert get_crime_subtype("robo", {"violence_used": True}) == "robo_con_violencia"


def test_subtype_none_when_no_structured_facts():
    assert get_crime_subtype("robo", None) is None
