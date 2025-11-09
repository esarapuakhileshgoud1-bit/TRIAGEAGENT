import streamlit as st
from mock_data import MockDataGenerator
from ai_triage import AITriageAgent
from engineer_assignment import EngineerAssignmentEngine
import json

def load_config():
    """Load configuration from sample_config.json"""
    try:
        with open('config/sample_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Failed to load configuration: {e}")
        return None

def main():
    st.title("🎯 AI Triage Dashboard")
    
    # Load configuration
    config = load_config()
    if not config:
        st.error("Please ensure config/sample_config.json exists")
        return
    
    # Sidebar controls
    st.sidebar.title("Controls")
    if st.sidebar.button("Fetch & Process Tickets"):
        with st.spinner("Generating and processing tickets..."):
            # Generate mock tickets
            generator = MockDataGenerator()
            tickets = generator.generate_all_tickets(servicenow_count=5, jira_count=3)
            
            # Triage tickets
            triage_agent = AITriageAgent(use_openai=False)  # Set to True to use OpenAI
            triaged_tickets = triage_agent.batch_triage(tickets)
            
            # Assign tickets
            assignment_engine = EngineerAssignmentEngine(config["engineers"])
            assigned_tickets = assignment_engine.assign_tickets(triaged_tickets)
            
            # Display results
            st.success(f"Processed {len(assigned_tickets)} tickets")
            
            # Show tickets table
            st.subheader("📋 Tickets")
            ticket_data = []
            for ticket in assigned_tickets:
                ticket_data.append({
                    "ID": ticket.get("number", ticket.get("key", "N/A")),
                    "Source": ticket["source"],
                    "Category": ticket["ai_category"],
                    "Priority": ticket["ai_priority"],
                    "Assigned To": ticket["assigned_engineer"],
                    "Description": ticket.get("short_description", ticket.get("summary", "N/A"))
                })
            
            st.table(ticket_data)
            
            # Show workload summary
            st.subheader("👥 Engineer Workload")
            workload = assignment_engine.get_workload_summary()
            st.bar_chart(workload)

if __name__ == "__main__":
    main()
