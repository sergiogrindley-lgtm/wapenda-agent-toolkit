"""
WhatsApp Webhook Parser and Schema Normalizer
Supports Meta WhatsApp Cloud API and Evolution API formats.
Zero external dependencies (uses standard dataclasses).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedMessage:
    message_id: str
    sender_phone: str
    sender_name: Optional[str] = "Anonymous"
    text: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    media_type: Optional[str] = "text"
    media_url: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None


class WhatsAppWebhookParser:
    @staticmethod
    def parse_meta_payload(payload: Dict[str, Any]) -> Optional[NormalizedMessage]:
        """Parses an official Meta WhatsApp Cloud API webhook payload."""
        try:
            entries = payload.get("entry", [])
            if not entries:
                return None
            changes = entries[0].get("changes", [])
            if not changes:
                return None
            value = changes[0].get("value", {})
            messages = value.get("messages", [])
            if not messages:
                return None
            
            msg = messages[0]
            contacts = value.get("contacts", [{}])
            contact_name = contacts[0].get("profile", {}).get("name", "User") if contacts else "User"

            msg_type = msg.get("type", "text")
            body = ""
            if msg_type == "text":
                body = msg.get("text", {}).get("body", "")
            elif msg_type == "interactive":
                interactive = msg.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    body = interactive.get("button_reply", {}).get("title", "")
                elif interactive.get("type") == "list_reply":
                    body = interactive.get("list_reply", {}).get("title", "")
            else:
                body = f"[{msg_type.upper()} Attachment]"

            return NormalizedMessage(
                message_id=msg.get("id", ""),
                sender_phone=msg.get("from", ""),
                sender_name=contact_name,
                text=body,
                media_type=msg_type,
                raw_payload=payload
            )
        except Exception:
            return None

    @staticmethod
    def parse_evolution_payload(payload: Dict[str, Any]) -> Optional[NormalizedMessage]:
        """Parses an Evolution API webhook payload."""
        try:
            data = payload.get("data", {})
            msg_key = data.get("key", {})
            msg_content = data.get("message", {})

            text = ""
            if "conversation" in msg_content:
                text = msg_content["conversation"]
            elif "extendedTextMessage" in msg_content:
                text = msg_content["extendedTextMessage"].get("text", "")
            else:
                text = "[Attachment/Audio]"

            sender = msg_key.get("remoteJid", "").split("@")[0]
            push_name = data.get("pushName", "User")

            return NormalizedMessage(
                message_id=msg_key.get("id", ""),
                sender_phone=sender,
                sender_name=push_name,
                text=text,
                media_type="text",
                raw_payload=payload
            )
        except Exception:
            return None
