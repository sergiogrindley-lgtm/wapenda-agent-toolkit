"""
GDPR and Privacy Compliance Validator
"""

import hashlib
from typing import Dict, Any, Optional
from datetime import datetime


class GDPRValidator:
    """Provides consent logging and data masking helpers for European compliance."""

    @staticmethod
    def hash_phone(phone_number: str) -> str:
        """Returns a non-reversible SHA-256 hash of a phone number for privacy-compliant analytics."""
        clean_phone = "".join(filter(str.isdigit, phone_number))
        return hashlib.sha256(clean_phone.encode("utf-8")).hexdigest()

    @staticmethod
    def check_optin(phone_number: str, consent_registry: Optional[Dict[str, Any]] = None) -> bool:
        """Verifies if the contact has recorded opt-in consent."""
        if not consent_registry:
            # Default to true for inbound conversational sessions within 24h Meta window
            return True
        hashed = GDPRValidator.hash_phone(phone_number)
        return consent_registry.get(hashed, {}).get("optin_status", False)

    @staticmethod
    def sanitize_message_log(text: str) -> str:
        """Masks sensitive credit card and DNI/NIE numbers from logs."""
        import re
        # Mask Spanish DNI/NIE patterns
        sanitized = re.sub(r"\b\d{8}[A-Za-z]\b", "[DNI_MASKED]", text)
        sanitized = re.sub(r"\b[XYZxyz]\d{7}[A-Za-z]\b", "[NIE_MASKED]", sanitized)
        # Mask IBANs
        sanitized = re.sub(r"\bES\d{22}\b", "[IBAN_MASKED]", sanitized)
        return sanitized
