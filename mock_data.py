"""
Mock Data Generator for ServiceNow and Jira Tickets
This module generates realistic sample ticket data for immediate testing
without requiring actual API connections.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict


class MockDataGenerator:
    """Generates mock ServiceNow and Jira ticket data for testing."""
    
    # Sample ticket descriptions for different categories
    TICKET_TEMPLATES = {
        "Network": [
            "VPN connection failing intermittently for remote users",
            "Network latency issues in East Coast data center",
            "Firewall rules blocking access to production database",
            "DNS resolution failure for internal domains",
            "Switch port errors causing packet loss on floor 3"
        ],
        "Database": [
            "PostgreSQL database running out of disk space",
            "MySQL replication lag exceeding threshold",
            "Database connection pool exhausted",
            "Slow query performance on user_transactions table",
            "MongoDB replica set member unreachable"
        ],
        "DevOps": [
            "CI/CD pipeline failing on build step",
            "Kubernetes pod stuck in CrashLoopBackOff",
            "Docker registry running out of storage",
            "Jenkins agent nodes offline",
            "Terraform state file locked preventing deployments"
        ],
        "Security": [
            "Suspicious login attempts detected from unusual location",
            "SSL certificate expiring in 7 days",
            "Security scan found critical vulnerabilities in dependencies",
            "Unauthorized access attempt to admin panel",
            "MFA tokens not being delivered to users"
        ],
        "Frontend": [
            "Website header not displaying correctly on mobile devices",
            "JavaScript error preventing form submission",
            "Page load time exceeding 10 seconds",
            "Shopping cart items disappearing on refresh",
            "CSS styling broken after latest deployment"
        ],
        "Backend": [
            "API endpoint returning 500 internal server error",
            "Payment processing service timing out",
            "Email notifications not being sent to users",
            "Background job queue backed up with 10,000+ jobs",
            "Session management causing users to be logged out"
        ],
        "Access": [
            "New employee needs access to Salesforce and Jira",
            "User locked out of account after password reset",
            "Request for admin privileges on production server",
            "Unable to access shared drive from home office",
            "VPN credentials expired for contractor"
        ],
        "Other": [
            "Printer not working on 2nd floor",
            "Conference room TV display flickering",
            "Software license renewal needed",
            "General inquiry about IT policies",
            "Request for new laptop for new hire"
        ]
    }
    
    PRIORITIES = ["High", "Medium", "Low"]
    STATUSES = ["New", "In Progress", "Pending", "Resolved"]
    
    @staticmethod
    def generate_servicenow_tickets(count: int = 20) -> List[Dict]:
        """
        Generate mock ServiceNow incident tickets.
        
        Args:
            count: Number of tickets to generate
            
        Returns:
            List of ServiceNow-formatted ticket dictionaries
        """
        tickets = []
        for i in range(count):
            category = random.choice(list(MockDataGenerator.TICKET_TEMPLATES.keys()))
            description = random.choice(MockDataGenerator.TICKET_TEMPLATES[category])
            
            created_date = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23)
            )
            
            ticket = {
                "sys_id": f"SN{10000 + i}",
                "number": f"INC{10000 + i}",
                "short_description": description,
                "description": f"Full details: {description}. User reported this issue needs immediate attention.",
                "priority": random.choice(["1", "2", "3"]),  # ServiceNow uses 1-5
                "state": random.choice(["1", "2", "3", "6"]),  # 1=New, 2=In Progress, 3=On Hold, 6=Resolved
                "created_on": created_date.isoformat(),
                "category": "Incident",
                "source": "ServiceNow",
                "caller_id": f"user{random.randint(1, 100)}@company.com",
                "assigned_to": "",
                "ai_category": "",
                "ai_priority": "",
                "ai_skills": "",
                "ai_summary": ""
            }
            tickets.append(ticket)
        
        return tickets
    
    @staticmethod
    def generate_jira_tickets(count: int = 15) -> List[Dict]:
        """
        Generate mock Jira issue tickets.
        
        Args:
            count: Number of tickets to generate
            
        Returns:
            List of Jira-formatted ticket dictionaries
        """
        tickets = []
        for i in range(count):
            category = random.choice(list(MockDataGenerator.TICKET_TEMPLATES.keys()))
            description = random.choice(MockDataGenerator.TICKET_TEMPLATES[category])
            
            created_date = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23)
            )
            
            ticket = {
                "id": f"JIRA{20000 + i}",
                "key": f"PROJ-{1000 + i}",
                "summary": description,
                "description": f"Details: {description}\n\nSteps to reproduce:\n1. User encounters issue\n2. Issue persists\n3. Requires technical investigation",
                "priority": random.choice(["High", "Medium", "Low"]),
                "status": random.choice(["To Do", "In Progress", "In Review", "Done"]),
                "created": created_date.isoformat(),
                "issuetype": random.choice(["Bug", "Task", "Story"]),
                "source": "Jira",
                "reporter": f"user{random.randint(1, 100)}",
                "assignee": None,
                "ai_category": "",
                "ai_priority": "",
                "ai_skills": "",
                "ai_summary": ""
            }
            tickets.append(ticket)
        
        return tickets
    
    @staticmethod
    def generate_all_tickets(servicenow_count: int = 20, jira_count: int = 15) -> List[Dict]:
        """
        Generate combined mock tickets from both ServiceNow and Jira.
        
        Args:
            servicenow_count: Number of ServiceNow tickets
            jira_count: Number of Jira tickets
            
        Returns:
            Combined list of all mock tickets
        """
        all_tickets = []
        all_tickets.extend(MockDataGenerator.generate_servicenow_tickets(servicenow_count))
        all_tickets.extend(MockDataGenerator.generate_jira_tickets(jira_count))
        return all_tickets


# For testing this module independently
if __name__ == "__main__":
    generator = MockDataGenerator()
    
    print("=" * 80)
    print("SAMPLE SERVICENOW TICKETS")
    print("=" * 80)
    sn_tickets = generator.generate_servicenow_tickets(3)
    for ticket in sn_tickets:
        print(f"\nTicket: {ticket['number']}")
        print(f"Description: {ticket['short_description']}")
        print(f"Priority: {ticket['priority']}")
    
    print("\n" + "=" * 80)
    print("SAMPLE JIRA TICKETS")
    print("=" * 80)
    jira_tickets = generator.generate_jira_tickets(3)
    for ticket in jira_tickets:
        print(f"\nTicket: {ticket['key']}")
        print(f"Summary: {ticket['summary']}")
        print(f"Priority: {ticket['priority']}")
