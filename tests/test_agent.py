import pytest
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import ITAgentService
from src.database import DatabaseManager

@pytest.fixture
def agent_service(tmp_path):
    """Fixture providing an ITAgentService initialized with an isolated database."""
    db_path = tmp_path / "test_veridian.db"
    db_manager = DatabaseManager(db_path=db_path)
    return ITAgentService(db_manager=db_manager)


# Scenario A (Issue 15): "My laptop is 3.5 years old and completely dead"
def test_scenario_a_laptop_replacement_idempotent(agent_service):
    query = "My laptop is 3.5 years old and completely dead"
    emp = {"employee": "Aditi Sharma", "email": "aditi.sharma@veridian-corp.example"}
    
    # First execution
    res1 = agent_service.process(query, employee_info=emp, request_id="REQ-01")
    t_id1 = res1["ticket_id"]
    
    assert res1["intent"] == "Laptop Replacement Request"
    assert "KB-03" in res1["source"]
    assert "KB-ASSET-01" in res1["source"]
    assert res1["status"] == "Pending IT Diagnostic Verification and Required Approvals"
    assert "older than 3 years" in res1["answer"].lower()
    assert "standard 4-year asset refresh cycle" in res1["answer"].lower()

    # Verify entities in decision_details
    nlu_entities = res1["decision_details"]["nlu_result"]["entities"]
    assert nlu_entities.get("reported_issue") == "Device does not power on"
    assert nlu_entities.get("failure_confirmed") is False

    # Second execution (idempotency check)
    res2 = agent_service.process(query, employee_info=emp, request_id="REQ-01")
    assert res2["ticket_id"] == t_id1  # Stable ticket ID

    # Verify audit logs count in DB = 1
    audit_logs = agent_service.db.get_audit_trail()
    req01_logs = [l for l in audit_logs if l["request_id"] == "REQ-01"]
    assert len(req01_logs) == 1


# Scenario B (Issue 15): "I think I got a phishing email asking for my login"
def test_scenario_b_phishing_security_idempotent(agent_service):
    query = "I think I got a phishing email asking for my login"
    emp = {"employee": "Ananya Reddy", "email": "ananya.reddy@veridian-corp.example"}

    res1 = agent_service.process(query, employee_info=emp, request_id="REQ-08")
    t_id1 = res1["ticket_id"]

    assert res1["priority"] == "Critical"
    assert res1["escalation_team"] == "IT Security"
    assert "security@veridian-corp.example" in res1["answer"]
    assert "not forward" in res1["answer"].lower()

    # Rerun check
    res2 = agent_service.process(query, employee_info=emp, request_id="REQ-08")
    assert res2["ticket_id"] == t_id1

    audit_logs = agent_service.db.get_audit_trail()
    req08_logs = [l for l in audit_logs if l["request_id"] == "REQ-08"]
    assert len(req08_logs) == 1


# Scenario C (Issue 15): "My mailbox is full and I can't send emails"
def test_scenario_c_mailbox_full(agent_service):
    query = "My mailbox is full and I can't send emails"
    emp = {"employee": "Rohit Desai", "email": "rohit.desai@veridian-corp.example"}

    res = agent_service.process(query, employee_info=emp, request_id="REQ-09")
    assert "KB-06" in res["source"]
    assert "25gb" in res["answer"].lower()
    assert "archiv" in res["answer"].lower()
    assert res["escalation_team"] in ["None", "Manager"]
    assert res["status"] in ["Resolved with guidance", "Self-Service Available"]


# Scenario D (Issue 15): Contractor VPN
def test_scenario_d_contractor_vpn(agent_service):
    query = "New contractor joining my team next week, they'll need VPN access"
    emp = {"employee": "Nikhil Bansal", "email": "nikhil.bansal@veridian-corp.example"}

    res = agent_service.process(query, employee_info=emp, request_id="REQ-11")
    assert "KB-02" in res["source"]
    assert res["escalation_team"] == "Manager"
    assert res["status"] == "Waiting for Manager Approval"


# Scenario E (Issue 15): WFH Equipment
def test_scenario_e_wfh_equipment(agent_service):
    query = "I've started working from home 4 days a week, how do I get a monitor?"
    emp = {"employee": "Farhan Ali", "email": "farhan.ali@veridian-corp.example"}

    res = agent_service.process(query, employee_info=emp, request_id="REQ-07")
    assert "KB-10" in res["source"]
    assert res["status"] == "Pending Manager & Finance Approval"
    assert "shipping only after" in res["answer"].lower() or "shipping" in res["answer"].lower()


# Test 11: Network Connectivity Issue (Dedicated Intent)
def test_network_connectivity_issue_dedicated(agent_service):
    query = "The network is not coming in my laptop"
    res = agent_service.process(query)

    assert res["intent"] == "Network Connectivity Issue"
    assert "KB-03" not in res["source"]
    assert "KB-ASSET-01" not in res["source"]
    assert "No Policy Found" in res["source"] or "No Policy Found" in res["relevant_policy"]
    assert res["escalation_team"] == "IT Support"


# Test Read-Only Trace Execution Mode (Issue 13)
def test_decision_trace_read_only(agent_service):
    query = "My laptop is 3.5 years old and completely dead"
    emp = {"employee": "Aditi Sharma", "email": "aditi.sharma@veridian-corp.example"}

    # Process first
    res1 = agent_service.process(query, employee_info=emp, request_id="REQ-01")
    t_id1 = res1["ticket_id"]

    # Trace execution in read-only mode
    trace_res = agent_service.process(query, employee_info=emp, request_id="REQ-01", read_only=True)
    assert trace_res["ticket_id"] == t_id1

    # Audit log count must remain 1
    audit_logs = agent_service.db.get_audit_trail()
    assert len([l for l in audit_logs if l["request_id"] == "REQ-01"]) == 1


# Test Decision Trace Stage 5 Ticket ID Consistency across Chat, Queue, Audit Trail, and Decision Trace
def test_decision_trace_stage_5_ticket_id_consistency(agent_service):
    query = "My laptop is 3.5 years old and completely dead"
    
    # Process query in Chat mode first
    chat_res = agent_service.process(query)
    chat_ticket_id = chat_res["ticket_id"]
    assert chat_ticket_id.startswith("AUTO-")

    # Inspect tickets table
    tickets = agent_service.db.get_all_tickets()
    matching_ticket = next((t for t in tickets if t["id"] == chat_ticket_id), None)
    assert matching_ticket is not None

    # Inspect audit trail
    audit_trail = agent_service.db.get_audit_trail()
    assert audit_trail[0]["generated_ticket_id"] == chat_ticket_id

    # Run Decision Trace in read-only mode
    trace_res = agent_service.process(query, read_only=True)
    assert trace_res["ticket_id"] == chat_ticket_id
    assert trace_res["decision_details"]["created_ticket"] is not None
    assert trace_res["decision_details"]["created_ticket"]["id"] == chat_ticket_id


# Test Database Reset Cleanliness (Issue 14)
def test_database_reset_cleanliness(agent_service):
    agent_service.process("Query 1", request_id="REQ-TEST1")
    agent_service.process("Query 2", request_id="REQ-TEST2")
    
    assert len(agent_service.db.get_audit_trail()) > 0

    agent_service.db.reset_database()
    assert len(agent_service.db.get_audit_trail()) == 0
    assert len([t for t in agent_service.db.get_all_tickets() if t["id"].startswith("AUTO-")]) == 0


# All 12 Mandatory Test Cases Verification
def test_all_12_mandatory_test_cases(agent_service):
    # Case 1: "I forgot my password"
    c1 = agent_service.process("I forgot my password")
    assert c1["intent"] == "Password Reset"
    assert "KB-01" in c1["source"]
    assert c1["status"] == "Self-Service Available"
    assert c1["ticket_id"] == "N/A"

    # Case 2: "My VPN credentials expired"
    c2 = agent_service.process("My VPN credentials expired")
    assert c2["intent"] == "VPN Credential Expiry"
    assert "KB-02" in c2["source"]
    assert c2["ticket_id"] == "N/A"

    # Case 3: "I'm a contractor and need VPN access"
    c3 = agent_service.process("I'm a contractor and need VPN access")
    assert c3["intent"] == "VPN Access"
    assert "KB-02" in c3["source"]
    assert "Manager" in c3["escalation_team"]
    assert c3["ticket_id"] != "N/A"

    # Case 4: "Install software not in catalog"
    c4 = agent_service.process("Install software not in catalog")
    assert c4["intent"] == "Software Installation Request"
    assert "KB-04" in c4["source"]
    assert c4["escalation_team"] == "IT Security"
    assert "3–5" in c4["answer"] or "3-5" in c4["answer"]
    assert c4["ticket_id"] != "N/A"

    # Case 5: "Printer says paper jam but there is no jam"
    c5 = agent_service.process("Printer says paper jam but there is no jam")
    assert c5["intent"] == "Printer Troubleshooting"
    assert "KB-05" in c5["source"]
    assert "spooler" in c5["answer"].lower()
    assert c5["ticket_id"] == "N/A"

    # Case 6: "My mailbox is full"
    c6 = agent_service.process("My mailbox is full")
    assert c6["intent"] == "Email Mailbox Quota"
    assert "KB-06" in c6["source"]
    assert "25gb" in c6["answer"].lower()
    assert c6["ticket_id"] == "N/A"

    # Case 7: "I suspect this email is phishing"
    c7 = agent_service.process("I suspect this email is phishing")
    assert c7["intent"] == "Security Incident Reporting"
    assert "KB-09" in c7["source"]
    assert c7["priority"] == "Critical"
    assert c7["escalation_team"] == "IT Security"
    assert "not forward" in c7["answer"].lower()
    assert c7["ticket_id"] != "N/A"

    # Case 8: "I work from home 4 days and need a monitor"
    c8 = agent_service.process("I work from home 4 days and need a monitor")
    assert c8["intent"] == "Work-From-Home Equipment Request"
    assert "KB-10" in c8["source"]
    assert "Finance" in c8["escalation_team"]
    assert c8["ticket_id"] != "N/A"

    # Case 9: "My laptop screen is flickering"
    c9 = agent_service.process("My laptop screen is flickering")
    assert c9["intent"] == "Laptop Hardware Issue"
    assert "KB-03" in c9["source"]
    assert c9["escalation_team"] == "IT Support"
    assert c9["ticket_id"] != "N/A"

    # Case 10: "My laptop is 3.5 years old and completely dead"
    c10 = agent_service.process("My laptop is 3.5 years old and completely dead")
    assert c10["intent"] == "Laptop Replacement Request"
    assert "KB-03" in c10["source"] and "KB-ASSET-01" in c10["source"]
    assert "older than 3 years" in c10["answer"].lower() or "3 years" in c10["answer"].lower()
    assert "4-year" in c10["answer"].lower() or "4 year" in c10["answer"].lower()
    assert c10["ticket_id"] != "N/A"

    # Case 11: "The network is not coming in my laptop"
    c11 = agent_service.process("The network is not coming in my laptop")
    assert c11["intent"] == "Network Connectivity Issue"
    assert "KB-03" not in c11["source"]
    assert "KB-ASSET-01" not in c11["source"]
    assert "No Policy Found" in c11["source"] or "No Policy Found" in c11["relevant_policy"]
    assert c11["escalation_team"] == "IT Support"
    assert c11["ticket_id"] != "N/A"

    # Case 12: "Can I get admin access to the finance reporting server?"
    c12 = agent_service.process("Can I get admin access to the finance reporting server?")
    assert c12["intent"] == "Admin Access Request"
    assert "Human Review Required" in c12["source"] or "Human Review Required" in c12["relevant_policy"]
    assert c12["status"] == "Human Review Required"
    assert c12["ticket_id"] != "N/A"


