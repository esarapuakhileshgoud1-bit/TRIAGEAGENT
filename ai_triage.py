"""
AI-Powered Ticket Triage Module
Uses OpenAI GPT-5 for intelligent ticket categorization, prioritization, and analysis.
Includes fallback mock logic when OpenAI API is unavailable.
"""

import os
import json
import re
from typing import Dict, List, Tuple

# Optional OpenAI client - import safely so demo runs without the package installed
try:
    from openai import OpenAI  # type: ignore
    _OPENAI_LIB_AVAILABLE = True
except Exception:
    OpenAI = None  # type: ignore
    _OPENAI_LIB_AVAILABLE = False


class AITriageAgent:
    """
    AI agent for triaging support tickets using OpenAI GPT-5.
    Automatically falls back to rule-based logic if API is unavailable.
    """
    
    # Categories for ticket classification
    CATEGORIES = [
        "Network", "Database", "DevOps", "Security", 
        "Frontend", "Backend", "Access", "Other"
    ]
    
    # Skills required for each category
    CATEGORY_SKILLS = {
        "Network": ["Network", "Security"],
        "Database": ["Database", "Backend"],
        "DevOps": ["DevOps", "Backend"],
        "Security": ["Security", "Network"],
        "Frontend": ["Frontend"],
        "Backend": ["Backend", "Database"],
        "Access": ["Access", "Security"],
        "Other": ["DevOps", "Backend"]
    }
    
    # Keywords for mock categorization
    CATEGORY_KEYWORDS = {
        "Network": ["vpn", "network", "firewall", "dns", "latency", "switch", "router", "connection"],
        "Database": ["database", "sql", "postgresql", "mysql", "mongodb", "query", "replication"],
        "DevOps": ["ci/cd", "pipeline", "kubernetes", "docker", "jenkins", "terraform", "deployment"],
        "Security": ["security", "ssl", "certificate", "vulnerability", "unauthorized", "mfa", "login"],
        "Frontend": ["frontend", "website", "css", "javascript", "mobile", "browser", "ui"],
        "Backend": ["api", "backend", "server", "endpoint", "payment", "email", "session"],
        "Access": ["access", "permission", "credentials", "password", "account", "privileges"],
        "Other": ["printer", "laptop", "license", "inquiry", "policy"]
    }
    
    # Priority keywords
    PRIORITY_KEYWORDS = {
        "High": ["critical", "down", "outage", "urgent", "production", "security", "vulnerability"],
        "Medium": ["slow", "intermittent", "warning", "issue", "problem"],
        "Low": ["request", "inquiry", "question", "enhancement"]
    }
    
    def __init__(self, use_openai: bool = True):
        """
        Initialize the AI Triage Agent.
        
        Args:
            use_openai: Whether to use OpenAI API (requires OPENAI_API_KEY)
        """
        self.use_openai = use_openai
        self.openai_available = False

        if use_openai:
            if not _OPENAI_LIB_AVAILABLE:
                print("⚠ OpenAI client library not installed. Install `openai` to enable enterprise AI. Using mock triage logic.")
            else:
                try:
                    api_key = os.environ.get("OPENAI_API_KEY")
                    if api_key:
                        # Using python_openai blueprint integration
                        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
                        # do not change this unless explicitly requested by the user
                        self.client = OpenAI(api_key=api_key)
                        self.openai_available = True
                        print("✓ OpenAI API initialized successfully")
                    else:
                        print("⚠ OPENAI_API_KEY not found, using mock triage logic")
                except Exception as e:
                    print(f"⚠ OpenAI initialization failed: {e}, using mock triage logic")
    
    def triage_ticket(self, ticket: Dict) -> Dict:
        """
        Triage a single ticket using AI or mock logic.
        
        Args:
            ticket: Ticket dictionary with description/summary
            
        Returns:
            Updated ticket with AI analysis
        """
        # Extract ticket text based on source
        if ticket.get("source") == "ServiceNow":
            ticket_text = ticket.get("short_description", "")
        else:  # Jira
            ticket_text = ticket.get("summary", "")
        
        full_description = ticket.get("description", ticket_text)
        
        if self.openai_available:
            try:
                return self._triage_with_openai(ticket, ticket_text, full_description)
            except Exception as e:
                print(f"⚠ OpenAI API error: {e}, falling back to mock logic")
                return self._triage_with_mock(ticket, ticket_text, full_description)
        else:
            return self._triage_with_mock(ticket, ticket_text, full_description)
    
    def _triage_with_openai(self, ticket: Dict, summary: str, description: str) -> Dict:
        """
        Triage ticket using OpenAI GPT-5.
        
        Args:
            ticket: Original ticket dictionary
            summary: Ticket summary/title
            description: Full ticket description
            
        Returns:
            Updated ticket with AI analysis
        """
        prompt = f"""Analyze this support ticket and provide a structured response in JSON format.

Ticket Summary: {summary}
Full Description: {description}

Please categorize this ticket and provide the following information:
1. category: Choose ONE from [{', '.join(self.CATEGORIES)}]
2. priority: Choose ONE from [High, Medium, Low]
3. required_skills: List 1-3 skills needed (e.g., Network, Database, DevOps, Security, Frontend, Backend, Access)
4. summary: A concise 1-2 sentence summary for engineer assignment

Respond with JSON in this exact format:
{{"category": "category_name", "priority": "priority_level", "required_skills": ["skill1", "skill2"], "summary": "brief summary"}}"""

        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = self.client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert IT support ticket triage agent. Analyze tickets and categorize them accurately."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content or "{}")
        
        # Update ticket with AI analysis
        ticket["ai_category"] = result.get("category", "Other")
        ticket["ai_priority"] = result.get("priority", "Medium")
        ticket["ai_skills"] = ", ".join(result.get("required_skills", ["Other"]))
        ticket["ai_summary"] = result.get("summary", summary)
        ticket["triage_method"] = "OpenAI GPT-5"
        
        return ticket
    
    def _triage_with_mock(self, ticket: Dict, summary: str, description: str) -> Dict:
        """
        Triage ticket using rule-based mock logic.
        
        Args:
            ticket: Original ticket dictionary
            summary: Ticket summary/title
            description: Full ticket description
            
        Returns:
            Updated ticket with mock analysis
        """
        combined_text = f"{summary} {description}".lower()
        
        # Categorize based on keywords
        category = "Other"
        max_matches = 0
        for cat, keywords in self.CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in combined_text)
            if matches > max_matches:
                max_matches = matches
                category = cat
        
        # Prioritize based on keywords
        priority = "Medium"
        for pri, keywords in self.PRIORITY_KEYWORDS.items():
            if any(kw in combined_text for kw in keywords):
                priority = pri
                break
        
        # Assign skills based on category
        required_skills = self.CATEGORY_SKILLS.get(category, ["Other"])
        
        # Generate summary
        summary_text = f"{category} issue: {summary[:80]}..."
        
        # Update ticket
        ticket["ai_category"] = category
        ticket["ai_priority"] = priority
        ticket["ai_skills"] = ", ".join(required_skills)
        ticket["ai_summary"] = summary_text
        ticket["triage_method"] = "Mock Rule-Based"
        
        return ticket
    
    def batch_triage(self, tickets: List[Dict]) -> List[Dict]:
        """
        Triage multiple tickets in batch.
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            List of triaged tickets
        """
        triaged_tickets = []
        for ticket in tickets:
            triaged_ticket = self.triage_ticket(ticket)
            triaged_tickets.append(triaged_ticket)
        
        return triaged_tickets


# For testing this module independently
if __name__ == "__main__":
    from mock_data import MockDataGenerator
    
    print("=" * 80)
    print("AI TRIAGE AGENT TEST")
    print("=" * 80)
    
    # Generate sample tickets
    generator = MockDataGenerator()
    tickets = generator.generate_all_tickets(servicenow_count=3, jira_count=2)
    
    # Initialize triage agent
    agent = AITriageAgent(use_openai=True)
    
    # Triage tickets
    print(f"\nTriaging {len(tickets)} tickets...\n")
    triaged = agent.batch_triage(tickets)
    
    # Display results
    for ticket in triaged:
        source = ticket.get("source")
        if source == "ServiceNow":
            title = ticket.get("short_description", "")
            ticket_id = ticket.get("number", "")
        else:
            title = ticket.get("summary", "")
            ticket_id = ticket.get("key", "")
        
        print(f"Ticket: {ticket_id}")
        print(f"Title: {title}")
        print(f"Category: {ticket['ai_category']}")
        print(f"Priority: {ticket['ai_priority']}")
        print(f"Skills: {ticket['ai_skills']}")
        print(f"Method: {ticket['triage_method']}")
        print("-" * 80)
