"""
Unit tests for Wapenda Agent Toolkit
"""

import unittest
from wapenda_toolkit import TriageEngine, DepartmentIntent, WhatsAppWebhookParser, GDPRValidator


class TestWapendaToolkit(unittest.TestCase):
    def test_triage_membership(self):
        text = "Hola, me gustaría renovar mi abono de Tribuna para esta temporada"
        intent = TriageEngine.classify_intent(text)
        self.assertEqual(intent, DepartmentIntent.MEMBERSHIP_AND_ABONOS)

    def test_triage_business_club(self):
        text = "Somos una empresa de Jerez interesada en patrocinio y vallas en Chapín"
        intent = TriageEngine.classify_intent(text)
        self.assertEqual(intent, DepartmentIntent.BUSINESS_CLUB_SPONSORSHIP)

    def test_triage_escalation(self):
        text = "Quiero poner una queja formal y hablar con un humano por favor"
        intent = TriageEngine.classify_intent(text)
        self.assertEqual(intent, DepartmentIntent.HUMAN_ESCALATION)

    def test_gdpr_hashing(self):
        phone = "+34 600 11 22 33"
        hashed = GDPRValidator.hash_phone(phone)
        self.assertEqual(len(hashed), 64)

    def test_gdpr_data_masking(self):
        text = "Mi DNI es 12345678Z y mi IBAN es ES1234567890123456789012"
        sanitized = GDPRValidator.sanitize_message_log(text)
        self.assertIn("[DNI_MASKED]", sanitized)
        self.assertIn("[IBAN_MASKED]", sanitized)


if __name__ == "__main__":
    unittest.main()
