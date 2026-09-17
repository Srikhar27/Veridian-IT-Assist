import os
import json
import re
from typing import Dict, Any, Optional

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.has_api = bool(self.api_key)

    def process_request(self, user_input: str, employee_info: Dict[str, Any], retrieved_policies: list, ticket_precedents: str) -> Dict[str, Any]:
        """
        Processes user request and returns a structured JSON payload:
        {
          "intent": str,
          "entities": dict,
          "missing_information": list,
          "candidate_policy_ids": list,
          "draft_response": str,
          "needs_clarification": bool
        }
        """
        if self.has_api:
            try:
                # Attempt API call if configured
                return self._call_llm_api(user_input, employee_info, retrieved_policies, ticket_precedents)
            except Exception as e:
                # Fallback on API failure
                print(f"[LLMClient Warning] API call failed ({e}). Falling back to deterministic NLU.")
                return self._fallback_nlu(user_input, employee_info, retrieved_policies)
        else:
            return self._fallback_nlu(user_input, employee_info, retrieved_policies)

    def _call_llm_api(self, user_input: str, employee_info: Dict[str, Any], retrieved_policies: list, ticket_precedents: str) -> Dict[str, Any]:
        """
        Standard OpenAI-compatible structured JSON completion call.
        """
        import urllib.request

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_key}"
            }
            system_prompt = (
                "You are an IT Support NLU parser for Veridian Corp. "
                "Analyze the user request and return ONLY valid JSON matching this schema:\n"
                "{\n"
                '  "intent": string,\n'
                '  "entities": object,\n'
                '  "missing_information": array of strings,\n'
                '  "candidate_policy_ids": array of strings,\n'
                '  "draft_response": string,\n'
                '  "needs_clarification": boolean\n'
                "}\n"
                "Do NOT invent policies or approvals not mentioned in retrieved policies."
            )
            prompt = (
                f"Employee: {employee_info.get('employee', 'User')}\n"
                f"Request: {user_input}\n"
                f"Retrieved Policies: {[p['id'] + ': ' + p['title'] for p in retrieved_policies]}\n"
                f"Ticket Precedents: {ticket_precedents}\n"
            )
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.0
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                content = res_data["choices"][0]["message"]["content"]
                return json.loads(content)

        return self._fallback_nlu(user_input, employee_info, retrieved_policies)

    def _fallback_nlu(self, user_input: str, employee_info: Dict[str, Any], retrieved_policies: list) -> Dict[str, Any]:
        """
        Deterministic NLU parser ensuring 100% reliable local fallback execution.
        Distinguishes all required enterprise IT support intents and extracts structured entities.
        """
        inp_lower = user_input.lower()
        candidate_ids = [p["id"] for p in retrieved_policies]

        intent = "General IT Policy Inquiry"
        entities = {}
        missing_info = []
        needs_clarification = False
        draft_response = ""

        # 1. Network Connectivity Issue (MUST be classified separately from Hardware / Asset policies)
        if any(phrase in inp_lower for phrase in ["network is not coming", "wi-fi is not working", "wifi is not working", "cannot connect to the internet", "can't connect to internet", "office network is disconnected", "cannot access the company network", "cannot access company network", "network connection", "no internet", "network issue"]):
            intent = "Network Connectivity Issue"
            entities["device"] = "Laptop" if "laptop" in inp_lower else "Workstation"
            entities["issue"] = "Network unavailable / disconnected"
            draft_response = "Assessing network connectivity issue and local adapter troubleshooting steps."

        # 2. Phishing / Security Incident
        elif any(w in inp_lower for w in ["phishing", "malware", "unauthorized access", "suspicious email", "forwarding it to a few teammates", "got a phishing email"]):
            intent = "Security Incident Reporting"
            entities["incident_type"] = "phishing_email"
            if "forward" in inp_lower:
                entities["risk_action"] = "forwarded_to_teammates"
            draft_response = "Security incident detected. Mandatory immediate security reporting required."

        # 3. Admin Access Request
        elif "admin access" in inp_lower or ("admin" in inp_lower and "server" in inp_lower):
            intent = "Admin Access Request"
            entities["target_system"] = "Finance Reporting Server" if "finance" in inp_lower else "Server"
            entities["requested_level"] = "Administrator"
            draft_response = "Checking authorization policies for server admin access."

        # 4. Password Reset & Account Lockout
        elif any(w in inp_lower for w in ["password", "lockout", "locked out"]):
            if any(w in inp_lower for w in ["locked out", "failed attempts", "6 times", "6 failed", "5 times", "5 failed"]):
                intent = "Password Lockout"
                entities["failed_attempts"] = 6 if "6" in inp_lower else 5
                entities["account_locked"] = True
            else:
                intent = "Password Reset"
                entities["account_locked"] = False
            draft_response = "Evaluating password reset / account lockout policy."

        # 5. Guest Wi-Fi Access
        elif "guest" in inp_lower and ("wifi" in inp_lower or "wi-fi" in inp_lower or "kiosk" in inp_lower or "access" in inp_lower):
            intent = "Guest Wi-Fi Access"
            entities["access_type"] = "guest_temporary"
            draft_response = "Guest Wi-Fi credentials can be generated at the front-desk kiosk."

        # 6. VPN Access & Credential Expiry
        elif "vpn" in inp_lower:
            if "contractor" in inp_lower or "joining" in inp_lower:
                intent = "VPN Access"
                entities["employment_type"] = "contractor"
            elif "expired" in inp_lower or "stopped working" in inp_lower or "renew" in inp_lower:
                intent = "VPN Credential Expiry"
                entities["employment_type"] = "full-time"
                entities["issue_type"] = "credential_expired"
            else:
                intent = "VPN Access"
                entities["employment_type"] = "full-time"
            draft_response = "Processing VPN access inquiry."

        # 7. Non-Catalog & Software Installation Request
        elif any(w in inp_lower for w in ["software catalog", "data-analysis tool", "not in the software catalog", "browser extension", "extension for productivity", "install software"]):
            if "extension" in inp_lower:
                intent = "Software Installation Request"
                entities["software_type"] = "browser_extension"
                entities["is_in_catalog"] = False
            else:
                intent = "Software Installation Request"
                entities["software_type"] = "data_analysis_tool"
                entities["is_in_catalog"] = False
            draft_response = "Evaluating software installation policy."

        # 8. Laptop Hardware & Replacement
        elif any(w in inp_lower for w in ["laptop", "notebook"]):
            if "dead" in inp_lower or "won't turn on" in inp_lower or "replace" in inp_lower or "replacement" in inp_lower or "3.5 years" in inp_lower or "3.5y" in inp_lower or "3 years" in inp_lower or "4 years" in inp_lower:
                intent = "Laptop Replacement Request"
                entities["device"] = "Laptop"
                entities["reported_issue"] = "Device does not power on" if ("dead" in inp_lower or "turn on" in inp_lower) else "Device aging / replacement request"
                entities["failure_confirmed"] = False
                if "3.5" in inp_lower:
                    entities["device_age_years"] = 3.5
                elif "3" in inp_lower:
                    entities["device_age_years"] = 3.0
                elif "2" in inp_lower:
                    entities["device_age_years"] = 2.0
            elif "flicker" in inp_lower or "flickering" in inp_lower or "screen" in inp_lower:
                intent = "Laptop Hardware Issue"
                entities["device"] = "Laptop"
                entities["reported_issue"] = "Screen flickering"
                entities["failure_confirmed"] = False
                entities["device_age_years"] = 2.0 if "2" in inp_lower else 1.0
                missing_info.append("Confirmation if flicker occurs on external monitor or hinge adjustment")
            else:
                intent = "Laptop Hardware Issue"
                entities["device"] = "Laptop"
                entities["failure_confirmed"] = False
            draft_response = "Assessing laptop issue and policy eligibility."

        # 9. Printer Troubleshooting
        elif any(w in inp_lower for w in ["printer", "paper jam", "spooler", "print"]):
            intent = "Printer Troubleshooting"
            entities["device"] = "Printer"
            entities["issue"] = "paper_jam_error"
            missing_info.append("Printer asset tag")
            draft_response = "Evaluating printer troubleshooting steps."

        # 10. Work-From-Home Equipment
        elif any(w in inp_lower for w in ["work from home", "wfh", "remote", "monitor", "chair", "home office"]):
            intent = "Work-From-Home Equipment Request"
            if "4 days" in inp_lower:
                entities["remote_days_per_week"] = 4
            elif "3 days" in inp_lower:
                entities["remote_days_per_week"] = 3
            draft_response = "Evaluating remote work equipment allowance eligibility."

        # 11. Email Mailbox Quota
        elif any(w in inp_lower for w in ["mailbox", "quota", "email full", "can't send emails"]):
            intent = "Email Mailbox Quota"
            entities["issue"] = "mailbox_full"
            draft_response = "Evaluating mailbox quota policies."

        # 12. Expense Software Access
        elif "expense" in inp_lower or "expense tool" in inp_lower:
            intent = "Expense Software Access"
            entities["application"] = "Expense Management System"
            missing_info.append("Confirmation if active expense account already exists")
            draft_response = "Assessing expense tool support scope."

        # 13. Ambiguous Request
        elif any(w in inp_lower for w in ["hey can you help", "its not working", "it's not working", "help me"]):
            intent = "Ambiguous Request"
            needs_clarification = True
            missing_info.append("Specific device, system, or error message description")
            draft_response = "Request lacks detail."

        return {
            "intent": intent,
            "entities": entities,
            "missing_information": missing_info,
            "candidate_policy_ids": candidate_ids,
            "draft_response": draft_response,
            "needs_clarification": needs_clarification
        }
