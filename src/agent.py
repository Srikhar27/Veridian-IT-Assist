import json
from typing import Dict, Any, List, Optional
from src.database import DatabaseManager
from src.policy_retriever import PolicyRetriever
from src.ticket_context import TicketContextRetriever
from src.llm_client import LLMClient
from src.decision_engine import DecisionEngine
from src.ticket_manager import TicketManager
from src.audit import AuditLogger

class ITAgentService:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        self.policies = self.db.get_policies()
        self.tickets = self.db.get_all_tickets()
        
        self.policy_retriever = PolicyRetriever(self.policies)
        self.ticket_retriever = TicketContextRetriever(self.tickets)
        self.llm_client = LLMClient()
        self.decision_engine = DecisionEngine()
        self.ticket_manager = TicketManager(self.db)
        self.audit_logger = AuditLogger(self.db)

    def process(
        self,
        user_input: str,
        employee_info: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        read_only: bool = False,
        force_reprocess: bool = False
    ) -> Dict[str, Any]:
        """
        Main Agent Execution Pipeline with Idempotency & Deduplication:
        1. Check if request_id or user_input has already been processed. Return saved payload if so.
        2. NLU / Intent Extraction & Entity Analysis
        3. Knowledge Base Policy Retrieval
        4. Relevant Ticket History Retrieval
        5. Deterministic Decision Engine Validation
        6. Structured Ticket Creation (if needed, single stable ticket_id per request_id)
        7. Immutable Audit Log Recording (single record per request)
        """
        if not user_input or not user_input.strip():
            return {
                "intent": "Empty Input",
                "relevant_policy": "None",
                "answer": "Please provide details regarding your IT issue or question.",
                "action": "Prompt user for input.",
                "status": "Invalid Input",
                "priority": "Low",
                "escalation_team": "None",
                "reason": "Input string was empty or whitespace.",
                "source": "System",
                "ticket_id": "N/A"
            }

        emp_info = employee_info or {"employee": "Anonymous Employee", "email": "employee@veridian-corp.example"}
        req_id = request_id or "CHAT-SESSION"

        # Step 0: Check idempotency & return saved payload if request was already processed
        if not force_reprocess:
            existing_payload = self.db.get_existing_processed_payload(request_id=req_id, user_input=user_input)
            if existing_payload:
                return existing_payload

        # Step 1: Retrieve Relevant Knowledge Base Policies
        matching_policies, primary_policy_citation = self.policy_retriever.retrieve_policies(user_input)

        # Step 2: Retrieve Relevant Ticket Precedents
        relevant_tickets = self.ticket_retriever.retrieve_relevant_tickets(user_input)
        ticket_precedent_summary = self.ticket_retriever.format_ticket_precedent_summary(relevant_tickets)

        # Step 3: LLM / Fallback NLU Processing
        nlu_result = self.llm_client.process_request(
            user_input=user_input,
            employee_info=emp_info,
            retrieved_policies=matching_policies,
            ticket_precedents=ticket_precedent_summary
        )

        # Step 4: Deterministic Decision Engine Validation & Policy Rule Enforcement
        decision = self.decision_engine.evaluate(
            user_input=user_input,
            nlu_result=nlu_result,
            employee_info=emp_info,
            retrieved_policies=matching_policies,
            ticket_precedents=ticket_precedent_summary
        )

        # Handle Read-Only Mode (e.g. Decision Trace preview without modifying state)
        if read_only:
            existing_ticket_id = "N/A"
            existing_payload = self.db.get_existing_processed_payload(request_id=req_id, user_input=user_input)
            if existing_payload:
                existing_ticket_id = existing_payload.get("ticket_id", "N/A")

            if existing_ticket_id == "N/A":
                found_id = self.db.find_existing_ticket_id(request_id=req_id, user_input=user_input, intent=decision.get("intent"))
                if found_id:
                    existing_ticket_id = found_id

            created_ticket_obj = self.db.get_ticket_by_id(existing_ticket_id) if existing_ticket_id != "N/A" else None

            return {
                "intent": decision.get("intent", nlu_result.get("intent", "IT Inquiry")),
                "relevant_policy": decision.get("relevant_policy", primary_policy_citation),
                "answer": decision.get("answer", ""),
                "action": decision.get("action", ""),
                "status": decision.get("status", "Resolved"),
                "priority": decision.get("priority", "Low"),
                "escalation_team": decision.get("escalation_team", "None"),
                "reason": decision.get("reason", ""),
                "source": decision.get("source", primary_policy_citation),
                "ticket_id": existing_ticket_id,
                "decision_details": {
                    "nlu_result": nlu_result,
                    "retrieved_policies": matching_policies,
                    "ticket_precedents": relevant_tickets,
                    "rule_decision": decision,
                    "created_ticket": created_ticket_obj
                }
            }

        # Step 5: Structured Ticket Creation (if required by decision)
        created_ticket = self.ticket_manager.create_ticket_if_needed(decision, emp_info, user_input, request_id=req_id)
        ticket_id = created_ticket["id"] if created_ticket else "N/A"


        # Step 6: Form Response Payload
        response_payload = {
            "intent": decision.get("intent", nlu_result.get("intent", "IT Inquiry")),
            "relevant_policy": decision.get("relevant_policy", primary_policy_citation),
            "answer": decision.get("answer", ""),
            "action": decision.get("action", ""),
            "status": decision.get("status", "Resolved"),
            "priority": decision.get("priority", "Low"),
            "escalation_team": decision.get("escalation_team", "None"),
            "reason": decision.get("reason", ""),
            "source": decision.get("source", primary_policy_citation),
            "ticket_id": ticket_id,
            "decision_details": {
                "nlu_result": nlu_result,
                "retrieved_policies": matching_policies,
                "ticket_precedents": relevant_tickets,
                "rule_decision": decision,
                "created_ticket": created_ticket
            }
        }

        # Step 7: Immutable Audit Log Writing (with JSON serialization for idempotency cache)
        payload_json = json.dumps(response_payload)
        self.audit_logger.log_interaction(
            request_id=req_id,
            employee_info=emp_info,
            user_input=user_input,
            nlu_result=nlu_result,
            retrieved_policies=matching_policies,
            ticket_precedent=ticket_precedent_summary,
            decision=decision,
            ticket=created_ticket,
            payload_json=payload_json
        )

        return response_payload
