"""
Multi-Department Triage and Intent Classification Engine
"""

from enum import Enum
from typing import Dict, Any, List


class DepartmentIntent(str, Enum):
    MEMBERSHIP_AND_ABONOS = "MEMBERSHIP_AND_ABONOS"
    TICKETING_AND_MATCHDAY = "TICKETING_AND_MATCHDAY"
    YOUTH_ACADEMY_CANTERA = "YOUTH_ACADEMY_CANTERA"
    BUSINESS_CLUB_SPONSORSHIP = "BUSINESS_CLUB_SPONSORSHIP"
    STORE_AND_MERCHANDISING = "STORE_AND_MERCHANDISING"
    PRESS_AND_MEDIA = "PRESS_AND_MEDIA"
    GENERAL_CUSTOMER_SERVICE = "GENERAL_CUSTOMER_SERVICE"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"


class TriageEngine:
    KEYWORDS_MAP = {
        DepartmentIntent.MEMBERSHIP_AND_ABONOS: [
            "abono", "abonar", "renovar", "carnet", "cuota", "socio", "asiento", "grada", "tribuna", "preferencia", "fondo", "financiar"
        ],
        DepartmentIntent.TICKETING_AND_MATCHDAY: [
            "entrada", "ticket", "taquilla", "puerta", "torno", "estadio", "partido", "horario", "aparcamiento", "parking", "chapin", "acceso"
        ],
        DepartmentIntent.YOUTH_ACADEMY_CANTERA: [
            "cantera", "prebenjamin", "benjamin", "alevin", "infantil", "cadete", "juvenil", "filial", "entrenamiento", "tutor", "padres", "partes medicos"
        ],
        DepartmentIntent.BUSINESS_CLUB_SPONSORSHIP: [
            "patrocinio", "patrocinador", "empresa", "publicidad", "business club", "valla", "palco vip", "convenio", "factura", "b2b"
        ],
        DepartmentIntent.STORE_AND_MERCHANDISING: [
            "tienda", "camiseta", "equipacion", "comprar", "talla", "merchandising", "bufanda", "envio", "stock"
        ],
        DepartmentIntent.PRESS_AND_MEDIA: [
            "prensa", "acreditacion", "periodista", "entrevista", "medio", "rueda de prensa", "nota de prensa"
        ]
    }

    @classmethod
    def classify_intent(cls, message_text: str) -> DepartmentIntent:
        """Classifies incoming text into an operational department."""
        text_lower = message_text.lower()

        # Check explicit human escalation trigger
        if any(w in text_lower for w in ["humano", "agente", "hablar con alguien", "persona", "queja", "reclamacion"]):
            return DepartmentIntent.HUMAN_ESCALATION

        scores: Dict[DepartmentIntent, int] = {dept: 0 for dept in cls.KEYWORDS_MAP}

        for dept, keywords in cls.KEYWORDS_MAP.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[dept] += 1

        best_dept = max(scores, key=scores.get)
        if scores[best_dept] > 0:
            return best_dept

        return DepartmentIntent.GENERAL_CUSTOMER_SERVICE
