# 🎯 AI-Powered Triage Agent

An intelligent ticket management system that uses AI to automatically categorize, prioritize, and assign support tickets from ServiceNow and Jira to the right engineers.

## Executive summary (for executives / CEO)

This project is a demo-ready AI Triage solution that shows the end-to-end flow from ticket ingestion (ServiceNow/Jira) to AI-driven categorization and automated engineer assignment. It is configured to run locally using mock data for safe demos and includes templates for production integrations (OpenAI, Delta Lake, ServiceNow, Jira).

Key metrics to highlight during a demo:
- Tickets processed per minute (demo uses mock data)
- Percentage of high-priority tickets routed correctly
- Engineer workload balance after automated assignment

Use the `docs/EXECUTIVE_SUMMARY.md` for a 2–3 minute CEO-facing demo script.

## ✨ Features

- **🤖 AI-Powered Triage**: Uses OpenAI GPT-5 to intelligently categorize and prioritize tickets
- **👥 Smart Assignment**: Assigns tickets to engineers based on skills, workload, and availability
- **📊 Real-Time Dashboard**: Interactive Streamlit dashboard with analytics and filtering
- **🔌 Ready-to-Plug APIs**: Production-ready ServiceNow and Jira integration templates
- **💾 Flexible Storage**: Local CSV/Parquet with Delta Lake integration templates
- **🎭 Mock Data Mode**: Works immediately with sample data, no API keys required

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download this project
cd triage-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application (Local)

PowerShell (Windows):

```powershell
# From repository root
.\run_local.ps1
```

Cross-platform (macOS / Linux / Windows WSL):

```bash
# From repository root
python -m streamlit run triage_ai.py
```

The dashboard will open at `http://localhost:8501` (or visit `http://127.0.0.1:8501`).

### 3. First Use

1. Click **"Fetch & Process Tickets"** in the sidebar
2. The app will generate mock tickets and process them with AI
3. Explore the dashboard to see categorization, assignments, and analytics

## 📋 Project Structure

```
triage-ai/
├── triage_ai.py              # Main Streamlit application
├── mock_data.py               # Mock ServiceNow/Jira ticket generator
├── ai_triage.py               # AI-powered categorization engine
├── engineer_assignment.py     # Skills-based assignment algorithm
├── data_storage.py            # CSV/Parquet/Delta Lake storage
├── api_integrations.py        # ServiceNow & Jira API templates
├── config/
│   └── sample_config.json     # Configuration file
├── data/                      # Ticket storage (auto-created)
├── logs/                      # Action logs (auto-created)
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore patterns
└── README.md                  # This file
```

## ⚙️ Configuration

### Basic Setup

Edit `config/sample_config.json` to configure:

- **Engineers**: Add/modify team members with their skills
- **OpenAI**: Enable/disable AI categorization
- **APIs**: Enable ServiceNow and Jira integrations
- **Storage**: Choose between CSV, Parquet, or Delta Lake

Tip: Set `"enterprise_mode": true` in `config/sample_config.json` to enable enterprise integrations (OpenAI, ServiceNow, Jira). When `enterprise_mode` is false the app will run in demo/mock mode regardless of per-integration flags.

### Adding OpenAI API Key

For AI-powered triage (optional):

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set as environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
3. Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

**Note**: The app works without OpenAI using intelligent mock logic!

## 🔌 Production API Integration

The API integration code is **production-ready and active**. Simply configure credentials and enable the APIs.

### ServiceNow Integration

1. **Update Configuration** (`config/sample_config.json`):
   ```json
   {
     "servicenow": {
       "enabled": true,
       "instance_url": "https://your-instance.service-now.com",
       "username": "YOUR_USERNAME",
       "password": "YOUR_PASSWORD",
       "table": "incident"
     }
   }
   ```

2. **Set Environment Variables** (recommended for security):
   ```bash
   export SERVICENOW_USERNAME="your-username"
   export SERVICENOW_PASSWORD="your-password"
   ```

3. **Test Connection**:
   - Click "Fetch & Process Tickets" in the dashboard
   - The app will attempt to connect to ServiceNow
   - If successful, real tickets will be displayed
   - If connection fails, detailed error messages will guide you
   - Falls back to mock data automatically if API is unavailable

### Jira Integration

1. **Generate API Token**:
   - Go to [Atlassian API Tokens](https://id.atlassian.com/manage/api-tokens)
   - Create a new API token

2. **Update Configuration**:
   ```json
   {
     "jira": {
       "enabled": true,
       "server_url": "https://your-domain.atlassian.net",
       "email": "your-email@company.com",
       "api_token": "YOUR_API_TOKEN",
       "jql_query": "project = PROJ AND status != Done"
     }
   }
   ```

3. **Test Connection**:
   - Click "Fetch & Process Tickets" in the dashboard
   - The app will attempt to connect to Jira
   - If successful, real issues will be displayed
   - If connection fails, you'll see specific error messages (401 = bad credentials, 403 = permissions, 404 = wrong URL)
   - Falls back to mock data automatically if API is unavailable

### API Error Handling

The application provides detailed feedback for common issues:
- **401 Unauthorized**: Invalid credentials - check username/password or API token
- **403 Forbidden**: Insufficient permissions - verify account has API access
- **404 Not Found**: Wrong endpoint URL - verify instance/server URL
- **Connection Error**: Cannot reach server - check network and firewall
- **Timeout**: Request took > 30 seconds - check API performance

All API errors are displayed in the dashboard with actionable guidance.

## 💾 Storage Options

### Local Storage (Default)

Tickets are automatically saved to `data/` folder as Parquet files:
```json
{
  "data_storage": {
    "local_mode": true,
    "format": "parquet"
  }
}
```

### Delta Lake (Enterprise)

For production deployments with high volume:

1. **Install Delta Lake**:
   ```bash
   pip install delta-spark pyspark
   ```

2. **Update Configuration**:
   ```json
   {
     "data_storage": {
       "local_mode": false,
       "delta_lake_enabled": true,
       "delta_table_path": "s3://your-bucket/delta-tables/tickets"
     }
   }
   ```

3. **Uncomment Delta Code** in `data_storage.py`

## 👥 Engineer Management

Add or modify engineers in `config/sample_config.json`:

```json
{
  "engineers": [
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
    }
  ]
}
```

**Available Skills**: Network, Database, DevOps, Security, Frontend, Backend, Access, Other

## 📊 Dashboard Features

### Metrics Overview
- Total tickets processed
- High priority ticket count
- Unassigned tickets
- Active categories

### Analytics Charts
- **Category Distribution**: Bar chart of tickets by category
- **Engineer Workload**: Current ticket assignments per engineer
- **Priority Breakdown**: Pie chart of priority distribution

### Ticket Filters
- Filter by priority (High, Medium, Low)
- Filter by category
- Filter by assigned engineer

### Ticket Table
- View all ticket details
- AI-generated summaries
- Source system tracking
- Assignment status

## 🧪 Testing Individual Modules

Each module can be tested independently:

```bash
# Test mock data generator
python mock_data.py

# Test AI triage engine
python ai_triage.py

# Test engineer assignment
python engineer_assignment.py

# Test data storage
python data_storage.py
```

## 🐳 Docker Deployment (Optional)

A `docker-compose.yml` template is provided for containerized deployment:

```bash
# Build and run
docker-compose up -d

# Access at http://localhost:5000
```

## 🔐 Security Best Practices

1. **Never commit secrets**: All credentials are in `.gitignore`
2. **Use environment variables**: Store API keys in `.env` file
3. **Rotate credentials regularly**: Especially for production APIs
4. **Limit API permissions**: Use read-only accounts where possible
5. **Enable HTTPS**: For production deployments

## 📝 Logging

All triage actions are logged to `logs/triage_actions.log`:

```json
{
  "timestamp": "2025-01-15T10:30:00",
  "action": "triage_and_assign",
  "tickets_processed": 35,
  "method": "OpenAI GPT-5"
}
```

## 🛠️ Troubleshooting

### Issue: "No tickets found"
- **Solution**: Check API credentials in config or ensure mock data is enabled

### Issue: "OpenAI API error"
- **Solution**: Verify OPENAI_API_KEY is set correctly, or use mock mode

### Issue: "Delta Lake not working"
- **Solution**: Install delta-spark: `pip install delta-spark pyspark`

### Issue: "ServiceNow/Jira connection failed"
- **Solution**: Verify credentials, network access, and uncomment production code

## 🚀 Deployment to Production

### Local / Development
- Use the local Streamlit command above for development and testing.

### Cloud Deployment (AWS/Azure/GCP)
1. Set up environment variables in cloud provider
2. Use Docker container for consistent deployment
3. Configure load balancer and auto-scaling
4. Enable monitoring and logging
5. Set up CI/CD pipeline for updates

## 📚 API Categories

The AI categorizes tickets into:
- **Network**: VPN, DNS, firewall, connectivity issues
- **Database**: SQL, replication, performance, backups
- **DevOps**: CI/CD, Kubernetes, Docker, deployments
- **Security**: SSL, vulnerabilities, unauthorized access
- **Frontend**: UI, JavaScript, mobile, CSS issues
- **Backend**: API, server errors, integrations
- **Access**: Permissions, accounts, credentials
- **Other**: General IT support requests

## 🤝 Contributing

To extend this project:

1. Add new categories in `ai_triage.py`
2. Customize assignment logic in `engineer_assignment.py`
3. Add more API integrations in `api_integrations.py`
4. Enhance dashboard in `triage_ai.py`

## 📄 License

This project is provided as-is for educational and commercial use.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review code comments for detailed explanations
3. Test individual modules for debugging

## 🎓 Learn More

- **OpenAI API**: https://platform.openai.com/docs
- **ServiceNow REST API**: https://developer.servicenow.com/dev.do
- **Jira REST API**: https://developer.atlassian.com/cloud/jira/platform/rest/v3
- **Streamlit Docs**: https://docs.streamlit.io
- **Delta Lake**: https://delta.io

---

**Built with ❤️ using Streamlit, OpenAI GPT-5, and Python**
