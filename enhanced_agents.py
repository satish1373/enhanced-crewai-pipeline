"""
Enhanced Multi-Language and Specialized Agents
"""

from crewai import Agent
from typing import Dict, List, Optional
import re

class AgentFactory:
    """Factory for creating specialized agents based on ticket requirements"""
    
    @staticmethod
    def create_router_agent():
        return Agent(
            role="Technical Router & Task Analyzer",
            goal="Analyze Jira tickets, determine programming language, complexity, and route to appropriate specialized agents",
            backstory="An experienced technical architect who can assess requirements across multiple technologies and domains.",
            verbose=True
        )
    
    @staticmethod
    def create_language_agents() -> Dict[str, Agent]:
        """Create language-specific coding agents"""
        return {
            "python": Agent(
                role="Python Developer",
                goal="Write clean, efficient Python code following PEP8 standards",
                backstory="Expert Python developer with deep knowledge of frameworks like Django, Flask, FastAPI, and data science libraries.",
                verbose=True
            ),
            "javascript": Agent(
                role="JavaScript Developer", 
                goal="Write modern JavaScript/TypeScript code with proper ES6+ patterns",
                backstory="Full-stack JavaScript developer experienced in Node.js, React, Vue, and modern JS frameworks.",
                verbose=True
            ),
            "java": Agent(
                role="Java Developer",
                goal="Write robust Java code following enterprise patterns and best practices",
                backstory="Senior Java developer with expertise in Spring Boot, microservices, and enterprise architectures.",
                verbose=True
            ),
            "go": Agent(
                role="Go Developer",
                goal="Write efficient, concurrent Go code with proper error handling",
                backstory="Systems programmer specializing in Go, microservices, and cloud-native applications.",
                verbose=True
            ),
            "rust": Agent(
                role="Rust Developer",
                goal="Write safe, performant Rust code with proper memory management",
                backstory="Systems developer focused on performance-critical applications and memory safety.",
                verbose=True
            )
        }
    
    @staticmethod
    def create_domain_agents() -> Dict[str, Agent]:
        """Create domain-specific agents"""
        return {
            "web_frontend": Agent(
                role="Frontend Web Developer",
                goal="Create responsive, accessible web interfaces with modern frameworks",
                backstory="UI/UX focused developer with expertise in React, Vue, Angular, and modern CSS.",
                verbose=True
            ),
            "web_backend": Agent(
                role="Backend API Developer", 
                goal="Build scalable, secure APIs and microservices",
                backstory="Backend specialist focused on RESTful APIs, GraphQL, databases, and cloud services.",
                verbose=True
            ),
            "data_science": Agent(
                role="Data Scientist & ML Engineer",
                goal="Develop data analysis pipelines and machine learning models",
                backstory="Data science expert with deep knowledge of pandas, scikit-learn, TensorFlow, and statistical analysis.",
                verbose=True
            ),
            "devops": Agent(
                role="DevOps Engineer",
                goal="Create infrastructure as code, CI/CD pipelines, and deployment automation",
                backstory="Site reliability engineer experienced with Docker, Kubernetes, Terraform, and cloud platforms.",
                verbose=True
            ),
            "mobile": Agent(
                role="Mobile App Developer",
                goal="Build native and cross-platform mobile applications",
                backstory="Mobile development expert in React Native, Flutter, iOS, and Android platforms.",
                verbose=True
            ),
            "security": Agent(
                role="Security Specialist",
                goal="Implement security best practices and identify vulnerabilities",
                backstory="Cybersecurity expert focused on secure coding practices, penetration testing, and compliance.",
                verbose=True
            )
        }
    
    @staticmethod
    def create_specialized_reviewers() -> Dict[str, Agent]:
        """Create specialized review agents"""
        return {
            "code_reviewer": Agent(
                role="Senior Code Reviewer",
                goal="Review code for quality, performance, and maintainability",
                backstory="Principal engineer with 15+ years experience in code reviews across multiple languages.",
                verbose=True
            ),
            "security_reviewer": Agent(
                role="Security Code Reviewer",
                goal="Identify security vulnerabilities and compliance issues",
                backstory="Security specialist focused on OWASP guidelines, vulnerability assessment, and secure coding.",
                verbose=True
            ),
            "performance_reviewer": Agent(
                role="Performance Specialist",
                goal="Optimize code for performance and scalability",
                backstory="Performance engineer specializing in profiling, optimization, and high-scale systems.",
                verbose=True
            )
        }

class LanguageDetector:
    """Detect programming language and domain from ticket content"""
    
    LANGUAGE_KEYWORDS = {
        "python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "pytest", "scikit-learn", "tensorflow", "keras"],
        "javascript": ["javascript", "js", "node", "react", "vue", "angular", "npm", "typescript", "jest"],
        "java": ["java", "spring", "maven", "gradle", "junit", "hibernate", "jpa"],
        "go": ["golang", "go", "goroutine", "gin", "fiber", "microservice"],
        "rust": ["rust", "cargo", "tokio", "serde", "cli"],
        "sql": ["database", "sql", "mysql", "postgres", "mongodb"],
        "docker": ["docker", "container", "kubernetes", "dockerfile"],
        "terraform": ["terraform", "infrastructure", "aws", "azure", "gcp"]
    }
    
    DOMAIN_KEYWORDS = {
        "web_frontend": ["frontend", "ui", "ux", "responsive", "css", "html"],
        "web_backend": ["backend", "api", "rest", "graphql", "microservice"],
        "data_science": ["data", "analysis", "machine learning", "ml", "ai", "statistics"],
        "devops": ["devops", "ci/cd", "pipeline", "deployment", "infrastructure"],
        "mobile": ["mobile", "ios", "android", "react native", "flutter"],
        "security": ["security", "authentication", "authorization", "encryption"]
    }
    
    @classmethod
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
        
        return "python"  # Default language
    
    @classmethod
    def detect_domain(cls, ticket_content: str) -> Optional[str]:
        """Detect domain specialization from ticket content"""
        content_lower = ticket_content.lower()
        
        domain_scores = {}
        for domain, keywords in cls.DOMAIN_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                domain_scores[domain] = score
        
        return max(domain_scores, key=domain_scores.get) if domain_scores else None

class TestFrameworkSelector:
    """Select appropriate test frameworks based on language and domain"""
    
    TEST_FRAMEWORKS = {
        "python": {
            "unit": "pytest",
            "integration": "pytest + requests",
            "performance": "pytest-benchmark",
            "template": """
import pytest
import {module_name}

class Test{ClassName}:
    def test_{function_name}_basic(self):
        # Basic functionality test
        result = {module_name}.{function_name}({basic_input})
        assert result == {expected_output}
    
    def test_{function_name}_edge_cases(self):
        # Edge case testing
        with pytest.raises({exception_type}):
            {module_name}.{function_name}({invalid_input})
    
    def test_{function_name}_performance(self, benchmark):
        # Performance test
        result = benchmark({module_name}.{function_name}, {performance_input})
        assert result is not None
"""
        },
        "javascript": {
            "unit": "Jest",
            "integration": "Jest + Supertest",
            "e2e": "Cypress",
            "template": """
const {module_name} = require('./{module_name}');

describe('{function_name}', () => {
    test('should handle basic input correctly', () => {
        const result = {module_name}.{function_name}({basic_input});
        expect(result).toBe({expected_output});
    });
    
    test('should throw error for invalid input', () => {
        expect(() => {
            {module_name}.{function_name}({invalid_input});
        }).toThrow({exception_type});
    });
    
    test('should handle edge cases', () => {
        // Edge case testing
    });
});
"""
        },
        "java": {
            "unit": "JUnit 5",
            "integration": "Spring Test",
            "template": """
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

class {ClassName}Test {
    
    @Test
    @DisplayName("Should handle basic input correctly")
    void test{FunctionName}Basic() {
        // Arrange
        {ClassName} instance = new {ClassName}();
        
        // Act
        var result = instance.{function_name}({basic_input});
        
        // Assert
        assertEquals({expected_output}, result);
    }
    
    @Test
    @DisplayName("Should throw exception for invalid input")
    void test{FunctionName}InvalidInput() {
        {ClassName} instance = new {ClassName}();
        
        assertThrows({ExceptionType}.class, () -> {
            instance.{function_name}({invalid_input});
        });
    }
}
"""
        }
    }
    
    @classmethod
    def get_test_template(cls, language: str, test_type: str = "unit") -> str:
        """Get test template for specific language and test type"""
        framework_info = cls.TEST_FRAMEWORKS.get(language, cls.TEST_FRAMEWORKS["python"])
        return framework_info.get("template", "")
    
    @classmethod
    def get_test_framework(cls, language: str, test_type: str = "unit") -> str:
        """Get recommended test framework for language and test type"""
        framework_info = cls.TEST_FRAMEWORKS.get(language, cls.TEST_FRAMEWORKS["python"])
        return framework_info.get(test_type, framework_info.get("unit", "pytest"))

class SmartAgentSelector:
    """Intelligently select agents based on ticket analysis"""
    
    def __init__(self):
        self.router = AgentFactory.create_router_agent()  # Add missing router
        self.language_agents = AgentFactory.create_language_agents()
        self.domain_agents = AgentFactory.create_domain_agents()
        self.specialized_reviewers = AgentFactory.create_specialized_reviewers()
    
    def select_agents_for_ticket(self, ticket_content: str, ticket_summary: str) -> Dict[str, Agent]:
        """Select appropriate agents based on ticket analysis"""
        full_content = f"{ticket_summary} {ticket_content}"
        
        # Detect language and domain
        language = LanguageDetector.detect_language(full_content)
        domain = LanguageDetector.detect_domain(full_content)
        
        selected_agents = {}
        
        # Add language-specific coder
        if language and language in self.language_agents:
            selected_agents["coder"] = self.language_agents[language]
        else:
            selected_agents["coder"] = self.language_agents["python"]  # Default
        
        # Add domain-specific agent if detected
        if domain and domain in self.domain_agents:
            selected_agents["domain_specialist"] = self.domain_agents[domain]
        
        # Add appropriate reviewers
        selected_agents["code_reviewer"] = self.specialized_reviewers["code_reviewer"]
        
        # Add security reviewer for security-related tickets
        if "security" in full_content.lower():
            selected_agents["security_reviewer"] = self.specialized_reviewers["security_reviewer"]
        
        # Add performance reviewer for performance-related tickets
        if any(word in full_content.lower() for word in ["performance", "optimization", "speed", "scale"]):
            selected_agents["performance_reviewer"] = self.specialized_reviewers["performance_reviewer"]
        
        return selected_agents, language, domain