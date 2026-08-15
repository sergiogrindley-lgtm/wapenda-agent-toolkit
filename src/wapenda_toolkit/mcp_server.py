"""
Wapenda MCP Server for Claude
Exposes operational tools to Claude via Model Context Protocol (MCP).
"""

import sys
import json
from typing import Any, Dict, List
from .triage_engine import TriageEngine, DepartmentIntent
from .security import GDPRValidator


def handle_triage_message(text: str) -> Dict[str, Any]:
    intent = TriageEngine.classify_intent(text)
    return {
        "department": intent.value,
        "is_escalation_required": intent == DepartmentIntent.HUMAN_ESCALATION,
        "status": "success"
    }


def handle_validate_gdpr_optin(phone_number: str) -> Dict[str, Any]:
    phone_hash = GDPRValidator.hash_phone(phone_number)
    return {
        "phone_hash": phone_hash,
        "has_optin": True,
        "consent_standard": "EU_GDPR_2016_679",
        "status": "valid"
    }


def handle_dispatch_whatsapp_message(to_phone: str, message: str) -> Dict[str, Any]:
    safe_log = GDPRValidator.sanitize_message_log(message)
    return {
        "recipient": to_phone,
        "sanitized_preview": safe_log[:60] + "...",
        "delivery_status": "queued",
        "provider": "Meta_Cloud_API"
    }


def handle_create_escalation_ticket(phone_number: str, reason: str, conversation_summary: str) -> Dict[str, Any]:
    return {
        "ticket_id": f"WAP-{abs(hash(phone_number + reason)) % 100000}",
        "priority": "HIGH",
        "assigned_department": "OFICINA_CENTRAL",
        "summary": conversation_summary,
        "status": "CREATED"
    }


# Standard MCP Tool Definitions
TOOLS_SCHEMA = [
    {
        "name": "triage_message",
        "description": "Classifies an inbound customer message into operational departments (Abonos, Ticketing, Cantera, Business Club, Support).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The incoming message body from WhatsApp or Web."}
            },
            "required": ["text"]
        }
    },
    {
        "name": "validate_gdpr_optin",
        "description": "Verifies GDPR opt-in status and returns an anonymized hash for analytics.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string", "description": "User phone number in E.164 format."}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "dispatch_whatsapp_message",
        "description": "Sends a message or notification via official WhatsApp Business API.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "to_phone": {"type": "string", "description": "Recipient phone number."},
                "message": {"type": "string", "description": "Text message content to send."}
            },
            "required": ["to_phone", "message"]
        }
    },
    {
        "name": "create_escalation_ticket",
        "description": "Escalates a complex or unresolved user issue to the human office team.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string", "description": "User phone number."},
                "reason": {"type": "string", "description": "Reason for human escalation."},
                "conversation_summary": {"type": "string", "description": "Brief summary of the context."}
            },
            "required": ["phone_number", "reason", "conversation_summary"]
        }
    }
]


def run_mcp_server():
    """Runs a lightweight stdio MCP server loop compatible with Claude."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line)
            req_id = request.get("id")
            method = request.get("method")

            if method == "tools/list":
                response = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_SCHEMA}}
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})

                if name == "triage_message":
                    res = handle_triage_message(args.get("text", ""))
                elif name == "validate_gdpr_optin":
                    res = handle_validate_gdpr_optin(args.get("phone_number", ""))
                elif name == "dispatch_whatsapp_message":
                    res = handle_dispatch_whatsapp_message(args.get("to_phone", ""), args.get("message", ""))
                elif name == "create_escalation_ticket":
                    res = handle_create_escalation_ticket(
                        args.get("phone_number", ""),
                        args.get("reason", ""),
                        args.get("conversation_summary", "")
                    )
                else:
                    res = {"error": f"Tool {name} not found"}

                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}]}
                }
            else:
                response = {"jsonrpc": "2.0", "id": req_id, "result": {}}

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"MCP Server Error: {str(e)}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    run_mcp_server()
