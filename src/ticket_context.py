from typing import List, Dict, Any, Optional

class TicketContextRetriever:
    def __init__(self, tickets: List[Dict[str, Any]]):
        self.tickets = tickets

    def retrieve_relevant_tickets(self, query: str, category: str = "") -> List[Dict[str, Any]]:
        """
        Finds relevant existing/historical tickets based on issue text or category.
        Enforces domain-specific constraints (e.g. screen flickering does NOT match laptop replacement).
        Returns list of structured ticket dictionaries enriched with match_reason.
        """
        query_lower = query.lower()
        matched = []

        is_screen_flicker = any(w in query_lower for w in ["flicker", "flickering", "screen flickering"])
        is_replacement = any(w in query_lower for w in ["replace", "replacement", "dead", "won't turn on", "new laptop"])
        is_network = any(phrase in query_lower for phrase in [
            "network is not coming", "wi-fi is not working", "wifi is not working",
            "cannot connect to the internet", "can't connect to internet",
            "office network is disconnected", "cannot access the company network"
        ])

        for ticket in self.tickets:
            issue_lower = ticket.get("issue", "").lower()
            t_cat = ticket.get("category", "").lower()

            relevance_score = 0
            match_reason = ""

            # Guard 1: Screen flickering must NOT match laptop replacement tickets
            if is_screen_flicker and not is_replacement:
                if "replace" in issue_lower or "replacement" in issue_lower:
                    continue
                if "flicker" in issue_lower or "screen" in issue_lower:
                    relevance_score += 15
                    match_reason = "Historical hardware ticket matching screen display issue"

            # Guard 2: Network connectivity queries should not match asset replacement or unrelated hardware
            elif is_network:
                if "network" in issue_lower or "connectivity" in issue_lower or "adapter" in issue_lower:
                    relevance_score += 10
                    match_reason = "Matching historical network connectivity ticket"
                else:
                    continue

            # Specific intent matching
            elif any(w in query_lower for w in ["phishing", "suspicious email"]) and ("phishing" in issue_lower or "security" in issue_lower):
                relevance_score += 12
                match_reason = "Precedent on reported phishing email incident"

            elif "vpn" in query_lower and "vpn" in issue_lower:
                if "contractor" in query_lower and "contractor" in issue_lower:
                    relevance_score += 15
                    match_reason = "Contractor VPN access workflow precedent"
                elif ("expire" in query_lower or "expired" in query_lower) and ("expire" in issue_lower or "expired" in issue_lower):
                    relevance_score += 15
                    match_reason = "VPN credential expiration resolution precedent"
                else:
                    relevance_score += 8
                    match_reason = "VPN access request precedent"

            elif ("password" in query_lower or "locked out" in query_lower) and ("password" in issue_lower or "locked" in issue_lower):
                relevance_score += 12
                match_reason = "Password self-service / unlock precedent"

            elif any(w in query_lower for w in ["software", "catalog", "install", "extension"]) and ("software" in issue_lower or "catalog" in issue_lower):
                relevance_score += 12
                match_reason = "Non-catalog software review workflow precedent"

            elif ("mailbox" in query_lower or "quota" in query_lower) and ("mailbox" in issue_lower or "quota" in issue_lower):
                relevance_score += 12
                match_reason = "Mailbox quota approval and expansion precedent"

            elif ("printer" in query_lower or "jam" in query_lower or "print" in query_lower) and ("printer" in issue_lower or "jam" in issue_lower):
                relevance_score += 12
                match_reason = "Printer queue and paper jam troubleshooting precedent"

            elif any(w in query_lower for w in ["wfh", "work from home", "remote", "monitor"]) and ("home office" in issue_lower or "equipment" in issue_lower or "wfh" in issue_lower):
                relevance_score += 12
                match_reason = "Work-from-home allowance approval precedent"

            elif ("guest" in query_lower or "kiosk" in query_lower) and ("guest" in issue_lower or "wi-fi" in issue_lower or "wifi" in issue_lower):
                relevance_score += 12
                match_reason = "Guest Wi-Fi kiosk issuance precedent"

            elif is_replacement and ("replace" in issue_lower or "replacement" in issue_lower or "3.2" in issue_lower):
                relevance_score += 14
                match_reason = "Laptop lifecycle replacement eligibility precedent"

            elif category and t_cat == category.lower():
                relevance_score += 3
                match_reason = f"Category match on {ticket.get('category')}"

            if relevance_score > 0:
                t_copy = dict(ticket)
                t_copy["match_reason"] = match_reason
                t_copy["relevance_score"] = relevance_score
                t_copy["active_status"] = "Active" if ticket.get("is_active", False) else "Closed (Historical)"
                matched.append((relevance_score, t_copy))

        matched.sort(key=lambda x: x[0], reverse=True)
        return [m[1] for m in matched[:3]]

    def format_ticket_precedent_summary(self, matched_tickets: List[Dict[str, Any]]) -> str:
        if not matched_tickets:
            return "No prior ticket precedent found."
        
        summaries = []
        for t in matched_tickets:
            status_label = "Active" if t.get("is_active", False) else "Historical"
            reason = t.get("match_reason", "Keyword match")
            summaries.append(f"[{t['id']}] ({status_label}) {t['employee']} - '{t['issue']}' [{reason}] -> Status: {t['status']}")
        
        return " | ".join(summaries)
