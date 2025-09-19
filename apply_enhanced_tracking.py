#!/usr/bin/env python3
"""
Automated Integration Script for Enhanced Ticket Tracking
Applies all enhancements to support updated tickets and failed processing recovery
"""

import os
import shutil
from datetime import datetime

def apply_enhanced_tracking_integration():
    """Apply comprehensive enhanced tracking integration"""
    
    print("Applying Enhanced Ticket Tracking Integration...")
    print("=" * 60)
    
    # Backup enhanced_main.py
    backup_name = f"enhanced_main_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    if os.path.exists("enhanced_main.py"):
        shutil.copy("enhanced_main.py", backup_name)
        print(f"✓ Created backup: {backup_name}")
    
    # Read current enhanced_main.py
    with open("enhanced_main.py", "r") as f:
        content = f.read()
    
    # Apply integration patches
    
    # 1. Add import for enhanced tracking
    import_section = '''# Import enhanced modules
from enhanced_agents import SmartAgentSelector, LanguageDetector, TestFrameworkSelector
from error_recovery import resilience_manager, ServiceResilienceManager
from monitoring_system import (
    MetricsCollector, SystemMetricsCollector, PipelineMetricsCollector,
    AlertManager, ThresholdAlertRule, AlertLevel, HealthChecker, DashboardData,
    slack_notification_handler, email_notification_handler
)'''
    
    new_import_section = '''# Import enhanced modules
from enhanced_agents import SmartAgentSelector, LanguageDetector, TestFrameworkSelector
from error_recovery import resilience_manager, ServiceResilienceManager
from monitoring_system import (
    MetricsCollector, SystemMetricsCollector, PipelineMetricsCollector,
    AlertManager, ThresholdAlertRule, AlertLevel, HealthChecker, DashboardData,
    slack_notification_handler, email_notification_handler
)
from enhanced_ticket_tracking import EnhancedTicketTracker, SmartTicketProcessor'''
    
    if import_section in content:
        content = content.replace(import_section, new_import_section)
        print("✓ Added enhanced tracking imports")
    
    # 2. Add setup_enhanced_tracking method
    setup_external_services_end = '''        # GitHub client will be created per-request with circuit breaker
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO")'''
    
    enhanced_setup = '''        # GitHub client will be created per-request with circuit breaker
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
        logger.info("Enhanced ticket tracking initialized")'''
    
    if setup_external_services_end in content:
        content = content.replace(setup_external_services_end, enhanced_setup)
        print("✓ Added enhanced tracking setup")
    
    # 3. Replace fetch_new_ticket with enhanced version
    old_fetch_method = '''    @resilience_manager.create_resilient_call("jira", "api_call")
    async def fetch_new_ticket(self, jql: Optional[str] = None) -> Optional[Any]:
        """Fetch new Jira ticket with resilience"""
        try:
            jql = jql or f'project = {os.getenv("JIRA_PROJECT_KEY")} AND status = "To Do" ORDER BY created DESC'
            issues = self.jira_client.search_issues(jql, maxResults=1)
            return issues[0] if issues else None
        except Exception as e:
            logger.error(f"Failed to fetch Jira ticket: {e}")
            raise'''
    
    new_fetch_method = '''    @resilience_manager.create_resilient_call("jira", "api_call")
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
            raise'''
    
    if old_fetch_method in content:
        content = content.replace(old_fetch_method, new_fetch_method)
        print("✓ Updated fetch methods for enhanced tracking")
    
    # 4. Replace run_pipeline method
    old_run_pipeline = '''    async def run_pipeline(self):
        """Main pipeline execution loop"""
        logger.info("Starting Enhanced CrewAI automation pipeline")
        logger.info(f"Loaded {len(self.persistence['processed_tickets'])} processed tickets")
        
        # Setup health checks
        self.setup_health_checks()
        
        while True:
            try:
                logger.info("Checking for new Jira tickets...")
                ticket = await self.fetch_new_ticket()
                
                if ticket and ticket.key not in self.persistence["processed_tickets"]:
                    success = await self.process_ticket_enhanced(ticket)
                    if success:
                        logger.info(f"Successfully processed ticket {ticket.key}")
                    else:
                        logger.warning(f"Failed to process ticket {ticket.key}")
                else:
                    logger.info("No new tickets to process")
                
            except KeyboardInterrupt:
                logger.info("Pipeline stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                self.metrics_collector.record_metric("pipeline_unexpected_errors", 1)
            
            logger.info(f"Sleeping for {POLL_INTERVAL} seconds...")
            await asyncio.sleep(POLL_INTERVAL)'''
    
    new_run_pipeline = '''    async def run_pipeline(self):
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
            await asyncio.sleep(POLL_INTERVAL)'''
    
    if old_run_pipeline in content:
        content = content.replace(old_run_pipeline, new_run_pipeline)
        print("✓ Updated main pipeline loop for enhanced tracking")
    
    # 5. Update process_ticket_enhanced to use tracking
    process_ticket_start = '''    async def process_ticket_enhanced(self, ticket: Any) -> bool:
        """Process ticket with enhanced multi-language and monitoring support"""
        ticket_key = ticket.key
        start_time = time.time()
        
        try:
            self.pipeline_metrics.record_ticket_started(ticket_key)
            logger.info(f"Processing Jira ticket: {ticket_key} - {ticket.fields.summary}")
            
            # Mark as processed early to prevent reprocessing
            self.persistence["processed_tickets"].add(ticket_key)
            self.save_processed_tickets()'''
    
    enhanced_process_start = '''    async def process_ticket_enhanced(self, ticket: Any) -> bool:
        """Process ticket with enhanced multi-language and monitoring support"""
        ticket_key = ticket.key
        start_time = time.time()
        
        try:
            self.pipeline_metrics.record_ticket_started(ticket_key)
            logger.info(f"Processing Jira ticket: {ticket_key} - {ticket.fields.summary}")'''
    
    if process_ticket_start in content:
        content = content.replace(process_ticket_start, enhanced_process_start)
        print("✓ Updated process_ticket_enhanced method")
    
    # 6. Add tracking update in language detection section
    language_detection_section = '''        logger.info(f"Detected language: {language}, domain: {domain}")
        self.metrics_collector.record_metric("ticket_language_detected", 1, 
                                            labels={"language": language, "domain": domain or "general"})'''
    
    enhanced_language_section = '''        logger.info(f"Detected language: {language}, domain: {domain}")
        self.metrics_collector.record_metric("ticket_language_detected", 1, 
                                            labels={"language": language, "domain": domain or "general"})
        
        # Update tracking with detected language/domain
        if hasattr(self, 'ticket_tracker'):
            version = self.ticket_tracker.ticket_versions.get(ticket_key)
            if version:
                version.language_detected = language
                version.domain_detected = domain
                self.ticket_tracker.save_ticket_data()'''
    
    if language_detection_section in content:
        content = content.replace(language_detection_section, enhanced_language_section)
        print("✓ Added language/domain tracking update")
    
    # 7. Add enhanced status method
    old_get_status = '''    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive pipeline status"""
        return {
            "pipeline_status": "running",
            "dashboard_data": self.dashboard.get_dashboard_data(),
            "circuit_breaker_status": resilience_manager.get_health_status(),
            "processed_tickets": len(self.persistence["processed_tickets"]),
            "timestamp": datetime.now().isoformat()
        }'''
    
    new_get_status = '''    def get_status(self) -> Dict[str, Any]:
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
            return {"error": "Enhanced tracking not initialized"}'''
    
    if old_get_status in content:
        content = content.replace(old_get_status, new_get_status)
        print("✓ Added enhanced status methods")
    
    # 8. Add List import if not present
    if "from typing import" in content and "List" not in content.split("from typing import")[1].split("\n")[0]:
        old_typing = "from typing import Optional, Dict, Any"
        new_typing = "from typing import Optional, Dict, Any, List, tuple"
        content = content.replace(old_typing, new_typing)
        print("✓ Added missing typing imports")
    
    # Save updated file
    with open("enhanced_main.py", "w") as f:
        f.write(content)
    
    print("✓ Applied all enhanced tracking integration patches")
    return True

def create_management_script():
    """Create management script for enhanced tracking"""
    
    management_script = '''#!/usr/bin/env python3
"""
Enhanced Pipeline Management Script
Manage tickets, view statistics, and control reprocessing
"""

import json
import sys
from datetime import datetime
from enhanced_ticket_tracking import EnhancedTicketTracker

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_pipeline.py <command>")
        print("Commands:")
        print("  status        - Show pipeline statistics")
        print("  failed        - Show failed tickets")
        print("  retry <key>   - Mark ticket for retry")
        print("  clear <key>   - Clear ticket from tracking")
        print("  reset         - Reset all tracking data")
        return
    
    command = sys.argv[1]
    tracker = EnhancedTicketTracker()
    
    if command == "status":
        stats = tracker.get_processing_statistics()
        print("Pipeline Statistics:")
        print(f"  Total tickets: {stats['total_tickets']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Processing: {stats['processing']}")
        print(f"  Retry candidates: {stats['retry_candidates']}")
        print(f"  By language: {stats['by_language']}")
        print(f"  By domain: {stats['by_domain']}")
    
    elif command == "failed":
        failed = tracker.get_failed_tickets()
        print(f"Failed tickets ready for retry ({len(failed)}):")
        for ticket in failed:
            print(f"  {ticket.ticket_key}: {ticket.summary}")
            print(f"    Attempts: {ticket.attempt_count}")
            print(f"    Last error: {ticket.last_error}")
            print()
    
    elif command == "retry" and len(sys.argv) > 2:
        ticket_key = sys.argv[2]
        if ticket_key in tracker.ticket_versions:
            version = tracker.ticket_versions[ticket_key]
            version.processing_status = version.processing_status.NEEDS_REPROCESSING
            tracker.save_ticket_data()
            print(f"Marked {ticket_key} for reprocessing")
        else:
            print(f"Ticket {ticket_key} not found")
    
    elif command == "clear" and len(sys.argv) > 2:
        ticket_key = sys.argv[2]
        if ticket_key in tracker.ticket_versions:
            del tracker.ticket_versions[ticket_key]
            tracker.save_ticket_data()
            print(f"Cleared {ticket_key} from tracking")
        else:
            print(f"Ticket {ticket_key} not found")
    
    elif command == "reset":
        confirm = input("Are you sure you want to reset all tracking data? (yes/no): ")
        if confirm.lower() == "yes":
            tracker.ticket_versions = {}
            tracker.save_ticket_data()
            print("All tracking data cleared")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
'''
    
    with open("manage_pipeline.py", "w") as f:
        f.write(management_script)
    
    print("✓ Created pipeline management script")

def create_testing_script():
    """Create testing script for enhanced tracking"""
    
    test_script = '''#!/usr/bin/env python3
"""
Test Enhanced Ticket Tracking
"""

import asyncio
from enhanced_ticket_tracking import EnhancedTicketTracker, SmartTicketProcessor

async def test_enhanced_tracking():
    print("Testing Enhanced Ticket Tracking...")
    
    # Test tracker initialization
    tracker = EnhancedTicketTracker("test_tracking.json")
    print("✓ Tracker initialized")
    
    # Test JQL generation
    jql = tracker.generate_enhanced_jql("TEST")
    print(f"✓ Generated JQL: {jql[:100]}...")
    
    # Test statistics
    stats = tracker.get_processing_statistics()
    print(f"✓ Statistics: {stats}")
    
    print("Enhanced tracking tests completed!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_tracking())
'''
    
    with open("test_enhanced_tracking.py", "w") as f:
        f.write(test_script)
    
    print("✓ Created enhanced tracking test script")

if __name__ == "__main__":
    print("Enhanced Ticket Tracking Integration")
    print("=" * 50)
    
    # Check if enhanced_ticket_tracking.py exists
    if not os.path.exists("enhanced_ticket_tracking.py"):
        print("❌ enhanced_ticket_tracking.py not found!")
        print("Please copy the enhanced_ticket_tracking.py file first.")
        exit(1)
    
    # Apply integration
    if apply_enhanced_tracking_integration():
        print("✓ Integration applied successfully!")
        
        # Create management tools
        create_management_script()
        create_testing_script()
        
        print("\n" + "=" * 50)
        print("INTEGRATION COMPLETE")
        print("=" * 50)
        print("\nThe enhanced pipeline now supports:")
        print("• Processing updated Jira tickets")
        print("• Automatic retry of failed tickets")
        print("• Reprocessing based on labels/comments")
        print("• Smart content change detection")
        print("• Comprehensive ticket versioning")
        print("• Enhanced status reporting")
        print("\nNext steps:")
        print("1. Test: python test_enhanced_tracking.py")
        print("2. Start: python enhanced_main.py")
        print("3. Manage: python manage_pipeline.py status")
        print("\nManagement commands:")
        print("• python manage_pipeline.py status")
        print("• python manage_pipeline.py failed") 
        print("• python manage_pipeline.py retry TICKET-123")
        
    else:
        print("❌ Integration failed!")