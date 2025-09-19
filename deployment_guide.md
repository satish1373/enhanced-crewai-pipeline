# Enhanced CrewAI Pipeline Deployment Guide

## Overview
The enhanced pipeline now includes:
- Multi-language support (Python, JavaScript, Java, Go, Rust)
- Specialized domain agents (Web, Data Science, DevOps, Mobile, Security)
- Circuit breakers and retry mechanisms
- Comprehensive monitoring and alerting
- Health checks and dashboard

## Installation

### 1. Update Requirements
```bash
pip install -r requirements_enhanced.txt
```

### 2. Upload Enhanced Files to Replit
Replace/add these files:
- `enhanced_agents.py` - Multi-language and specialized agents
- `error_recovery.py` - Circuit breakers and retry mechanisms  
- `monitoring_system.py` - Comprehensive monitoring
- `enhanced_main.py` - Enhanced main pipeline
- `requirements_enhanced.txt` - Updated dependencies

### 3. Environment Variables
Add these new optional variables in Replit Secrets:

```bash
# Monitoring & Alerting
DASHBOARD_PORT=8080
POLL_INTERVAL=60
MAX_ATTEMPTS=5

# Enhanced Notifications (optional)
GRAFANA_URL=your-grafana-url
PROMETHEUS_ENABLED=true
```

## Enhanced Features

### Multi-Language Support
The pipeline now automatically detects and handles:

**Supported Languages:**
- Python (Django, Flask, FastAPI, Data Science)
- JavaScript/TypeScript (Node.js, React, Vue, Angular)
- Java (Spring Boot, Enterprise patterns)
- Go (Microservices, Cloud-native)
- Rust (Systems programming)

**Domain Specialization:**
- Web Frontend (React, Vue, Angular)
- Web Backend (APIs, Microservices)
- Data Science (ML, Analytics)
- DevOps (Infrastructure, CI/CD)
- Mobile (React Native, Flutter)
- Security (Compliance, Vulnerability assessment)

### Error Recovery & Resilience

**Circuit Breakers:**
- OpenAI API: 3 failures trigger 2-minute cooldown
- GitHub API: 5 failures trigger 1-minute cooldown
- Jira API: 3 failures trigger 90-second cooldown

**Retry Mechanisms:**
- Exponential backoff with jitter
- Configurable max attempts per operation
- Service-specific retry policies

**Fallback Strategies:**
- Local file backup when GitHub unavailable
- Simplified code generation when OpenAI unavailable
- Manual logging when Jira unavailable

### Monitoring & Alerting

**System Metrics:**
- CPU, Memory, Disk usage
- Network I/O statistics
- Process performance

**Pipeline Metrics:**
- Ticket processing times
- Agent performance statistics
- Success/failure rates by language
- API call latencies and error rates

**Alert Rules:**
- High CPU/Memory usage (>80%)
- Ticket failure rate (>3 in 30 min)
- Slow processing (>30 min per ticket)
- Service outages

**Health Checks:**
- External service connectivity
- Agent availability
- System resource status

## Usage

### 1. Run Enhanced Pipeline
```bash
python enhanced_main.py
```

### 2. Monitor Dashboard
The pipeline provides comprehensive monitoring data accessible via:
```python
# In Python console or separate script
from enhanced_main import EnhancedPipeline
pipeline = EnhancedPipeline()
status = pipeline.get_status()
print(json.dumps(status, indent=2))
```

### 3. Test Multi-Language Support
Create Jira tickets with language-specific requirements:

**Python Data Science Ticket:**
```
Title: "Create machine learning model for customer segmentation"
Description: "Use Python pandas and scikit-learn to build customer clustering model"
```

**JavaScript React Ticket:**
```
Title: "Build responsive user dashboard component"
Description: "Create React component with Material-UI for user analytics dashboard"
```

**Java Spring Boot Ticket:**
```
Title: "Implement REST API for user management"
Description: "Build Spring Boot microservice with JPA for user CRUD operations"
```

## Monitoring Endpoints

### Health Check
```bash
curl http://localhost:8080/health
```

### Metrics
```bash
curl http://localhost:8080/metrics
```

### Dashboard Data
```bash
curl http://localhost:8080/dashboard
```

## Advanced Configuration

### Custom Language Support
Add new languages by extending `enhanced_agents.py`:

```python
# Add to LanguageDetector.LANGUAGE_KEYWORDS
"rust": ["rust", "cargo", "tokio", "serde"],

# Add to AgentFactory.create_language_agents()
"rust": Agent(
    role="Rust Developer",
    goal="Write safe, performant Rust code",
    backstory="Systems developer focused on memory safety."
)
```

### Custom Alert Rules
```python
# Add to setup_alert_rules() in enhanced_main.py
self.alert_manager.add_alert_rule(
    ThresholdAlertRule(
        "custom_metric_alert",
        "custom_metric_name",
        threshold=100.0,
        level=AlertLevel.WARNING
    )
)
```

### Custom Health Checks
```python
# Add to setup_health_checks()
def check_custom_service():
    # Your health check logic
    return True

self.health_checker.register_health_check(
    "custom_service", 
    check_custom_service, 
    interval_seconds=120
)
```

## Troubleshooting

### High Memory Usage
- Check `system_memory_usage` metric
- Reduce `retention_hours` in MetricsCollector
- Increase `POLL_INTERVAL` to reduce frequency

### Circuit Breaker Triggering
- Check service health in dashboard
- Verify API tokens and connectivity
- Review circuit breaker thresholds

### Missing Language Support
- Verify language detection keywords
- Check agent configuration
- Review test framework mappings

### Performance Issues
- Monitor agent execution times
- Check API response latencies
- Review system resource usage

## Production Deployment

### 1. Resource Requirements
- **CPU:** 2+ cores recommended
- **Memory:** 4GB+ for optimal performance
- **Storage:** 10GB+ for logs and metrics retention

### 2. Monitoring Setup
- Configure external monitoring (Grafana/Prometheus)
- Set up log aggregation
- Configure alerting channels

### 3. High Availability
- Deploy multiple instances with load balancing
- Use external databases for persistence
- Implement backup and recovery procedures

## Security Considerations

### API Token Management
- Rotate tokens regularly
- Use environment-specific tokens
- Monitor token usage

### Network Security
- Use HTTPS for all external communications
- Implement rate limiting
- Monitor for suspicious activity

### Code Security
- Enable security agent for all tickets
- Review generated code before deployment
- Implement automated security scanning

The enhanced pipeline provides enterprise-grade reliability, monitoring, and multi-language support while maintaining the original automation capabilities.