CRIME_CATALOG = {
    "robo": {
        "display_name": "Robo",
        "detection_keywords": [
            "robo",
            "robar",
            "asalto",
            "despojo",
            "sustraccion",
            "apoderamiento",
            "cosa ajena",
            "bien mueble",
            "carterazo",
            "ratero",
            "hurto",
            "arrebato",
            "quitaron",
            "robaron",
            "asaltaron",
            "despojaron",
        ],
        "extract_fields": {
            "violence_used": "bool",
            "weapon_used": "bool",
            "weapon_type": "str|null",
            "victim_count": "str|null",
            "estimated_value": "str|null",
            "perpetrators_count": "str|null",
            "location_type": "str|null",
            "forced_entry": "bool",
        },
        "classifier_questions": [
            "¿Se usó violencia física o amenaza contra la víctima?",
            "¿Se utilizó algún arma? ¿De qué tipo?",
            "¿Cuántas personas participaron en el robo?",
            "¿Cuál es el valor aproximado de lo sustraído?",
            "¿Hubo allanamiento de morada o lugar cerrado?",
            "¿El robo ocurrió en lugar habitado o destinado a habitación?",
        ],
        "subtypes": {
            "robo_simple": {
                "display_name": "Robo simple",
                "activation_condition": "not violence_used and not weapon_used and not forced_entry",
                "aggravating_factors": [],
            },
            "robo_con_violencia": {
                "display_name": "Robo con violencia",
                "activation_condition": "violence_used or weapon_used",
                "aggravating_factors": [
                    "violencia_fisica",
                    "violencia_moral",
                    "arma_blanca",
                    "arma_fuego",
                ],
            },
            "robo_en_pandilla": {
                "display_name": "Robo en pandilla",
                "activation_condition": "perpetrators_count >= 3",
                "aggravating_factors": [
                    "tres_o_mas_personas",
                ],
            },
            "robo_en_lugar_habitado": {
                "display_name": "Robo en lugar habitado",
                "activation_condition": "location_type == 'habitado' or forced_entry",
                "aggravating_factors": [
                    "casa_habitacion",
                    "lugar_cerrado",
                ],
            },
        },
        "legal_search_terms": [
            "robo",
            "apoderamiento",
            "cosa ajena mueble",
            "robo simple",
            "robo con violencia",
            "robo agravado",
            "lugar habitado",
        ],
        "minimum_investigation_steps": [
            {
                "step": "Acta de entrevista con la víctima",
                "legal_basis": "Art. 264 CNPP — Entrevistas a testigos y víctimas",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Inspección del lugar de los hechos",
                "legal_basis": "Art. 267 CNPP — Inspección del lugar",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Avalúo de los bienes sustraídos",
                "legal_basis": "Art. 271 CNPP — Peritajes",
                "urgent": False,
                "applies_when": "always",
            },
            {
                "step": "Certificado médico de lesiones (si aplica)",
                "legal_basis": "Art. 271 CNPP — Peritajes médicos",
                "urgent": True,
                "applies_when": "violence_used",
            },
            {
                "step": "Recabar imágenes de cámaras de videovigilancia",
                "legal_basis": "Art. 279 CNPP — Cadena de custodia",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Solicitud de dictamen balístico (si arma de fuego)",
                "legal_basis": "Art. 271 CNPP — Peritajes especializados",
                "urgent": True,
                "applies_when": "weapon_used",
            },
            {
                "step": "Identificación de testigos presenciales",
                "legal_basis": "Art. 264 CNPP — Entrevistas",
                "urgent": False,
                "applies_when": "always",
            },
        ],
    },
    "lesiones": {
        "display_name": "Lesiones",
        "detection_keywords": [
            "lesiones",
            "lesionado",
            "lesionada",
            "golpes",
            "golpeo",
            "heridas",
            "herido",
            "hematomas",
            "moretones",
            "cortadas",
            "fractura",
            "fracturado",
            "agresion fisica",
            "agredido",
            "agredida",
            "ataque",
            "atacado",
            "atacada",
            "punalada",
            "mordida",
            "quemadura",
            "incapacidad",
            "cicatriz",
            "deformidad",
        ],
        "extract_fields": {
            "injury_type": "str|null",
            "weapon_used": "bool",
            "weapon_type": "str|null",
            "healing_time_days": "str|null",
            "permanent_damage": "bool",
            "body_part_affected": "str|null",
            "medical_attention_received": "bool",
            "relationship_to_aggressor": "str|null",
        },
        "classifier_questions": [
            "¿Qué tipo de lesiones presenta la víctima (cortadas, fracturas, quemaduras)?",
            "¿Cuántos días de incapacidad médica se otorgaron?",
            "¿Las lesiones dejan cicatriz, deformidad o daño permanente?",
            "¿Se utilizó algún arma u objeto para causar las lesiones?",
            "¿La víctima recibió atención médica?",
            "¿Existe relación entre víctima y agresor?",
        ],
        "subtypes": {
            "lesiones_simples": {
                "display_name": "Lesiones simples",
                "activation_condition": "healing_time_days <= 15 and not permanent_damage",
                "aggravating_factors": [],
            },
            "lesiones_que_tardan_mas_de_quince_dias": {
                "display_name": "Lesiones que tardan más de quince días en sanar",
                "activation_condition": "healing_time_days > 15",
                "aggravating_factors": [
                    "incapacidad_mayor_quince_dias",
                ],
            },
            "lesiones_que_dejan_cicatriz": {
                "display_name": "Lesiones que dejan cicatriz o deformidad",
                "activation_condition": "permanent_damage",
                "aggravating_factors": [
                    "cicatriz_notable",
                    "deformidad_permanente",
                    "dano_permanente",
                ],
            },
            "lesiones_con_arma": {
                "display_name": "Lesiones con arma",
                "activation_condition": "weapon_used",
                "aggravating_factors": [
                    "arma_blanca",
                    "arma_fuego",
                    "objeto_contundente",
                ],
            },
        },
        "legal_search_terms": [
            "lesiones",
            "dano en la salud",
            "lesiones dolosas",
            "lesiones culposas",
            "cicatriz",
            "deformidad",
        ],
        "minimum_investigation_steps": [
            {
                "step": "Certificado médico de lesiones",
                "legal_basis": "Art. 271 CNPP — Peritajes médicos",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Acta de entrevista con la víctima",
                "legal_basis": "Art. 264 CNPP — Entrevistas a testigos y víctimas",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Inspección del lugar de los hechos",
                "legal_basis": "Art. 267 CNPP — Inspección del lugar",
                "urgent": False,
                "applies_when": "always",
            },
            {
                "step": "Fotografías de las lesiones",
                "legal_basis": "Art. 279 CNPP — Cadena de custodia",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Dictamen pericial sobre tiempo de sanación",
                "legal_basis": "Art. 271 CNPP — Peritajes",
                "urgent": False,
                "applies_when": "always",
            },
            {
                "step": "Solicitud de historial médico",
                "legal_basis": "Art. 266 CNPP — Solicitud de información",
                "urgent": False,
                "applies_when": "medical_attention_received",
            },
            {
                "step": "Dictamen pericial sobre secuelas permanentes",
                "legal_basis": "Art. 271 CNPP — Peritajes especializados",
                "urgent": False,
                "applies_when": "permanent_damage",
            },
        ],
    },
    "homicidio": {
        "display_name": "Homicidio",
        "detection_keywords": [
            "homicidio",
            "muerte",
            "muerto",
            "muerta",
            "fallecido",
            "fallecida",
            "mataron",
            "mato",
            "asesinato",
            "asesinado",
            "privar de la vida",
            "privacion de la vida",
            "cadaver",
            "cadáver",
            "sin vida",
            "perdio la vida",
            "defuncion",
            "quitarse la vida",
        ],
        "extract_fields": {
            "cause_of_death": "str|null",
            "weapon_used": "bool",
            "weapon_type": "str|null",
            "perpetrators_count": "str|null",
            "relationship_to_aggressor": "str|null",
            "premeditation_detected": "bool",
            "treachery_detected": "bool",
            "victim_age": "str|null",
            "victim_gender": "str|null",
        },
        "classifier_questions": [
            "¿Cuál fue la causa de muerte según el informe pericial?",
            "¿Se utilizó algún arma u objeto?",
            "¿Existió premeditación o alevosía?",
            "¿Cuántas personas participaron?",
            "¿Existe relación entre la víctima y el agresor?",
            "¿Se trata de feminicidio (víctima mujer con razones de género)?",
        ],
        "subtypes": {
            "homicidio_doloso": {
                "display_name": "Homicidio doloso",
                "activation_condition": "not premeditation_detected and not treachery_detected",
                "aggravating_factors": [],
            },
            "homicidio_calificado": {
                "display_name": "Homicidio calificado",
                "activation_condition": "premeditation_detected or treachery_detected",
                "aggravating_factors": [
                    "premeditacion",
                    "alevosia",
                    "ventaja",
                    "traicion",
                ],
            },
            "homicidio_en_pandilla": {
                "display_name": "Homicidio en pandilla",
                "activation_condition": "perpetrators_count >= 3",
                "aggravating_factors": [
                    "tres_o_mas_personas",
                ],
            },
        },
        "legal_search_terms": [
            "homicidio",
            "privar de la vida",
            "homicidio doloso",
            "homicidio calificado",
            "alevosia",
            "premeditacion",
        ],
        "minimum_investigation_steps": [
            {
                "step": "Levantamiento del cadáver e inspección del lugar",
                "legal_basis": "Art. 267 CNPP — Inspección del lugar",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Necropsia de ley",
                "legal_basis": "Art. 271 CNPP — Peritajes médicos forenses",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Acta de entrevista con testigos y familiares",
                "legal_basis": "Art. 264 CNPP — Entrevistas a testigos y víctimas",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Dictamen pericial balístico (si arma de fuego)",
                "legal_basis": "Art. 271 CNPP — Peritajes especializados",
                "urgent": True,
                "applies_when": "weapon_used",
            },
            {
                "step": "Dictamen de química forense",
                "legal_basis": "Art. 271 CNPP — Peritajes",
                "urgent": False,
                "applies_when": "always",
            },
            {
                "step": "Recabar imágenes de cámaras de videovigilancia",
                "legal_basis": "Art. 279 CNPP — Cadena de custodia",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Investigación de motivos y relaciones de la víctima",
                "legal_basis": "Art. 213 CNPP — Investigación",
                "urgent": False,
                "applies_when": "always",
            },
            {
                "step": "Dictamen de psicología forense al agresor (si detenido)",
                "legal_basis": "Art. 271 CNPP — Peritajes",
                "urgent": False,
                "applies_when": "always",
            },
        ],
    },
    "violacion": {
        "display_name": "Violación",
        "detection_keywords": [
            "violacion",
            "violo",
            "violada",
            "violado",
            "cópula",
            "copula",
            "acto sexual",
            "conducta sexual",
            "acceso carnal",
            "penetracion",
            "sin consentimiento",
            "abuso sexual",
            "estupro",
            "forzada",
            "forzado",
            "sometida sexualmente",
            "agredida sexualmente",
        ],
        "extract_fields": {
            "sexual_conduct_detected": "bool",
            "victim_age_group": "str|null",
            "relationship_to_aggressor": "str|null",
            "violence_detected": "bool",
            "threat_detected": "bool",
            "unconscious_detected": "bool",
            "unable_to_resist_detected": "bool",
            "explicit_crime_mentioned": "str|null",
            "victim_gender": "str|null",
            "location_type": "str|null",
        },
        "classifier_questions": [
            "¿Se usó violencia física, violencia moral o amenazas?",
            "¿La víctima era menor de quince años?",
            "¿La víctima podía comprender el significado del hecho y resistirlo?",
            "¿Existe relación familiar, custodia, guarda, educación o autoridad?",
            "¿La víctima se encontraba inconsciente o bajo efectos de sustancias?",
            "¿Hubo penetración o actos sexuales diversos?",
        ],
        "subtypes": {
            "violacion_simple": {
                "display_name": "Violación",
                "activation_condition": "sexual_conduct_detected and not unconscious_detected and not unable_to_resist_detected",
                "aggravating_factors": [],
            },
            "violacion_equiparada": {
                "display_name": "Violación equiparada",
                "activation_condition": "unconscious_detected or unable_to_resist_detected",
                "aggravating_factors": [
                    "inconsciencia",
                    "incapacidad_de_resistencia",
                    "sustancias",
                ],
            },
            "violacion_con_agravantes": {
                "display_name": "Violación con agravantes",
                "activation_condition": "victim_age_group == 'menor de quince años' or relationship_to_aggressor",
                "aggravating_factors": [
                    "menor_de_quince",
                    "relacion_familiar",
                    "autoridad",
                    "custodia",
                    "guarda",
                ],
            },
            "estupro": {
                "display_name": "Estupro",
                "activation_condition": "victim_age_group in ['menor de edad', 'menor de quince años'] and not violence_detected",
                "aggravating_factors": [
                    "engano",
                    "seduccion",
                ],
            },
        },
        "legal_search_terms": [
            "violacion",
            "copula",
            "violacion equiparada",
            "abuso sexual",
            "estupro",
            "actos sexuales",
        ],
        "minimum_investigation_steps": [
            {
                "step": "Acta de entrevista con la víctima (Cámara Gesell si menor)",
                "legal_basis": "Art. 264 CNPP — Entrevistas a víctimas; Art. 206 CNPP — Testimonio de menores",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Certificado médico ginecológico",
                "legal_basis": "Art. 271 CNPP — Peritajes médicos",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Dictamen de psicología forense a la víctima",
                "legal_basis": "Art. 271 CNPP — Peritajes",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Recolección de indicios biológicos (kit de violación)",
                "legal_basis": "Art. 279 CNPP — Cadena de custodia",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Inspección del lugar de los hechos",
                "legal_basis": "Art. 267 CNPP — Inspección del lugar",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Certificado médico de lesiones (si violencia)",
                "legal_basis": "Art. 271 CNPP — Peritajes médicos",
                "urgent": True,
                "applies_when": "violence_detected",
            },
            {
                "step": "Solicitud de medidas de protección para la víctima",
                "legal_basis": "Art. 154 CNPP — Medidas de protección",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Dictamen toxicológico (si sustancias)",
                "legal_basis": "Art. 271 CNPP — Peritajes especializados",
                "urgent": True,
                "applies_when": "unconscious_detected",
            },
        ],
    },
    "violencia_familiar": {
        "display_name": "Violencia Familiar",
        "detection_keywords": [
            "violencia familiar",
            "violencia domestica",
            "violencia intrafamiliar",
            "maltrato familiar",
            "golpes en casa",
            "agresion familiar",
            "padre agresor",
            "madre agresora",
            "esposo agresor",
            "esposa agresora",
            "esposo me golpea",
            "esposa me golpea",
            "mi esposo",
            "mi esposa",
            "pareja agresora",
            "concubino",
            "concubina",
            "marido",
            "esposa",
            "esposo",
            "conyuge",
            "cónyuge",
            "hijo agresor",
            "violencia de pareja",
            "violencia conyugal",
            "maltrato conyugal",
            "agresion domestica",
            "pelea familiar",
            "violencia en el hogar",
            "golpeo a su esposa",
            "golpeo a su esposo",
            "golpeo a la victima su pareja",
            "domicilio conyugal",
            "domicilio familiar",
        ],
        "extract_fields": {
            "violence_type": "str|null",
            "frequency": "str|null",
            "relationship_to_aggressor": "str|null",
            "minors_present": "bool",
            "victim_age": "str|null",
            "victim_gender": "str|null",
            "weapon_used": "bool",
            "threats_to_kill": "bool",
            "economic_violence": "bool",
            "psychological_violence": "bool",
        },
        "classifier_questions": [
            "¿Qué tipo de violencia se ejerce (física, psicológica, económica, sexual)?",
            "¿Con qué frecuencia ocurren los hechos de violencia?",
            "¿Existen menores de edad en el hogar que sean testigos o víctimas?",
            "¿Existe relación de matrimonio, concubinato, parentesco o pareja?",
            "¿Ha habido amenazas de muerte?",
            "¿Se ha ejercido violencia económica (control de recursos)?",
        ],
        "subtypes": {
            "violencia_fisica": {
                "display_name": "Violencia familiar física",
                "activation_condition": "violence_type == 'fisica'",
                "aggravating_factors": [
                    "lesiones",
                    "arma",
                ],
            },
            "violencia_psicologica": {
                "display_name": "Violencia familiar psicológica",
                "activation_condition": "psychological_violence",
                "aggravating_factors": [
                    "amenazas",
                    "humillacion",
                    "aislamiento",
                ],
            },
            "violencia_economica": {
                "display_name": "Violencia familiar económica",
                "activation_condition": "economic_violence",
                "aggravating_factors": [
                    "control_economico",
                    "privacion_recursos",
                ],
            },
            "violencia_con_menores_testigos": {
                "display_name": "Violencia familiar con menores testigos",
                "activation_condition": "minors_present",
                "aggravating_factors": [
                    "menores_testigos",
                    "afectacion_menores",
                ],
            },
        },
        "legal_search_terms": [
            "violencia familiar",
            "violencia domestica",
            "violencia intrafamiliar",
            "maltrato familiar",
            "agresion familiar",
        ],
        "minimum_investigation_steps": [
            {
                "step": "Acta de entrevista con la víctima",
                "legal_basis": "Art. 264 CNPP — Entrevistas a víctimas",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Solicitud de medidas de protección urgentes",
                "legal_basis": "Art. 154 CNPP — Medidas de protección",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Certificado médico de lesiones (si violencia física)",
                "legal_basis": "Art. 271 CNPP — Peritajes médicos",
                "urgent": True,
                "applies_when": "violence_type == 'fisica'",
            },
            {
                "step": "Dictamen de psicología forense a la víctima",
                "legal_basis": "Art. 271 CNPP — Peritajes",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Dictamen de trabajo social (visita domiciliaria)",
                "legal_basis": "Art. 271 CNPP — Peritajes",
                "urgent": False,
                "applies_when": "always",
            },
            {
                "step": "Entrevista a menores testigos (Cámara Gesell)",
                "legal_basis": "Art. 206 CNPP — Testimonio de menores",
                "urgent": False,
                "applies_when": "minors_present",
            },
            {
                "step": "Valoración de riesgo de feminicidio",
                "legal_basis": "Art. 154 CNPP — Medidas de protección; Protocolo Alba",
                "urgent": True,
                "applies_when": "threats_to_kill",
            },
            {
                "step": "Recabar denuncias previas contra el agresor",
                "legal_basis": "Art. 213 CNPP — Investigación",
                "urgent": False,
                "applies_when": "always",
            },
        ],
    },
    "fraude": {
        "display_name": "Fraude",
        "detection_keywords": [
            "fraude",
            "estafa",
            "engano",
            "engaño",
            "defraudacion",
            "defraudado",
            "defraudada",
            "timado",
            "timada",
            "estafado",
            "estafada",
            "estafaron",
            "dinero no devuelto",
            "no me pago",
            "incumplimiento doloso",
            "simulacion",
            "falsificacion",
            "documento falso",
            "firma falsa",
            "suplantacion",
            "piramide",
            "esquema ponzi",
            "inversion fraudulenta",
        ],
        "extract_fields": {
            "deception_method": "str|null",
            "amount_defrauded": "str|null",
            "document_forgery": "bool",
            "victim_count": "str|null",
            "perpetrators_count": "str|null",
            "contract_involved": "bool",
            "online_fraud": "bool",
            "victim_age": "str|null",
        },
        "classifier_questions": [
            "¿Cuál fue el método de engaño utilizado?",
            "¿Cuál es el monto aproximado defraudado?",
            "¿Se utilizaron documentos falsos o firmas apócrifas?",
            "¿Cuántas víctimas hay?",
            "¿Existió un contrato de por medio?",
            "¿El fraude se realizó por medios electrónicos o en línea?",
        ],
        "subtypes": {
            "fraude_simple": {
                "display_name": "Fraude simple",
                "activation_condition": "not document_forgery and not online_fraud",
                "aggravating_factors": [],
            },
            "fraude_con_documentos_falsos": {
                "display_name": "Fraude con documentos falsos",
                "activation_condition": "document_forgery",
                "aggravating_factors": [
                    "falsificacion_documentos",
                    "firma_falsa",
                    "suplantacion",
                ],
            },
            "fraude_electronico": {
                "display_name": "Fraude electrónico",
                "activation_condition": "online_fraud",
                "aggravating_factors": [
                    "medios_electronicos",
                    "internet",
                ],
            },
            "fraude_en_pandilla": {
                "display_name": "Fraude en pandilla",
                "activation_condition": "perpetrators_count >= 3",
                "aggravating_factors": [
                    "tres_o_mas_personas",
                ],
            },
        },
        "legal_search_terms": [
            "fraude",
            "defraudacion",
            "simulacion",
            "estafa",
            "documento falso",
            "falsificacion",
            "perjuicio patrimonial",
        ],
        "minimum_investigation_steps": [
            {
                "step": "Acta de entrevista con la víctima",
                "legal_basis": "Art. 264 CNPP — Entrevistas a víctimas",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Recopilación de documentos probatorios (contratos, recibos, transferencias)",
                "legal_basis": "Art. 266 CNPP — Solicitud de información",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Dictamen pericial contable",
                "legal_basis": "Art. 271 CNPP — Peritajes",
                "urgent": False,
                "applies_when": "always",
            },
            {
                "step": "Dictamen pericial en documentoscopia (si documentos falsos)",
                "legal_basis": "Art. 271 CNPP — Peritajes especializados",
                "urgent": False,
                "applies_when": "document_forgery",
            },
            {
                "step": "Solicitud de estados de cuenta bancarios",
                "legal_basis": "Art. 266 CNPP — Solicitud de información",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Dictamen pericial en informática forense (si fraude electrónico)",
                "legal_basis": "Art. 271 CNPP — Peritajes especializados",
                "urgent": False,
                "applies_when": "online_fraud",
            },
            {
                "step": "Identificación de otras víctimas",
                "legal_basis": "Art. 213 CNPP — Investigación",
                "urgent": False,
                "applies_when": "victim_count > 1",
            },
        ],
    },
    "unknown": {
        "display_name": "Delito no clasificado",
        "detection_keywords": [],
        "extract_fields": {
            "explicit_crime_mentioned": "str|null",
            "violence_detected": "bool",
            "threat_detected": "bool",
            "weapon_used": "bool",
            "victim_count": "str|null",
            "perpetrators_count": "str|null",
        },
        "classifier_questions": [
            "¿Qué tipo de delito se cometió?",
            "¿Se usó violencia física o amenazas?",
            "¿Se utilizó algún arma?",
            "¿Cuántas víctimas hay?",
            "¿Cuántas personas participaron?",
        ],
        "subtypes": {},
        "legal_search_terms": [
            "delito",
            "conducta delictiva",
            "tipo penal",
        ],
        "minimum_investigation_steps": [
            {
                "step": "Acta de entrevista con la víctima",
                "legal_basis": "Art. 264 CNPP — Entrevistas a víctimas",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Inspección del lugar de los hechos",
                "legal_basis": "Art. 267 CNPP — Inspección del lugar",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Recopilación de indicios y cadena de custodia",
                "legal_basis": "Art. 279 CNPP — Cadena de custodia",
                "urgent": True,
                "applies_when": "always",
            },
            {
                "step": "Identificación de testigos",
                "legal_basis": "Art. 264 CNPP — Entrevistas",
                "urgent": False,
                "applies_when": "always",
            },
        ],
    },
}



# Orden de prioridad para resolver ambigüedades entre tipos de delito.
# Tipos con mayor índice tienen prioridad cuando el score es similar.
CRIME_PRIORITY: dict[str, int] = {
    "homicidio": 10,
    "violacion": 9,
    "violencia_familiar": 7,
    "fraude": 6,
    "lesiones": 5,
    "robo": 5,
    "unknown": 0,
}

import re as _re

# Señales de muerte evaluadas como palabras completas (word boundary)
# para evitar falsos positivos como "mato" dentro de "hematomas".
_DEATH_PATTERN = _re.compile(
    r"\b(?:fallecido|fallecida|muerto|muerta|cadaver|sin vida|perdio la vida"
    r"|privacion de la vida|homicidio|muerte|defuncion|necropsia"
    r"|mato|mataron|asesinado|asesinada)\b"
)


def detect_crime_type(facts: str) -> str:
    from legal_rules import normalize_text

    normalized_facts = normalize_text(facts)

    # Señal dura: indicadores de muerte como palabras completas
    if _DEATH_PATTERN.search(normalized_facts):
        return "homicidio"

    scores: dict[str, int] = {}
    for crime_key, crime_data in CRIME_CATALOG.items():
        if crime_key == "unknown":
            continue
        count = 0
        for keyword in crime_data["detection_keywords"]:
            # Usar word boundary para evitar falsos positivos de substring
            if _re.search(r"\b" + _re.escape(keyword) + r"\b", normalized_facts):
                count += 1
        if count > 0:
            scores[crime_key] = count

    if not scores:
        return "unknown"

    max_score = max(scores.values())
    # Entre los tipos con score máximo, elegir el de mayor prioridad
    top_types = [k for k, v in scores.items() if v == max_score]
    return max(top_types, key=lambda k: CRIME_PRIORITY.get(k, 0))


def get_crime_catalog_entry(crime_type: str) -> dict:
    return CRIME_CATALOG.get(crime_type, CRIME_CATALOG["unknown"])


def get_missing_questions_for_crime(
    crime_type: str,
    structured_facts: dict | None = None,
) -> list[str]:
    crime_entry = get_crime_catalog_entry(crime_type)
    return crime_entry.get("classifier_questions", [])


def get_investigation_steps_for_crime(
    crime_type: str,
    structured_facts: dict | None = None,
) -> list[dict]:
    crime_entry = get_crime_catalog_entry(crime_type)
    all_steps = crime_entry.get("minimum_investigation_steps", [])

    if not structured_facts:
        return [step for step in all_steps if step["applies_when"] == "always"]

    applicable_steps = []
    for step in all_steps:
        condition = step["applies_when"]
        if condition == "always":
            applicable_steps.append(step)
        elif evaluate_condition(condition, structured_facts):
            applicable_steps.append(step)

    return applicable_steps


def evaluate_condition(condition: str, structured_facts: dict) -> bool:
    if "==" in condition:
        field, value = condition.split("==", 1)
        field = field.strip()
        value = value.strip().strip("'\"")
        return str(structured_facts.get(field, "")).strip().lower() == value.lower()

    if "!=" in condition:
        field, value = condition.split("!=", 1)
        field = field.strip()
        value = value.strip().strip("'\"")
        return str(structured_facts.get(field, "")).strip().lower() != value.lower()

    if ">=" in condition:
        field, value = condition.split(">=", 1)
        field = field.strip()
        value = int(value.strip())
        try:
            actual = int(structured_facts.get(field, 0))
            return actual >= value
        except (ValueError, TypeError):
            return False

    if "<=" in condition:
        field, value = condition.split("<=", 1)
        field = field.strip()
        value = int(value.strip())
        try:
            actual = int(structured_facts.get(field, 0))
            return actual <= value
        except (ValueError, TypeError):
            return False

    if ">" in condition:
        field, value = condition.split(">", 1)
        field = field.strip()
        value = int(value.strip())
        try:
            actual = int(structured_facts.get(field, 0))
            return actual > value
        except (ValueError, TypeError):
            return False

    field_value = structured_facts.get(condition)
    if isinstance(field_value, bool):
        return field_value
    if isinstance(field_value, str):
        return field_value.strip().lower() not in ("", "false", "no", "none", "null")

    return False


def get_active_subtypes(
    crime_type: str,
    structured_facts: dict | None = None,
) -> list[dict]:
    crime_entry = get_crime_catalog_entry(crime_type)
    subtypes = crime_entry.get("subtypes", {})

    if not structured_facts:
        return []

    active_subtypes = []
    for subtype_key, subtype_data in subtypes.items():
        condition = subtype_data.get("activation_condition", "")
        if evaluate_subtype_condition(condition, structured_facts):
            active_subtypes.append({
                "key": subtype_key,
                **subtype_data,
            })

    return active_subtypes


def evaluate_subtype_condition(condition: str, structured_facts: dict) -> bool:
    if " and " in condition:
        parts = condition.split(" and ")
        return all(evaluate_condition(part.strip(), structured_facts) for part in parts)

    if " or " in condition:
        parts = condition.split(" or ")
        return any(evaluate_condition(part.strip(), structured_facts) for part in parts)

    if "not " in condition:
        field = condition.replace("not ", "").strip()
        return not evaluate_condition(field, structured_facts)

    if " in " in condition:
        field, values_str = condition.split(" in ", 1)
        field = field.strip()
        values_str = values_str.strip("[]")
        values = [v.strip().strip("'\"") for v in values_str.split(",")]
        actual = str(structured_facts.get(field, "")).strip().lower()
        return actual in [v.lower() for v in values]

    return evaluate_condition(condition, structured_facts)
