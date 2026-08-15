"""
Wapenda Agent Toolkit
====================
An open-source Model Context Protocol (MCP) server and developer toolkit
for connecting Claude and AI agents with WhatsApp and business operations.
"""

from .whatsapp_handler import WhatsAppWebhookParser, NormalizedMessage
from .triage_engine import TriageEngine, DepartmentIntent
from .security import GDPRValidator

__version__ = "0.1.0"
__all__ = [
    "WhatsAppWebhookParser",
    "NormalizedMessage",
    "TriageEngine",
    "DepartmentIntent",
    "GDPRValidator",
]
