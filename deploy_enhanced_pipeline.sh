#!/bin/bash
set -e

echo "==========================================================="
echo "ENHANCED CREWAI PIPELINE DEPLOYMENT SCRIPT"
echo "==========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

print_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Phase 1: Backup and Environment Check
print_status "Phase 1: Environment Preparation"

# Create backup
BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
print_info "Created backup directory: $BACKUP_DIR"

# Backup existing files
for file in main.py requirements.txt test_setup.py *.json; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        print_info "Backed up: $file"
    fi
done

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
print_info "Python version: $python_version"

# Check if running in Replit
if [ -n "$REPL_ID" ]; then
    print_info "Running in Replit environment"
    PYTHON_CMD="python3"
else
    print_info "Running in local environment"
    PYTHON_CMD="python3"
fi

# Phase 2: Dependencies Installation
print_status "Phase 2: Installing Enhanced Dependencies"

# Update requirements
cat > requirements_enhanced.txt << 'EOF'
crewai>=0.28.8
openai>=1.13.3
PyGithub>=2.1.1
requests>=2.31.0
jira>=3.5.2
python-dotenv>=1.0.0
psutil>=5.9.0
fastapi>=0.104.0
uvicorn>=0.24.0
aiofiles>=23.2.1
EOF

print_info "Created enhanced requirements file"

# Install dependencies
print_info "Installing dependencies..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements_enhanced.txt

# Verify critical imports
print_info "Verifying dependency installation..."
$PYTHON_CMD -c "
import sys
modules = ['crewai', 'psutil', 'fastapi', 'uvicorn', 'aiofiles']
failed = []
for module in modules:
    try:
        __import__(module)
        print(f'✓ {module}')
    except ImportError as e:
        print(f'✗ {module}: {e}')
        failed.append(module)
        
if failed:
    print(f'Failed to import: {failed}')
    sys.exit(1)
else:
    print('All dependencies verified successfully')
"

# Phase 3: Deploy Enhanced Files
print_status "Phase 3: Deploying Enhanced Components"

# Note: In a real deployment, you would copy the actual files here
# For this script, we'll create placeholders and instructions

print_info "Files to copy to your Replit project:"
echo "  1. enhanced_agents.py"
echo "  2. error_recovery.py" 
echo "  3. monitoring_system.py"
echo "  4. enhanced_main.py"
echo "  5. test_enhanced_system.py"
echo "  6. create_test_tickets.py"

# Phase 4: Environment Configuration
print_status "Phase 4: Environment Configuration Check"

# Check required environment variables
required_vars=(
    "OPENAI_API_KEY"
    "GITHUB_TOKEN" 
    "GITHUB_REPO"
    "JIRA_HOST"
    "JIRA_EMAIL"
    "JIRA_API_TOKEN"
    "JIRA_PROJECT_KEY"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    else
        print_info "$var: ✓ Set"
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    print_warning "Please set these in Replit Secrets before continuing"
fi

# Check optional variables
optional_vars=(
    "SLACK_WEBHOOK_URL"
    "EMAIL_HOST"
    "EMAIL_USER"
    "EMAIL_PASS"
    "EMAIL_TO"
)

for var in "${optional_vars[@]}"; do
    if [ -n "${!var}" ]; then
        print_info "$var: ✓ Set (optional)"
    else
        print_warning "$var: Not set (optional notification feature disabled)"
    fi
done

# Phase 5: System Health Check
print_status "Phase 5: System Health Check"

# Check system resources
print_info "System Resources:"
if command -v free >/dev/null 2>&1; then
    echo "Memory:"
    free -h | head -2
else
    echo "Memory check not available on this system"
fi

if command -v df >/dev/null 2>&1; then
    echo "Disk Space:"
    df -h / | head -2
else
    echo "Disk check not available on this system"
fi

# CPU info
if [ -f /proc/cpuinfo ]; then
    cpu_cores=$(nproc)
    print_info "CPU Cores: $cpu_cores"
else
    print_info "CPU info not available"
fi

# Phase 6: Run Tests
print_status "Phase 6: Running Enhanced System Tests"

if [ -f "test_enhanced_system.py" ]; then
    print_info "Running comprehensive test suite..."
    $PYTHON_CMD test_enhanced_system.py
    
    if [ $? -eq 0 ]; then
        print_status "All tests passed! System is ready."
    else
        print_error "Some tests failed. Please review and fix issues."
        exit 1
    fi
else
    print_warning "test_enhanced_system.py not found. Please copy the test file."
fi

# Phase 7: Create Test Data
print_status "Phase 7: Test Data Preparation"

if [ -f "create_test_tickets.py" ]; then
    read -p "Do you want to create test Jira tickets? (y/n): " create_tickets
    if [ "$create_tickets" = "y" ] || [ "$create_tickets" = "Y" ]; then
        print_info "Creating test tickets..."
        $PYTHON_CMD create_test_tickets.py
    else
        print_info "Skipping test ticket creation"
    fi
else
    print_warning "create_test_tickets.py not found. Please copy the ticket creation script."
fi

# Phase 8: Deployment Summary
print_status "Phase 8: Deployment Summary"

echo ""
echo "==========================================================="
echo "DEPLOYMENT SUMMARY"
echo "==========================================================="

print_status "Enhanced pipeline deployment completed!"

echo ""
echo "Next Steps:"
echo "1. Copy all enhanced module files to your Replit project:"
echo "   - enhanced_agents.py"
echo "   - error_recovery.py"
echo "   - monitoring_system.py" 
echo "   - enhanced_main.py"
echo "   - test_enhanced_system.py"
echo "   - create_test_tickets.py"
echo ""
echo "2. Run the test suite:"
echo "   python test_enhanced_system.py"
echo ""
echo "3. Create test tickets (optional):"
echo "   python create_test_tickets.py"
echo ""
echo "4. Start the enhanced pipeline:"
echo "   python enhanced_main.py"
echo ""
echo "5. Monitor the dashboard and logs for multi-language processing"
echo ""

# Create monitoring commands file
cat > monitoring_commands.txt << 'EOF'
# Enhanced Pipeline Monitoring Commands

# Check pipeline status
python -c "
from enhanced_main import EnhancedPipeline
pipeline = EnhancedPipeline()
status = pipeline.get_status()
print('Pipeline Status:', status['pipeline_status'])
print('Processed Tickets:', status['processed_tickets'])
"

# View system metrics
python -c "
from monitoring_system import MetricsCollector, SystemMetricsCollector
collector = MetricsCollector()
sys_collector = SystemMetricsCollector(collector)
sys_collector._collect_metrics()
print('CPU Usage:', collector.get_metric_stats('system_cpu_usage', 5))
print('Memory Usage:', collector.get_metric_stats('system_memory_usage', 5))
"

# Check active alerts
python -c "
from enhanced_main import EnhancedPipeline
pipeline = EnhancedPipeline()
alerts = pipeline.alert_manager.get_active_alerts()
print(f'Active Alerts: {len(alerts)}')
for alert in alerts:
    print(f'- {alert.name}: {alert.message}')
"

# View circuit breaker status
python -c "
from error_recovery import resilience_manager
status = resilience_manager.get_health_status()
for service, health in status.items():
    print(f'{service}: {health[\"state\"]} (failures: {health[\"failure_count\"]})')
"

# Test language detection
python -c "
from enhanced_agents import LanguageDetector
test_content = 'Create a React component with TypeScript and Material-UI'
language = LanguageDetector.detect_language(test_content)
domain = LanguageDetector.detect_domain(test_content)
print(f'Detected Language: {language}')
print(f'Detected Domain: {domain}')
"
EOF

print_info "Created monitoring_commands.txt with helpful monitoring commands"

# Create startup script
cat > start_enhanced_pipeline.sh << 'EOF'
#!/bin/bash

echo "Starting Enhanced CrewAI Pipeline..."

# Check if all files exist
required_files=(
    "enhanced_agents.py"
    "error_recovery.py"
    "monitoring_system.py"
    "enhanced_main.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "ERROR: Missing required files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo "Please copy all enhanced module files before starting."
    exit 1
fi

# Run tests first
echo "Running pre-startup tests..."
python test_enhanced_system.py

if [ $? -eq 0 ]; then
    echo "All tests passed. Starting enhanced pipeline..."
    python enhanced_main.py
else
    echo "Tests failed. Please fix issues before starting pipeline."
    exit 1
fi
EOF

chmod +x start_enhanced_pipeline.sh
print_info "Created start_enhanced_pipeline.sh startup script"

# Create quick reference guide
cat > ENHANCED_QUICK_REFERENCE.md << 'EOF'
# Enhanced CrewAI Pipeline Quick Reference

## Starting the Pipeline
```bash
./start_enhanced_pipeline.sh
```

## Manual Start (after copying files)
```bash
python enhanced_main.py
```

## Running Tests
```bash
python test_enhanced_system.py
```

## Creating Test Tickets
```bash
python create_test_tickets.py
```

## Monitoring Commands
```bash
source monitoring_commands.txt
```

## Language Support
- **Python**: pandas, Django, Flask, FastAPI, data science
- **JavaScript**: React, Vue, Angular, Node.js, TypeScript
- **Java**: Spring Boot, JPA, enterprise patterns
- **Go**: Gin, microservices, concurrent programming
- **Rust**: CLI tools, systems programming, performance

## Domain Specializations
- **Web Frontend**: React, Vue, Angular, responsive design
- **Web Backend**: REST APIs, microservices, databases
- **Data Science**: ML models, analytics, visualization
- **DevOps**: CI/CD, Docker, Kubernetes, infrastructure
- **Mobile**: React Native, Flutter, native apps
- **Security**: Vulnerability assessment, compliance

## Key Features
1. **Multi-Language Detection**: Automatic language/domain detection
2. **Circuit Breakers**: Automatic failover for external services
3. **Comprehensive Monitoring**: Metrics, alerts, health checks
4. **Specialized Agents**: Domain-specific expertise
5. **Error Recovery**: Retry mechanisms and fallback strategies

## File Structure
```
enhanced_pipeline/
├── enhanced_agents.py      # Multi-language and specialized agents
├── error_recovery.py       # Circuit breakers and retry logic
├── monitoring_system.py    # Metrics, alerts, health checks
├── enhanced_main.py        # Main pipeline with all enhancements
├── test_enhanced_system.py # Comprehensive test suite
├── create_test_tickets.py  # Test ticket creation
└── start_enhanced_pipeline.sh # Startup script
```

## Troubleshooting

### Import Errors
```bash
pip install -r requirements_enhanced.txt
```

### Missing Environment Variables
Check Replit Secrets for:
- OPENAI_API_KEY
- GITHUB_TOKEN, GITHUB_REPO  
- JIRA_HOST, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY

### High Resource Usage
- Increase POLL_INTERVAL (default: 60 seconds)
- Reduce metrics retention (default: 48 hours)
- Monitor system_cpu_usage and system_memory_usage metrics

### Circuit Breaker Issues
Check circuit breaker status and service health:
```python
from error_recovery import resilience_manager
print(resilience_manager.get_health_status())
```
EOF

print_info "Created ENHANCED_QUICK_REFERENCE.md"

if [ ${#missing_vars[@]} -eq 0 ]; then
    print_status "DEPLOYMENT SUCCESSFUL!"
    echo ""
    echo "Your enhanced CrewAI pipeline is ready to use with:"
    echo "- Multi-language support (Python, JS, Java, Go, Rust)"
    echo "- Specialized domain agents"
    echo "- Circuit breakers and error recovery"
    echo "- Comprehensive monitoring and alerting"
    echo ""
    echo "To start the pipeline:"
    echo "1. Copy all enhanced module files to your Replit project"
    echo "2. Run: python test_enhanced_system.py"
    echo "3. Run: python enhanced_main.py"
else
    print_warning "DEPLOYMENT COMPLETED WITH WARNINGS"
    echo ""
    echo "Please set the missing environment variables before starting the pipeline."
fi

print_info "Deployment script completed. Check the logs above for any issues."