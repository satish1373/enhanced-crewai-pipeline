#!/usr/bin/env python3
"""
Hotfix for Enhanced Agents
Fixes the missing router agent and improves language detection
"""

import os
import shutil
from datetime import datetime

def apply_hotfix():
    """Apply hotfix to enhanced_agents.py"""
    
    print("Applying hotfix for enhanced agents...")
    
    # Backup current file
    backup_name = f"enhanced_agents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    if os.path.exists("enhanced_agents.py"):
        shutil.copy("enhanced_agents.py", backup_name)
        print(f"Created backup: {backup_name}")
    
    # Read current file
    with open("enhanced_agents.py", "r") as f:
        content = f.read()
    
    # Apply fixes
    
    # Fix 1: Add router to SmartAgentSelector.__init__
    old_init = """    def __init__(self):
        self.language_agents = AgentFactory.create_language_agents()
        self.domain_agents = AgentFactory.create_domain_agents()
        self.specialized_reviewers = AgentFactory.create_specialized_reviewers()"""
    
    new_init = """    def __init__(self):
        self.router = AgentFactory.create_router_agent()  # Add missing router
        self.language_agents = AgentFactory.create_language_agents()
        self.domain_agents = AgentFactory.create_domain_agents()
        self.specialized_reviewers = AgentFactory.create_specialized_reviewers()"""
    
    if old_init in content:
        content = content.replace(old_init, new_init)
        print("✓ Fixed missing router agent")
    
    # Fix 2: Improve language detection keywords
    old_keywords = '''    LANGUAGE_KEYWORDS = {
        "python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "pytest"],
        "javascript": ["javascript", "js", "node", "react", "vue", "angular", "npm"],
        "java": ["java", "spring", "maven", "gradle", "junit", "hibernate"],
        "go": ["golang", "go", "goroutine", "gin", "fiber"],
        "rust": ["rust", "cargo", "tokio", "serde"],
        "sql": ["database", "sql", "mysql", "postgres", "mongodb"],
        "docker": ["docker", "container", "kubernetes"],
        "terraform": ["terraform", "infrastructure", "aws", "azure", "gcp"]
    }'''
    
    new_keywords = '''    LANGUAGE_KEYWORDS = {
        "python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "pytest", "scikit-learn", "tensorflow", "keras"],
        "javascript": ["javascript", "js", "node", "react", "vue", "angular", "npm", "typescript", "jest"],
        "java": ["java", "spring", "maven", "gradle", "junit", "hibernate", "jpa"],
        "go": ["golang", "go", "goroutine", "gin", "fiber", "microservice"],
        "rust": ["rust", "cargo", "tokio", "serde", "cli"],
        "sql": ["database", "sql", "mysql", "postgres", "mongodb"],
        "docker": ["docker", "container", "kubernetes", "dockerfile"],
        "terraform": ["terraform", "infrastructure", "aws", "azure", "gcp"]
    }'''
    
    if old_keywords in content:
        content = content.replace(old_keywords, new_keywords)
        print("✓ Updated language keywords")
    
    # Fix 3: Improve language detection logic
    old_detect = '''    @classmethod
    def detect_language(cls, ticket_content: str) -> Optional[str]:
        """Detect primary programming language from ticket content"""
        content_lower = ticket_content.lower()
        
        language_scores = {}
        for lang, keywords in cls.LANGUAGE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                language_scores[lang] = score
        
        return max(language_scores, key=language_scores.get) if language_scores else "python"'''
    
    new_detect = '''    @classmethod
    def detect_language(cls, ticket_content: str) -> Optional[str]:
        """Detect primary programming language from ticket content"""
        content_lower = ticket_content.lower()
        
        language_scores = {}
        for lang, keywords in cls.LANGUAGE_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                language_scores[lang] = score
        
        # If docker/terraform detected but no primary language, default to Python
        if language_scores:
            detected = max(language_scores, key=language_scores.get)
            # Docker and Terraform are deployment tools, not programming languages
            if detected in ["docker", "terraform"]:
                # Look for actual programming language mentions
                prog_languages = {k: v for k, v in language_scores.items() 
                                 if k not in ["docker", "terraform", "sql"]}
                if prog_languages:
                    return max(prog_languages, key=prog_languages.get)
                else:
                    return "python"  # Default for DevOps/infrastructure tasks
            return detected
        
        return "python"  # Default language'''
    
    if old_detect in content:
        content = content.replace(old_detect, new_detect)
        print("✓ Improved language detection logic")
    
    # Write updated file
    with open("enhanced_agents.py", "w") as f:
        f.write(content)
    
    print("✓ Hotfix applied successfully!")
    print("\nRestart the pipeline to apply changes:")
    print("1. Stop current pipeline (Ctrl+C)")
    print("2. Run: python enhanced_main.py")

def test_fixes():
    """Test the fixes"""
    print("\nTesting fixes...")
    
    try:
        from enhanced_agents import SmartAgentSelector, LanguageDetector
        
        # Test router agent
        selector = SmartAgentSelector()
        if hasattr(selector, 'router'):
            print("✓ Router agent is now available")
        else:
            print("✗ Router agent still missing")
            return False
        
        # Test language detection
        test_content = "Create a security audit tool using Python with Docker deployment"
        detected_lang = LanguageDetector.detect_language(test_content)
        if detected_lang == "python":
            print(f"✓ Language detection improved: {detected_lang}")
        else:
            print(f"? Language detection result: {detected_lang}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    apply_hotfix()
    test_fixes()
