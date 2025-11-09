"""
ServiceNow and Jira API Integration Templates
Ready-to-plug production code for fetching and updating tickets.

IMPORTANT: This module contains commented template code for production use.
Replace placeholder values with actual credentials and endpoints.
"""

import os
import requests
from typing import List, Dict, Optional
import json


class ServiceNowAPI:
    """
    ServiceNow REST API integration for fetching and updating incident tickets.
    
    SETUP INSTRUCTIONS:
    1. Set environment variables or update config/sample_config.json:
       - SERVICENOW_INSTANCE_URL (e.g., https://your-instance.service-now.com)
       - SERVICENOW_USERNAME
       - SERVICENOW_PASSWORD
    2. Set enabled=true in config for ServiceNow
    3. Uncomment the production methods below
    """
    
    def __init__(self, instance_url: str, username: str, password: str):
        """
        Initialize ServiceNow API client.
        
        Args:
            instance_url: ServiceNow instance URL
            username: ServiceNow username
            password: ServiceNow password
        """
        self.instance_url = instance_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def fetch_tickets(self, table: str = "incident", limit: int = 100, 
                     query: Optional[str] = None) -> List[Dict]:
        """
        Fetch tickets from ServiceNow.
        
        PRODUCTION CODE - ACTIVE:
        This code is production-ready and will attempt to connect when called.
        
        Args:
            table: ServiceNow table name (default: incident)
            limit: Maximum number of tickets to fetch
            query: Optional sysparm_query filter (e.g., "state=1^priority=1")
            
        Returns:
            List of ticket dictionaries, or empty list if connection fails
        """
        endpoint = f"{self.instance_url}/api/now/table/{table}"
        params = {
            'sysparm_limit': limit,
            'sysparm_display_value': 'true'
        }
        
        if query:
            params['sysparm_query'] = query
        else:
            # Default: fetch new and in-progress incidents
            params['sysparm_query'] = 'state!=6^state!=7'  # Not resolved/closed
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Transform to standard format
            tickets = []
            for record in data.get('result', []):
                ticket = {
                    'sys_id': record.get('sys_id'),
                    'number': record.get('number'),
                    'short_description': record.get('short_description'),
                    'description': record.get('description'),
                    'priority': record.get('priority'),
                    'state': record.get('state'),
                    'created_on': record.get('sys_created_on'),
                    'category': record.get('category'),
                    'source': 'ServiceNow',
                    'caller_id': record.get('caller_id'),
                    'assigned_to': record.get('assigned_to'),
                    'ai_category': '',
                    'ai_priority': '',
                    'ai_skills': '',
                    'ai_summary': ''
                }
                tickets.append(ticket)
            
            print(f"✓ Successfully fetched {len(tickets)} tickets from ServiceNow")
            return tickets
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"ServiceNow API HTTP error: {e.response.status_code}"
            if e.response.status_code == 401:
                error_msg += " - Invalid credentials"
            elif e.response.status_code == 403:
                error_msg += " - Access forbidden. Check API permissions"
            elif e.response.status_code == 404:
                error_msg += " - Endpoint not found. Verify instance URL"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"ServiceNow API connection error: Cannot reach {self.instance_url}"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
        except requests.exceptions.Timeout as e:
            error_msg = "ServiceNow API timeout: Request took longer than 30 seconds"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"ServiceNow API error: {str(e)}"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
    
    def update_ticket(self, sys_id: str, updates: Dict) -> bool:
        """
        Update a ServiceNow ticket.
        
        PRODUCTION CODE - ACTIVE:
        This code is production-ready and will attempt to update when called.
        
        Args:
            sys_id: Ticket system ID
            updates: Dictionary of fields to update (e.g., {'assigned_to': 'user_id', 'state': '2'})
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"{self.instance_url}/api/now/table/incident/{sys_id}"
        
        try:
            response = self.session.patch(endpoint, json=updates, timeout=30)
            response.raise_for_status()
            print(f"✓ Successfully updated ServiceNow ticket {sys_id}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Error updating ServiceNow ticket {sys_id}: {e}")
            return False


class JiraAPI:
    """
    Jira REST API integration for fetching and updating issues.
    
    SETUP INSTRUCTIONS:
    1. Set environment variables or update config/sample_config.json:
       - JIRA_SERVER_URL (e.g., https://your-domain.atlassian.net)
       - JIRA_EMAIL
       - JIRA_API_TOKEN (generate from https://id.atlassian.com/manage/api-tokens)
    2. Set enabled=true in config for Jira
    3. Uncomment the production methods below
    """
    
    def __init__(self, server_url: str, email: str, api_token: str):
        """
        Initialize Jira API client.
        
        Args:
            server_url: Jira server URL
            email: User email for authentication
            api_token: API token for authentication
        """
        self.server_url = server_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.session = requests.Session()
        self.session.auth = (email, api_token)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def fetch_tickets(self, jql: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """
        Fetch issues from Jira using JQL.
        
        PRODUCTION CODE - ACTIVE:
        This code is production-ready and will attempt to connect when called.
        
        Args:
            jql: JQL query string (e.g., "project = PROJ AND status != Done")
            max_results: Maximum number of issues to fetch
            
        Returns:
            List of issue dictionaries
        """
        endpoint = f"{self.server_url}/rest/api/3/search"
        
        if not jql:
            # Default: fetch open issues
            jql = "status != Done AND status != Closed"
        
        params = {
            'jql': jql,
            'maxResults': max_results,
            'fields': 'summary,description,priority,status,created,issuetype,reporter,assignee'
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Transform to standard format
            tickets = []
            for issue in data.get('issues', []):
                fields = issue.get('fields', {})
                ticket = {
                    'id': issue.get('id'),
                    'key': issue.get('key'),
                    'summary': fields.get('summary'),
                    'description': fields.get('description', ''),
                    'priority': fields.get('priority', {}).get('name', 'Medium'),
                    'status': fields.get('status', {}).get('name', 'Open'),
                    'created': fields.get('created'),
                    'issuetype': fields.get('issuetype', {}).get('name', 'Task'),
                    'source': 'Jira',
                    'reporter': fields.get('reporter', {}).get('displayName', ''),
                    'assignee': fields.get('assignee', {}).get('displayName', None),
                    'ai_category': '',
                    'ai_priority': '',
                    'ai_skills': '',
                    'ai_summary': ''
                }
                tickets.append(ticket)
            
            print(f"✓ Successfully fetched {len(tickets)} issues from Jira")
            return tickets
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Jira API HTTP error: {e.response.status_code}"
            if e.response.status_code == 401:
                error_msg += " - Invalid credentials (check email and API token)"
            elif e.response.status_code == 403:
                error_msg += " - Access forbidden. Check API token permissions"
            elif e.response.status_code == 404:
                error_msg += " - Endpoint not found. Verify server URL"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Jira API connection error: Cannot reach {self.server_url}"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
        except requests.exceptions.Timeout as e:
            error_msg = "Jira API timeout: Request took longer than 30 seconds"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Jira API error: {str(e)}"
            print(f"✗ {error_msg}")
            raise Exception(error_msg)
    
    def update_ticket(self, issue_key: str, updates: Dict) -> bool:
        """
        Update a Jira issue.
        
        PRODUCTION CODE - ACTIVE:
        This code is production-ready and will attempt to update when called.
        
        Args:
            issue_key: Issue key (e.g., "PROJ-123")
            updates: Dictionary of fields to update
                    Example: {'assignee': {'accountId': 'user_account_id'}}
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"{self.server_url}/rest/api/3/issue/{issue_key}"
        
        payload = {'fields': updates}
        
        try:
            response = self.session.put(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            print(f"✓ Successfully updated Jira issue {issue_key}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Error updating Jira issue {issue_key}: {e}")
            return False
    
    def add_comment(self, issue_key: str, comment: str) -> bool:
        """
        Add a comment to a Jira issue.
        
        PRODUCTION CODE - ACTIVE:
        This code is production-ready and will attempt to add comment when called.
        
        Args:
            issue_key: Issue key
            comment: Comment text
            
        Returns:
            True if successful, False otherwise
        """
        endpoint = f"{self.server_url}/rest/api/3/issue/{issue_key}/comment"
        
        payload = {
            'body': {
                'type': 'doc',
                'version': 1,
                'content': [{
                    'type': 'paragraph',
                    'content': [{
                        'type': 'text',
                        'text': comment
                    }]
                }]
            }
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            print(f"✓ Successfully added comment to Jira issue {issue_key}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Error adding comment to Jira issue {issue_key}: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("API INTEGRATION TEST")
    print("=" * 80)
    print("\n⚠ This is template code with mock responses.")
    print("To use production APIs:")
    print("1. Configure credentials in config/sample_config.json or environment variables")
    print("2. Uncomment production code in api_integrations.py")
    print("3. Set enabled=true for ServiceNow/Jira in config")
    print("\n" + "=" * 80)
