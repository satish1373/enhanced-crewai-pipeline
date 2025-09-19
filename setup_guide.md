# CrewAI Automation Pipeline Setup Guide

## Overview
This pipeline automates code generation and review triggered by Jira tickets, with GitHub integration and quality assurance checks.

## Step 1: Prerequisites

### API Keys and Tokens Required:
1. **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **GitHub Personal Access Token** - Create at GitHub Settings > Developer settings > Personal access tokens
   - Required scopes: `repo`, `workflow`
3. **Jira API Token** - Generate at Atlassian Account Settings > Security > API tokens
4. **Slack Webhook URL** (Optional) - Create at Slack App settings
5. **Email credentials** (Optional) - Use app-specific passwords for Gmail

## Step 2: Replit Setup

### 2.1 Create New Replit Project
1. Go to [replit.com](https://replit.com)
2. Click "Create Repl"
3. Choose "Python" template
4. Name: `crewai-automation-pipeline`

### 2.2 Upload Files
Copy these files to your Replit project:
- `main.py` (main pipeline script)
- `requirements.txt` (dependencies)
- `.env.example` (configuration template)

### 2.3 Install Dependencies
In the Replit Shell, run:
```bash
pip install -r requirements.txt
```

## Step 3: Configuration

### 3.1 Set Environment Variables in Replit
1. Click the "Secrets" tab (lock icon) in Replit sidebar
2. Add each variable from `.env.example`:

**Required Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `GITHUB_TOKEN`: Your GitHub personal access token
- `GITHUB_REPO`: Format as `username/repository-name`
- `JIRA_HOST`: Your Jira domain (e.g., `company.atlassian.net`)
- `JIRA_EMAIL`: Your Jira login email
- `JIRA_API_TOKEN`: Your Jira API token
- `JIRA_PROJECT_KEY`: Jira project key (e.g., `PROJ`)

**Optional Variables:**
- `POLL_INTERVAL`: Seconds between Jira checks (default: 60)
- `MAX_ATTEMPTS`: Max review attempts (default: 5)
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications
- `EMAIL_HOST`: SMTP server (e.g., `smtp.gmail.com`)
- `EMAIL_PORT`: SMTP port (default: 587)
- `EMAIL_USER`: Your email address
- `EMAIL_PASS`: Email app password
- `EMAIL_TO`: Recipient email address

### 3.2 Verify Configuration
Run this test in Replit console:
```python
import os
required = ["OPENAI_API_KEY", "GITHUB_TOKEN", "GITHUB_REPO", "JIRA_HOST", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"]
missing = [var for var in required if not os.getenv(var)]
print("Missing variables:", missing if missing else "None - All set!")
```

## Step 4: GitHub Repository Setup

### 4.1 Create Repository
1. Create a new GitHub repository
2. Initialize with README
3. Set as public or private (your choice)

### 4.2 Verify GitHub Token Permissions
Test token access:
```python
from github import Github
g = Github("your-token")
repo = g.get_repo("username/repo-name")
print(f"Repository: {repo.full_name}")
```

## Step 5: Jira Project Setup

### 5.1 Create Jira Project
1. Create project with key matching `JIRA_PROJECT_KEY`
2. Ensure you have permissions to:
   - Read issues
   - Add comments
   - Transition issues

### 5.2 Test Jira Connection
```python
from jira import JIRA
jira = JIRA(
    options={"server": "https://your-domain.atlassian.net"},
    basic_auth=("your-email", "your-api-token")
)
projects = jira.projects()
print([p.key for p in projects])
```

## Step 6: Running the Pipeline

### 6.1 Start the Pipeline
In Replit, click the "Run" button or execute:
```bash
python main.py
```

### 6.2 Monitor Logs
The pipeline will:
- Check for new Jira tickets every 60 seconds (configurable)
- Log all activities to `pipeline.log`
- Create audit trail in `workflow_summary.json`
- Track processed tickets in `processed_tickets.json`

## Step 7: Testing the Workflow

### 7.1 Create Test Jira Ticket
1. Go to your Jira project
2. Create new issue with status "To Do"
3. Set description: "Write a Python function that calculates factorial"

### 7.2 Expected Workflow
1. Pipeline detects new ticket
2. Coder agent generates initial code
3. Reviewer agent refactors and adds tests
4. QA agent validates code quality
5. Code pushed to GitHub branches
6. Final version merged to main
7. Notifications sent (if configured)
8. Jira ticket updated with results

## Step 8: Monitoring and Maintenance

### 8.1 Log Files
- `pipeline.log`: Real-time pipeline logs
- `workflow_summary.json`: Complete audit trail
- `processed_tickets.json`: Processed ticket tracking

### 8.2 Replit Always-On
For continuous operation:
1. Upgrade to Replit Pro
2. Enable "Always On" for your repl
3. Pipeline will run 24/7

## Troubleshooting

### Common Issues:

**Import Errors:**
```bash
pip install --upgrade -r requirements.txt
```

**API Authentication:**
- Verify all tokens are valid and not expired
- Check token permissions/scopes

**Jira Connection:**
- Ensure API token has correct permissions
- Verify Jira host URL format

**GitHub Push Failures:**
- Check repository exists and is accessible
- Verify token has `repo` scope

**CrewAI Errors:**
- Ensure OpenAI API key has sufficient credits
- Check for rate limiting

### Debug Mode:
Set environment variable `DEBUG=true` for verbose logging.

## Security Notes

1. Never commit API keys to GitHub
2. Use Replit Secrets for all sensitive data
3. Regularly rotate API tokens
4. Monitor usage and costs
5. Enable 2FA on all accounts

## Support

For issues:
1. Check `pipeline.log` for error details
2. Verify all environment variables
3. Test individual components (Jira, GitHub, OpenAI)
4. Review workflow summary for failed attempts