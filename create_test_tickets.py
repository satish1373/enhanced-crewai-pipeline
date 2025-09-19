#!/usr/bin/env python3
"""
Create Test Jira Tickets for Multi-Language Testing
"""

import os
from jira import JIRA

def create_test_tickets():
    """Create comprehensive test tickets for enhanced pipeline"""
    
    # Initialize Jira client
    jira_options = {"server": f"https://{os.getenv('JIRA_HOST')}"}
    jira_client = JIRA(
        options=jira_options,
        basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))
    )
    
    project_key = os.getenv("JIRA_PROJECT_KEY")
    
    test_tickets = [
        {
            "summary": "Create Python data analysis function with pandas",
            "description": """Create a Python function that analyzes customer purchase data using pandas.

Requirements:
- Read CSV data with customer purchases
- Calculate monthly revenue trends
- Identify top 10 customers by total purchase amount
- Export results to Excel format
- Include proper error handling for missing data
- Add comprehensive unit tests with pytest

Expected deliverables:
- Python module with analysis functions
- Unit tests with >90% coverage
- Documentation with usage examples
- Sample data processing script""",
            "priority": "Medium"
        },
        {
            "summary": "Build React dashboard component with Material-UI",
            "description": """Develop a responsive dashboard component using React and Material-UI.

Requirements:
- Display key metrics with interactive charts
- Implement real-time data updates via WebSocket
- Add filtering and date range selection
- Ensure mobile responsiveness
- Include proper TypeScript types
- Add comprehensive Jest tests

Technical stack:
- React 18+ with hooks
- Material-UI v5
- Chart.js for visualizations
- TypeScript for type safety
- Jest and React Testing Library for tests""",
            "priority": "High"
        },
        {
            "summary": "Implement Java Spring Boot REST API for user management",
            "description": """Create a comprehensive user management REST API using Spring Boot.

Requirements:
- Full CRUD operations for user entities
- JWT-based authentication and authorization
- Role-based access control (Admin, User)
- Input validation and error handling
- PostgreSQL database integration with JPA
- OpenAPI/Swagger documentation
- Comprehensive unit and integration tests

Endpoints needed:
- POST /api/users (create user)
- GET /api/users (list users with pagination)
- GET /api/users/{id} (get user details)
- PUT /api/users/{id} (update user)
- DELETE /api/users/{id} (delete user)
- POST /api/auth/login (authenticate user)""",
            "priority": "High"
        },
        {
            "summary": "Develop Go microservice for notification handling",
            "description": """Build a high-performance notification microservice using Go.

Requirements:
- Handle multiple notification channels (email, SMS, push)
- Implement message queuing with Redis
- Add rate limiting and retry mechanisms
- Include health checks and metrics endpoints
- Docker containerization
- Concurrent processing with goroutines
- Comprehensive testing with testify

Technical specifications:
- Use Gin framework for HTTP server
- Redis for message queuing and caching
- MongoDB for notification history
- Prometheus metrics integration
- Circuit breaker pattern for external services""",
            "priority": "Medium"
        },
        {
            "summary": "Create Rust CLI tool for log analysis",
            "description": """Develop a fast CLI tool in Rust for analyzing large log files.

Requirements:
- Parse multiple log formats (Apache, Nginx, JSON)
- Generate statistics (requests per hour, error rates, top IPs)
- Support filtering by date ranges and log levels
- Memory-efficient processing of multi-GB files
- Colored terminal output with progress bars
- Comprehensive error handling
- Unit and integration tests

Features:
- Concurrent file processing
- Regex pattern matching for custom formats
- Export results to JSON/CSV
- Configuration file support (TOML)
- Cross-platform compatibility (Linux, macOS, Windows)""",
            "priority": "Low"
        },
        {
            "summary": "Build DevOps CI/CD pipeline with Docker and Kubernetes",
            "description": """Create a complete CI/CD pipeline for microservices deployment.

Requirements:
- Multi-stage Docker builds for optimization
- Kubernetes deployment manifests
- Automated testing integration
- Security scanning (container and code)
- Rolling deployment strategy
- Monitoring and alerting setup
- Infrastructure as Code with Terraform

Pipeline stages:
1. Code quality checks (linting, security scan)
2. Unit and integration tests
3. Docker image build and push
4. Kubernetes deployment to staging
5. Automated acceptance tests
6. Production deployment approval
7. Health checks and rollback capability

Tools: GitHub Actions, Docker, Kubernetes, Terraform, Helm""",
            "priority": "High"
        },
        {
            "summary": "Implement mobile authentication with React Native",
            "description": """Develop a secure authentication system for mobile app using React Native.

Requirements:
- Email/password and social login (Google, Apple)
- Biometric authentication (fingerprint, face ID)
- JWT token management with refresh
- Secure storage for sensitive data
- Offline capability with data sync
- Cross-platform compatibility (iOS and Android)
- Comprehensive testing with Detox

Security features:
- Certificate pinning for API calls
- Encrypted local storage
- Session timeout handling
- Jailbreak/root detection
- OWASP Mobile security compliance

UI/UX requirements:
- Native look and feel per platform
- Accessibility support
- Loading states and error handling
- Smooth animations and transitions""",
            "priority": "High"
        },
        {
            "summary": "Security audit and vulnerability assessment tool",
            "description": """Create a comprehensive security assessment tool for web applications.

Requirements:
- Automated vulnerability scanning (OWASP Top 10)
- Code analysis for security issues
- Dependencies vulnerability check
- SSL/TLS configuration assessment
- Authentication and authorization testing
- Generate detailed security reports
- Integration with CI/CD pipelines

Security checks:
- SQL injection detection
- XSS vulnerability scanning
- CSRF protection verification
- Insecure direct object references
- Security misconfiguration detection
- Sensitive data exposure checks
- Insufficient logging and monitoring

Deliverables:
- Python-based scanning tool
- HTML/PDF report generation
- JSON API for CI/CD integration
- Docker container for easy deployment
- Comprehensive documentation""",
            "priority": "Medium"
        }
    ]
    
    created_tickets = []
    
    for ticket_data in test_tickets:
        try:
            issue_dict = {
                'project': {'key': project_key},
                'summary': ticket_data['summary'],
                'description': ticket_data['description'],
                'issuetype': {'name': 'Task'},
                'priority': {'name': ticket_data['priority']}
            }
            
            new_issue = jira_client.create_issue(fields=issue_dict)
            created_tickets.append(new_issue.key)
            print(f"✓ Created ticket: {new_issue.key} - {ticket_data['summary']}")
            
        except Exception as e:
            print(f"✗ Failed to create ticket '{ticket_data['summary']}': {e}")
    
    return created_tickets

if __name__ == "__main__":
    print("Creating comprehensive test tickets for enhanced pipeline...")
    print("=" * 60)
    
    # Check environment variables
    required_vars = ["JIRA_HOST", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"✗ Missing environment variables: {', '.join(missing)}")
        exit(1)
    
    try:
        tickets = create_test_tickets()
        print("=" * 60)
        print(f"✓ Successfully created {len(tickets)} test tickets")
        print("✓ Test tickets cover: Python, JavaScript, Java, Go, Rust, DevOps, Mobile, Security")
        print("✓ Pipeline can now be tested with diverse, realistic scenarios")
        print("\nCreated tickets:")
        for ticket in tickets:
            print(f"  - {ticket}")
        
    except Exception as e:
        print(f"✗ Failed to create test tickets: {e}")
        exit(1)