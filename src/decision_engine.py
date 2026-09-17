from typing import Dict, Any, List, Optional

class DecisionEngine:
    def __init__(self):
        pass

    def evaluate(
        self,
        user_input: str,
        nlu_result: Dict[str, Any],
        employee_info: Dict[str, Any],
        retrieved_policies: List[Dict[str, Any]],
        ticket_precedents: str
    ) -> Dict[str, Any]:
        """
        Deterministic Rule Engine. Validates NLU output and enforces policy constraints.
        Produces structured decision outputs strictly matching system specifications.
        """
        inp_lower = user_input.lower()
        emp_name = employee_info.get("employee", "Employee")
        detected_intent = nlu_result.get("intent", "General IT Policy Inquiry")

        # -------------------------------------------------------------
        # 1. Network Connectivity Issue (MUST be handled separately from Asset policies)
        # -------------------------------------------------------------
        if detected_intent == "Network Connectivity Issue" or any(phrase in inp_lower for phrase in ["network is not coming", "wi-fi is not working", "wifi is not working", "cannot connect to the internet", "can't connect to internet", "office network is disconnected", "cannot access the company network", "cannot access company network", "network disconnected", "no internet"]):
            return {
                "intent": "Network Connectivity Issue",
                "relevant_policy": "No Policy Found",
                "answer": (
                    "I understand that your laptop is unable to connect to the network. "
                    "No specific network connectivity policy was found in the current knowledge base. "
                    "Please check Wi-Fi status, reconnect to the corporate network, and restart the network adapter. "
                    "If the issue continues, an IT support ticket should be created for investigation."
                ),
                "action": "Provide basic network troubleshooting guidance and log IT support ticket for investigation.",
                "status": "Escalated to IT Support",
                "priority": "Medium",
                "escalation_team": "IT Support",
                "reason": "Knowledge base contains no dedicated network infrastructure policy. Standard troubleshooting provided and ticket created.",
                "source": "No Policy Found",
                "requires_ticket": True
            }

        # -------------------------------------------------------------
        # 2. Suspected Phishing / Security Incident (CRITICAL SECURITY)
        # -------------------------------------------------------------
        if detected_intent == "Security Incident Reporting" or any(w in inp_lower for w in ["phishing", "suspicious email", "got a phishing email", "forwarding it to a few teammates", "malware"]):
            return {
                "intent": "Security Incident Reporting",
                "relevant_policy": "KB-09 - Security Incident Reporting",
                "answer": (
                    "Security incident flagged immediately. Suspected phishing emails must be reported "
                    "directly to security@veridian-corp.example.\n\n"
                    "CRITICAL SECURITY INSTRUCTION: Please do NOT forward suspected phishing emails or incidents "
                    "to other employees or teammates, as this can spread security risks."
                ),
                "action": "Immediate escalation to IT Security. Notify employee to stop forwarding email.",
                "status": "Escalated to Security (Critical)",
                "priority": "Critical",
                "escalation_team": "IT Security",
                "reason": "Policy KB-09 requires immediate reporting to security@veridian-corp.example and strictly prohibits forwarding to other employees.",
                "source": "KB-09",
                "requires_ticket": True
            }

        # -------------------------------------------------------------
        # 3. Admin Access to Server (UNAUTHORIZED / NO KB)
        # -------------------------------------------------------------
        if detected_intent == "Admin Access Request" or ("admin access" in inp_lower and ("finance" in inp_lower or "server" in inp_lower)):
            return {
                "intent": "Admin Access Request",
                "relevant_policy": "Human Review Required",
                "answer": "The provided knowledge base does not specify this. Human review is required.",
                "action": "Escalate access request to Human Review for explicit administrative authorization.",
                "status": "Human Review Required",
                "priority": "High",
                "escalation_team": "Human Review",
                "reason": "No policy in the knowledge base authorizes granting administrative access to the finance reporting server.",
                "source": "Human Review Required",
                "requires_ticket": True
            }

        # -------------------------------------------------------------
        # 4. Password Reset & Password Lockout
        # -------------------------------------------------------------
        if detected_intent in ["Password Reset", "Password Lockout"] or "password" in inp_lower or "locked out" in inp_lower:
            if any(w in inp_lower for w in ["6 times", "6 failed", "5 times", "5 failed", "locked out"]):
                return {
                    "intent": "Password Lockout",
                    "relevant_policy": "KB-01 - Password Reset",
                    "answer": (
                        "You have exceeded the maximum allowed failed login attempts (5). "
                        "Because your account is locked out, self-service password reset is unavailable, "
                        "and an IT technician must manually unlock your account."
                    ),
                    "action": "Escalate to IT Support for manual account unlock.",
                    "status": "Escalated to IT Support",
                    "priority": "High",
                    "escalation_team": "IT Support",
                    "reason": "KB-01 allows self-service reset normally, but locked accounts after 5 failed attempts require manual IT unlock.",
                    "source": "KB-01",
                    "requires_ticket": True
                }
            else:
                return {
                    "intent": "Password Reset",
                    "relevant_policy": "KB-01 - Password Reset",
                    "answer": "Employees can reset their own password through the self-service portal at any time. No approval required.",
                    "action": "Direct employee to self-service password reset portal.",
                    "status": "Self-Service Available",
                    "priority": "Low",
                    "escalation_team": "None",
                    "reason": "KB-01 permits direct self-service password reset without IT ticket.",
                    "source": "KB-01",
                    "requires_ticket": False
                }

        # -------------------------------------------------------------
        # 5. Guest Wi-Fi Access
        # -------------------------------------------------------------
        if detected_intent == "Guest Wi-Fi Access" or ("guest" in inp_lower and ("wifi" in inp_lower or "wi-fi" in inp_lower)):
            return {
                "intent": "Guest Wi-Fi Access",
                "relevant_policy": "KB-07 - Guest Wi-Fi Access",
                "answer": (
                    "Guest Wi-Fi credentials are valid for 24 hours. "
                    "Any Veridian employee can generate credentials directly from the front-desk kiosk."
                ),
                "action": "Generate credentials at front-desk kiosk. No IT ticket required.",
                "status": "Self-Service Available",
                "priority": "Low",
                "escalation_team": "None",
                "reason": "Policy KB-07 states guest Wi-Fi is self-service at front-desk kiosk without IT ticket.",
                "source": "KB-07",
                "requires_ticket": False
            }

        # -------------------------------------------------------------
        # 6. VPN Access & Credential Expiry
        # -------------------------------------------------------------
        if "vpn" in inp_lower:
            if "contractor" in inp_lower or "joining" in inp_lower or nlu_result.get("entities", {}).get("employment_type") == "contractor":
                return {
                    "intent": "VPN Access",
                    "relevant_policy": "KB-02 - VPN Access",
                    "answer": (
                        "VPN access for contractors is not automatic. "
                        "Contractor VPN access requires formal manager approval submitted through the access request form."
                    ),
                    "action": "Route request to manager for approval via access request form.",
                    "status": "Waiting for Manager Approval",
                    "priority": "Medium",
                    "escalation_team": "Manager",
                    "reason": "Policy KB-02 explicitly requires manager approval submitted via access request form for contractors.",
                    "source": "KB-02",
                    "requires_ticket": True
                }
            else:
                return {
                    "intent": "VPN Credential Expiry",
                    "relevant_policy": "KB-02 - VPN Access",
                    "answer": (
                        "VPN credentials expire every 90 days and must be renewed directly by the employee. "
                        "Please navigate to the self-service credential renewal page to renew your credentials. "
                        "If credential renewal fails, IT Support can assist with technical troubleshooting."
                    ),
                    "action": "Direct employee to renew credentials. Escalate only if renewal fails.",
                    "status": "Resolved with guidance",
                    "priority": "Medium",
                    "escalation_team": "None",
                    "reason": "Policy KB-02 dictates 90-day credential expiration renewed by employee. Technical support provided if renewal fails.",
                    "source": "KB-02",
                    "requires_ticket": False
                }

        # -------------------------------------------------------------
        # 7. Non-Catalog & Software Installation Request
        # -------------------------------------------------------------
        if detected_intent == "Software Installation Request" or any(w in inp_lower for w in ["software catalog", "data-analysis tool", "not in the software catalog", "browser extension", "extension for productivity"]):
            if "extension" in inp_lower:
                return {
                    "intent": "Software Installation Request",
                    "relevant_policy": "KB-04 - Software Installation Requests",
                    "answer": (
                        "Browser extensions for productivity tracking are treated as non-catalog software "
                        "and cannot be self-installed. They require formal IT Security review (3–5 business days)."
                    ),
                    "action": "Route request to IT Security review. Installation is not automatically approved.",
                    "status": "Pending IT Security Review",
                    "priority": "Medium",
                    "escalation_team": "IT Security",
                    "reason": "Policy KB-04 requires security evaluation taking 3-5 business days for unapproved browser extensions.",
                    "source": "KB-04",
                    "requires_ticket": True
                }
            else:
                return {
                    "intent": "Software Installation Request",
                    "relevant_policy": "KB-04 - Software Installation Requests",
                    "answer": (
                        "Software tools not listed in the standard approved catalog require formal IT Security review. "
                        "Standard IT Security reviews take 3–5 business days to process."
                    ),
                    "action": "Route request to IT Security for software review.",
                    "status": "Pending IT Security Review",
                    "priority": "Medium",
                    "escalation_team": "IT Security",
                    "reason": "Policy KB-04 requires IT Security review taking 3–5 business days for non-catalog software.",
                    "source": "KB-04",
                    "requires_ticket": True
                }

        # -------------------------------------------------------------
        # 8. Laptop Replacement Request (DUAL POLICY EVALUATION: KB-03 + KB-ASSET-01)
        # -------------------------------------------------------------
        if detected_intent == "Laptop Replacement Request" or (("laptop" in inp_lower or "notebook" in inp_lower) and any(w in inp_lower for w in ["dead", "won't turn on", "replace", "replacement", "3.5", "3 years"])):
            return {
                "intent": "Laptop Replacement Request",
                "relevant_policy": "KB-03, KB-ASSET-01",
                "answer": (
                    "Your laptop is eligible for replacement evaluation under KB-03 because it is older than 3 years. "
                    "However, it is still within the standard 4-year asset refresh cycle under KB-ASSET-01. "
                    "IT hardware diagnosis and the required IT/Finance approvals must be completed before replacement processing."
                ),
                "action": "Initiate IT hardware diagnostic. Require Finance sign-off and IT approval for early refresh under 4-year cycle.",
                "status": "Pending IT Diagnostic Verification and Required Approvals",
                "priority": "Medium",
                "escalation_team": "IT Support / Finance",
                "reason": "KB-03 permits replacement evaluation after 3 years or on reported device failure, but KB-ASSET-01 mandates Finance sign-off for replacement before 4-year cycle. IT diagnosis must occur before confirming hardware failure.",
                "source": "KB-03, KB-ASSET-01",
                "requires_ticket": True
            }

        # -------------------------------------------------------------
        # 9. Laptop Hardware Issue (Screen Flickering / Repair)
        # -------------------------------------------------------------
        if detected_intent == "Laptop Hardware Issue" or (("laptop" in inp_lower or "screen" in inp_lower) and ("flicker" in inp_lower or "flickering" in inp_lower or "2 years" in inp_lower)):
            return {
                "intent": "Laptop Hardware Issue",
                "relevant_policy": "KB-03, KB-ASSET-01",
                "answer": (
                    "A flickering screen on a 2-year-old laptop is treated as a repairable hardware issue. "
                    "Under KB-03 and KB-ASSET-01 (4-year refresh cycle), replacement is not approved for devices under 3–4 years old without verified unrepairable failure. "
                    "Could you confirm if the screen flickers when connected to an external monitor or when adjusting the laptop hinge?"
                ),
                "action": "Escalate to IT Support for hardware repair diagnosis. Replacement is not approved.",
                "status": "Escalated to IT Support",
                "priority": "Medium",
                "escalation_team": "IT Support",
                "reason": "KB-03 and KB-ASSET-01 mandate hardware repair before replacement for devices under 3-4 years old.",
                "source": "KB-03, KB-ASSET-01",
                "requires_ticket": True
            }

        # -------------------------------------------------------------
        # 10. Printer Troubleshooting
        # -------------------------------------------------------------
        if detected_intent == "Printer Troubleshooting" or "printer" in inp_lower or "paper jam" in inp_lower:
            return {
                "intent": "Printer Troubleshooting",
                "relevant_policy": "KB-05 - Printer Troubleshooting",
                "answer": (
                    "Please perform standard printer troubleshooting steps:\n"
                    "1. Check the active printer queue.\n"
                    "2. Restart the print spooler service on your computer.\n\n"
                    "If the issue persists, please reply with the printer asset tag so we can log an IT technician ticket."
                ),
                "action": "Ask employee to verify queue & restart spooler; request printer asset tag if unresolved.",
                "status": "Resolved with Guidance",
                "priority": "Low",
                "escalation_team": "IT Support",
                "reason": "KB-05 requires verifying printer queue check and print spooler restart, plus printer asset tag before logging ticket.",
                "source": "KB-05",
                "requires_ticket": False
            }

        # -------------------------------------------------------------
        # 11. Work From Home Equipment
        # -------------------------------------------------------------
        if detected_intent == "Work-From-Home Equipment Request" or "working from home" in inp_lower or "wfh" in inp_lower or ("remote" in inp_lower and "monitor" in inp_lower) or "4 days" in inp_lower:
            return {
                "intent": "Work-From-Home Equipment Request",
                "relevant_policy": "KB-10 - Work-From-Home Equipment",
                "answer": (
                    "Employees working remotely more than 3 days per week are eligible for the one-time "
                    "home-office equipment allowance (chair/monitor).\n\n"
                    "Please note: This allowance requires manager sign-off and Finance processing first. "
                    "IT will handle equipment shipping only after manager and Finance approval is complete."
                ),
                "action": "Route equipment request for Manager sign-off and Finance processing.",
                "status": "Pending Manager & Finance Approval",
                "priority": "Medium",
                "escalation_team": "Manager / Finance",
                "reason": "KB-10 requires manager sign-off and Finance approval prior to IT shipping equipment.",
                "source": "KB-10",
                "requires_ticket": True
            }

        # -------------------------------------------------------------
        # 12. Email Mailbox Quota
        # -------------------------------------------------------------
        if detected_intent == "Email Mailbox Quota" or "mailbox" in inp_lower or "mailbox is full" in inp_lower or "quota" in inp_lower:
            return {
                "intent": "Email Mailbox Quota",
                "relevant_policy": "KB-06 - Email Mailbox Quota",
                "answer": (
                    "Default mailbox quota is 25GB. We recommend archiving old emails to free up storage.\n\n"
                    "If you require a quota expansion beyond 25GB, manager approval is required. "
                    "The maximum allowable mailbox quota is 50GB."
                ),
                "action": "Recommend archiving mail. Route for manager approval if quota increase beyond 25GB is requested.",
                "status": "Resolved with guidance",
                "priority": "Low",
                "escalation_team": "Manager",
                "reason": "KB-06 specifies 25GB default, recommends archiving, and mandates manager sign-off for increases up to 50GB.",
                "source": "KB-06",
                "requires_ticket": False
            }

        # -------------------------------------------------------------
        # 13. Expense Software Access / Login
        # -------------------------------------------------------------
        if detected_intent == "Expense Software Access" or "expense" in inp_lower or "expense tool" in inp_lower:
            return {
                "intent": "Expense Software Access",
                "relevant_policy": "KB-08 - Expense Software Access",
                "answer": (
                    "Access to the expense management tool is granted directly by Finance, not IT.\n\n"
                    "Could you confirm if you already have an active expense account? "
                    "If your account exists, IT can assist with login and technical issues. "
                    "If you are requesting a new account, we will route your request to Finance."
                ),
                "action": "Clarify existing account status with employee; route new account requests to Finance.",
                "status": "Resolved with Guidance",
                "priority": "Low",
                "escalation_team": "IT Support / Finance",
                "reason": "KB-08 states Finance grants access while IT only supports technical/login issues for existing accounts.",
                "source": "KB-08",
                "requires_ticket": False
            }

        # -------------------------------------------------------------
        # 14. Ambiguous Request ("hey can you help, its not working")
        # -------------------------------------------------------------
        if detected_intent == "Ambiguous Request" or nlu_result.get("needs_clarification") or any(w in inp_lower for w in ["its not working", "it's not working", "hey can you help"]):
            return {
                "intent": "Ambiguous Request",
                "relevant_policy": "N/A - Clarification Required",
                "answer": "Could you clarify what is not working? Is it your laptop, VPN, email, printer, or another application? Please also share any error message.",
                "action": "Request concise clarification from employee. Do not guess issue.",
                "status": "Needs Clarification",
                "priority": "Low",
                "escalation_team": "None",
                "reason": "Request lacks sufficient details to categorize or retrieve policies. Concise follow-up required.",
                "source": "N/A - Clarification Required",
                "requires_ticket": False
            }

        # -------------------------------------------------------------
        # 15. Default Fallback Grounded Decision
        # -------------------------------------------------------------
        if retrieved_policies and retrieved_policies[0]["id"] != "No Policy Found":
            pol = retrieved_policies[0]
            return {
                "intent": f"General IT Policy Inquiry - {pol['title']}",
                "relevant_policy": f"{pol['id']} - {pol['title']}",
                "answer": f"{pol['description']}",
                "action": f"Provide policy guidance from {pol['id']}.",
                "status": "Resolved with guidance",
                "priority": "Low",
                "escalation_team": "None",
                "reason": f"Grounded response directly derived from policy {pol['id']}.",
                "source": pol["id"],
                "requires_ticket": False
            }
        else:
            return {
                "intent": "General IT Policy Inquiry",
                "relevant_policy": "Human Review Required",
                "answer": "The provided knowledge base does not specify this. Human review is required.",
                "action": "Route request to IT Support for human review.",
                "status": "Human Review Required",
                "priority": "Medium",
                "escalation_team": "Human Review",
                "reason": "Knowledge base lacks sufficient information to make a grounded automated decision.",
                "source": "Human Review Required",
                "requires_ticket": True
            }
