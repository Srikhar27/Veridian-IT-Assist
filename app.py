import streamlit as st
import pandas as pd
import altair as alt
import json
from datetime import datetime
from pathlib import Path

from src.database import DatabaseManager
from src.agent import ITAgentService

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Veridian IT Assist — Enterprise AI Support & Decision Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Premium Enterprise Dark Theme CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0B0F19;
        color: #F3F4F6;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Global Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Top Header Bar */
    .enterprise-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem 1.75rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title-main {
        font-size: 1.75rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-sub {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 0.25rem;
    }

    /* KPI Metric Cards */
    .kpi-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: transform 0.2s, border-color 0.2s;
    }
    .kpi-card:hover {
        border-color: #3B82F6;
        transform: translateY(-2px);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0.4rem 0 0.2rem 0;
    }
    .kpi-delta {
        font-size: 0.85rem;
        font-weight: 600;
    }
    .delta-green { color: #34D399; }
    .delta-blue { color: #60A5FA; }
    .delta-amber { color: #FBBF24; }
    .delta-red { color: #F87171; }

    /* Custom Status Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    .badge-resolved { background-color: rgba(52, 211, 153, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.3); }
    .badge-selfservice { background-color: rgba(96, 165, 250, 0.15); color: #60A5FA; border: 1px solid rgba(96, 165, 250, 0.3); }
    .badge-approval { background-color: rgba(251, 191, 36, 0.15); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.3); }
    .badge-escalated { background-color: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.3); }
    .badge-human { background-color: rgba(167, 139, 250, 0.15); color: #A78BFA; border: 1px solid rgba(167, 139, 250, 0.3); }
    .badge-clarify { background-color: rgba(148, 163, 184, 0.15); color: #CBD5E1; border: 1px solid rgba(148, 163, 184, 0.3); }

    /* Priority Badges */
    .p-critical { background-color: #7F1D1D; color: #FEE2E2; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }
    .p-high { background-color: #7C2D12; color: #FFEDD5; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }
    .p-medium { background-color: #1E3A8A; color: #DBEAFE; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }
    .p-low { background-color: #064E3B; color: #D1FAE5; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }

    /* Decision Trace Step Panel */
    .trace-step-panel {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .trace-step-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #60A5FA;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #334155;
        padding-bottom: 0.5rem;
    }

    /* Policy Card styling */
    .policy-card-box {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .policy-tag {
        background-color: #2563EB;
        color: #FFFFFF;
        font-family: monospace;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
    }

    /* Hide Default Streamlit Menu clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Service Initialization
# -----------------------------------------------------------------------------
@st.cache_resource
def get_services():
    db = DatabaseManager()
    agent = ITAgentService(db_manager=db)
    return db, agent

db, agent_service = get_services()

# Session State for Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------------------------------------------------------
# GLOBAL SIDEBAR LAYOUT
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
        <div style="background: linear-gradient(135deg, #2563EB, #1D4ED8); padding: 10px; border-radius: 10px; font-size: 1.6rem;">🛡️</div>
        <div>
            <div style="font-weight: 800; font-size: 1.2rem; color: #F8FAFC; letter-spacing: -0.02em;">VERIDIAN</div>
            <div style="font-size: 0.8rem; color: #38BDF8; font-weight: 600;">IT ASSIST ENTERPRISE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATION",
        [
            "📊 Overview Dashboard",
            "💬 AI Support Chat",
            "📋 Employee Requests",
            "🎟️ Ticket Queue",
            "📚 Knowledge Base",
            "🔍 Audit Trail",
            "🔬 Agent Decision Trace"
        ],
        index=0
    )

    st.markdown("---")
    
    st.markdown("### System Controls")
    if st.button("🔄 Reset Runtime Data & State", help="Reset ticket queue and audit trail to default baseline data", use_container_width=True):
        db.reset_database()
        st.session_state.chat_history = []
        st.success("Database runtime state cleanly reset!")
        st.rerun()

    st.markdown("---")
    
    st.markdown("""
    <div style="background: #0F172A; border: 1px solid #1E293B; border-radius: 8px; padding: 0.85rem; font-size: 0.8rem;">
        <div style="color: #34D399; font-weight: 700; margin-bottom: 4px;">● All Systems Operational</div>
        <div style="color: #94A3B8;">Grounded Rule Engine: <b style="color:#F1F5F9;">Active</b></div>
        <div style="color: #94A3B8;">Policy Source Truth: <b style="color:#F1F5F9;">KB-01 to KB-10 + KB-ASSET-01</b></div>
        <div style="color: #94A3B8;">User: <b style="color:#F1F5F9;">IT Operations Admin</b></div>
    </div>
    """, unsafe_allow_html=True)


# Helper function to render global page header
def render_header(title: str, subtitle: str):
    st.markdown(f"""
    <div class="enterprise-header">
        <div>
            <div class="header-title-main">🛡️ {title}</div>
            <div class="header-sub">{subtitle}</div>
        </div>
        <div style="text-align: right; display: flex; gap: 15px; align-items: center;">
            <div style="background: #0F172A; border: 1px solid #334155; padding: 6px 12px; border-radius: 8px; font-size: 0.8rem; color: #94A3B8;">
                Engine: <span style="color: #38BDF8; font-weight: 700;">Deterministic Rule v2.4</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Helper function for status badges
def get_status_badge_html(status: str) -> str:
    s_lower = status.lower()
    if any(k in s_lower for k in ["resolved", "direct guidance"]):
        return f'<span class="badge badge-resolved">{status}</span>'
    elif "self-service" in s_lower:
        return f'<span class="badge badge-selfservice">{status}</span>'
    elif any(k in s_lower for k in ["approval", "waiting", "pending"]):
        return f'<span class="badge badge-approval">{status}</span>'
    elif any(k in s_lower for k in ["escalated", "critical", "in progress"]):
        return f'<span class="badge badge-escalated">{status}</span>'
    elif "human review" in s_lower:
        return f'<span class="badge badge-human">{status}</span>'
    else:
        return f'<span class="badge badge-clarify">{status}</span>'


# Helper function for priority badges
def get_priority_badge_html(priority: str) -> str:
    p_lower = priority.lower()
    if p_lower == "critical":
        return f'<span class="p-critical">CRITICAL</span>'
    elif p_lower == "high":
        return f'<span class="p-high">HIGH</span>'
    elif p_lower == "medium":
        return f'<span class="p-medium">MEDIUM</span>'
    else:
        return f'<span class="p-low">LOW</span>'


# =============================================================================
# PAGE 1: OVERVIEW DASHBOARD
# =============================================================================
if page == "📊 Overview Dashboard":
    render_header(
        "Veridian IT Assist — Overview Dashboard",
        "Executive operational dashboard: AI support metrics, policy compliance, and live ITSM queue analytics"
    )

    requests = db.get_employee_requests()
    tickets = db.get_all_tickets()

    total_requests = len(requests)
    processed = [r for r in requests if r.get("decision") != "Pending Processing"]
    resolved = sum(1 for r in processed if any(k in r.get("current_status", "").lower() for k in ["resolved", "self-service", "guidance"]))
    active_tickets = sum(1 for t in tickets if t.get("is_active", True))
    pending_approvals = sum(1 for r in processed if any(k in r.get("current_status", "").lower() for k in ["approval", "waiting", "pending"]))
    critical_incidents = sum(1 for t in tickets if t.get("priority") == "Critical")

    # Top KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Requests</div>
            <div class="kpi-value">{total_requests}</div>
            <div class="kpi-delta delta-blue">15 Assignment Batch</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Auto Resolved</div>
            <div class="kpi-value">{resolved}</div>
            <div class="kpi-delta delta-green">Self-Service & Guidance</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Active Tickets</div>
            <div class="kpi-value">{active_tickets}</div>
            <div class="kpi-delta delta-amber">ITSM Queue</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Pending Approvals</div>
            <div class="kpi-value">{pending_approvals}</div>
            <div class="kpi-delta delta-amber">Manager / Finance</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Critical Incidents</div>
            <div class="kpi-value">{critical_incidents}</div>
            <div class="kpi-delta delta-red">Immediate Security</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Section
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("### 📈 Request Category Breakdown")
        cat_counts = {}
        for r in requests:
            cat = r.get("category", "General IT")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
        cat_df = pd.DataFrame([{"Category": k, "Count": v} for k, v in cat_counts.items()])
        if not cat_df.empty:
            chart1 = alt.Chart(cat_df).mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6, color="#3B82F6").encode(
                x=alt.X("Count:Q", title="Number of Requests"),
                y=alt.Y("Category:N", sort="-x", title="Category"),
                tooltip=["Category", "Count"]
            ).properties(height=280)
            st.altair_chart(chart1, use_container_width=True)

    with ch2:
        st.markdown("### ⚖️ Resolution vs Escalation Distribution")
        status_counts = {}
        for r in processed:
            st_val = r.get("current_status", "Unprocessed")
            status_counts[st_val] = status_counts.get(st_val, 0) + 1
        
        if not status_counts:
            status_counts = {"Pending Batch Run": 15}

        st_df = pd.DataFrame([{"Status": k, "Count": v} for k, v in status_counts.items()])
        chart2 = alt.Chart(st_df).mark_arc(innerRadius=60).encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Status:N", scale=alt.Scale(scheme="set2")),
            tooltip=["Status", "Count"]
        ).properties(height=280)
        st.altair_chart(chart2, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 Recent Employee Requests Log")

    if requests:
        df_display = pd.DataFrame(requests)
        st.dataframe(
            df_display[["id", "employee", "date", "request", "initial_action", "current_status", "ticket_id"]],
            use_container_width=True,
            column_config={
                "id": "Request ID",
                "employee": "Employee",
                "date": "Date",
                "request": "Request Description",
                "initial_action": "Initial Action",
                "current_status": "Agent Status",
                "ticket_id": "Ticket ID"
            }
        )


# =============================================================================
# PAGE 2: AI SUPPORT CHAT
# =============================================================================
elif page == "💬 AI Support Chat":
    render_header(
        "Veridian AI Support Assistant",
        "Interact with the grounded AI support agent for policy inquiries, access requests, hardware issues, and security reporting"
    )

    # Quick Suggestion Buttons
    st.markdown("**⚡ Quick Test Prompts (Click to Run):**")
    p1, p2, p3, p4, p5, p6 = st.columns(6)

    selected_prompt = None
    if p1.button("🔑 Reset Password", help="Test Case 1"):
        selected_prompt = "I forgot my password"
    if p2.button("🌐 Network Issue", help="Test Case 11 - Dedicated Intent"):
        selected_prompt = "The network is not coming in my laptop"
    if p3.button("🚨 Phishing Email", help="Test Case 7"):
        selected_prompt = "I suspect this email is phishing"
    if p4.button("💻 Dead Laptop 3.5y", help="Test Case 10 - Dual Policy KB-03 + KB-ASSET-01"):
        selected_prompt = "My laptop is 3.5 years old and completely dead"
    if p5.button("🔒 Contractor VPN", help="Test Case 3"):
        selected_prompt = "I'm a contractor and need VPN access"
    if p6.button("📦 Software Install", help="Test Case 4"):
        selected_prompt = "Install software not in catalog"

    user_input = st.chat_input("Describe your IT issue or question...") or selected_prompt

    if user_input:
        with st.spinner("Analyzing query against Veridian Knowledge Base policies..."):
            response = agent_service.process(user_input)
            st.session_state.chat_history.append({
                "user": user_input,
                "agent": response
            })

    # Render Chat History
    for idx, item in enumerate(reversed(st.session_state.chat_history)):
        res = item["agent"]
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**{item['user']}**")

        with st.chat_message("assistant", avatar="🛡️"):
            st.markdown(f"### 🛡️ Decision Result")

            badge_html = get_status_badge_html(res['status'])
            p_badge = get_priority_badge_html(res['priority'])

            st.markdown(f"""
            <div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1.25rem; margin-bottom:1rem;">
                <div style="display:flex; justify-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:0.5rem; margin-bottom:0.75rem;">
                    <div><b style="color:#60A5FA;">Intent:</b> {res['intent']}</div>
                    <div>{badge_html} &nbsp; {p_badge}</div>
                </div>
                <div style="font-size:1.05rem; line-height:1.6; margin-bottom:1rem; color:#F8FAFC;">
                    {res['answer']}
                </div>
                <div style="grid-template-columns: 1fr 1fr; display:grid; gap:10px; font-size:0.85rem; background:#0F172A; padding:0.75rem; border-radius:6px; border:1px solid #1E293B;">
                    <div><b>Required Action:</b> {res['action']}</div>
                    <div><b>Escalation Team:</b> <span style="color:#FBBF24;">{res['escalation_team']}</span></div>
                    <div><b>Source Citation:</b> <span class="policy-tag">{res['source']}</span></div>
                    <div><b>Generated Ticket ID:</b> <code style="color:#38BDF8;">{res['ticket_id']}</code></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if res["ticket_id"] != "N/A":
                st.success(f"🎟️ Ticket `{res['ticket_id']}` logged automatically in ITSM ticket queue.")

            with st.expander("🔬 View Agent Decision Trace"):
                st.json(res.get("decision_details", {}))


# =============================================================================
# PAGE 3: EMPLOYEE REQUESTS
# =============================================================================
elif page == "📋 Employee Requests":
    render_header(
        "Employee Support Requests (REQ-01 to REQ-15)",
        "Process and manage official employee support assignment test cases"
    )

    requests = db.get_employee_requests()

    col_b, col_m = st.columns([1, 3])
    with col_b:
        if st.button("🚀 Process All 15 Requests Batch", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            for idx, req in enumerate(requests):
                agent_service.process(
                    user_input=req["request"],
                    employee_info={"employee": req["employee"], "email": req["email"]},
                    request_id=req["id"]
                )
                progress_bar.progress((idx + 1) / len(requests))
            st.success("All 15 employee requests processed successfully!")
            st.rerun()

    # Search & Filters
    f1, f2, f3 = st.columns(3)
    with f1:
        s_query = st.text_input("🔍 Search Request or Employee", "")
    with f2:
        s_filter = st.selectbox("Filter Status", ["All"] + list(set(r.get("current_status", "Not started") for r in requests)))
    with f3:
        e_filter = st.selectbox("Filter Employee", ["All"] + list(set(r["employee"] for r in requests)))

    filtered_reqs = requests
    if s_query:
        filtered_reqs = [r for r in filtered_reqs if s_query.lower() in r["request"].lower() or s_query.lower() in r["employee"].lower()]
    if s_filter != "All":
        filtered_reqs = [r for r in filtered_reqs if r.get("current_status") == s_filter]
    if e_filter != "All":
        filtered_reqs = [r for r in filtered_reqs if r["employee"] == e_filter]

    st.markdown(f"Showing **{len(filtered_reqs)}** requests:")

    df_r = pd.DataFrame(filtered_reqs)
    if not df_r.empty:
        st.dataframe(
            df_r[["id", "employee", "date", "request", "initial_action", "current_status", "ticket_id"]],
            use_container_width=True,
            column_config={
                "id": "ID",
                "employee": "Employee",
                "date": "Date",
                "request": "Request Description",
                "initial_action": "Initial State",
                "current_status": "Decision Status",
                "ticket_id": "Ticket ID"
            }
        )

    st.markdown("---")
    st.subheader("Interactive Single Request Execution")
    sel_r_str = st.selectbox("Select Request ID to process", [r["id"] + " - " + r["employee"] for r in requests])
    
    if sel_r_str:
        sel_id = sel_r_str.split(" - ")[0]
        r_obj = next(r for r in requests if r["id"] == sel_id)

        st.info(f"**Request ID:** `{r_obj['id']}` | **Employee:** {r_obj['employee']} ({r_obj['email']})\n\n**Query:** *\"{r_obj['request']}\"*")

        if st.button(f"⚡ Process Agent Pipeline for {sel_id}"):
            res = agent_service.process(
                user_input=r_obj["request"],
                employee_info={"employee": r_obj["employee"], "email": r_obj["email"]},
                request_id=r_obj["id"]
            )
            st.success(f"Agent execution completed for {sel_id}!")
            st.json({
                "intent": res["intent"],
                "relevant_policy": res["relevant_policy"],
                "answer": res["answer"],
                "action": res["action"],
                "status": res["status"],
                "priority": res["priority"],
                "escalation_team": res["escalation_team"],
                "ticket_id": res["ticket_id"]
            })
            st.rerun()


# =============================================================================
# PAGE 4: TICKET QUEUE
# =============================================================================
elif page == "🎟️ Ticket Queue":
    render_header(
        "Service Ticket Queue & ITSM Operations",
        "Monitor active IT service tickets, auto-generated escalations, and assigned teams"
    )

    tickets = db.get_all_tickets()

    # KPI summary
    open_t = sum(1 for t in tickets if t.get("status") in ["Active", "Open", "Escalated to IT Support"])
    pending_t = sum(1 for t in tickets if "Approval" in t.get("status", "") or "Review" in t.get("status", ""))
    crit_t = sum(1 for t in tickets if t.get("priority") == "Critical")

    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.metric("Open / Active Tickets", open_t)
    with tc2:
        st.metric("Pending Approvals", pending_t)
    with tc3:
        st.metric("Critical Priority", crit_t)

    st.markdown("<br>", unsafe_allow_html=True)

    tf1, tf2 = st.columns(2)
    with tf1:
        t_team = st.selectbox("Filter Team", ["All"] + list(set(t.get("assigned_team", "IT Support") for t in tickets)))
    with tf2:
        t_prio = st.selectbox("Filter Priority", ["All", "Critical", "High", "Medium", "Low"])

    filtered_t = tickets
    if t_team != "All":
        filtered_t = [t for t in filtered_t if t.get("assigned_team") == t_team]
    if t_prio != "All":
        filtered_t = [t for t in filtered_t if t.get("priority") == t_prio]

    df_t = pd.DataFrame(filtered_t)
    if not df_t.empty:
        st.dataframe(
            df_t[["id", "employee", "issue", "category", "status", "assigned_team", "priority", "source_policy"]],
            use_container_width=True,
            column_config={
                "id": "Ticket ID",
                "employee": "Employee",
                "issue": "Issue Summary",
                "category": "Category",
                "status": "Ticket Status",
                "assigned_team": "Assigned Team",
                "priority": "Priority",
                "source_policy": "Policy Citation"
            }
        )

    st.markdown("### Ticket Inspector")
    sel_tk = st.selectbox("Select Ticket ID to Inspect", [t["id"] for t in tickets])
    if sel_tk:
        tk_obj = next(t for t in tickets if t["id"] == sel_tk)
        st.json(tk_obj)


# =============================================================================
# PAGE 5: KNOWLEDGE BASE
# =============================================================================
elif page == "📚 Knowledge Base":
    render_header(
        "Knowledge Base & Policy Repository",
        "Authoritative enterprise IT policies (KB-01 to KB-10 and KB-ASSET-01 Asset Policy Extract)"
    )

    policies = db.get_policies()

    kb_s = st.text_input("🔍 Search Knowledge Base Policies", "")
    kb_c = st.selectbox("Filter Category", ["All"] + list(set(p.get("category", "General") for p in policies)))

    filtered_p = policies
    if kb_s:
        filtered_p = [p for p in filtered_p if kb_s.lower() in p["title"].lower() or kb_s.lower() in p["description"].lower() or kb_s.lower() in p["id"].lower()]
    if kb_c != "All":
        filtered_p = [p for p in filtered_p if p.get("category") == kb_c]

    for p in filtered_p:
        app_req = p.get("approval_required", "None")
        badge_cls = "badge-resolved"
        if "Security" in app_req or "Critical" in app_req:
            badge_cls = "badge-escalated"
        elif "Manager" in app_req or "Finance" in app_req or "Required" in app_req:
            badge_cls = "badge-approval"
        elif "None" in app_req:
            badge_cls = "badge-selfservice"

        st.markdown(f"""
        <div class="policy-card-box">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                <div>
                    <span class="policy-tag">{p['id']}</span> &nbsp;
                    <span style="font-size:1.1rem; font-weight:700; color:#F8FAFC;">{p['title']}</span>
                </div>
                <div>
                    <span class="badge {badge_cls}">{app_req}</span>
                </div>
            </div>
            <div style="color:#94A3B8; font-size:0.9rem; margin-bottom:0.75rem;">Category: <b>{p.get('category', 'General')}</b></div>
            <div style="color:#E2E8F0; font-size:0.95rem; line-height:1.5;">{p['description']}</div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# PAGE 6: AUDIT TRAIL
# =============================================================================
elif page == "🔍 Audit Trail":
    render_header(
        "Agent Audit Trail & Compliance Dashboard",
        "Chronological audit log of all user queries, detected intents, policy citations, decisions, and ticket logs"
    )

    audit_logs = db.get_audit_trail()
    tickets = db.get_all_tickets()

    if audit_logs:
        total_aud = len(audit_logs)
        policy_grounded = sum(1 for l in audit_logs if l.get("retrieved_policy") not in ["Human Review Required", "No Policy Found", "N/A - Clarification Required"])
        sec_escalations = sum(1 for l in audit_logs if l.get("escalation_team") == "IT Security")
        human_reviews = sum(1 for l in audit_logs if l.get("escalation_team") == "Human Review")
        auto_tickets = sum(1 for t in tickets if t.get("id", "").startswith("AUTO-"))

        ac1, ac2, ac3, ac4, ac5 = st.columns(5)
        with ac1:
            st.metric("Total Audit Entries", total_aud)
        with ac2:
            st.metric("Policy Grounded Requests", policy_grounded)
        with ac3:
            st.metric("Security Escalations", sec_escalations)
        with ac4:
            st.metric("Human Reviews", human_reviews)
        with ac5:
            st.metric("Tickets Created", auto_tickets)

        st.markdown("<br>", unsafe_allow_html=True)

        df_a = pd.DataFrame(audit_logs)
        st.dataframe(
            df_a[["audit_id_formatted", "timestamp", "request_id", "employee", "user_input", "detected_intent", "retrieved_policy", "action_taken", "generated_ticket_id", "final_status"]],
            use_container_width=True,
            column_config={
                "audit_id_formatted": "Audit ID",
                "timestamp": "Timestamp",
                "request_id": "Request ID",
                "employee": "Employee",
                "user_input": "User Input",
                "detected_intent": "Detected Intent",
                "retrieved_policy": "Policy Citation",
                "action_taken": "Action Taken",
                "generated_ticket_id": "Ticket ID",
                "final_status": "Final Status"
            }
        )

        st.markdown("### Audit Log Entry Details")
        sel_map = {}
        for l in audit_logs:
            aud_fmt = l.get('audit_id_formatted') or f"AUD-{l['id']:05d}"
            req_fmt = l.get('request_id') or 'REQ'
            emp_fmt = l.get('employee') or 'User'
            int_fmt = l.get('detected_intent') or 'Inquiry'
            label = f"{aud_fmt} | {req_fmt} | {emp_fmt} | {int_fmt}"
            sel_map[label] = l

        sel_label = st.selectbox("Select Audit Entry to Inspect", list(sel_map.keys()))
        if sel_label:
            log_item = sel_map[sel_label]
            
            st.markdown(f"""
            <div style="background:#1E293B; border:1px solid #334155; border-radius:10px; padding:1.25rem;">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:0.9rem;">
                    <div><b>Audit ID:</b> <span class="policy-tag">{log_item.get('audit_id_formatted', f"AUD-{log_item['id']:05d}")}</span></div>
                    <div><b>Request ID:</b> <code>{log_item.get('request_id')}</code></div>
                    <div><b>Employee:</b> {log_item.get('employee')}</div>
                    <div><b>Detected Intent:</b> {log_item.get('detected_intent')}</div>
                    <div><b>Retrieved Policy:</b> <span class="policy-tag">{log_item.get('retrieved_policy')}</span></div>
                    <div><b>Generated Ticket ID:</b> <code>{log_item.get('generated_ticket_id')}</code></div>
                    <div><b>Escalation Team:</b> {log_item.get('escalation_team')}</div>
                    <div><b>Final Status:</b> {log_item.get('final_status')}</div>
                </div>
                <hr style="border-color:#334155;">
                <div><b>User Query:</b> <i>"{log_item.get('user_input')}"</i></div>
                <div style="margin-top:6px;"><b>Action Taken:</b> {log_item.get('action_taken')}</div>
                <div style="margin-top:6px;"><b>Decision Reason:</b> {log_item.get('decision')}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("View Raw Audit Entry JSON"):
                st.json(log_item)
    else:
        st.info("No audit logs recorded yet. Process queries in AI Support Chat or Employee Requests to populate audit trail.")


# =============================================================================
# PAGE 7: AGENT DECISION TRACE (SIGNATURE FEATURE)
# =============================================================================
elif page == "🔬 Agent Decision Trace":
    render_header(
        "Agent Decision Trace — AI Observability",
        "Step-by-step visual inspection of how NLU, Policy Retrieval, Ticket History, and Rule Engine generate grounded decisions"
    )

    default_trace_query = "My laptop is 3.5 years old and completely dead"
    trace_query = st.text_area("Enter any query to trace step-by-step agent execution:", default_trace_query, height=80)

    st.markdown("**Quick Preset Queries:**")
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("1. Laptop Replacement (3.5y)"):
        trace_query = "My laptop is 3.5 years old and completely dead"
    if q2.button("2. Network Connectivity"):
        trace_query = "The network is not coming in my laptop"
    if q3.button("3. Password Lockout"):
        trace_query = "I'm locked out of my account, tried my password 6 times."
    if q4.button("4. Phishing Email"):
        trace_query = "I suspect this email is phishing"

    if st.button("🔬 Execute Trace Pipeline", type="primary", use_container_width=True):
        res = agent_service.process(trace_query, read_only=True)
        details = res.get("decision_details", {})

        nlu = details.get("nlu_result", {})
        policies = details.get("retrieved_policies", [])
        tickets_precedent = details.get("ticket_precedents", [])
        rule_dec = details.get("rule_decision", {})

        st.markdown("---")
        st.markdown("## ⚙️ 5-Stage Decision Pipeline Trace")

        # STAGE 1
        st.markdown(f"""
        <div class="trace-step-panel">
            <div class="trace-step-header">🧠 STAGE 1: NLU & Entity Extraction</div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                <div><b>Detected Intent:</b> <span style="color:#38BDF8; font-weight:700;">{res['intent']}</span></div>
                <div><b>Needs Clarification:</b> {nlu.get('needs_clarification', False)}</div>
                <div><b>Extracted Entities:</b> <code>{json.dumps(nlu.get('entities', {}))}</code></div>
                <div><b>Missing Information:</b> {nlu.get('missing_information', []) or 'None'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # STAGE 2
        p_list_str = ", ".join([f"[{p['id']}] {p['title']}" for p in policies]) if policies else "No Matching Policy Found"
        st.markdown(f"""
        <div class="trace-step-panel">
            <div class="trace-step-header">📚 STAGE 2: Knowledge Base Policy Grounding</div>
            <div><b>Retrieved Policy Citations:</b> <span class="policy-tag">{p_list_str}</span></div>
            <div style="margin-top:8px; font-size:0.9rem; color:#CBD5E1;">
                Grounding Source of Truth: Policies KB-01 through KB-10 and KB-ASSET-01 Extract.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # STAGE 3
        st.markdown(f"""
        <div class="trace-step-panel">
            <div class="trace-step-header">🎟️ STAGE 3: Ticket Precedent Matching</div>
            <div><b>Precedent Ticket Count:</b> {len(tickets_precedent)} tickets evaluated</div>
            <div style="font-size:0.85rem; color:#94A3B8; margin-top:6px;">
                Ticket history used as supporting evidence only; does not override policy rules or current query.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # STAGE 4
        st.markdown(f"""
        <div class="trace-step-panel">
            <div class="trace-step-header">⚖️ STAGE 4: Deterministic Rule Engine Decision</div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; font-size:0.95rem;">
                <div><b>Evaluated Rule:</b> {rule_dec.get('relevant_policy', 'N/A')}</div>
                <div><b>Status Outcome:</b> {get_status_badge_html(res['status'])}</div>
                <div><b>Required Action:</b> {res['action']}</div>
                <div><b>Escalation Target:</b> <b style="color:#FBBF24;">{res['escalation_team']}</b></div>
                <div><b>Priority Level:</b> {get_priority_badge_html(res['priority'])}</div>
                <div><b>Ticket Required:</b> {rule_dec.get('requires_ticket', False)}</div>
            </div>
            <div style="margin-top:10px; background:#0F172A; padding:10px; border-radius:6px; border:1px solid #334155;">
                <b>Decision Reason:</b> {res['reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # STAGE 5
        st.markdown(f"""
        <div class="trace-step-panel">
            <div class="trace-step-header">🚀 STAGE 5: Final Response Synthesis & Ticket Logging</div>
            <div style="font-size:1.05rem; line-height:1.6; color:#F8FAFC; margin-bottom:1rem;">
                {res['answer']}
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; background:#0F172A; padding:10px 14px; border-radius:6px;">
                <div><b>Source Citation:</b> <span class="policy-tag">{res['source']}</span></div>
                <div><b>Ticket ID Logged:</b> <code style="color:#38BDF8; font-size:1rem;">{res['ticket_id']}</code></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View Raw Step Execution JSON"):
            st.json(res)
