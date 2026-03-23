import streamlit as st
import pandas as pd

from pipeline import run_pipeline
from core.vector_store import (
    get_vector_store,
    retrieve_tasks_from_store,
    get_all_tasks,
    update_task_status,
    delete_task,
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Task Manager",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Mono', monospace !important; }

    .stApp { background: #0f1117; color: #e2e8f0; }

    /* Sidebar */
    div[data-testid="stSidebar"] {
        background: #13151f !important;
        border-right: 1px solid #2d3148;
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        background: #1e2130 !important;
        border: 1px solid #2d3148 !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    .stSelectbox > div > div {
        background: #1e2130 !important;
        border: 1px solid #2d3148 !important;
        color: #e2e8f0 !important;
    }

    /* Buttons */
    .stButton > button {
        background: #6366f1 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 0.8rem !important;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #4f46e5 !important; }

    /* Metric card */
    .metric-card {
        background: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }

    /* Task card */
    .task-card {
        background: #1e2130;
        border-left: 4px solid;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }

    /* Badge pill */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Alert boxes */
    .success-box {
        background: #052e16;
        border: 1px solid #16a34a;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }
    .error-box {
        background: #450a0a;
        border: 1px solid #dc2626;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }

    /* Dataframe */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* Expander */
    details { background: #1e2130 !important; border-radius: 8px !important; border: 1px solid #2d3148 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

PRIORITY_COLORS = {
    "Critical": "#ef4444",
    "High": "#f97316",
    "Medium": "#eab308",
    "Low": "#22c55e",
}
STATUS_COLORS = {
    "Pending": "#6366f1",
    "In Progress": "#3b82f6",
    "Complete": "#22c55e",
    "Blocked": "#ef4444",
}
CATEGORY_ICONS = {
    "Development": "💻",
    "Design": "🎨",
    "Research": "🔬",
    "Marketing": "📣",
    "Operations": "⚙️",
    "Finance": "💰",
    "HR": "👥",
    "Other": "📌",
}
STATUSES = ["Pending", "In Progress", "Complete", "Blocked"]


def badge(label: str, color: str, text_color: str = "white") -> str:
    return (
        f"<span class='badge' style='background:{color};color:{text_color}'>"
        f"{label}</span>"
    )


def compute_stats(tasks: list[dict]) -> dict:
    if not tasks:
        return {
            "total": 0,
            "completion_rate": 0,
            "by_priority": {},
            "by_status": {},
            "by_category": {},
        }
    total = len(tasks)
    done = sum(1 for t in tasks if t.get("status") == "Complete")
    by_priority = {}
    by_status = {}
    by_category = {}
    for t in tasks:
        by_priority[t.get("priority", "—")] = (
            by_priority.get(t.get("priority", "—"), 0) + 1
        )
        by_status[t.get("status", "—")] = by_status.get(t.get("status", "—"), 0) + 1
        by_category[t.get("category", "—")] = (
            by_category.get(t.get("category", "—"), 0) + 1
        )
    return {
        "total": total,
        "completion_rate": round(done / total * 100),
        "by_priority": by_priority,
        "by_status": by_status,
        "by_category": by_category,
    }


# ── Session state ─────────────────────────────────────────────────────────────

if "store" not in st.session_state:
    with st.spinner("🔌 Connecting to vector store…"):
        try:
            st.session_state.store = get_vector_store()
            st.session_state.store_ready = True
        except Exception as exc:
            st.session_state.store_ready = False
            st.session_state.store_error = str(exc)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🧠 AI Task Manager")
    st.markdown("---")

    menu = st.radio(
        "Navigate",
        ["➕ Add Task", "🔍 Search", "📋 All Tasks", "📊 Dashboard"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    if st.session_state.get("store_ready"):
        st.success("✅ Vector Store connected")
    else:
        st.error(f"❌ {st.session_state.get('store_error', 'Store unavailable')}")

    st.markdown("---")
    st.caption("Built with LangGraph · FAISS · Ollama · Streamlit")

# ── Guard ─────────────────────────────────────────────────────────────────────

if not st.session_state.get("store_ready"):
    st.error(
        "**Cannot connect to services.**\n\n"
        "Ensure Ollama is running and models are pulled:\n"
        "```\nollama pull llama3:8b\nollama pull nomic-embed-text\n```"
    )
    st.stop()

store = st.session_state.store


# ═══════════════════════════════════════════════════════════════
# ADD TASK
# ═══════════════════════════════════════════════════════════════

if menu == "➕ Add Task":
    st.markdown("# ➕ Add New Task")
    st.markdown(
        "Describe your task in plain English. The AI pipeline will **categorise**, "
        "**prioritise**, and **validate** it before storing."
    )

    with st.form("add_task_form", clear_on_submit=True):
        task_input = st.text_area(
            "Task Description",
            placeholder="e.g. Review the pull request for the new authentication module by EOD.",
            height=140,
        )
        submitted = st.form_submit_button("🚀 Process Task", use_container_width=False)

    if submitted and task_input.strip():
        with st.spinner("🤖 Running multi-agent pipeline…"):
            res = run_pipeline(task_input.strip())
            st.session_state.store = get_vector_store()

        if res.get("stored"):
            cat = res.get("categorized_task") or {}
            pri_color = PRIORITY_COLORS.get(cat.get("priority", ""), "#6366f1")
            st.markdown(
                f"""
                <div class="success-box">
                    <h4>✅ Task stored successfully!</h4>
                    <p><strong>ID:</strong> <code>{res.get('task_id','')[:8]}…</code></p>
                    <p><strong>Summary:</strong> {cat.get('summary','')}</p>
                    <p>
                        {badge(cat.get('priority',''), pri_color)}
                        &nbsp;
                        {badge(cat.get('category',''), '#2d3148', '#a5b4fc')}
                    </p>
                    <p><strong>Tags:</strong> {', '.join(cat.get('tags') or []) or '—'}</p>
                    <p><strong>Est. duration:</strong> {cat.get('estimated_duration') or '—'}</p>
                    <p style="font-size:0.8em;color:#64748b">
                        <em>Validation: {res.get('validation_message','')}</em>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="error-box">
                    <h4>❌ Pipeline failed</h4>
                    <p>{res.get('error','Unknown error')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Pipeline diagram
    st.markdown("---")
    st.markdown("### 🗺️ Agent Pipeline")
    steps = [
        ("1️⃣", "Input\nValidation", "#6366f1"),
        ("2️⃣", "LLM\nCategoriser", "#8b5cf6"),
        ("3️⃣", "Quality\nReviewer", "#a855f7"),
        ("4️⃣", "FAISS\nStorage", "#22c55e"),
        ("✅", "Task\nStored", "#16a34a"),
    ]
    for col, (icon, label, color) in zip(st.columns(5), steps):
        col.markdown(
            f"<div style='text-align:center;background:#1e2130;border:1px solid {color};"
            f"border-radius:10px;padding:16px'>"
            f"<div style='font-size:1.5rem'>{icon}</div>"
            f"<div style='font-size:0.8rem;margin-top:6px;color:#a5b4fc;"
            f"white-space:pre-line'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════════════════════════════

elif menu == "🔍 Search":
    st.markdown("# 🔍 Semantic Search")
    st.markdown(
        "Search tasks using natural language. Powered by **nomic-embed-text** embeddings."
    )

    q = st.text_input("Search query", placeholder="e.g. database performance issues")
    k = st.slider("Number of results", 1, 20, 5)

    if q.strip():
        with st.spinner("🔎 Searching vector store…"):
            results = retrieve_tasks_from_store(store, q, k=k)

        if results:
            st.success(f"Found **{len(results)}** semantically similar tasks")
            for r in results:
                # Support both dict and object
                task = r if isinstance(r, dict) else r.__dict__
                tid = task.get("task_id", "")
                summary = task.get("summary", "—")
                priority = task.get("priority", "—")
                status = task.get("status", "Pending")
                category = task.get("category", "Other")
                tags = task.get("tags") or []
                duration = task.get("estimated_duration") or "—"
                ts = task.get("timestamp", "")
                original = task.get("original_input", "")

                pri_color = PRIORITY_COLORS.get(priority, "#6366f1")
                sta_color = STATUS_COLORS.get(status, "#94a3b8")
                icon = CATEGORY_ICONS.get(category, "📌")

                with st.expander(f"{icon} {summary}", expanded=False):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.markdown(f"**ID:** `{tid[:8]}…`")
                    c2.markdown(badge(priority, pri_color), unsafe_allow_html=True)
                    c3.markdown(badge(status, sta_color), unsafe_allow_html=True)
                    c4.markdown(f"**{category}**")

                    st.markdown(f"**Original:** {original}")
                    st.markdown(f"**Tags:** {', '.join(tags) if tags else '—'}")
                    st.markdown(f"**Duration:** {duration}")
                    st.markdown(f"**Created:** {ts}")

                    new_status = st.selectbox(
                        "Update status",
                        STATUSES,
                        index=STATUSES.index(status) if status in STATUSES else 0,
                        key=f"search_status_{tid}",
                    )
                    if new_status != status:
                        if st.button("Save status", key=f"search_save_{tid}"):
                            s = get_vector_store()
                            update_task_status(s, tid, new_status)
                            st.session_state.store = s
                            st.success("Status updated!")
        else:
            st.info("No matching tasks found. Try a broader query.")


# ═══════════════════════════════════════════════════════════════
# ALL TASKS
# ═══════════════════════════════════════════════════════════════

elif menu == "📋 All Tasks":
    st.markdown("# 📋 All Tasks")

    store = get_vector_store()
    raw_tasks = get_all_tasks(store)

    if not raw_tasks:
        st.info("No tasks found. Add some tasks first!")
        st.stop()

    # Normalise to list of dicts
    tasks = [t if isinstance(t, dict) else t.__dict__ for t in raw_tasks]

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_priority = st.multiselect("Priority", list(PRIORITY_COLORS.keys()))
    with col2:
        filter_category = st.multiselect("Category", list(CATEGORY_ICONS.keys()))
    with col3:
        filter_status = st.multiselect("Status", STATUSES)

    filtered = tasks
    if filter_priority:
        filtered = [t for t in filtered if t.get("priority") in filter_priority]
    if filter_category:
        filtered = [t for t in filtered if t.get("category") in filter_category]
    if filter_status:
        filtered = [t for t in filtered if t.get("status") in filter_status]

    st.markdown(f"**Showing {len(filtered)} of {len(tasks)} tasks**")

    if filtered:
        df = pd.DataFrame(
            [
                {
                    "ID": t.get("task_id", "")[:8],
                    "Summary": t.get("summary", ""),
                    "Category": f"{CATEGORY_ICONS.get(t.get('category',''), '')} {t.get('category','')}",
                    "Priority": t.get("priority", ""),
                    "Status": t.get("status", ""),
                    "Duration": t.get("estimated_duration") or "—",
                    "Created": t.get("timestamp", ""),
                }
                for t in filtered
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Quick status update + delete
        st.markdown("---")
        st.markdown("### ✏️ Quick Actions")
        for t in filtered:
            tid = t.get("task_id", "")
            summary = t.get("summary", "")
            status = t.get("status", "Pending")

            c1, c2, c3, c4 = st.columns([4, 2, 1, 1])
            with c1:
                st.markdown(
                    f"<small><code>{tid[:8]}</code></small> {summary}",
                    unsafe_allow_html=True,
                )
            with c2:
                new_status = st.selectbox(
                    "",
                    STATUSES,
                    index=STATUSES.index(status) if status in STATUSES else 0,
                    key=f"all_status_{tid}",
                    label_visibility="collapsed",
                )
            with c3:
                if st.button("✓", key=f"all_save_{tid}", help="Update status"):
                    s = get_vector_store()
                    update_task_status(s, tid, new_status)
                    st.session_state.store = s
                    st.rerun()
            with c4:
                if st.button("🗑", key=f"del_{tid}", help="Delete task"):
                    s = get_vector_store()
                    delete_task(s, tid)
                    st.session_state.store = s
                    st.rerun()


# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════

elif menu == "📊 Dashboard":
    st.markdown("# 📊 Dashboard")

    try:
        import plotly.graph_objects as go
        import plotly.express as px

        HAS_PLOTLY = True
    except ImportError:
        HAS_PLOTLY = False

    store = get_vector_store()
    raw_tasks = get_all_tasks(store)
    tasks = [t if isinstance(t, dict) else t.__dict__ for t in raw_tasks]
    stats = compute_stats(tasks)

    # KPI cards
    kpi_data = [
        ("Total Tasks", stats["total"], "#6366f1"),
        ("Completion Rate", f"{stats['completion_rate']}%", "#22c55e"),
        (
            "Critical / High",
            stats["by_priority"].get("Critical", 0)
            + stats["by_priority"].get("High", 0),
            "#ef4444",
        ),
        ("In Progress", stats["by_status"].get("In Progress", 0), "#3b82f6"),
    ]
    for col, (label, value, color) in zip(st.columns(4), kpi_data):
        col.markdown(
            f"<div class='metric-card'>"
            f"<div style='font-size:2rem;font-weight:700;color:{color}'>{value}</div>"
            f"<div style='font-size:0.85rem;color:#94a3b8;margin-top:4px'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if not tasks:
        st.info("No tasks yet — add some tasks to see analytics here.")
        st.stop()

    if HAS_PLOTLY:
        col_l, col_r = st.columns(2)

        with col_l:
            priority_order = ["Critical", "High", "Medium", "Low"]
            labels = [p for p in priority_order if p in stats["by_priority"]]
            values = [stats["by_priority"][p] for p in labels]
            colors = [PRIORITY_COLORS.get(p, "#6366f1") for p in labels]

            fig_pri = go.Figure(
                go.Bar(
                    x=labels,
                    y=values,
                    marker_color=colors,
                    text=values,
                    textposition="outside",
                )
            )
            fig_pri.update_layout(
                title="Tasks by Priority",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                showlegend=False,
                height=300,
                margin=dict(t=40, b=20, l=20, r=20),
            )
            fig_pri.update_xaxes(showgrid=False)
            fig_pri.update_yaxes(showgrid=True, gridcolor="#2d3148")
            st.plotly_chart(fig_pri, use_container_width=True)

        with col_r:
            s_labels = list(stats["by_status"].keys())
            s_values = list(stats["by_status"].values())
            s_colors = [STATUS_COLORS.get(s, "#94a3b8") for s in s_labels]

            fig_sta = go.Figure(
                go.Pie(
                    labels=s_labels,
                    values=s_values,
                    hole=0.55,
                    marker_colors=s_colors,
                    textinfo="label+percent",
                    textfont_size=12,
                )
            )
            fig_sta.update_layout(
                title="Tasks by Status",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                showlegend=False,
                height=300,
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig_sta, use_container_width=True)

        if stats["by_category"]:
            cat_df = pd.DataFrame(
                [
                    {"Category": f"{CATEGORY_ICONS.get(k,'')} {k}", "Count": v}
                    for k, v in stats["by_category"].items()
                ]
            ).sort_values("Count", ascending=True)

            fig_cat = px.bar(
                cat_df,
                x="Count",
                y="Category",
                orientation="h",
                color="Count",
                color_continuous_scale=["#4f46e5", "#a855f7"],
            )
            fig_cat.update_layout(
                title="Tasks by Category",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                showlegend=False,
                height=280,
                margin=dict(t=40, b=20, l=20, r=20),
                coloraxis_showscale=False,
            )
            fig_cat.update_xaxes(showgrid=True, gridcolor="#2d3148")
            fig_cat.update_yaxes(showgrid=False)
            st.plotly_chart(fig_cat, use_container_width=True)

    else:
        # Fallback to native Streamlit charts if Plotly not installed
        st.markdown("#### Priority Breakdown")
        pri_df = pd.DataFrame(
            list(stats["by_priority"].items()), columns=["Priority", "Count"]
        ).set_index("Priority")
        st.bar_chart(pri_df)

        st.markdown("#### Status Breakdown")
        sta_df = pd.DataFrame(
            list(stats["by_status"].items()), columns=["Status", "Count"]
        ).set_index("Status")
        st.bar_chart(sta_df)

        st.markdown("#### Category Breakdown")
        cat_df = pd.DataFrame(
            list(stats["by_category"].items()), columns=["Category", "Count"]
        ).set_index("Category")
        st.bar_chart(cat_df)

        st.info("💡 Install `plotly` for richer charts: `pip install plotly`")
