# AI Triage Agent - Development Guidelines

## Project Overview
This is an AI-powered ticket management system that automatically categorizes, prioritizes and assigns support tickets from ServiceNow and Jira. The system uses OpenAI GPT-5 for intelligent triage with a fallback to rule-based logic.

## Key Components & Data Flow
1. **Ticket Sources** (`api_integrations.py`)
   - ServiceNow tickets via REST API
   - Jira issues via REST API
   - Mock data generation for development

2. **AI Triage** (`ai_triage.py`)
   - Uses OpenAI GPT-5 when enabled in `config/sample_config.json` and an `OPENAI_API_KEY` is provided
   - Falls back to rule-based mock logic automatically when OpenAI is not available
   - Categories: Network, Database, DevOps, Security, Frontend, Backend, Access, Other

3. **Engineer Assignment** (`engineer_assignment.py`)
   - Skill-based matching (60% weight)
   - Workload balancing (40% weight)
   - Priority-based assignment order (High > Medium > Low)

4. **Data Storage** (`data_storage.py`)
   - Local storage in Parquet format
   - Optional Delta Lake integration

## Development Patterns

### AI Integration
- OpenAI integration is optional and disabled by default in this repo. If enabled, code contains a fallback to rule-based mock logic.
```python
# default behavior in this distribution
return self._triage_with_mock(ticket)
```

### Configuration
- All settings in `config/sample_config.json`
- Use environment variables for sensitive credentials
- Config schema in `sample_config.json` serves as reference

### Error Handling
- Graceful fallbacks for API failures
- Detailed error messages with actionable guidance
- Service health checks before operations

### Testing
- Each module has independent test mode
- Run individual modules directly: `python module_name.py`
- Use mock data generator for development

## Project Structure
```
triage-ai/
├── triage_ai.py              # Main application
├── ai_triage.py             # AI categorization
├── engineer_assignment.py   # Assignment logic
├── api_integrations.py     # External APIs
└── config/
    └── sample_config.json  # Configuration
```

## Common Tasks
1. Adding new ticket category:
   - Add to `CATEGORIES` in `ai_triage.py`
   - Update `CATEGORY_SKILLS` and `CATEGORY_KEYWORDS`
   - Modify OpenAI prompt template

2. Modifying assignment logic:
   - Update score weights in `find_best_engineer()`
   - Modify skill matching in `calculate_skill_match_score()`

3. Adding API integration:
   - Follow templates in `api_integrations.py`
   - Add credentials to config
   - Implement health checks and error handling

## Important Notes
- Default Python environment: Local with `requirements.txt`
- Docker available for containerized deployment
- Production readiness requires API credentials and Delta Lake setup
- Always test with mock data before enabling external APIs