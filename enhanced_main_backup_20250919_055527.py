"""
Enhanced CrewAI Automation Pipeline
Multi-language support, error recovery, and comprehensive monitoring
"""

import os
import re
import runpy
import time
import json
import logging
import sys
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List, tuple

# Import enhanced modules
from enhanced_agents import SmartAgentSelector, LanguageDetector, TestFrameworkSelector
from error_recovery import resilience_manager, ServiceResilienceManager
from monitoring_system import (
    MetricsCollector, SystemMetricsCollector, PipelineMetricsCollector,
    AlertManager, ThresholdAlertRule, AlertLevel, HealthChecker, DashboardData,
    slack_notification_handler, email_notification_handler
)
from enhanced_ticket_tracking import EnhancedTicketTracker, SmartTicketProcessor

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

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", 5))
PROCESSED_TICKETS_FILE = "processed_tickets.json"
SUMMARY_FILE = "workflow_summary.json"
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8080))

# Required environment variables
REQUIRED_VARS = [
    "OPENAI_API_KEY", "GITHUB_TOKEN", "GITHUB_REPO",
    "JIRA_HOST", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"
]

class EnhancedPipeline:
    """Enhanced pipeline with multi-language support, error recovery, and monitoring"""
    
    def __init__(self):
        self.validate_config()
        self.setup_monitoring()
        self.setup_agents()
        self.setup_external_services()
        self.setup_alert_rules()
        self.persistence = self.load_persistence()
        
    def validate_config(self):
        """Validate required environment variables"""
        missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    def setup_monitoring(self):
        """Initialize monitoring components"""
        self.metrics_collector = MetricsCollector(retention_hours=48)
        self.system_metrics = SystemMetricsCollector(self.metrics_collector)
        self.pipeline_metrics = PipelineMetricsCollector(self.metrics_collector)
        self.alert_manager = AlertManager(self.metrics_collector)
        self.health_checker = HealthChecker(self.metrics_collector)
        self.dashboard = DashboardData(self.metrics_collector, self.alert_manager, self.health_checker)
        
        # Start monitoring
        self.system_metrics.start_collection()
        self.alert_manager.start_monitoring()
        
        # Setup notification handlers
        if slack_webhook := os.getenv("SLACK_WEBHOOK_URL"):
            self.alert_manager.add_notification_handler(slack_notification_handler(slack_webhook))
        
        if all(os.getenv(var) for var in ["EMAIL_HOST", "EMAIL_USER", "EMAIL_PASS", "EMAIL_TO"]):
            smtp_config = {
                "host": os.getenv("EMAIL_HOST"),
                "port": os.getenv("EMAIL_PORT", "587"),
                "user": os.getenv("EMAIL_USER"),
                "password": os.getenv("EMAIL_PASS"),
                "from": os.getenv("EMAIL_USER"),
                "to": os.getenv("EMAIL_TO")
            }
            self.alert_manager.add_notification_handler(email_notification_handler(smtp_config))
    
    def setup_agents(self):
        """Initialize enhanced agent system"""
        self.agent_selector = SmartAgentSelector()
        self.language_detector = LanguageDetector()
        self.test_framework_selector = TestFrameworkSelector()
    
    def setup_external_services(self):
        """Initialize external service connections with resilience"""
        # Jira client
        jira_options = {"server": f"https://{os.getenv('JIRA_HOST')}"}
        self.jira_client = JIRA(
            options=jira_options,
            basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
        )
        
        # GitHub client will be created per-request with circuit breaker
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO")
        
        # Initialize enhanced ticket tracking
        self.setup_enhanced_tracking()
    
    def setup_enhanced_tracking(self):
        """Initialize enhanced ticket tracking"""
        self.ticket_tracker = EnhancedTicketTracker("enhanced_ticket_tracking.json")
        self.smart_processor = SmartTicketProcessor(
            self.ticket_tracker, 
            self.jira_client, 
            self
        )
        self.smart_processor.set_project_key(os.getenv("JIRA_PROJECT_KEY"))
        logger.info("Enhanced ticket tracking initialized")
    
    def setup_alert_rules(self):
        """Setup monitoring alert rules"""
        # System alerts
        self.alert_manager.add_alert_rule(
            ThresholdAlertRule(
                "high_cpu_usage",
                "system_cpu_usage", 
                threshold=80.0,
                comparison="greater",
                duration_minutes=5,
                level=AlertLevel.WARNING
            )
        )
        
        self.alert_manager.add_alert_rule(
            ThresholdAlertRule(
                "high_memory_usage",
                "system_memory_usage",
                threshold=85.0,
                comparison="greater", 
                duration_minutes=3,
                level=AlertLevel.CRITICAL
            )
        )
        
        # Pipeline alerts
        self.alert_manager.add_alert_rule(
            ThresholdAlertRule(
                "high_ticket_failure_rate",
                "pipeline_tickets_failed",
                threshold=3.0,
                comparison="greater",
                duration_minutes=30,
                level=AlertLevel.ERROR
            )
        )
        
        self.alert_manager.add_alert_rule(
            ThresholdAlertRule(
                "slow_ticket_processing",
                "pipeline_ticket_duration",
                threshold=1800.0,  # 30 minutes
                comparison="greater",
                duration_minutes=10,
                level=AlertLevel.WARNING
            )
        )
    
    def load_persistence(self) -> Dict[str, Any]:
        """Load persistent data"""
        processed_tickets = set()
        workflow_summary = {}
        
        if os.path.exists(PROCESSED_TICKETS_FILE):
            try:
                with open(PROCESSED_TICKETS_FILE, "r") as f:
                    processed_tickets = set(json.load(f))
            except Exception as e:
                logger.error(f"Failed to load processed tickets: {e}")
        
        if os.path.exists(SUMMARY_FILE):
            try:
                with open(SUMMARY_FILE, "r") as f:
                    workflow_summary = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load workflow summary: {e}")
        
        return {
            "processed_tickets": processed_tickets,
            "workflow_summary": workflow_summary
        }
    
    @resilience_manager.create_resilient_call("jira", "api_call")
    async def fetch_tickets_to_process(self) -> List[tuple]:
        """Fetch all tickets that need processing using enhanced logic"""
        try:
            return self.smart_processor.get_tickets_to_process()
        except Exception as e:
            logger.error(f"Failed to fetch tickets: {e}")
            return []
    
    @resilience_manager.create_resilient_call("jira", "api_call")
    async def fetch_new_ticket(self, jql: Optional[str] = None) -> Optional[Any]:
        """Fetch new Jira ticket with resilience (legacy method)"""
        try:
            jql = jql or f'project = {os.getenv("JIRA_PROJECT_KEY")} AND status = "To Do" ORDER BY created DESC'
            issues = self.jira_client.search_issues(jql, maxResults=1)
            return issues[0] if issues else None
        except Exception as e:
            logger.error(f"Failed to fetch Jira ticket: {e}")
            raise
    
    @resilience_manager.create_resilient_call("github", "api_call")
    async def push_to_github_branch(self, file_path: str, branch_name: str, commit_message: str) -> bool:
        """Push file to GitHub branch with resilience"""
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.github_repo)
            
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
            raise
    
    @resilience_manager.create_resilient_call("github", "api_call")
    async def merge_branch_to_main(self, branch_name: str) -> Optional[str]:
        """Merge branch to main with resilience"""
        try:
            g = Github(self.github_token)
            repo = g.get_repo(self.github_repo)
            
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
            raise
    
    def extract_code_blocks(self, text) -> list:
        """Extract code blocks handling CrewOutput objects"""
        if hasattr(text, 'raw'):
            text = text.raw
        elif hasattr(text, 'result'):
            text = text.result
        elif not isinstance(text, str):
            text = str(text)
        
        return re.findall(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    
    def run_code_with_monitoring(self, file_path: str, language: str) -> tuple[bool, str]:
        """Run code with performance monitoring"""
        start_time = time.time()
        try:
            if language == "python":
                runpy.run_path(file_path)
            elif language == "javascript":
                os.system(f"node {file_path}")
            elif language == "java":
                # Compile and run Java
                class_name = os.path.splitext(os.path.basename(file_path))[0]
                os.system(f"javac {file_path} && java {class_name}")
            # Add more language support as needed
            
            duration = time.time() - start_time
            self.metrics_collector.record_metric(f"code_execution_duration_{language}", duration, unit="seconds")
            return True, ""
        except Exception as e:
            duration = time.time() - start_time
            self.metrics_collector.record_metric(f"code_execution_duration_{language}", duration, unit="seconds")
            return False, str(e)
    
    async def process_ticket_enhanced(self, ticket: Any) -> bool:
        """Process ticket with enhanced multi-language and monitoring support"""
        ticket_key = ticket.key
        start_time = time.time()
        
        try:
            self.pipeline_metrics.record_ticket_started(ticket_key)
            logger.info(f"Processing Jira ticket: {ticket_key} - {ticket.fields.summary}")
            
            task_description = ticket.fields.description or "Implement functionality based on ticket description."
            full_content = f"{ticket.fields.summary} {task_description}"
            
            # Detect language and select appropriate agents
            selected_agents, language, domain = self.agent_selector.select_agents_for_ticket(
                task_description, ticket.fields.summary
            )
            
            logger.info(f"Detected language: {language}, domain: {domain}")
            self.metrics_collector.record_metric("ticket_language_detected", 1, 
                                                labels={"language": language, "domain": domain or "general"})
            
            # Step 1: Router analysis (enhanced with language/domain context)
            router_result = await self.execute_agent_with_monitoring(
                "router", 
                self.create_router_task(full_content, language, domain),
                selected_agents.get("router", self.agent_selector.router)
            )
            
            # Step 2: Specialized coding based on language/domain
            coder_result = await self.execute_agent_with_monitoring(
                "coder",
                self.create_coding_task(task_description, router_result, language, domain),
                selected_agents["coder"]
            )
            
            code_blocks = self.extract_code_blocks(coder_result)
            if not code_blocks:
                logger.error("No code generated by coder agent")
                self.pipeline_metrics.record_ticket_completed(ticket_key, success=False)
                return False
            
            original_code = code_blocks[0].strip()
            with open("original_code.py", "w", encoding="utf-8") as f:
                f.write(original_code)
            
            # Step 3: Enhanced review process with language-specific testing
            successful_branch = None
            
            for attempt in range(1, MAX_ATTEMPTS + 1):
                logger.info(f"Review attempt #{attempt}")
                
                # Reviewer with language-specific guidance
                review_result = await self.execute_agent_with_monitoring(
                    "reviewer",
                    self.create_review_task(original_code, router_result, language, attempt),
                    selected_agents.get("code_reviewer", selected_agents["coder"])
                )
                
                blocks = self.extract_code_blocks(review_result)
                if not blocks:
                    logger.error(f"No code returned from review attempt {attempt}")
                    continue
                
                refactored_code = blocks[-1].strip()
                with open("refactored_code.py", "w", encoding="utf-8") as f:
                    f.write(refactored_code)
                
                # Test the code with language-specific runner
                tests_passed, error = self.run_code_with_monitoring("refactored_code.py", language)
                
                # Enhanced QA with multiple reviewers if available
                qa_results = await self.run_qa_checks(refactored_code, router_result, language, selected_agents)
                qa_approved = all(result["approved"] for result in qa_results.values())
                
                branch_name = f"review_attempt_{attempt}_{language}"
                
                # Push to GitHub with resilience
                try:
                    await self.push_to_github_branch("refactored_code.py", branch_name, f"Review attempt #{attempt} - {language}")
                    
                    # Save comprehensive logs
                    full_log = self.create_comprehensive_log(
                        router_result, coder_result, review_result, qa_results, language, domain
                    )
                    with open("crewai_output.txt", "w", encoding="utf-8") as f:
                        f.write(full_log)
                    await self.push_to_github_branch("crewai_output.txt", branch_name, f"Logs attempt #{attempt}")
                    
                except Exception as e:
                    logger.error(f"Failed to push to GitHub: {e}")
                    # Continue processing even if GitHub fails
                
                # Record attempt in monitoring
                self.record_attempt_metrics(ticket_key, attempt, tests_passed, qa_approved, language, domain)
                
                if tests_passed and qa_approved:
                    logger.info("All tests passed and QA approved!")
                    successful_branch = branch_name
                    break
                else:
                    logger.warning(f"Attempt {attempt} - Tests: {tests_passed}, QA: {qa_approved}")
                    if error:
                        logger.warning(f"Test error: {error}")
            
            # Step 4: Merge and notify if successful
            success = False
            if successful_branch:
                try:
                    pr_url = await self.merge_branch_to_main(successful_branch)
                    if pr_url:
                        await self.send_notifications(ticket, successful_branch, pr_url, language, domain)
                        await self.update_jira_ticket(ticket, successful_branch, pr_url, language)
                        success = True
                        logger.info(f"Ticket {ticket_key} processed successfully!")
                except Exception as e:
                    logger.error(f"Failed to merge or notify: {e}")
            
            # Record completion
            duration = time.time() - start_time
            self.pipeline_metrics.record_ticket_completed(ticket_key, success)
            self.metrics_collector.record_metric("ticket_total_duration", duration, 
                                                labels={"language": language, "success": str(success)}, 
                                                unit="seconds")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_key}: {e}")
            duration = time.time() - start_time
            self.pipeline_metrics.record_ticket_completed(ticket_key, success=False)
            self.metrics_collector.record_metric("ticket_total_duration", duration, 
                                                labels={"language": "unknown", "success": "false"}, 
                                                unit="seconds")
            return False
    
    async def execute_agent_with_monitoring(self, agent_name: str, task: Task, agent: Agent) -> str:
        """Execute agent with performance monitoring"""
        start_time = time.time()
        try:
            crew = Crew(agents=[agent], tasks=[task])
            result = crew.kickoff()
            
            # Convert CrewOutput to string
            if hasattr(result, 'raw'):
                result = result.raw
            elif not isinstance(result, str):
                result = str(result)
            
            duration = time.time() - start_time
            self.pipeline_metrics.record_agent_performance(agent_name, duration, True)
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            self.pipeline_metrics.record_agent_performance(agent_name, duration, False)
            logger.error(f"Agent {agent_name} failed: {e}")
            raise
    
    def create_router_task(self, content: str, language: str, domain: str) -> Task:
        """Create enhanced router task with language/domain context"""
        return Task(
            description=f"""Analyze this ticket for {language} development in {domain or 'general'} domain:
            
Content: {content}

Provide analysis including:
1. Complexity level and time estimate
2. {language}-specific implementation approach
3. Recommended frameworks/libraries for {language}
4. Test strategy for {language}
5. Domain-specific considerations for {domain or 'general programming'}
6. Potential challenges and edge cases
7. Security considerations

Respond in structured format with clear sections.""",
            expected_output="Structured analysis with language-specific guidance and domain expertise",
            agent=None  # Will be set by caller
        )
    
    def create_coding_task(self, description: str, router_analysis: str, language: str, domain: str) -> Task:
        """Create language-specific coding task"""
        framework_guidance = self.get_framework_guidance(language, domain)
        
        return Task(
            description=f"""Implement the following requirement in {language}:

Original Request: {description}

Router Analysis: {router_analysis}

Language-Specific Guidelines:
{framework_guidance}

Requirements:
1. Use {language} best practices and idioms
2. Include proper error handling
3. Add comprehensive documentation
4. Follow language-specific style guides
5. Include basic test examples
6. Consider performance and security

Deliver production-ready {language} code.""",
            expected_output=f"Complete, production-ready {language} code with documentation and basic tests",
            agent=None
        )
    
    def create_review_task(self, code: str, router_analysis: str, language: str, attempt: int) -> Task:
        """Create language-specific review task"""
        test_template = self.test_framework_selector.get_test_template(language)
        test_framework = self.test_framework_selector.get_test_framework(language)
        
        return Task(
            description=f"""Review and enhance this {language} code (attempt #{attempt}):

Code to Review:
{code}

Router Analysis: {router_analysis}

Enhancement Requirements:
1. Refactor for {language} best practices
2. Implement comprehensive {test_framework} tests
3. Add performance optimizations
4. Ensure security best practices
5. Improve error handling and logging
6. Add proper documentation

Test Template to Follow:
{test_template}

Return the enhanced code with full test suite.""",
            expected_output=f"Enhanced {language} code with comprehensive {test_framework} test suite and documentation",
            agent=None
        )
    
    async def run_qa_checks(self, code: str, router_analysis: str, language: str, selected_agents: Dict[str, Agent]) -> Dict[str, Dict[str, Any]]:
        """Run multiple QA checks based on available specialized agents"""
        qa_results = {}
        
        # Primary code review
        if "code_reviewer" in selected_agents:
            qa_results["code_quality"] = await self.run_single_qa_check(
                "code_reviewer", code, router_analysis, language, 
                "code quality, maintainability, and best practices",
                selected_agents["code_reviewer"]
            )
        
        # Security review if security agent available
        if "security_reviewer" in selected_agents:
            qa_results["security"] = await self.run_single_qa_check(
                "security_reviewer", code, router_analysis, language,
                "security vulnerabilities and compliance",
                selected_agents["security_reviewer"]
            )
        
        # Performance review if performance agent available
        if "performance_reviewer" in selected_agents:
            qa_results["performance"] = await self.run_single_qa_check(
                "performance_reviewer", code, router_analysis, language,
                "performance optimization and scalability",
                selected_agents["performance_reviewer"]
            )
        
        return qa_results
    
    async def run_single_qa_check(self, reviewer_type: str, code: str, router_analysis: str, 
                                language: str, focus_area: str, agent: Agent) -> Dict[str, Any]:
        """Run a single QA check"""
        try:
            task = Task(
                description=f"""Review this {language} code focusing on {focus_area}:

Code: {code}

Router Analysis: {router_analysis}

Check for:
1. {language}-specific issues
2. {focus_area.title()} concerns
3. Industry standards compliance
4. Documentation quality

Respond with APPROVED or REJECTED followed by detailed feedback.""",
                expected_output=f"APPROVED/REJECTED decision with detailed {focus_area} assessment",
                agent=agent
            )
            
            result = await self.execute_agent_with_monitoring(reviewer_type, task, agent)
            approved = "approved" in result.lower()
            
            return {
                "approved": approved,
                "feedback": result,
                "reviewer_type": reviewer_type
            }
        except Exception as e:
            logger.error(f"QA check {reviewer_type} failed: {e}")
            return {
                "approved": False,
                "feedback": f"QA check failed: {e}",
                "reviewer_type": reviewer_type
            }
    
    def get_framework_guidance(self, language: str, domain: str) -> str:
        """Get framework-specific guidance"""
        guidance_map = {
            "python": {
                "web_backend": "Use FastAPI or Django REST framework. Include Pydantic models.",
                "data_science": "Use pandas, numpy, scikit-learn. Include data validation.",
                "general": "Follow PEP 8. Use type hints. Include docstrings."
            },
            "javascript": {
                "web_frontend": "Use modern ES6+. Consider React or Vue patterns.",
                "web_backend": "Use Express.js or Fastify. Include proper middleware.",
                "general": "Use modern JavaScript patterns. Include JSDoc comments."
            },
            "java": {
                "web_backend": "Use Spring Boot. Follow Java enterprise patterns.",
                "general": "Follow Java conventions. Use proper OOP design patterns."
            }
        }
        
        return guidance_map.get(language, {}).get(domain, guidance_map.get(language, {}).get("general", "Follow language best practices."))
    
    def create_comprehensive_log(self, router_result: str, coder_result: str, review_result: str, 
                                qa_results: Dict[str, Dict[str, Any]], language: str, domain: str) -> str:
        """Create comprehensive log with all results"""
        qa_summary = "\n".join([
            f"{reviewer_type.upper()} Review ({result['reviewer_type']}):\n{result['feedback']}\n"
            for reviewer_type, result in qa_results.items()
        ])
        
        return f"""Enhanced CrewAI Pipeline Execution Log
Language: {language}
Domain: {domain or 'General'}
Timestamp: {datetime.now().isoformat()}

=== ROUTER ANALYSIS ===
{router_result}

=== CODER OUTPUT ===
{coder_result}

=== REVIEWER OUTPUT ===
{review_result}

=== QA REVIEWS ===
{qa_summary}

=== METRICS ===
Processing completed with enhanced monitoring and multi-language support.
"""
    
    def record_attempt_metrics(self, ticket_key: str, attempt: int, tests_passed: bool, 
                             qa_approved: bool, language: str, domain: str):
        """Record detailed attempt metrics"""
        labels = {
            "ticket": ticket_key,
            "attempt": str(attempt),
            "language": language,
            "domain": domain or "general"
        }
        
        self.metrics_collector.record_metric("attempt_tests_passed", 1 if tests_passed else 0, labels)
        self.metrics_collector.record_metric("attempt_qa_approved", 1 if qa_approved else 0, labels)
        self.metrics_collector.record_metric("attempt_completed", 1, labels)
    
    def save_processed_tickets(self):
        """Save processed tickets to file"""
        try:
            with open(PROCESSED_TICKETS_FILE, "w") as f:
                json.dump(list(self.persistence["processed_tickets"]), f)
        except Exception as e:
            logger.error(f"Failed to save processed tickets: {e}")
    
    async def send_notifications(self, ticket: Any, branch_name: str, pr_url: str, language: str, domain: str):
        """Send enhanced notifications with language/domain context"""
        message = f"""CrewAI Enhanced Pipeline Notification

✅ Ticket: {ticket.key} - {ticket.fields.summary}
🔗 PR: {pr_url}
💻 Language: {language}
🎯 Domain: {domain or 'General'}
🌿 Branch: {branch_name}

Multi-language pipeline successfully processed and merged to main."""
        
        # Send to configured notification channels
        if slack_webhook := os.getenv("SLACK_WEBHOOK_URL"):
            try:
                payload = {"text": message}
                requests.post(slack_webhook, json=payload, timeout=10)
            except Exception as e:
                logger.error(f"Slack notification failed: {e}")
    
    @resilience_manager.create_resilient_call("jira", "api_call")
    async def update_jira_ticket(self, ticket: Any, branch_name: str, pr_url: str, language: str):
        """Update Jira ticket with enhanced information"""
        try:
            comment = f"""Enhanced CrewAI workflow completed successfully!

✅ Branch: {branch_name}
🔗 Pull Request: {pr_url}
💻 Language: {language}
🤖 Agents: Multi-agent collaboration with specialized review
📊 Monitoring: Full metrics and alerting enabled

The code has been automatically generated, reviewed, tested, and merged to main branch."""
            
            self.jira_client.add_comment(ticket.key, comment)
            logger.info(f"Updated Jira ticket {ticket.key}")
        except Exception as e:
            logger.error(f"Failed to update Jira ticket: {e}")
            raise
    
    async def run_pipeline(self):
        """Enhanced main pipeline execution loop with comprehensive tracking"""
        logger.info("Starting Enhanced CrewAI automation pipeline with comprehensive tracking")
        
        # Setup health checks
        self.setup_health_checks()
        
        while True:
            try:
                logger.info("Checking for tickets to process...")
                
                # Process all tickets that need processing
                results = await self.smart_processor.process_tickets()
                
                if results["processed"] > 0 or results["failed"] > 0:
                    logger.info(f"Processing cycle complete: {results['processed']} processed, {results['failed']} failed")
                    
                    # Log any errors
                    for error in results["errors"]:
                        logger.error(f"Processing error: {error}")
                    
                    # Generate status report
                    status_report = self.smart_processor.get_status_report()
                    logger.info(f"Pipeline statistics: {status_report['statistics']}")
                    
                    # Alert on failed tickets ready for retry
                    retry_candidates = status_report.get("failed_tickets_ready_for_retry", [])
                    if retry_candidates:
                        logger.warning(f"{len(retry_candidates)} tickets ready for retry")
                        for candidate in retry_candidates:
                            logger.info(f"Retry candidate: {candidate['key']} - {candidate['summary'][:50]}...")
                else:
                    logger.info("No tickets need processing")
                
            except KeyboardInterrupt:
                logger.info("Pipeline stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                self.metrics_collector.record_metric("pipeline_unexpected_errors", 1)
            
            logger.info(f"Sleeping for {POLL_INTERVAL} seconds...")
            await asyncio.sleep(POLL_INTERVAL)
    
    def setup_health_checks(self):
        """Setup health checks for external services"""
        
        def check_jira_health():
            try:
                self.jira_client.myself()
                return True
            except:
                return False
        
        def check_github_health():
            try:
                g = Github(self.github_token)
                g.get_user()
                return True
            except:
                return False
        
        def check_openai_health():
            try:
                # Simple API check - could be enhanced
                return bool(os.getenv("OPENAI_API_KEY"))
            except:
                return False
        
        self.health_checker.register_health_check("jira", check_jira_health, 120)
        self.health_checker.register_health_check("github", check_github_health, 120)  
        self.health_checker.register_health_check("openai", check_openai_health, 300)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        base_status = {
            "pipeline_status": "running",
            "dashboard_data": self.dashboard.get_dashboard_data(),
            "circuit_breaker_status": resilience_manager.get_health_status(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add enhanced tracking if available
        if hasattr(self, 'smart_processor'):
            enhanced_status = self.smart_processor.get_status_report()
            base_status.update({
                "enhanced_tracking": enhanced_status,
                "ticket_statistics": enhanced_status["statistics"],
                "retry_candidates": len(enhanced_status.get("failed_tickets_ready_for_retry", []))
            })
        else:
            # Fallback to old persistence data
            base_status["processed_tickets"] = len(self.persistence.get("processed_tickets", []))
        
        return base_status
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get detailed enhanced tracking status"""
        if hasattr(self, 'smart_processor'):
            return self.smart_processor.get_status_report()
        else:
            return {"error": "Enhanced tracking not initialized"}
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down enhanced pipeline...")
        self.system_metrics.stop_collection()
        self.alert_manager.stop_monitoring()
        logger.info("Enhanced pipeline shutdown complete")

async def main():
    """Main entry point"""
    pipeline = EnhancedPipeline()
    
    try:
        await pipeline.run_pipeline()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        pipeline.shutdown()

if __name__ == "__main__":
    asyncio.run(main())