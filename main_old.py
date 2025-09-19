"""
CrewAI Automation Pipeline
Integrates Jira, GitHub, Slack/Email notifications with QA workflow
"""

import os
import re
import runpy
import time
import json
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from crewai import Agent, Task, Crew
    from github import Github
    import requests
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from jira import JIRA
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))  # seconds
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", 5))
PROCESSED_TICKETS_FILE = "processed_tickets.json"
SUMMARY_FILE = "workflow_summary.json"

# Required environment variables
REQUIRED_VARS = [
    "OPENAI_API_KEY", "GITHUB_TOKEN", "GITHUB_REPO",
    "JIRA_HOST", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"
]

class ConfigError(Exception):
    """Configuration error"""
    pass

class WorkflowError(Exception):
    """Workflow execution error"""
    pass

def validate_config():
    """Validate required environment variables"""
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        raise ConfigError(f"Missing required environment variables: {', '.join(missing)}")

def safe_get_env(key: str, default: str = "") -> str:
    """Safely get environment variable"""
    return os.getenv(key, default).strip()

# Initialize configuration
try:
    validate_config()
    
    # Core config
    OPENAI_API_KEY = safe_get_env("OPENAI_API_KEY")
    GITHUB_TOKEN = safe_get_env("GITHUB_TOKEN")
    GITHUB_REPO = safe_get_env("GITHUB_REPO")
    
    # Jira config
    JIRA_HOST = safe_get_env("JIRA_HOST")
    JIRA_EMAIL = safe_get_env("JIRA_EMAIL")
    JIRA_API_TOKEN = safe_get_env("JIRA_API_TOKEN")
    JIRA_PROJECT_KEY = safe_get_env("JIRA_PROJECT_KEY")
    
    # Optional notification config
    SLACK_WEBHOOK_URL = safe_get_env("SLACK_WEBHOOK_URL")
    EMAIL_HOST = safe_get_env("EMAIL_HOST")
    EMAIL_PORT = int(safe_get_env("EMAIL_PORT", "587"))
    EMAIL_USER = safe_get_env("EMAIL_USER")
    EMAIL_PASS = safe_get_env("EMAIL_PASS")
    EMAIL_TO = safe_get_env("EMAIL_TO")
    
except ConfigError as e:
    logger.error(f"Configuration error: {e}")
    sys.exit(1)

# Initialize Jira client
try:
    jira_options = {"server": f"https://{JIRA_HOST}"}
    jira_client = JIRA(
        options=jira_options,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )
except Exception as e:
    logger.error(f"Failed to initialize Jira client: {e}")
    sys.exit(1)

# CrewAI Agents
coder = Agent(
    role="Python Coder",
    goal="Write efficient and clean Python code",
    backstory="A detail-oriented software developer who always follows best practices.",
    verbose=True
)

reviewer = Agent(
    role="Code Reviewer & Self-Correcting Refactorer",
    goal="Review, refactor, validate, and correct Python code until all tests pass",
    backstory="An experienced software architect ensuring correctness and production-ready quality.",
    verbose=True
)

qa_agent = Agent(
    role="Quality Assurance & Compliance Checker",
    goal="Verify Python code for correctness, best practices, security, and test coverage",
    backstory="A meticulous QA engineer ensuring production-ready, secure, and high-quality code.",
    verbose=True
)

def extract_code_blocks(text: str) -> list:
    """Extract Python code blocks from markdown-like output"""
    return re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)

def run_code(file_path: str) -> tuple[bool, str]:
    """Run a Python file and capture errors"""
    try:
        runpy.run_path(file_path)
        return True, ""
    except Exception as e:
        return False, str(e)

def fetch_new_ticket(jql: Optional[str] = None) -> Optional[Any]:
    """Fetch new Jira ticket"""
    try:
        jql = jql or f'project = {JIRA_PROJECT_KEY} AND status = "To Do" ORDER BY created ASC'
        issues = jira_client.search_issues(jql, maxResults=1)
        return issues[0] if issues else None
    except Exception as e:
        logger.error(f"Failed to fetch Jira ticket: {e}")
        return None

def update_ticket(issue: Any, branch_name: str, pr_url: str, test_summary: str, log_snippet: str = ""):
    """Update Jira ticket with results"""
    try:
        comment = f"""CrewAI workflow completed:
✅ Branch: {branch_name}
🔗 PR Link: {pr_url}
🧪 Test Summary: {test_summary}
📄 Logs (snippet):
{log_snippet[:500]}"""
        jira_client.add_comment(issue.key, comment)
        logger.info(f"Updated Jira ticket {issue.key}")
    except Exception as e:
        logger.error(f"Failed to update Jira ticket: {e}")

def push_to_github_branch(file_path: str, branch_name: str, commit_message: str) -> bool:
    """Push file to GitHub branch"""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        
        # Create branch
        try:
            source = repo.get_branch("main")
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)
            logger.info(f"Branch '{branch_name}' created from main")
        except Exception:
            logger.warning(f"Branch '{branch_name}' may already exist")
        
        # Read and commit file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        try:
            repo_file = repo.get_contents(file_path, ref=branch_name)
            repo.update_file(file_path, commit_message, content, repo_file.sha, branch=branch_name)
        except Exception:
            repo.create_file(file_path, commit_message, content, branch=branch_name)
        
        logger.info(f"{file_path} committed to branch '{branch_name}'")
        return True
    except Exception as e:
        logger.error(f"Failed to push to GitHub: {e}")
        return False

def merge_branch_to_main(branch_name: str) -> Optional[str]:
    """Merge branch to main and return PR URL"""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        
        pr = repo.create_pull(
            title=f"Merge {branch_name} into main",
            body="Automated merge of final refactored code with passing tests",
            head=branch_name,
            base="main"
        )
        pr.merge(merge_method="merge")
        logger.info(f"Branch '{branch_name}' successfully merged into main")
        return pr.html_url
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        return None

def notify_slack(branch_name: str, pr_url: str, test_summary: str, log_snippet: str = ""):
    """Send Slack notification"""
    if not SLACK_WEBHOOK_URL:
        return
    
    try:
        message = f"""*CrewAI Auto-Merge Notification*
✅ Branch `{branch_name}` merged into `main`
🔗 PR: {pr_url}
🧪 Test Results: {test_summary}
📄 Logs (first 500 chars):
```{log_snippet[:500]}```"""
        
        requests.post(SLACK_WEBHOOK_URL, json={"text": message}, timeout=10)
        logger.info("Slack notification sent")
    except Exception as e:
        logger.error(f"Slack notification failed: {e}")

def notify_email(branch_name: str, pr_url: str, test_summary: str, log_snippet: str = ""):
    """Send email notification"""
    if not all([EMAIL_HOST, EMAIL_USER, EMAIL_PASS, EMAIL_TO]):
        return
    
    try:
        subject = f"CrewAI Auto-Merge: {branch_name} merged into main"
        body = f"""CrewAI Auto-Merge Notification

✅ Branch `{branch_name}` merged into `main`
🔗 PR: {pr_url}

🧪 Test Results: {test_summary}

📄 Logs (first 500 chars):
{log_snippet[:500]}"""
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        server.quit()
        logger.info("Email notification sent")
    except Exception as e:
        logger.error(f"Email notification failed: {e}")

# Persistence functions
def load_processed_tickets() -> set:
    """Load processed tickets from file"""
    if os.path.exists(PROCESSED_TICKETS_FILE):
        try:
            with open(PROCESSED_TICKETS_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            logger.error(f"Failed to load processed tickets: {e}")
    return set()

def mark_ticket_processed(ticket_key: str, processed_tickets: set):
    """Mark ticket as processed"""
    processed_tickets.add(ticket_key)
    try:
        with open(PROCESSED_TICKETS_FILE, "w") as f:
            json.dump(list(processed_tickets), f)
    except Exception as e:
        logger.error(f"Failed to save processed tickets: {e}")

def load_workflow_summary() -> dict:
    """Load workflow summary from file"""
    if os.path.exists(SUMMARY_FILE):
        try:
            with open(SUMMARY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workflow summary: {e}")
    return {}

def record_attempt(workflow_summary: dict, ticket_key: str, summary: str, 
                  branch_name: str, tests_passed: bool, qa_approved: bool, log_snippet: str):
    """Record attempt in workflow summary"""
    if ticket_key not in workflow_summary:
        workflow_summary[ticket_key] = {
            "summary": summary,
            "attempts": [],
            "final_branch": None,
            "pr_url": None,
            "status": None,
            "timestamp": datetime.now().isoformat()
        }
    
    workflow_summary[ticket_key]["attempts"].append({
        "branch_name": branch_name,
        "tests_passed": tests_passed,
        "qa_approved": qa_approved,
        "log_snippet": log_snippet[:500],
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        with open(SUMMARY_FILE, "w") as f:
            json.dump(workflow_summary, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save workflow summary: {e}")

def record_final(workflow_summary: dict, ticket_key: str, final_branch: str, 
                pr_url: str, status: str = "merged"):
    """Record final result in workflow summary"""
    if ticket_key in workflow_summary:
        workflow_summary[ticket_key]["final_branch"] = final_branch
        workflow_summary[ticket_key]["pr_url"] = pr_url
        workflow_summary[ticket_key]["status"] = status
        workflow_summary[ticket_key]["completed_timestamp"] = datetime.now().isoformat()
        
        try:
            with open(SUMMARY_FILE, "w") as f:
                json.dump(workflow_summary, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save final workflow summary: {e}")

def process_ticket(ticket: Any, processed_tickets: set, workflow_summary: dict):
    """Process a single Jira ticket through the workflow"""
    logger.info(f"Processing Jira ticket: {ticket.key} - {ticket.fields.summary}")
    mark_ticket_processed(ticket.key, processed_tickets)
    
    task_description = ticket.fields.description or "Implement functionality based on ticket description."
    
    # Step 1: Coder generates initial code
    try:
        coding_task = Task(description=task_description, agent=coder)
        crew = Crew(agents=[coder], tasks=[coding_task])
        coder_result = crew.kickoff()
        
        code_blocks = extract_code_blocks(coder_result)
        original_code = code_blocks[0].strip() if code_blocks else ""
        
        if not original_code:
            logger.error("No code generated by Coder agent")
            return
        
        with open("original_code.py", "w", encoding="utf-8") as f:
            f.write(original_code)
        
    except Exception as e:
        logger.error(f"Coder agent failed: {e}")
        return
    
    # Step 2: Reviewer iterative self-correction
    refactored_code = original_code
    successful_branch = None
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(f"Reviewer attempt #{attempt}")
        
        try:
            review_task_template = """Review the following Python code:
{code}

1. Refactor for readability, performance, and best practices.
2. Wrap in main() with multiple test cases including:
   - First 5 primes are [2,3,5,7,11]
   - Primes below 10 are [2,3,5,7]
   - Primes below 2 return []
   - Primes below 1 return []
3. Print test results with ✅ or ❌ indicators
4. Correct failing tests automatically.
5. Return final refactored code."""
            
            review_task = Task(
                description=review_task_template.format(code=refactored_code),
                agent=reviewer
            )
            review_crew = Crew(agents=[reviewer], tasks=[review_task])
            review_result = review_crew.kickoff()
            
            blocks = extract_code_blocks(review_result)
            if not blocks:
                logger.error(f"No code returned from Reviewer attempt {attempt}")
                continue
            
            refactored_code = blocks[-1].strip()
            with open("refactored_code.py", "w", encoding="utf-8") as f:
                f.write(refactored_code)
            
            # Test the code
            tests_passed, error = run_code("refactored_code.py")
            branch_name = f"review_attempt_{attempt}"
            
            # QA Check
            qa_approved = False
            qa_result = ""
            try:
                qa_task_template = """Check the following Python code for quality, style, security, and test coverage:
{code}

1. Verify PEP8 compliance
2. Check for potential bugs and security issues
3. Validate all tests pass
4. Respond with either "APPROVED" or "REJECTED" followed by your comments"""
                
                qa_task = Task(
                    description=qa_task_template.format(code=refactored_code),
                    agent=qa_agent
                )
                qa_crew = Crew(agents=[qa_agent], tasks=[qa_task])
                qa_result = qa_crew.kickoff()
                qa_approved = "approved" in qa_result.lower()
                
            except Exception as e:
                logger.error(f"QA agent failed: {e}")
                qa_result = f"QA check failed: {e}"
            
            # Push to GitHub
            push_to_github_branch("refactored_code.py", branch_name, f"Reviewer attempt #{attempt}")
            
            # Save logs
            with open("crewai_output.txt", "w", encoding="utf-8") as f:
                full_log = f"{coder_result}\n--- Reviewer Logs ---\n{review_result}\n--- QA Logs ---\n{qa_result}"
                f.write(full_log)
            push_to_github_branch("crewai_output.txt", branch_name, f"Logs attempt #{attempt}")
            
            # Record attempt
            record_attempt(
                workflow_summary, ticket.key, ticket.fields.summary,
                branch_name, tests_passed, qa_approved, full_log
            )
            
            if tests_passed and qa_approved:
                logger.info("All tests passed and QA approved!")
                successful_branch = branch_name
                break
            else:
                logger.warning(f"Attempt {attempt} - Tests: {tests_passed}, QA: {qa_approved}")
                if error:
                    logger.warning(f"Test error: {error}")
        
        except Exception as e:
            logger.error(f"Reviewer attempt {attempt} failed: {e}")
    
    # Step 3: Merge and notify if successful
    if successful_branch:
        pr_url = merge_branch_to_main(successful_branch)
        if pr_url:
            test_summary = "All automated tests passed and QA approved"
            
            with open("crewai_output.txt", "r", encoding="utf-8") as f:
                log_snippet = f.read()
            
            notify_slack(successful_branch, pr_url, test_summary, log_snippet)
            notify_email(successful_branch, pr_url, test_summary, log_snippet)
            update_ticket(ticket, successful_branch, pr_url, test_summary, log_snippet)
            record_final(workflow_summary, ticket.key, successful_branch, pr_url)
            
            logger.info(f"Ticket {ticket.key} processed successfully!")
        else:
            logger.error(f"Failed to merge branch {successful_branch}")
    else:
        logger.warning(f"Ticket {ticket.key} failed all attempts")

def main():
    """Main workflow loop"""
    logger.info("Starting CrewAI automation pipeline")
    
    # Load persistence
    processed_tickets = load_processed_tickets()
    workflow_summary = load_workflow_summary()
    
    logger.info(f"Loaded {len(processed_tickets)} processed tickets")
    
    while True:
        try:
            logger.info("Checking for new Jira tickets...")
            ticket = fetch_new_ticket()
            
            if ticket and ticket.key not in processed_tickets:
                process_ticket(ticket, processed_tickets, workflow_summary)
            else:
                logger.info("No new tickets to process")
            
        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        
        logger.info(f"Sleeping for {POLL_INTERVAL} seconds...")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()