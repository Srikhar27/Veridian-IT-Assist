from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class ChatRequest(BaseModel):
    query: str
    employee: Optional[str] = 'Anonymous Employee'
    email: Optional[str] = 'employee@veridian-corp.example'
    request_id: Optional[str] = None

class ChatResponse(BaseModel):
    intent: str
    relevant_policy: str
    answer: str
    action: str
    status: str
    priority: str
    escalation_team: str
    reason: str
    source: str
    ticket_id: str
    decision_details: Optional[Dict[str, Any]] = None

class TraceRequest(BaseModel):
    query: str
    employee: Optional[str] = 'Anonymous Employee'
    email: Optional[str] = 'employee@veridian-corp.example'
    request_id: Optional[str] = None

class TicketUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_team: Optional[str] = None
    resolution_notes: Optional[str] = None

class SingleRequestProcess(BaseModel):
    request_id: str
