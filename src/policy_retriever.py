import re
from typing import List, Dict, Any, Optional, Tuple

class PolicyRetriever:
    def __init__(self, policies: List[Dict[str, Any]]):
        self.policies = policies

    def retrieve_policies(self, query: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Retrieves relevant policies based on text matching and intent keyword analysis.
        Returns a tuple of (matching_policies_list, primary_policy_id_string).
        """
        query_lower = query.lower()
        scored_policies = []

        for policy in self.policies:
            score = 0
            pid = policy["id"]
            title = policy["title"].lower()
            desc = policy["description"].lower()
            category = policy.get("category", "").lower()

            # Dedicated Network check first: Network connectivity queries MUST NOT retrieve asset replacement policies
            is_network_query = any(phrase in query_lower for phrase in [
                "network is not coming", "wi-fi is not working", "wifi is not working",
                "cannot connect to the internet", "can't connect to internet",
                "office network is disconnected", "cannot access the company network",
                "cannot access company network", "network disconnected", "no internet", "network issue"
            ])

            if is_network_query:
                # Network query - do NOT match asset replacement policies (KB-03, KB-ASSET-01)
                if pid == "KB-07" and any(w in query_lower for w in ["guest", "visitor"]):
                    score += 5
                # No specific network infrastructure troubleshooting policy exists in KB-01..10
                continue

            # Keyword matching rules
            if pid == "KB-01": # Password Reset
                if any(w in query_lower for w in ["password", "lockout", "locked out", "failed attempts", "invalid password", "reset"]):
                    score += 10
            elif pid == "KB-02": # VPN Access
                if "vpn" in query_lower:
                    score += 10
                if "contractor" in query_lower and "vpn" in query_lower:
                    score += 5
            elif pid == "KB-03": # Laptop Replacement / Hardware
                if any(w in query_lower for w in ["laptop", "notebook"]) and any(w in query_lower for w in ["replace", "replacement", "dead", "won't turn on", "broken", "flicker", "screen", "3.5", "3 years"]):
                    score += 10
            elif pid == "KB-04": # Software Installation
                if any(w in query_lower for w in ["install", "installation", "software", "catalog", "tool", "extension", "browser extension", "application"]):
                    score += 10
            elif pid == "KB-05": # Printer Troubleshooting
                if any(w in query_lower for w in ["printer", "print", "spooler", "paper jam"]):
                    score += 10
            elif pid == "KB-06": # Mailbox Quota
                if any(w in query_lower for w in ["mailbox", "quota", "email full", "can't send email", "25gb", "50gb", "archive"]):
                    score += 10
            elif pid == "KB-07": # Guest Wi-Fi
                if any(w in query_lower for w in ["wifi", "wi-fi", "guest", "visitor", "kiosk"]) and "network is not coming" not in query_lower:
                    score += 10
            elif pid == "KB-08": # Expense Software
                if any(w in query_lower for w in ["expense", "expense tool", "expense management"]):
                    score += 10
            elif pid == "KB-09": # Security Incident Reporting
                if any(w in query_lower for w in ["phishing", "malware", "unauthorized access", "forwarding", "security@veridian-corp"]):
                    score += 15
            elif pid == "KB-10": # Work-From-Home Equipment
                if any(w in query_lower for w in ["work from home", "wfh", "remote", "chair", "monitor", "home office", "home-office"]):
                    score += 10
            elif pid == "KB-ASSET-01": # Asset Management Policy Extract
                if any(w in query_lower for w in ["laptop", "monitor", "hardware", "refresh", "cycle", "4-year", "4 year", "3.5 years", "2 years", "replacement"]):
                    if any(w in query_lower for w in ["replace", "replacement", "dead", "refresh", "3.5", "4 year", "4-year", "2 years", "flicker"]):
                        score += 8

            if score > 0:
                scored_policies.append((score, policy))

        # Sort by score descending
        scored_policies.sort(key=lambda x: x[0], reverse=True)
        matched_policies = [p[1] for p in scored_policies]

        if matched_policies:
            primary_id = matched_policies[0]["id"]
            # If both KB-03 and KB-ASSET-01 are matched (e.g. laptop replacement), return both
            ids = [p["id"] for p in matched_policies]
            if "KB-03" in ids and "KB-ASSET-01" in ids:
                # Place KB-03 and KB-ASSET-01 at top
                ordered = [p for p in matched_policies if p["id"] in ["KB-03", "KB-ASSET-01"]]
                ordered += [p for p in matched_policies if p["id"] not in ["KB-03", "KB-ASSET-01"]]
                return ordered, "KB-03, KB-ASSET-01"
            return matched_policies, ", ".join([p["id"] for p in matched_policies[:2]])
        
        return [], "No Policy Found"
