AI Triage Agent — Executive Summary

Purpose
-------
Provide senior leadership with a concise overview of what the AI Triage Agent does and why it matters.

What it does
------------
- Automatically ingests support tickets from ServiceNow and Jira (templates provided).
- Uses an AI triage engine (OpenAI GPT-5 by default) with a robust rule-based fallback to:
  - Categorize tickets into area (Network, Database, DevOps, Security, Frontend, Backend, Access, Other)
  - Prioritize tickets (High/Medium/Low)
  - Recommend required skills and a short AI-written summary
- Assigns tickets to engineers using a skill+workload based algorithm with configurable weights.
- Persists triaged tickets locally (Parquet) with optional Delta Lake templates for enterprise scaling.

Business value
--------------
- Faster routing to the right engineering teams reduces mean time to acknowledgement (MTTA).
- Consistent categorization improves SLA reporting and prioritization.
- Provides transparency: AI-generated summaries and assignment rationale are stored with each ticket.

Security & Compliance
---------------------
- No secrets are committed to repo. The app reads credentials from environment variables.
- OpenAI and API credentials must be provisioned via secure secrets management in production.
- Data persistence uses local Parquet by default; Delta Lake templates are included for cloud-grade storage.

Demo plan (2-3 minute CEO demo)
-------------------------------
1. Run the app locally: `python -m streamlit run triage_ai.py` or use `run_local.ps1` on Windows.
2. Click "Fetch & Process Tickets" to generate mock tickets and show end-to-end flow.
3. Show the analytics dashboard: category distribution, workload, and a sample assigned ticket.
4. Explain how to enable ServiceNow/Jira and OpenAI by updating `config/sample_config.json` and providing secrets via environment variables.

Next steps for production
-------------------------
- Provision secrets in a secrets manager (AWS Secrets Manager, Azure Key Vault, etc.).
- Add a CI/CD pipeline to build Docker image, run tests, and deploy to a staging environment.
- Integrate logging + monitoring (structured logs, Prometheus/Grafana or cloud-native equivalents).
- Harden authentication and network access; use private endpoints for API calls.

Contact
-------
For deeper technical or deployment questions, open an issue in the repo or contact the engineering team.
