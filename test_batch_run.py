from src.agent import ITAgentService
from src.database import DatabaseManager

db = DatabaseManager()
agent = ITAgentService(db_manager=db)

requests = db.get_employee_requests()
print(f"Loaded {len(requests)} employee requests.")

for r in requests:
    res = agent.process(
        user_input=r["request"],
        employee_info={"employee": r["employee"], "email": r["email"]},
        request_id=r["id"]
    )
    print(f"[{r['id']}] {r['employee']} -> Status: {res['status']} | Policy: {res['source']} | Ticket: {res['ticket_id']}")
