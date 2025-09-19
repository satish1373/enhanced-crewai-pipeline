#!/usr/bin/env python3
"""
Fix Task Agent Assignment
The CrewAI Task objects need to have agents properly assigned
"""

import os
import shutil
from datetime import datetime

def fix_task_agent_assignments():
    """Fix the task agent assignment issue in enhanced_main.py"""
    
    print("Fixing task agent assignments...")
    
    # Backup current file
    backup_name = f"enhanced_main_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    if os.path.exists("enhanced_main.py"):
        shutil.copy("enhanced_main.py", backup_name)
        print(f"Created backup: {backup_name}")
    
    # Read current file
    with open("enhanced_main.py", "r") as f:
        content = f.read()
    
    # Fix 1: Update create_router_task to assign agent
    old_router_task = '''    def create_router_task(self, content: str, language: str, domain: str) -> Task:
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
        )'''
    
    new_router_task = '''    def create_router_task(self, content: str, language: str, domain: str, agent) -> Task:
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
            agent=agent
        )'''
    
    if old_router_task in content:
        content = content.replace(old_router_task, new_router_task)
        print("✓ Fixed router task agent assignment")
    
    # Fix 2: Update create_coding_task to assign agent
    old_coding_task = '''    def create_coding_task(self, description: str, router_analysis: str, language: str, domain: str) -> Task:
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
        )'''
    
    new_coding_task = '''    def create_coding_task(self, description: str, router_analysis: str, language: str, domain: str, agent) -> Task:
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
            agent=agent
        )'''
    
    if old_coding_task in content:
        content = content.replace(old_coding_task, new_coding_task)
        print("✓ Fixed coding task agent assignment")
    
    # Fix 3: Update create_review_task to assign agent
    old_review_task = '''    def create_review_task(self, code: str, router_analysis: str, language: str, attempt: int) -> Task:
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
        )'''
    
    new_review_task = '''    def create_review_task(self, code: str, router_analysis: str, language: str, attempt: int, agent) -> Task:
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
            agent=agent
        )'''
    
    if old_review_task in content:
        content = content.replace(old_review_task, new_review_task)
        print("✓ Fixed review task agent assignment")
    
    # Fix 4: Update the task creation calls to pass agents
    old_router_call = '''            router_result = await self.execute_agent_with_monitoring(
                "router", 
                self.create_router_task(full_content, language, domain),
                selected_agents.get("router", self.agent_selector.router)
            )'''
    
    new_router_call = '''            router_result = await self.execute_agent_with_monitoring(
                "router", 
                self.create_router_task(full_content, language, domain, self.agent_selector.router),
                self.agent_selector.router
            )'''
    
    if old_router_call in content:
        content = content.replace(old_router_call, new_router_call)
        print("✓ Fixed router task call")
    
    old_coder_call = '''            coder_result = await self.execute_agent_with_monitoring(
                "coder",
                self.create_coding_task(task_description, router_result, language, domain),
                selected_agents["coder"]
            )'''
    
    new_coder_call = '''            coder_result = await self.execute_agent_with_monitoring(
                "coder",
                self.create_coding_task(task_description, router_result, language, domain, selected_agents["coder"]),
                selected_agents["coder"]
            )'''
    
    if old_coder_call in content:
        content = content.replace(old_coder_call, new_coder_call)
        print("✓ Fixed coder task call")
    
    old_review_call = '''                review_result = await self.execute_agent_with_monitoring(
                    "reviewer",
                    self.create_review_task(original_code, router_result, language, attempt),
                    selected_agents.get("code_reviewer", selected_agents["coder"])
                )'''
    
    new_review_call = '''                review_result = await self.execute_agent_with_monitoring(
                    "reviewer",
                    self.create_review_task(original_code, router_result, language, attempt, selected_agents.get("code_reviewer", selected_agents["coder"])),
                    selected_agents.get("code_reviewer", selected_agents["coder"])
                )'''
    
    if old_review_call in content:
        content = content.replace(old_review_call, new_review_call)
        print("✓ Fixed review task call")
    
    # Fix 5: Update run_single_qa_check to assign agent
    old_qa_task = '''            task = Task(
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
            )'''
    
    # This one already has agent=agent, so it's correct
    
    # Write updated file
    with open("enhanced_main.py", "w") as f:
        f.write(content)
    
    print("✓ All task agent assignments fixed!")
    return True

if __name__ == "__main__":
    if fix_task_agent_assignments():
        print("\n✓ Fix applied successfully!")
        print("\nRestart the pipeline:")
        print("python enhanced_main.py")
    else:
        print("\n✗ Fix failed. Check the file manually.")
