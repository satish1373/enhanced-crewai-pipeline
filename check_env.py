import os
required = ["OPENAI_API_KEY", "GITHUB_TOKEN", "GITHUB_REPO", "JIRA_HOST", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"]
missing = [var for var in required if not os.getenv(var)]
print("Missing variables:", missing if missing else "None - All set!")
