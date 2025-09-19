#!/usr/bin/env python3
"""
Enhanced CrewAI Multi-Language Automation Pipeline
Integrated with comprehensive ticket tracking system
"""

import os
import time
import json
from datetime import datetime

# Fix the import error - remove the problematic import
try:
    from jira import JIRA
    print("✅ JIRA imported successfully")
except ImportError:
    print("❌ JIRA not available - install with: pip install jira")
    exit(1)

try:
    from enhanced_ticket_tracking import EnhancedTicketTracker, SmartTicketProcessor
    print("✅ Enhanced tracking imported successfully")
except ImportError as e:
    print(f"❌ Enhanced tracking import error: {e}")
    print("Make sure enhanced_ticket_tracking.py is in the same directory")
    exit(1)

# -------------------- Configuration --------------------
JIRA_HOST = os.getenv("JIRA_HOST")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "TEST")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))

# -------------------- Initialize Enhanced Tracking --------------------
try:
    if JIRA_HOST and JIRA_EMAIL and JIRA_API_TOKEN:
        # Fix JIRA_HOST URL if it's missing the scheme
        jira_url = JIRA_HOST
        if not jira_url.startswith(('http://', 'https://')):
            jira_url = f"https://{jira_url}"
        
        print(f"🔗 Connecting to JIRA: {jira_url}")
        jira = JIRA(server=jira_url, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        print("✅ JIRA connection established")
    else:
        print("⚠️  JIRA credentials not set - running in demo mode")
        jira = None
    
    enhanced_tracker = EnhancedTicketTracker(JIRA_PROJECT_KEY)
    smart_processor = SmartTicketProcessor(enhanced_tracker, jira, None)  # Pass required arguments
    print("✅ Enhanced tracking initialized")
    
except Exception as e:
    print(f"❌ Initialization error: {e}")
    exit(1)

# -------------------- Core Functions --------------------

def get_pending_tickets():
    """Enhanced ticket fetching with comprehensive tracking"""
    if not jira:
        print("⚠️  No JIRA connection - returning demo tickets")
        return []
    
    try:
        # Use enhanced JQL query that catches more scenarios
        jql_query = enhanced_tracker.generate_jql()
        print(f"🔍 Using enhanced JQL: {jql_query}")
        
        tickets = jira.search_issues(jql_query, maxResults=50)
        
        # Filter tickets using smart processor
        pending_tickets = []
        for ticket in tickets:
            if smart_processor.should_process_ticket(ticket.key, ticket.raw):
                pending_tickets.append(ticket)
                print(f"✅ Queued for processing: {ticket.key}")
            else:
                print(f"⏭️  Skipping: {ticket.key} (already processed or not ready)")
        
        return pending_tickets
        
    except Exception as e:
        print(f"❌ Error fetching tickets: {e}")
        return []

def detect_primary_language(text):
    """Detect the primary programming language from ticket content"""
    text_lower = text.lower()
    
    # Language indicators with weights
    language_indicators = {
        'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', '.py', 'pip install'],
        'javascript': ['javascript', 'js', 'react', 'node.js', 'npm', 'typescript', '.js', '.ts'],
        'java': ['java', 'spring', 'spring boot', 'maven', 'gradle', '.java', 'jvm'],
        'php': ['php', 'laravel', 'symfony', 'composer', '.php'],
        'csharp': ['c#', 'csharp', '.net', 'asp.net', 'visual studio', '.cs'],
        'ruby': ['ruby', 'rails', 'gem install', '.rb'],
        'go': ['golang', 'go lang', '.go'],
        'rust': ['rust', 'cargo', '.rs'],
        'swift': ['swift', 'ios', 'xcode', '.swift']
    }
    
    scores = {}
    for language, indicators in language_indicators.items():
        score = sum(1 for indicator in indicators if indicator in text_lower)
        if score > 0:
            scores[language] = score
    
    return max(scores.items(), key=lambda x: x[1])[0] if scores else 'general'

def process_single_ticket(ticket):
    """Enhanced single ticket processing with tracking"""
    ticket_key = ticket.key
    
    try:
        # Mark as processing started
        smart_processor.mark_processing_start(ticket_key)
        
        # Extract ticket information
        title = ticket.fields.summary
        description = ticket.fields.description or "No description provided"
        
        # Detect language and domain
        detected_info = smart_processor.detect_language_and_domain(
            title + " " + description
        )
        
        print(f"🔄 Processing {ticket_key}: {title}")
        print(f"📊 Detected: {detected_info['language']} | {detected_info['domain']}")
        
        # Simulate processing (replace with your CrewAI logic)
        print(f"🤖 Processing with {detected_info['language']} specialist...")
        time.sleep(2)  # Simulate work
        
        # Simulate successful result
        result = f"Solution for {title} using {detected_info['language']}"
        
        # Mark as successfully completed
        smart_processor.mark_processing_complete(
            ticket_key, 
            result,
            detected_info
        )
        
        # Add comment to Jira ticket
        if jira:
            comment = f"""
✅ **Automated Processing Complete**

**Language Detected:** {detected_info['language']}
**Domain:** {detected_info['domain']}

**Solution:**
{result}

---
*Processed by Enhanced Pipeline*
            """
            
            jira.add_comment(ticket, comment)
            print(f"✅ Added comment to {ticket_key}")
        
        return {"success": True, "ticket": ticket_key, "result": result}
        
    except Exception as e:
        # Mark as failed (will be retried later)
        smart_processor.mark_processing_failed(
            ticket_key, 
            str(e),
            detected_info if 'detected_info' in locals() else {}
        )
        print(f"❌ Error processing {ticket_key}: {e}")
        return {"success": False, "ticket": ticket_key, "error": str(e)}

def main_processing_loop():
    """Enhanced main loop with comprehensive statistics"""
    cycle_count = 0
    
    print("🚀 Starting Enhanced Pipeline with Comprehensive Tracking")
    print("=" * 70)
    
    while True:
        try:
            cycle_count += 1
            print(f"\n🔄 Processing Cycle #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get pending tickets using enhanced detection
            pending_tickets = get_pending_tickets()
            
            if not pending_tickets:
                print("✅ No tickets to process")
            else:
                print(f"📋 Found {len(pending_tickets)} tickets to process")
                
                # Process each ticket
                results = []
                for ticket in pending_tickets:
                    result = process_single_ticket(ticket)
                    results.append(result)
                    time.sleep(2)  # Prevent API rate limiting
                
                # Generate processing summary
                successful = [r for r in results if r['success']]
                failed = [r for r in results if not r['success']]
                
                print(f"\n📊 Cycle Results:")
                print(f"   ✅ Successful: {len(successful)}")
                print(f"   ❌ Failed: {len(failed)}")
                
                if failed:
                    print("   Failed tickets:")
                    for f in failed:
                        print(f"      - {f['ticket']}: {f['error']}")
            
            # Get and display comprehensive statistics
            stats = enhanced_tracker.get_statistics()
            print(f"\n📈 Pipeline Statistics:")
            print(f"   Total tracked: {stats['total_tickets']}")
            print(f"   Completed: {stats['completed']}")
            print(f"   Failed: {stats['failed']}")
            print(f"   Retry candidates: {stats['retry_candidates']}")
            
            if stats['by_language']:
                print(f"   By language: {dict(stats['by_language'])}")
            
            # Check for retry candidates
            if stats['retry_candidates'] > 0:
                print(f"⚠️  {stats['retry_candidates']} tickets ready for retry")
            
            print(f"\n⏳ Waiting {POLL_INTERVAL} seconds before next cycle...")
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 Pipeline stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(30)  # Wait before retrying

def show_pipeline_status():
    """Show current pipeline status"""
    stats = enhanced_tracker.get_statistics()
    print("\n📊 Enhanced Pipeline Status:")
    print(f"   Total tickets tracked: {stats['total_tickets']}")
    print(f"   Successfully completed: {stats['completed']}")
    print(f"   Failed (will retry): {stats['failed']}")
    print(f"   Currently processing: {stats['processing']}")
    print(f"   Ready for retry: {stats['retry_candidates']}")
    
    if stats['by_language']:
        print("\n📈 Breakdown by Language:")
        for lang, count in stats['by_language'].items():
            print(f"   {lang}: {count}")
    
    if stats['by_domain']:
        print("\n🏷️  Breakdown by Domain:")
        for domain, count in stats['by_domain'].items():
            print(f"   {domain}: {count}")

def test_mode():
    """Run in test mode without JIRA"""
    print("🧪 Running in Test Mode")
    print("=" * 30)
    
    # Test enhanced tracking functionality
    print("\n🔧 Testing Enhanced Tracking:")
    
    # Test JQL generation
    jql = enhanced_tracker.generate_jql()
    print(f"✅ JQL: {jql}")
    
    # Test language detection
    test_text = "Create a Python Flask web application with JWT authentication"
    detected = smart_processor.detect_language_and_domain(test_text)
    print(f"✅ Language Detection: {detected}")
    
    # Test statistics
    stats = enhanced_tracker.get_statistics()
    print(f"✅ Statistics: {stats}")
    
    print("\n✅ Test mode complete!")

if __name__ == "__main__":
    if not jira:
        print("⚠️  No JIRA connection - running in test mode")
        test_mode()
    else:
        # Show initial status
        show_pipeline_status()
        
        # Start main processing loop
        main_processing_loop()