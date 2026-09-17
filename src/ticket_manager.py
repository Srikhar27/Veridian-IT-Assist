from typing import Dict, Any, Optional
from src.database import DatabaseManager

class TicketManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def create_ticket_if_needed(
        self,
        decision: Dict[str, Any],
        employee_info: Dict[str, Any],
        user_input: str,
        request_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Creates a new structured ticket if the decision mandates ticket creation.
        Returns the created ticket dict, or None if no ticket was created.
        Checks for an existing ticket first to guarantee consistent ticket IDs across all screens.
        """
        if not decision.get("requires_ticket", False):
            return None

        # Check if a ticket was already generated for this request/query/intent
        existing_id = self.db.find_existing_ticket_id(
            request_id=request_id,
            user_input=user_input,
            intent=decision.get("intent")
        )
        if existing_id:
            existing_ticket = self.db.get_ticket_by_id(existing_id)
            if existing_ticket:
                return existing_ticket

        auto_id = self.db.get_next_auto_ticket_id()
        employee_name = employee_info.get("employee", "Employee")
        
        ticket = {
            "id": auto_id,
            "employee": employee_name,
            "issue": user_input[:120] if user_input else decision.get("intent", "IT Support Request"),
            "category": decision.get("intent", "General IT"),
            "status": decision.get("status", "Active"),
            "is_active": True,
            "assigned_team": decision.get("escalation_team", "IT Support"),
            "priority": decision.get("priority", "Medium"),
            "source_policy": decision.get("source", "N/A"),
            "escalation_reason": decision.get("reason", "Action required by policy rule engine")
        }

        self.db.save_ticket(ticket)
        return ticket

