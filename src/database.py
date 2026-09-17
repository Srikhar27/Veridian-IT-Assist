import json
import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "veridian_it.db"

class DatabaseManager:
    def __init__(self, data_dir: Path = DATA_DIR, db_path: Path = DB_PATH):
        self.data_dir = Path(data_dir)
        self.db_path = Path(db_path)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_sqlite()

    def _init_sqlite(self):
        """Initialize SQLite schema for persistent runtime state, tickets, and audit logs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                employee TEXT,
                issue TEXT,
                category TEXT,
                status TEXT,
                is_active INTEGER,
                assigned_team TEXT,
                priority TEXT,
                source_policy TEXT,
                escalation_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                request_id TEXT,
                employee TEXT,
                user_input TEXT,
                detected_intent TEXT,
                retrieved_policy TEXT,
                relevant_ticket_history TEXT,
                decision TEXT,
                action_taken TEXT,
                escalation_team TEXT,
                priority TEXT,
                generated_ticket_id TEXT,
                final_status TEXT,
                payload_json TEXT
            )
        """)

        # Ensure payload_json column exists if migrating existing db
        cursor.execute("PRAGMA table_info(audit_logs)")
        cols = [row[1] for row in cursor.fetchall()]
        if "payload_json" not in cols:
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN payload_json TEXT")

        # Employee requests processed state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_requests (
                request_id TEXT PRIMARY KEY,
                decision TEXT,
                status TEXT,
                ticket_id TEXT,
                payload_json TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("PRAGMA table_info(processed_requests)")
        pr_cols = [row[1] for row in cursor.fetchall()]
        if "payload_json" not in pr_cols:
            cursor.execute("ALTER TABLE processed_requests ADD COLUMN payload_json TEXT")

        conn.commit()
        conn.close()

        # Seed initial tickets if database tickets table is empty
        self.seed_initial_tickets()

    def get_policies(self) -> List[Dict[str, Any]]:
        file_path = self.data_dir / "policies.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def get_employee_requests(self) -> List[Dict[str, Any]]:
        file_path = self.data_dir / "employee_requests.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                requests = json.load(f)
            
            # Merge with processed state from database if available
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT request_id, decision, status, ticket_id FROM processed_requests")
            processed_map = {row[0]: {"decision": row[1], "status": row[2], "ticket_id": row[3]} for row in cursor.fetchall()}
            conn.close()

            for req in requests:
                rid = req["id"]
                if rid in processed_map:
                    req["decision"] = processed_map[rid]["decision"]
                    req["current_status"] = processed_map[rid]["status"]
                    req["ticket_id"] = processed_map[rid]["ticket_id"]
                else:
                    req["decision"] = "Pending Processing"
                    req["current_status"] = req.get("initial_action", "Not started")
                    req["ticket_id"] = "N/A"
            return requests
        return []

    def seed_initial_tickets(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tickets")
        count = cursor.fetchone()[0]
        if count == 0:
            file_path = self.data_dir / "tickets.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    tickets = json.load(f)
                for t in tickets:
                    cursor.execute("""
                        INSERT OR REPLACE INTO tickets 
                        (id, employee, issue, category, status, is_active, assigned_team, priority, source_policy, escalation_reason)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        t["id"],
                        t["employee"],
                        t["issue"],
                        t.get("category", "General"),
                        t["status"],
                        1 if t.get("is_active", False) else 0,
                        t.get("assigned_team", "IT Support"),
                        t.get("priority", "Medium"),
                        t.get("source_policy", "N/A"),
                        t.get("escalation_reason", "")
                    ))
                conn.commit()
        conn.close()

    def get_all_tickets(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
        rows = cursor.fetchall()
        tickets = [dict(row) for row in rows]
        conn.close()
        return tickets

    def get_ticket_by_id(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        if not ticket_id or ticket_id == "N/A":
            return None
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None


    def save_ticket(self, ticket: Dict[str, Any]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO tickets
            (id, employee, issue, category, status, is_active, assigned_team, priority, source_policy, escalation_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket["id"],
            ticket["employee"],
            ticket["issue"],
            ticket.get("category", "General"),
            ticket["status"],
            1 if ticket.get("is_active", True) else 0,
            ticket.get("assigned_team", "IT Support"),
            ticket.get("priority", "Medium"),
            ticket.get("source_policy", "N/A"),
            ticket.get("escalation_reason", "")
        ))
        conn.commit()
        conn.close()

    def get_next_auto_ticket_id(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tickets WHERE id LIKE 'AUTO-%'")
        auto_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        nums = []
        for aid in auto_ids:
            try:
                num = int(aid.split("-")[1])
                nums.append(num)
            except (IndexError, ValueError):
                pass
        
        next_num = max(nums) + 1 if nums else 1001
        return f"AUTO-{next_num}"

    def find_existing_ticket_id(self, request_id: Optional[str] = None, user_input: Optional[str] = None, intent: Optional[str] = None) -> Optional[str]:
        """
        Find an existing ticket ID in tickets, audit_logs, or processed_requests table.
        Ensures stable 1-to-1 ticket mapping across all screens.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. By request_id in processed_requests or audit_logs
        if request_id and request_id != "CHAT-SESSION":
            cursor.execute("SELECT ticket_id FROM processed_requests WHERE request_id = ? AND ticket_id != 'N/A'", (request_id,))
            row = cursor.fetchone()
            if row and row["ticket_id"]:
                conn.close()
                return row["ticket_id"]

            cursor.execute("SELECT generated_ticket_id FROM audit_logs WHERE request_id = ? AND generated_ticket_id != 'N/A' ORDER BY id DESC LIMIT 1", (request_id,))
            row = cursor.fetchone()
            if row and row["generated_ticket_id"]:
                conn.close()
                return row["generated_ticket_id"]

            # If a specific employee request ID was passed (e.g., REQ-13) and has no recorded ticket yet, do not reuse another request's ticket
            conn.close()
            return None


        # 2. By user_input query in audit_logs or tickets
        if user_input:
            inp_clean = user_input.strip().lower()
            cursor.execute("SELECT generated_ticket_id FROM audit_logs WHERE LOWER(TRIM(user_input)) = ? AND generated_ticket_id != 'N/A' ORDER BY id DESC LIMIT 1", (inp_clean,))
            row = cursor.fetchone()
            if row and row["generated_ticket_id"]:
                conn.close()
                return row["generated_ticket_id"]

        conn.close()
        return None

    def get_existing_processed_payload(self, request_id: Optional[str] = None, user_input: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Check if request_id or user_input query has already been processed.
        Returns saved response_payload if found, else None.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        row = None
        if request_id and request_id != "CHAT-SESSION":
            cursor.execute("SELECT payload_json FROM audit_logs WHERE request_id = ? ORDER BY id DESC LIMIT 1", (request_id,))
            row = cursor.fetchone()
            if not row or not row["payload_json"]:
                cursor.execute("SELECT payload_json FROM processed_requests WHERE request_id = ?", (request_id,))
                row = cursor.fetchone()
        
        if not row and user_input:
            inp_clean = user_input.strip().lower()
            cursor.execute("SELECT payload_json FROM audit_logs WHERE LOWER(TRIM(user_input)) = ? ORDER BY id DESC LIMIT 1", (inp_clean,))
            row = cursor.fetchone()

        conn.close()

        if row and row["payload_json"]:
            try:
                return json.loads(row["payload_json"])
            except Exception:
                pass
        return None

    def record_audit(self, audit_entry: Dict[str, Any]) -> int:
        """
        Records an audit log entry and returns inserted auto-increment integer ID.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs 
            (request_id, employee, user_input, detected_intent, retrieved_policy, 
             relevant_ticket_history, decision, action_taken, escalation_team, 
             priority, generated_ticket_id, final_status, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_entry.get("request_id", "SESSION"),
            audit_entry.get("employee", "Anonymous"),
            audit_entry.get("user_input", ""),
            audit_entry.get("detected_intent", ""),
            audit_entry.get("retrieved_policy", ""),
            audit_entry.get("relevant_ticket_history", ""),
            audit_entry.get("decision", ""),
            audit_entry.get("action_taken", ""),
            audit_entry.get("escalation_team", "None"),
            audit_entry.get("priority", "Low"),
            audit_entry.get("generated_ticket_id", "N/A"),
            audit_entry.get("final_status", ""),
            audit_entry.get("payload_json", "")
        ))
        inserted_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return inserted_id

    def record_processed_request(self, request_id: str, decision: str, status: str, ticket_id: str, payload_json: str = ""):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO processed_requests (request_id, decision, status, ticket_id, payload_json)
            VALUES (?, ?, ?, ?, ?)
        """, (request_id, decision, status, ticket_id, payload_json))
        conn.commit()
        conn.close()

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC")
        rows = cursor.fetchall()
        audit_trail = []
        for row in rows:
            d = dict(row)
            d["audit_id_formatted"] = f"AUD-{d['id']:05d}"
            audit_trail.append(d)
        conn.close()
        return audit_trail

    def reset_database(self):
        """Reset SQLite runtime state back to clean baseline initial data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tickets")
        cursor.execute("DELETE FROM audit_logs")
        cursor.execute("DELETE FROM processed_requests")
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('audit_logs', 'tickets', 'processed_requests')")
        except Exception:
            pass
        conn.commit()
        conn.close()
        self.seed_initial_tickets()
