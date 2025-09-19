#!/usr/bin/env python3
"""
Enhanced Ticket Tracking System
Comprehensive ticket processing with smart retry logic, language detection, and statistics
"""

import os
import json
import time
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta


class EnhancedTicketTracker:
    """Enhanced ticket tracker with comprehensive detection and retry logic"""
    
    def __init__(self, project_key: str):
        """Initialize the enhanced ticket tracker"""
        self.project_key = project_key
        self.history_file = "ticket_tracking.json"
        self.config = {
            'base_statuses': ['To Do'],
            'max_retries': 3,
            'retry_delays': [300, 900, 3600, 7200],  # 5min, 15min, 1hr, 2hr
            'reprocess_labels': ['reprocess', 'update'],
            'reprocess_comments': ['reprocess', 'retry'],
            'lookback_days': 7
        }
    
    def generate_jql(self, include_recent_updates: bool = True, 
                    include_retry_candidates: bool = True) -> str:
        """Generate comprehensive JQL query for ticket detection"""
        
        base_statuses = self.config.get('base_statuses', ['To Do'])
        
        # Create status condition without f-string issues
        status_list = ','.join('"' + status + '"' for status in base_statuses)
        status_condition = f"status IN ({status_list})"
        
        conditions = [f"project = {self.project_key}"]
        
        # Main status condition
        main_conditions = [status_condition]
        
        if include_recent_updates:
            # Include recently updated tickets with reprocess labels/comments
            lookback_days = self.config.get('lookback_days', 7)
            recent_conditions = [
                f"updated >= -{lookback_days}d AND (labels = 'reprocess' OR labels = 'update')",
                f"updated >= -{lookback_days}d AND (comment ~ 'reprocess' OR comment ~ 'retry')"
            ]
            main_conditions.extend(recent_conditions)
        
        # Combine all conditions
        combined_conditions = f"({' OR '.join(main_conditions)})"
        conditions.append(combined_conditions)
        
        jql_query = f"{' AND '.join(conditions)} ORDER BY updated DESC"
        
        return jql_query
    
    def _load_history(self) -> Dict[str, Any]:
        """Load ticket processing history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Warning: Could not load history file: {e}")
            return {}
    
    def _save_history(self, history: Dict[str, Any]) -> None:
        """Save ticket processing history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history file: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics"""
        history = self._load_history()
        
        stats = {
            'total_tickets': len(history),
            'completed': 0,
            'failed': 0,
            'processing': 0,
            'needs_reprocessing': 0,
            'by_language': {},
            'by_domain': {},
            'retry_candidates': 0
        }
        
        for ticket_key, ticket_data in history.items():
            status = ticket_data.get('status', 'unknown')
            
            if status == 'completed':
                stats['completed'] += 1
            elif status == 'failed':
                stats['failed'] += 1
                # Check if ready for retry
                if self._is_ready_for_retry(ticket_data):
                    stats['retry_candidates'] += 1
            elif status == 'processing':
                stats['processing'] += 1
            elif status == 'needs_reprocessing':
                stats['needs_reprocessing'] += 1
            
            # Count by language and domain
            metadata = ticket_data.get('metadata', {})
            language = metadata.get('language', 'unknown')
            domain = metadata.get('domain', 'unknown')
            
            stats['by_language'][language] = stats['by_language'].get(language, 0) + 1
            stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
        
        return stats
    
    def _is_ready_for_retry(self, ticket_data: Dict) -> bool:
        """Check if a failed ticket is ready for retry"""
        if ticket_data.get('status') != 'failed':
            return False
        
        retry_count = ticket_data.get('retry_count', 0)
        max_retries = self.config.get('max_retries', 3)
        
        if retry_count >= max_retries:
            return False
        
        last_attempt = ticket_data.get('last_attempt')
        if not last_attempt:
            return True
        
        # Calculate retry delay
        retry_delays = self.config.get('retry_delays', [300, 900, 3600, 7200])
        delay_index = min(retry_count, len(retry_delays) - 1)
        delay_seconds = retry_delays[delay_index]
        
        time_since_last = time.time() - last_attempt
        return time_since_last >= delay_seconds
    
    def get_retry_candidates(self) -> List[Dict[str, Any]]:
        """Get list of tickets ready for retry"""
        history = self._load_history()
        candidates = []
        
        for ticket_key, ticket_data in history.items():
            if self._is_ready_for_retry(ticket_data):
                candidates.append({
                    'ticket_key': ticket_key,
                    'retry_count': ticket_data.get('retry_count', 0),
                    'last_error': ticket_data.get('last_error', 'Unknown error'),
                    'last_attempt': ticket_data.get('last_attempt')
                })
        
        return candidates


class SmartTicketProcessor:
    """Smart ticket processor with language detection and tracking"""
    
    def __init__(self, ticket_tracker: EnhancedTicketTracker, jira_client=None, pipeline_processor=None):
        """Initialize the smart processor"""
        self.ticket_tracker = ticket_tracker
        self.jira_client = jira_client
        self.pipeline_processor = pipeline_processor
        self.processing_file = "processing_history.json"
        
        # Language detection patterns
        self.language_patterns = {
            'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', '.py', 'pip install', 'pytest'],
            'javascript': ['javascript', 'js', 'react', 'node.js', 'npm', 'typescript', '.js', '.ts', 'yarn'],
            'java': ['java', 'spring', 'spring boot', 'maven', 'gradle', '.java', 'jvm', 'junit'],
            'php': ['php', 'laravel', 'symfony', 'composer', '.php', 'phpunit'],
            'csharp': ['c#', 'csharp', '.net', 'asp.net', 'visual studio', '.cs', 'nuget'],
            'ruby': ['ruby', 'rails', 'gem install', '.rb', 'bundler'],
            'go': ['golang', 'go lang', '.go', 'go mod'],
            'rust': ['rust', 'cargo', '.rs', 'rustc'],
            'swift': ['swift', 'ios', 'xcode', '.swift', 'cocoapods'],
            'kotlin': ['kotlin', 'android', '.kt', 'gradle'],
            'scala': ['scala', '.scala', 'sbt'],
            'r': ['r lang', '.r', 'rstudio', 'cran'],
            'sql': ['sql', 'mysql', 'postgresql', 'sqlite', 'database']
        }
        
        # Domain detection patterns
        self.domain_patterns = {
            'web_development': ['web', 'website', 'frontend', 'backend', 'api', 'rest', 'http'],
            'mobile_development': ['mobile', 'ios', 'android', 'react native', 'flutter'],
            'data_science': ['data', 'analytics', 'machine learning', 'ml', 'ai', 'statistics'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'ci/cd', 'deployment'],
            'testing': ['test', 'testing', 'qa', 'unit test', 'integration test', 'automation'],
            'security': ['security', 'auth', 'authentication', 'encryption', 'vulnerability'],
            'database': ['database', 'db', 'sql', 'nosql', 'mongodb', 'redis'],
            'ui_ux': ['ui', 'ux', 'design', 'interface', 'user experience'],
            'game_development': ['game', 'unity', 'unreal', 'gamedev'],
            'blockchain': ['blockchain', 'crypto', 'smart contract', 'web3']
        }
    
    def should_process_ticket(self, ticket_key: str, ticket_data: Dict) -> bool:
        """Determine if a ticket should be processed"""
        history = self._load_processing_history()
        
        if ticket_key not in history:
            # New ticket - should process
            return True
        
        ticket_history = history[ticket_key]
        
        # Check if ticket is already completed
        if ticket_history.get('status') == 'completed':
            # Check if content has changed
            current_hash = self._calculate_content_hash(ticket_data)
            stored_hash = ticket_history.get('content_hash')
            
            if current_hash != stored_hash:
                # Content changed - mark for reprocessing
                self._mark_for_reprocessing(ticket_key, "Content changed")
                return True
            return False
        
        # Check if currently processing
        if ticket_history.get('status') == 'processing':
            # Check if processing has timed out (over 1 hour)
            last_update = ticket_history.get('last_update', 0)
            if time.time() - last_update > 3600:  # 1 hour timeout
                return True
            return False
        
        # Check if failed and ready for retry
        if ticket_history.get('status') == 'failed':
            return self.ticket_tracker._is_ready_for_retry(ticket_history)
        
        # Check if marked for reprocessing
        if ticket_history.get('status') == 'needs_reprocessing':
            return True
        
        return True
    
    def detect_language_and_domain(self, text: str) -> Dict[str, str]:
        """Detect primary language and domain from text content"""
        text_lower = text.lower()
        
        # Detect language
        language_scores = {}
        for language, patterns in self.language_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > 0:
                language_scores[language] = score
        
        detected_language = max(language_scores.items(), key=lambda x: x[1])[0] if language_scores else 'general'
        
        # Detect domain
        domain_scores = {}
        for domain, patterns in self.domain_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            if score > 0:
                domain_scores[domain] = score
        
        detected_domain = max(domain_scores.items(), key=lambda x: x[1])[0] if domain_scores else 'general'
        
        return {
            'language': detected_language,
            'domain': detected_domain,
            'confidence': {
                'language': language_scores.get(detected_language, 0),
                'domain': domain_scores.get(detected_domain, 0)
            }
        }
    
    def mark_processing_start(self, ticket_key: str) -> None:
        """Mark ticket as processing started"""
        history = self._load_processing_history()
        
        if ticket_key not in history:
            history[ticket_key] = {}
        
        history[ticket_key].update({
            'status': 'processing',
            'start_time': time.time(),
            'last_update': time.time(),
            'attempt_count': history[ticket_key].get('attempt_count', 0) + 1
        })
        
        self._save_processing_history(history)
    
    def mark_processing_complete(self, ticket_key: str, result: str, metadata: Dict) -> None:
        """Mark ticket as successfully completed"""
        history = self._load_processing_history()
        
        if ticket_key not in history:
            history[ticket_key] = {}
        
        history[ticket_key].update({
            'status': 'completed',
            'completion_time': time.time(),
            'last_update': time.time(),
            'result': result[:1000],  # Truncate long results
            'metadata': metadata,
            'retry_count': 0  # Reset retry count on success
        })
        
        self._save_processing_history(history)
    
    def mark_processing_failed(self, ticket_key: str, error: str, metadata: Dict) -> None:
        """Mark ticket as failed"""
        history = self._load_processing_history()
        
        if ticket_key not in history:
            history[ticket_key] = {}
        
        retry_count = history[ticket_key].get('retry_count', 0) + 1
        
        history[ticket_key].update({
            'status': 'failed',
            'failure_time': time.time(),
            'last_update': time.time(),
            'last_attempt': time.time(),
            'last_error': error[:500],  # Truncate long errors
            'retry_count': retry_count,
            'metadata': metadata
        })
        
        self._save_processing_history(history)
    
    def clear_ticket_history(self, ticket_key: str) -> None:
        """Clear processing history for a specific ticket"""
        history = self._load_processing_history()
        if ticket_key in history:
            del history[ticket_key]
            self._save_processing_history(history)
    
    def _load_processing_history(self) -> Dict[str, Any]:
        """Load processing history from file"""
        try:
            if os.path.exists(self.processing_file):
                with open(self.processing_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Warning: Could not load processing history: {e}")
            return {}
    
    def _save_processing_history(self, history: Dict[str, Any]) -> None:
        """Save processing history to file"""
        try:
            with open(self.processing_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save processing history: {e}")
    
    def _calculate_content_hash(self, ticket_data: Dict) -> str:
        """Calculate hash of ticket content for change detection"""
        content = str(ticket_data.get('fields', {}).get('summary', '')) + \
                 str(ticket_data.get('fields', {}).get('description', ''))
        return hashlib.md5(content.encode()).hexdigest()
    
    def _mark_for_reprocessing(self, ticket_key: str, reason: str) -> None:
        """Mark ticket for reprocessing"""
        history = self._load_processing_history()
        
        if ticket_key not in history:
            history[ticket_key] = {}
        
        history[ticket_key].update({
            'status': 'needs_reprocessing',
            'reprocess_reason': reason,
            'last_update': time.time()
        })
        
        self._save_processing_history(history)


class PipelineStatistics:
    """Pipeline statistics and reporting"""
    
    def __init__(self, tracker: EnhancedTicketTracker, processor: SmartTicketProcessor):
        self.tracker = tracker
        self.processor = processor
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive pipeline report"""
        stats = self.tracker.get_statistics()
        retry_candidates = self.tracker.get_retry_candidates()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': stats,
            'retry_candidates': len(retry_candidates),
            'retry_details': retry_candidates[:5],  # First 5 candidates
            'health_status': self._calculate_health_status(stats),
            'recommendations': self._generate_recommendations(stats)
        }
        
        return report
    
    def _calculate_health_status(self, stats: Dict) -> str:
        """Calculate overall pipeline health"""
        total = stats['total_tickets']
        if total == 0:
            return 'healthy'
        
        success_rate = stats['completed'] / total
        failed_rate = stats['failed'] / total
        
        if success_rate >= 0.9:
            return 'healthy'
        elif success_rate >= 0.7:
            return 'warning'
        else:
            return 'critical'
    
    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """Generate recommendations based on statistics"""
        recommendations = []
        
        if stats['retry_candidates'] > 5:
            recommendations.append("High number of retry candidates - consider investigating common failure patterns")
        
        if stats['failed'] > stats['completed']:
            recommendations.append("Failure rate is high - review error logs and processing logic")
        
        # Language-specific recommendations
        languages = stats.get('by_language', {})
        if languages:
            most_common = max(languages.items(), key=lambda x: x[1])
            recommendations.append(f"Most common language: {most_common[0]} ({most_common[1]} tickets)")
        
        return recommendations


# Factory function for easy initialization
def create_enhanced_tracking_system(project_key: str, jira_client=None) -> Tuple[EnhancedTicketTracker, SmartTicketProcessor]:
    """Create and configure the enhanced tracking system"""
    tracker = EnhancedTicketTracker(project_key)
    processor = SmartTicketProcessor(tracker, jira_client)
    
    return tracker, processor


# Example usage and testing
if __name__ == "__main__":
    print("Testing Enhanced Ticket Tracking System...")
    
    # Create instances
    tracker = EnhancedTicketTracker("TEST")
    processor = SmartTicketProcessor(tracker)
    
    print(f"✓ Tracker initialized for project: {tracker.project_key}")
    
    # Test JQL generation
    jql = tracker.generate_jql()
    print(f"✓ Generated JQL: {jql}")
    
    # Test language detection
    test_text = "Create a Python Django web application with user authentication"
    detected = processor.detect_language_and_domain(test_text)
    print(f"✓ Language detection: {detected}")
    
    # Test statistics
    stats = tracker.get_statistics()
    print(f"✓ Statistics: {stats}")
    
    print("Enhanced tracking tests completed!")