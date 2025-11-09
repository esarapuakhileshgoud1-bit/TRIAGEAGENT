"""
AI-Powered Triage Agent - Main Application
Streamlit dashboard for intelligent ticket triage and assignment.

Run with: streamlit run triage_ai.py --server.port 5000
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import logging

# Import custom modules
from mock_data import MockDataGenerator
from ai_triage import AITriageAgent
from engineer_assignment import EngineerAssignmentEngine
from data_storage import DataStorage
from api_integrations import ServiceNowAPI, JiraAPI

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Triage Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Suppress only the specific Plotly deprecation message about passing keyword args
# and avoid blanket suppression which hides other important warnings/errors.
warnings.filterwarnings(
    "ignore",
    message=r".*keyword arguments have been deprecated.*",
    category=DeprecationWarning,
)

# Additionally silence noisy Plotly/Streamlit logger warnings about keyword args
# which are emitted via logging rather than the warnings module in some versions.
logging.getLogger('plotly').setLevel(logging.ERROR)


@st.cache_data
def load_config():
    """Load configuration from JSON file."""
    config_path = "config/sample_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


@st.cache_resource
def initialize_components(config):
    """Initialize triage components."""
    # Initialize AI triage agent
    # OpenAI integration is optional - enabled via config. If enabled but no API key
    # is present the agent will fall back to mock logic.
    use_openai = config.get("openai", {}).get("enabled", True)
    triage_agent = AITriageAgent(use_openai=use_openai)
    
    # Initialize engineer assignment engine
    engineers = config.get("engineers", [])
    assignment_engine = EngineerAssignmentEngine(engineers)
    
    # Initialize data storage
    storage_config = config.get("data_storage", {})
    storage = DataStorage(storage_config)
    
    return triage_agent, assignment_engine, storage


def fetch_tickets_from_apis(config):
    """
    Fetch tickets from ServiceNow and Jira APIs.
    Falls back to mock data only if no APIs are enabled or all enabled APIs failed.
    """
    all_tickets = []
    api_errors = []
    api_success = []
    
    # Check if any APIs are enabled
    sn_enabled = config.get("servicenow", {}).get("enabled", False)
    jira_enabled = config.get("jira", {}).get("enabled", False)
    any_api_enabled = sn_enabled or jira_enabled
    
    # ServiceNow integration
    if sn_enabled:
        try:
            sn_api = ServiceNowAPI(
                instance_url=config.get("servicenow", {}).get("instance_url"),
                username=config.get("servicenow", {}).get("username"),
                password=config.get("servicenow", {}).get("password")
            )
            sn_tickets = sn_api.fetch_tickets()
            all_tickets.extend(sn_tickets)
            api_success.append("ServiceNow")
            st.success(f"✓ Fetched {len(sn_tickets)} tickets from ServiceNow")
        except Exception as e:
            error_msg = f"ServiceNow API failed: {str(e)}"
            api_errors.append(error_msg)
            st.error(f"✗ {error_msg}")
    
    # Jira integration
    if jira_enabled:
        try:
            jira_api = JiraAPI(
                server_url=config.get("jira", {}).get("server_url"),
                email=config.get("jira", {}).get("email"),
                api_token=config.get("jira", {}).get("api_token")
            )
            jira_tickets = jira_api.fetch_tickets(jql=config.get("jira", {}).get("jql_query"))
            all_tickets.extend(jira_tickets)
            api_success.append("Jira")
            st.success(f"✓ Fetched {len(jira_tickets)} issues from Jira")
        except Exception as e:
            error_msg = f"Jira API failed: {str(e)}"
            api_errors.append(error_msg)
            st.error(f"✗ {error_msg}")
    
    # Decide whether to use mock data
    # Only use mock if: (1) no APIs enabled, or (2) all enabled APIs failed
    use_mock = False
    
    if not any_api_enabled:
        # No APIs configured - use mock data
        st.info("📊 No APIs enabled. Using mock ticket data for demonstration.")
        st.info("💡 To use real data: Enable ServiceNow/Jira in config/sample_config.json")
        use_mock = True
    elif api_success:
        # At least one API succeeded (even if it returned 0 tickets)
        if not all_tickets:
            st.info("✓ API connections successful, but no tickets found matching the criteria.")
    else:
        # All enabled APIs failed
        st.warning("⚠ All enabled API connections failed. Using mock data for demonstration.")
        st.info("💡 To fix: Update credentials in config/sample_config.json and ensure API endpoints are accessible.")
        use_mock = True
    
    # Generate mock data if needed
    if use_mock:
        generator = MockDataGenerator()
        all_tickets = generator.generate_all_tickets(servicenow_count=200, jira_count=100)  # Total 300 tickets
    
    return all_tickets


def process_tickets(tickets, triage_agent, assignment_engine, storage):
    """Process tickets through triage and assignment."""
    # Triage tickets with AI
    with st.spinner("🤖 AI is analyzing tickets..."):
        triaged_tickets = triage_agent.batch_triage(tickets)
    
    # Assign tickets to engineers
    with st.spinner("👥 Assigning tickets to engineers..."):
        assigned_tickets = assignment_engine.assign_tickets(triaged_tickets)
    
    # Save to storage
    storage.save_tickets(assigned_tickets)
    
    # Log action
    storage.append_log({
        "action": "triage_and_assign",
        "tickets_processed": len(assigned_tickets),
        "method": assigned_tickets[0].get("triage_method", "Unknown") if assigned_tickets else "None"
    })
    
    return assigned_tickets


def display_metrics(df):
    """Display key metrics in the dashboard."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tickets", len(df))
    
    with col2:
        high_priority = len(df[df['ai_priority'] == 'High'])
        st.metric("High Priority", high_priority)
    
    with col3:
        unassigned = len(df[df['assigned_engineer'] == 'Unassigned'])
        st.metric("Unassigned", unassigned)
    
    with col4:
        categories = df['ai_category'].nunique()
        st.metric("Categories", categories)


def display_category_chart(df):
    """Display ticket distribution by category."""
    category_counts = df['ai_category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    # Use a discrete color sequence for category bars so each category has
    # a stable, accessible color rather than a continuous color mapped to count.
    color_sequence = px.colors.qualitative.Plotly
    fig = px.bar(
        category_counts,
        x='Category',
        y='Count',
        title='Ticket Distribution by Category',
        color='Category',
        color_discrete_sequence=color_sequence
    )
    fig.update_layout(showlegend=False)
    # Use Streamlit's use_container_width and explicit Plotly config to avoid
    # forwarding deprecated keyword args to Plotly (see Streamlit deprecation guidance).
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})


def display_workload_chart(df):
    """Display engineer workload distribution."""
    # Defensive handling: ensure column exists and has string values
    if 'assigned_engineer' not in df.columns:
        st.info("No assignment data available to build workload chart.")
        return

    # Replace null/empty with 'Unassigned' for clarity
    series = df['assigned_engineer'].fillna('Unassigned').astype(str)
    series = series.replace('', 'Unassigned')

    workload = series.value_counts().reset_index()
    workload.columns = ['Engineer', 'Tickets']

    if workload.empty:
        st.info("No assigned tickets to display in workload chart.")
        return

    # Ensure Tickets is numeric
    workload['Tickets'] = workload['Tickets'].astype(int)

    # Sort descending so busiest engineers appear first
    workload = workload.sort_values('Tickets', ascending=False)

    # Use a discrete color sequence for distinct engineer colors
    fig = px.bar(
        workload,
        x='Engineer',
        y='Tickets',
        title='Engineer Workload Distribution',
        color='Engineer',  # Color by engineer instead of ticket count
        color_discrete_sequence=px.colors.qualitative.Set3,  # Use a distinct color palette
        text='Tickets'
    )
    # Place counts inside bars for clarity and make left margin larger so axis labels
    # and any annotations are not clipped. Remove the y-axis title which was
    # cluttering the left side of the chart.
    fig.update_traces(textposition='inside', textfont=dict(color='white'))
    fig.update_layout(showlegend=False, yaxis=dict(dtick=1, title=''), margin=dict(l=120))
    # Use Streamlit's use_container_width and explicit Plotly config to avoid
    # forwarding deprecated keyword args to Plotly (see Streamlit deprecation guidance).
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    # Show raw counts below the chart for quick diagnostics
    st.markdown("**Workload counts**")
    st.dataframe(workload.reset_index(drop=True), width='stretch')
    # Small interactive filter: pick an engineer from the chart to filter the ticket table
    try:
        engineers_list = workload['Engineer'].astype(str).tolist()
        sel = st.selectbox("Filter tickets by engineer (chart)", options=['All'] + engineers_list, index=0)
        if sel and sel != 'All':
            st.session_state['selected_engineer_from_chart'] = sel
        else:
            # Clear existing selection when 'All' chosen
            st.session_state.pop('selected_engineer_from_chart', None)
    except Exception:
        # If anything goes wrong building the selectbox, don't fail the chart render
        pass


def display_priority_breakdown(df):
    """Display priority breakdown pie chart."""
    priority_counts = df['ai_priority'].value_counts()
    
    colors = {'High': '#ff4b4b', 'Medium': '#ffa500', 'Low': '#4CAF50'}
    color_sequence = [colors.get(p, '#666666') for p in priority_counts.index]
    
    fig = px.pie(
        values=priority_counts.values,
        names=priority_counts.index,
        title='Priority Distribution',
        color_discrete_sequence=color_sequence
    )
    # Use Streamlit's use_container_width and explicit Plotly config to avoid
    # forwarding deprecated keyword args to Plotly (see Streamlit deprecation guidance).
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})


def display_ticket_table(df, filters):
    """Display filterable ticket table."""
    # Apply filters
    filtered_df = df.copy()
    
    if filters['priority'] != 'All':
        filtered_df = filtered_df[filtered_df['ai_priority'] == filters['priority']]
    
    if filters['category'] != 'All':
        filtered_df = filtered_df[filtered_df['ai_category'] == filters['category']]
    
    if filters['engineer'] != 'All':
        filtered_df = filtered_df[filtered_df['assigned_engineer'] == filters['engineer']]
    
    # Prepare display columns
    display_columns = [
        'ticket_id', 'title', 'ai_category', 'ai_priority', 
        'assigned_engineer', 'source', 'ai_summary'
    ]
    
    # Create display dataframe
    display_df = pd.DataFrame()
    if 'number' in filtered_df.columns:
        display_df['ticket_id'] = filtered_df.apply(
            lambda x: x['number'] if x['source'] == 'ServiceNow' else x.get('key', ''), axis=1
        )
        display_df['title'] = filtered_df.apply(
            lambda x: x.get('short_description', '') if x['source'] == 'ServiceNow' else x.get('summary', ''), axis=1
        )
    else:
        display_df['ticket_id'] = filtered_df.get('key', '')
        display_df['title'] = filtered_df.get('summary', '')
    
    display_df['ai_category'] = filtered_df['ai_category']
    display_df['ai_priority'] = filtered_df['ai_priority']
    display_df['assigned_engineer'] = filtered_df['assigned_engineer']
    display_df['source'] = filtered_df['source']
    display_df['ai_summary'] = filtered_df['ai_summary']
    
    # Display with styling
    st.dataframe(
        display_df,
        width='stretch',
        height=600,  # Increased height for better viewing of large datasets
        column_config={
            "ticket_id": st.column_config.TextColumn("Ticket ID", width="small"),
            "title": st.column_config.TextColumn("Title", width="large"),
            "ai_category": st.column_config.TextColumn("Category", width="small"),
            "ai_priority": st.column_config.TextColumn("Priority", width="small"),
            "assigned_engineer": st.column_config.TextColumn("Assigned To", width="medium"),
            "source": st.column_config.TextColumn("Source", width="small"),
            "ai_summary": st.column_config.TextColumn("AI Summary", width="large"),
        }
    )
    
    st.caption(f"Showing {len(display_df)} of {len(df)} tickets")


def main():
    """Main application logic."""
    # Header
    st.title("🎯 AI-Powered Triage Agent")
    st.markdown("Intelligent ticket categorization, prioritization, and assignment system")
    
    # Load configuration
    config = load_config()
    # Enterprise mode: if False, integrations (OpenAI, ServiceNow, Jira) are
    # forced off so the app runs in demo/mock mode. Set in config/sample_config.json
    enterprise_mode = config.get("enterprise_mode", False)
    if not enterprise_mode:
        st.info("🔬 Running in demo mode (enterprise_mode=false). Integrations are disabled.")
        # Force-disable integrations when demo mode is active
        config.setdefault("openai", {})["enabled"] = False
        config.setdefault("servicenow", {})["enabled"] = False
        config.setdefault("jira", {})["enabled"] = False
    
    # Initialize components
    triage_agent, assignment_engine, storage = initialize_components(config)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Display API status
        st.subheader("API Status")
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            st.success("✓ OpenAI API Connected")
        else:
            st.warning("⚠ Using Mock AI Logic")
        
        sn_enabled = config.get("servicenow", {}).get("enabled", False)
        st.info(f"{'✓' if sn_enabled else '○'} ServiceNow: {'Enabled' if sn_enabled else 'Disabled'}")
        
        jira_enabled = config.get("jira", {}).get("enabled", False)
        st.info(f"{'✓' if jira_enabled else '○'} Jira: {'Enabled' if jira_enabled else 'Disabled'}")
        
        st.divider()
        
        # Action buttons
        st.subheader("Actions")
        if st.button("🔄 Fetch & Process Tickets", type="primary", width='stretch'):
            st.session_state['refresh'] = True
        
        if st.button("📥 Load Saved Tickets", width='stretch'):
            st.session_state['load_saved'] = True

        # Admin / Debug panel
        with st.expander("🛠️ Admin / Assignment Diagnostics", expanded=False):
            st.caption("Inspect computed match scores and assignment rationale")
            show_diag = st.checkbox("Show assignment diagnostics")
            if show_diag:
                # Ensure tickets are available
                tickets_dbg = st.session_state.get('tickets', [])
                if not tickets_dbg:
                    st.info("No processed tickets available — run 'Fetch & Process Tickets' first.")
                else:
                    # Interactive weight controls
                    st.write("**Assignment weights** (skill vs workload)")
                    skill_pct = st.slider("Skill weight (%)", min_value=0, max_value=100, value=60)
                    # workload is implicit complement
                    workload_pct = 100 - skill_pct
                    st.caption(f"Computed weights — skill: {skill_pct}%, workload: {workload_pct}%")

                    # Build choices list
                    def ticket_label(t):
                        tid = t.get('number') or t.get('key') or t.get('sys_id') or 'N/A'
                        title = t.get('short_description') or t.get('summary') or ''
                        return f"{tid} — {title[:60]}"

                    choices = [ticket_label(t) for t in tickets_dbg]
                    sel = st.selectbox("Select ticket to inspect", options=list(range(len(choices))), format_func=lambda i: choices[i])
                    ticket = tickets_dbg[sel]

                    # Compute per-engineer diagnostics using assignment engine helpers
                    engineers = assignment_engine.engineers
                    rows = []
                    top_engineer = None
                    for eng in engineers:
                        skill_score = assignment_engine.calculate_skill_match_score(eng, ticket.get('ai_skills', ""))
                        workload_score = assignment_engine.calculate_workload_score(eng)
                        availability_score = assignment_engine.get_availability_score(eng)
                        # Combined score mirrors find_best_engineer logic but uses sliders
                        skill_w = skill_pct / 100.0
                        workload_w = workload_pct / 100.0
                        combined = (skill_score * skill_w) + (workload_score * workload_w)
                        if skill_score == 0.0:
                            combined = 0.1 + (workload_score * workload_w)

                        # compute matching skill names for rationale
                        engineer_skills = set(s.lower() for s in eng.get('skills', []))
                        req_skills_raw = ticket.get('ai_skills', "")
                        # normalize required skills
                        req_parts = []
                        if isinstance(req_skills_raw, (list, tuple, set)):
                            req_parts = [s.strip() for s in req_skills_raw]
                        else:
                            s = str(req_skills_raw)
                            if s.startswith('[') and s.endswith(']'):
                                s = s[1:-1]
                            req_parts = [p.strip().strip("'\"") for p in s.split(',') if p.strip()]
                        matching_skills = [r for r in req_parts if r and r.lower() in engineer_skills]

                        rows.append({
                            'engineer': eng['name'],
                            'skill_score': round(skill_score, 3),
                            'matching_skills': ", ".join(matching_skills) or "-",
                            'workload_score': round(workload_score, 3),
                            'availability': 'available' if availability_score == 1.0 else 'unavailable',
                            'combined_score': round(combined, 3)
                        })

                    import pandas as _pd
                    df_diag = _pd.DataFrame(rows).sort_values('combined_score', ascending=False).reset_index(drop=True)
                    st.write("### Assignment diagnostics")
                    st.dataframe(df_diag, width='stretch')

                    # Per-ticket rationale
                    best = df_diag.iloc[0]
                    rationale = f"Top suggestion: {best['engineer']} (score={best['combined_score']}). "
                    rationale += f"Matching skills: {best['matching_skills']}. "
                    rationale += f"Workload score: {best['workload_score']} (lower is busier)."
                    st.markdown("**Rationale:**")
                    st.info(rationale)

                    # Show the assigned engineer from processing
                    st.write("Assigned engineer:", ticket.get('assigned_engineer', 'Unassigned'))

                    # CSV export
                    csv = df_diag.to_csv(index=False)
                    st.download_button("📥 Download diagnostics CSV", data=csv, file_name=f"assignment_diag_{sel}.csv", mime='text/csv')
                    # Allow overflow toggle
                    allow_overflow = st.checkbox("Allow overflow assignments (ignore max_workload)", value=False)

                    # Apply weights and reassign button
                    if st.button("🔁 Apply weights & reassign", width='content'):
                        # compute weights
                        skill_w = skill_pct / 100.0
                        workload_w = 1.0 - skill_w
                        st.info(f"Reassigning with weights: skill={skill_w:.2f}, workload={workload_w:.2f}; allow_overflow={allow_overflow}")
                        # Re-run assignment from scratch with reset_workload=True
                        tickets_current = st.session_state.get('tickets', [])
                        if not tickets_current:
                            st.warning("No tickets available to reassign")
                        else:
                            with st.spinner("Reassigning tickets with new weights..."):
                                reassigned = assignment_engine.assign_tickets(tickets_current, skill_weight=skill_w, workload_weight=workload_w, reset_workload=True, allow_overflow=allow_overflow)
                                # Persist reassigned tickets
                                storage.save_tickets(reassigned)
                                st.session_state['tickets'] = reassigned
                                st.success(f"✓ Reassigned and saved {len(reassigned)} tickets with new weights")
    
    # Process tickets
    if 'tickets' not in st.session_state or st.session_state.get('refresh', False):
        with st.spinner("Fetching tickets..."):
            raw_tickets = fetch_tickets_from_apis(config)
            if raw_tickets:
                processed_tickets = process_tickets(raw_tickets, triage_agent, assignment_engine, storage)
                st.session_state['tickets'] = processed_tickets
                st.success(f"✓ Processed {len(processed_tickets)} tickets successfully!")
            else:
                st.session_state['tickets'] = []
                st.info("No tickets to process at this time.")
            st.session_state['refresh'] = False
    
    # Load saved tickets
    if st.session_state.get('load_saved', False):
        loaded_tickets = storage.get_latest_tickets()
        if loaded_tickets:
            st.session_state['tickets'] = loaded_tickets
            st.success(f"✓ Loaded {len(loaded_tickets)} saved tickets")
        else:
            st.warning("No saved tickets found")
        st.session_state['load_saved'] = False
    
    # Main dashboard
    tickets = st.session_state.get('tickets', [])
    
    if not tickets:
        st.info("👈 Click 'Fetch & Process Tickets' to start, or configure APIs in config/sample_config.json to fetch real tickets.")
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        This AI-powered triage system can work in three modes:
        
        1. **Demo Mode (Default)**: Uses mock ticket data for immediate testing
        2. **ServiceNow Mode**: Connect to your ServiceNow instance
        3. **Jira Mode**: Connect to your Jira workspace
        
        To enable real API integrations, edit `config/sample_config.json` and set `enabled: true` for your desired platform.
        """)
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(tickets)
    
    # Display metrics
    display_metrics(df)
    
    st.divider()
    
    # Charts section
    st.subheader("📊 Analytics")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        display_category_chart(df)
        display_priority_breakdown(df)
    
    with chart_col2:
        display_workload_chart(df)
    
    st.divider()
    
    # Filters section
    st.subheader("🎛️ Filter Tickets")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        priority_filter = st.selectbox(
            "Priority",
            ['All'] + sorted(df['ai_priority'].unique().tolist())
        )
    
    with filter_col2:
        category_filter = st.selectbox(
            "Category",
            ['All'] + sorted(df['ai_category'].unique().tolist())
        )
    
    with filter_col3:
        engineer_filter = st.selectbox(
            "Assigned Engineer",
            ['All'] + sorted(df['assigned_engineer'].unique().tolist())
        )

    # If a chart-based selection exists, override engineer_filter to keep UI in sync
    selected_from_chart = st.session_state.get('selected_engineer_from_chart')
    if selected_from_chart:
        engineer_filter = selected_from_chart
        st.caption(f"Filtering by chart selection: {selected_from_chart}")
    
    filters = {
        'priority': priority_filter,
        'category': category_filter,
        'engineer': engineer_filter
    }
    
    # Ticket table
    st.subheader("🎫 Ticket Details")
    display_ticket_table(df, filters)
    
    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Triage Method: {tickets[0].get('triage_method', 'Unknown')}")


if __name__ == "__main__":
    main()
