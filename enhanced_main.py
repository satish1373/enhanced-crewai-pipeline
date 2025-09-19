#!/usr/bin/env python3
"""
Enhanced CrewAI Multi-Language Automation Pipeline
Integrated with comprehensive ticket tracking system
"""

import os
import time
import json
from datetime import datetime
from code_storage_system import CodeStorageManager

code_storage = CodeStorageManager("generated_solutions")

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
    """Enhanced single ticket processing with comprehensive storage"""
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
        
        # Process with CrewAI (your existing logic)
        start_time = time.time()
        
        # Create appropriate task based on detected language
        language = detected_info['language'].lower()
        
        if language == 'python':
            agent = python_dev_agent
            task_description = f"""
            Develop a Python solution for: {title}
            
            Requirements: {description}
            
            Please provide:
            1. Complete Python code with proper structure
            2. Requirements.txt file
            3. Unit tests
            4. Documentation
            5. Usage examples
            """
        elif language == 'javascript':
            agent = js_dev_agent  
            task_description = f"""
            Develop a JavaScript/Node.js solution for: {title}
            
            Requirements: {description}
            
            Please provide:
            1. Complete JavaScript/TypeScript code
            2. Package.json configuration
            3. Test cases
            4. Documentation
            5. Usage examples
            """
        elif language == 'java':
            agent = java_dev_agent
            task_description = f"""
            Develop a Java solution for: {title}
            
            Requirements: {description}
            
            Please provide:
            1. Complete Java code with proper structure
            2. Maven/Gradle configuration
            3. JUnit tests
            4. Documentation  
            5. Usage examples
            """
        else:
            agent = router_agent
            task_description = f"""
            Analyze and provide a solution for: {title}
            
            Requirements: {description}
            
            Please:
            1. Determine the best technology approach
            2. Create a complete solution
            3. Include tests and documentation
            4. Provide implementation guidance
            """
        
        # Create and execute task
        task = Task(
            description=task_description,
            agent=agent,
            expected_output="Complete solution with code, tests, and documentation"
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[agent, qa_agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        processing_time = time.time() - start_time
        
        # ENHANCED: Store the complete solution with organized file structure
        solution_data = {
            'content': str(result),
            'language': detected_info['language'],
            'domain': detected_info['domain'],
            'title': title,
            'description': description,
            'agent': agent.role,
            'processing_time': processing_time,
            'tags': [
                detected_info['language'].lower(), 
                detected_info['domain'].lower().replace(' ', '_'), 
                'ai-generated',
                'crewai-solution'
            ],
            'complexity': determine_complexity(title, description),
            'ticket_priority': getattr(ticket.fields, 'priority', {}).get('name', 'Medium') if hasattr(ticket.fields, 'priority') else 'Medium'
        }
        
        # Store solution with organized file structure
        print("💾 Storing solution...")
        storage_result = code_storage.store_solution(ticket_key, solution_data)
        
        # Mark as successfully completed
        smart_processor.mark_processing_complete(
            ticket_key, 
            str(result),
            detected_info
        )
        
        # Enhanced JIRA comment with storage info and file links
        comment = f"""
✅ **Automated Processing Complete**

**Solution Details:**
- **Language Detected:** {detected_info['language']}
- **Domain:** {detected_info['domain']}
- **Processing Agent:** {agent.role}
- **Processing Time:** {processing_time:.2f}s

**📁 Solution Storage:**
- **Solution ID:** `{storage_result['solution_id']}`
- **Files Generated:** {len(storage_result['files'])}
- **Storage Path:** `{storage_result['storage_path']}`

**📂 Generated Files:**
"""
        
        # Add file list to comment
        for file_type, file_path in storage_result['files'].items():
            filename = os.path.basename(file_path)
            comment += f"- **{filename}** - {get_file_type_description(filename)}\n"
        
        comment += f"""

**🔍 Quick Access Commands:**
```bash
# View all files
ls -la "{storage_result['storage_path']}"

# View main solution
cat "{storage_result['storage_path']}/solution.*"

# View README
cat "{storage_result['storage_path']}/README.md"
```

**🔎 Search & Reuse:**
- Search similar solutions: `python manage_solutions.py search --language {detected_info['language']}`
- View solution details: `python manage_solutions.py get {storage_result['solution_id']}`

**Solution Preview:**
```
{str(result)[:800]}{'...' if len(str(result)) > 800 else ''}
```

---
*Processed by Enhanced CrewAI Pipeline with Comprehensive Storage*
*Reusable components available in organized file structure*
        """
        
        jira.add_comment(ticket, comment)
        
        # Transition ticket to done (adjust status as needed)
        try:
            transitions = jira.transitions(ticket)
            done_transition = next((t for t in transitions if 'done' in t['name'].lower()), None)
            if done_transition:
                jira.transition_issue(ticket, done_transition['id'])
                print(f"✅ Transitioned {ticket_key} to Done")
        except Exception as e:
            print(f"⚠️  Could not transition {ticket_key}: {e}")
        
        print(f"✅ Solution stored with ID: {storage_result['solution_id']}")
        print(f"📁 Files created: {len(storage_result['files'])}")
        print(f"🔗 Access path: {storage_result['storage_path']}")
        
        return {
            "success": True, 
            "ticket": ticket_key, 
            "result": str(result),
            "storage": storage_result,
            "processing_time": processing_time
        }
        
    except Exception as e:
        # Mark as failed (will be retried later)
        smart_processor.mark_processing_failed(
            ticket_key, 
            str(e),
            detected_info if 'detected_info' in locals() else {}
        )
        print(f"❌ Error processing {ticket_key}: {e}")
        return {"success": False, "ticket": ticket_key, "error": str(e)}

def determine_complexity(title, description):
    """Determine solution complexity based on requirements"""
    text = (title + " " + description).lower()
    
    # High complexity indicators
    high_indicators = [
        'microservices', 'distributed', 'scalable', 'enterprise',
        'machine learning', 'ai', 'real-time', 'high-performance',
        'multi-tenant', 'blockchain', 'kubernetes'
    ]
    
    # Low complexity indicators
    low_indicators = [
        'simple', 'basic', 'small', 'quick', 'single',
        'utility', 'helper', 'convert', 'format'
    ]
    
    if any(indicator in text for indicator in high_indicators):
        return 'high'
    elif any(indicator in text for indicator in low_indicators):
        return 'low'
    else:
        return 'medium'

def get_file_type_description(filename):
    """Get human-readable description for file types"""
    descriptions = {
        'solution.py': 'Main Python implementation',
        'solution.js': 'Main JavaScript implementation', 
        'solution.java': 'Main Java implementation',
        'test_': 'Unit tests',
        'requirements.txt': 'Python dependencies',
        'package.json': 'Node.js dependencies and configuration',
        'pom.xml': 'Maven project configuration',
        'Dockerfile': 'Docker containerization setup',
        'README.md': 'Documentation and usage guide',
        'metadata.json': 'Solution metadata and analytics',
        '.env.example': 'Environment variables template',
        'config.': 'Configuration file'
    }
    
    for pattern, description in descriptions.items():
        if pattern in filename:
            return description
    
    # Default descriptions by extension
    ext = os.path.splitext(filename)[1].lower()
    ext_descriptions = {
        '.py': 'Python code',
        '.js': 'JavaScript code',
        '.java': 'Java code', 
        '.html': 'HTML template',
        '.css': 'Stylesheet',
        '.sql': 'Database script',
        '.json': 'Configuration data',
        '.yaml': 'Configuration file',
        '.md': 'Documentation'
    }
    
    return ext_descriptions.get(ext, 'Generated file')

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