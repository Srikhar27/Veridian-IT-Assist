from typing import Dict, Any, List
from src.database import DatabaseManager

class AuditLogger:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def log_interaction(
        self,
        request_id: str,
        employee_info: Dict[str, Any],
        user_input: str,
        nlu_result: Dict[str, Any],
        retrieved_policies: List[Dict[str, Any]],
        ticket_precedent: str,
        decision: Dict[str, Any],
        ticket: Dict[str, Any] = None,
        payload_json: str = ""
    ):
        """
        Records an immutable audit entry in database.
        """
        pol_str = ", ".join([p["id"] for p in retrieved_policies]) if retrieved_policies else decision.get("source", "N/A")
        ticket_id = ticket["id"] if ticket else "N/A"
        
        audit_entry = {
            "request_id": request_id,
            "employee": employee_info.get("employee", "Anonymous"),
            "user_input": user_input,
            "detected_intent": nlu_result.get("intent", decision.get("intent", "Unknown")),
            "retrieved_policy": pol_str,
            "relevant_ticket_history": ticket_precedent,
            "decision": decision.get("reason", ""),
            "action_taken": decision.get("action", ""),
            "escalation_team": decision.get("escalation_team", "None"),
            "priority": decision.get("priority", "Low"),
            "generated_ticket_id": ticket_id,
            "final_status": decision.get("status", "Completed"),
            "payload_json": payload_json
        }

        inserted_id = self.db.record_audit(audit_entry)
        
        if request_id and request_id.startswith("REQ-"):
            self.db.record_processed_request(
                request_id,
                decision.get("reason", "Processed"),
                decision.get("status", "Processed"),
                ticket_id,
                payload_json
            )
        return inserted_id
