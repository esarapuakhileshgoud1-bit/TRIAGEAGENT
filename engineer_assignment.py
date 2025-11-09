"""
Engineer Assignment Module
Assigns tickets to engineers based on skills, availability, and workload balancing.
"""

from typing import List, Dict, Optional
import json
from data_storage import DataStorage


class EngineerAssignmentEngine:
    """
    Intelligent engine for assigning tickets to engineers based on:
    - Skill matching
    - Current workload
    - Availability status
    """
    
    def __init__(self, engineers: List[Dict]):
        """
        Initialize the assignment engine.
        
        Args:
            engineers: List of engineer dictionaries with skills, availability, and max_workload
        """
        self.engineers = engineers
        self.workload = {eng["name"]: 0 for eng in engineers}
        self.storage = DataStorage({"local_mode": True})
    
    def calculate_skill_match_score(self, engineer: Dict, required_skills: str) -> float:
        """
        Calculate how well an engineer's skills match the required skills.
        
        Args:
            engineer: Engineer dictionary
            required_skills: Comma-separated string of required skills
            
        Returns:
            Match score between 0.0 and 1.0
        """
        # Defensive parsing: required_skills may be a list, a comma-separated
        # string, or a stringified list (e.g. "['Network', 'Security']").
        if not required_skills:
            return 0.5

        engineer_skills = set(skill.strip().lower() for skill in engineer.get("skills", []))

        # Normalize required_skills to a set of clean lowercase tokens
        required_skills_set = set()
        if isinstance(required_skills, (list, tuple, set)):
            required_skills_set = set(s.strip().lower() for s in required_skills if s)
        else:
            # Remove surrounding brackets/quotes and split by comma
            s = str(required_skills).strip()
            if s.startswith("[") and s.endswith("]"):
                s = s[1:-1]
            parts = [p.strip().strip("'\"") for p in s.split(",") if p.strip()]
            required_skills_set = set(p.lower() for p in parts if p)

        if not required_skills_set:
            return 0.5

        # Calculate intersection
        matching_skills = engineer_skills.intersection(required_skills_set)
        match_score = len(matching_skills) / len(required_skills_set)

        return match_score
    
    def calculate_workload_score(self, engineer: Dict) -> float:
        """
        Calculate workload score (lower workload = higher score).
        
        Args:
            engineer: Engineer dictionary
            
        Returns:
            Workload score between 0.0 and 1.0
        """
        engineer_name = engineer["name"]
        current_workload = self.workload.get(engineer_name, 0)
        max_workload = engineer.get("max_workload", 5)
        
        if current_workload >= max_workload:
            return 0.0
        
        # Inverse relationship: less workload = higher score
        workload_score = 1.0 - (current_workload / max_workload)
        return workload_score
    
    def get_availability_score(self, engineer: Dict) -> float:
        """
        Get availability score.
        
        Args:
            engineer: Engineer dictionary
            
        Returns:
            1.0 if available, 0.0 if not
        """
        availability = engineer.get("availability", "available").lower()
        return 1.0 if availability == "available" else 0.0
    
    def find_best_engineer(self, ticket: Dict, skill_weight: float = 0.6, workload_weight: float = 0.4, allow_overflow: bool = False) -> Optional[str]:
        """
        Find the best engineer for a ticket based on skills, workload, and availability.
        
        Args:
            ticket: Ticket dictionary with ai_skills field
            
        Returns:
            Name of the best engineer, or None if no suitable engineer found
        """
        required_skills = ticket.get("ai_skills", "")
        
        best_engineer = None
        best_score = -1.0
        
        for engineer in self.engineers:
            # Calculate component scores
            skill_score = self.calculate_skill_match_score(engineer, required_skills)
            workload_score = self.calculate_workload_score(engineer)
            availability_score = self.get_availability_score(engineer)
            
            # Skip if not available
            if availability_score == 0.0:
                continue
            
            # Skip if at max workload (unless allow_overflow is True)
            if workload_score == 0.0 and not allow_overflow:
                continue
            
            # Combined score with configurable weights
            combined_score = (skill_score * skill_weight) + (workload_score * workload_weight)

            # If no skills match at all, prefer any available engineer by workload
            if skill_score == 0.0:
                # small penalty but allow assignment based on workload
                combined_score = 0.1 + (workload_score * workload_weight)

            if combined_score > best_score:
                best_score = combined_score
                best_engineer = engineer["name"]
        
        # If we didn't find a best engineer through normal scoring (e.g., all were
        # unavailable or filtered out for being at max workload), fall back to a
        # deterministic least-loaded available engineer so tickets are not left
        # unassigned. This fallback will ignore max_workload limits (but respects
        # availability where possible) to ensure no ticket remains unassigned.
        if best_engineer is None:
            # Prefer available engineers first
            available_candidates = [eng for eng in self.engineers if self.get_availability_score(eng) == 1.0]
            candidates = available_candidates if available_candidates else list(self.engineers)

            # Choose the candidate with the smallest current workload
            min_load = None
            chosen = None
            for eng in candidates:
                name = eng["name"]
                load = self.workload.get(name, 0)
                if min_load is None or load < min_load:
                    min_load = load
                    chosen = name
            
            # Log the fallback assignment
            ticket_id = "Unknown" if not hasattr(self, 'current_ticket_id') else self.current_ticket_id
            reason = "No suitable engineer found (fallback to least loaded)"
            self.storage.log_assignment(ticket_id, chosen, True, reason)
            
            return chosen
            
        return best_engineer
    
    def assign_ticket(self, ticket: Dict, skill_weight: float = 0.6, workload_weight: float = 0.4, allow_overflow: bool = False) -> Dict:
        """
        Assign a ticket to the best available engineer.
        
        Args:
            ticket: Ticket dictionary
            
        Returns:
            Updated ticket with assigned_engineer field
        """
        # Store ticket ID for logging
        self.current_ticket_id = ticket.get("number") or ticket.get("key") or "Unknown"
        
        assigned_engineer = self.find_best_engineer(ticket, skill_weight=skill_weight, workload_weight=workload_weight, allow_overflow=allow_overflow)

        if assigned_engineer:
            ticket["assigned_engineer"] = assigned_engineer
            # Increment workload
            self.workload[assigned_engineer] += 1
        else:
            ticket["assigned_engineer"] = "Unassigned"

        return ticket
    
    def assign_tickets(self, tickets: List[Dict], skill_weight: float = 0.6, workload_weight: float = 0.4, reset_workload: bool = False, allow_overflow: bool = False) -> List[Dict]:
        """
        Assign multiple tickets to engineers.
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            List of tickets with assignments
        """
        # Sort tickets by priority (High > Medium > Low)
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        sorted_tickets = sorted(
            tickets,
            key=lambda t: priority_order.get(t.get("ai_priority", "Medium"), 1)
        )
        
        # Optionally reset workloads to recompute assignment from scratch
        if reset_workload:
            self.reset_workload()

        assigned_tickets = []
        for ticket in sorted_tickets:
            assigned_ticket = self.assign_ticket(ticket, skill_weight=skill_weight, workload_weight=workload_weight, allow_overflow=allow_overflow)
            assigned_tickets.append(assigned_ticket)
        
        return assigned_tickets
    
    def get_workload_summary(self) -> Dict[str, int]:
        """
        Get current workload for all engineers.
        
        Returns:
            Dictionary of engineer names to ticket counts
        """
        return self.workload.copy()
    
    def reset_workload(self):
        """Reset all workload counters to zero."""
        self.workload = {eng["name"]: 0 for eng in self.engineers}


# For testing this module independently
if __name__ == "__main__":
    from mock_data import MockDataGenerator
    from ai_triage import AITriageAgent
    
    print("=" * 80)
    print("ENGINEER ASSIGNMENT ENGINE TEST")
    print("=" * 80)
    
    # Load sample engineer configuration
    sample_engineers = [
        {
            "name": "Alice Chen",
            "skills": ["Network", "Security", "DevOps"],
            "availability": "available",
            "max_workload": 5
        },
        {
            "name": "Bob Smith",
            "skills": ["Database", "Backend", "DevOps"],
            "availability": "available",
            "max_workload": 5
        },
        {
            "name": "Carol Martinez",
            "skills": ["Frontend", "Backend", "Access"],
            "availability": "available",
            "max_workload": 5
        }
    ]
    
    # Generate and triage tickets
    generator = MockDataGenerator()
    tickets = generator.generate_all_tickets(servicenow_count=5, jira_count=3)
    
    triage_agent = AITriageAgent(use_openai=False)
    triaged_tickets = triage_agent.batch_triage(tickets)
    
    # Assign tickets
    assignment_engine = EngineerAssignmentEngine(sample_engineers)
    assigned_tickets = assignment_engine.assign_tickets(triaged_tickets)
    
    # Display results
    print("\nAssignment Results:")
    print("-" * 80)
    for ticket in assigned_tickets:
        source = ticket.get("source")
        if source == "ServiceNow":
            ticket_id = ticket.get("number", "")
            title = ticket.get("short_description", "")[:50]
        else:
            ticket_id = ticket.get("key", "")
            title = ticket.get("summary", "")[:50]
        
        print(f"{ticket_id}: {title}...")
        print(f"  Category: {ticket['ai_category']} | Priority: {ticket['ai_priority']}")
        print(f"  Skills: {ticket['ai_skills']}")
        print(f"  Assigned to: {ticket['assigned_engineer']}")
        print()
    
    print("=" * 80)
    print("WORKLOAD SUMMARY")
    print("=" * 80)
    workload = assignment_engine.get_workload_summary()
    for engineer, count in workload.items():
        print(f"{engineer}: {count} tickets")
