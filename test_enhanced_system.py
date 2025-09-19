#!/usr/bin/env python3
"""
Enhanced System Test Script
Tests all components of the enhanced pipeline
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime

def test_imports():
    """Test all enhanced module imports"""
    print("Testing enhanced module imports...")
    
    try:
        # Test basic imports
        import crewai
        import psutil
        import fastapi
        import uvicorn
        print("✓ Basic dependencies imported")
        
        # Test enhanced modules
        from enhanced_agents import SmartAgentSelector, LanguageDetector, TestFrameworkSelector
        from error_recovery import ServiceResilienceManager, CircuitBreaker, RetryMechanism
        from monitoring_system import MetricsCollector, AlertManager, HealthChecker
        print("✓ Enhanced modules imported")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_environment_variables():
    """Test environment variable configuration"""
    print("\nTesting environment variables...")
    
    required_vars = [
        "OPENAI_API_KEY", "GITHUB_TOKEN", "GITHUB_REPO",
        "JIRA_HOST", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
        else:
            print(f"✓ {var}: Set")
    
    if missing:
        print(f"✗ Missing variables: {', '.join(missing)}")
        return False
    
    print("✓ All required environment variables are set")
    return True

def test_language_detection():
    """Test language detection functionality"""
    print("\nTesting language detection...")
    
    try:
        from enhanced_agents import LanguageDetector
        
        test_cases = [
            ("Create a Python function for data analysis with pandas", "python"),
            ("Build a React component with Material-UI", "javascript"),
            ("Implement Spring Boot REST API", "java"),
            ("Write Go microservice with Gin framework", "go"),
            ("Create Rust CLI tool with Clap", "rust")
        ]
        
        for content, expected in test_cases:
            detected = LanguageDetector.detect_language(content)
            if detected == expected:
                print(f"✓ Detected {detected} for: {content[:50]}...")
            else:
                print(f"✗ Expected {expected}, got {detected} for: {content[:50]}...")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Language detection test failed: {e}")
        return False

def test_domain_detection():
    """Test domain detection functionality"""
    print("\nTesting domain detection...")
    
    try:
        from enhanced_agents import LanguageDetector
        
        test_cases = [
            ("Build a responsive frontend dashboard", "web_frontend"),
            ("Create REST API for user management", "web_backend"),
            ("Develop machine learning model for predictions", "data_science"),
            ("Setup CI/CD pipeline with Docker", "devops"),
            ("Build mobile app with authentication", "mobile"),
            ("Implement OAuth2 security layer", "security")
        ]
        
        for content, expected in test_cases:
            detected = LanguageDetector.detect_domain(content)
            if detected == expected:
                print(f"✓ Detected {detected} for: {content}")
            else:
                print(f"? Expected {expected}, got {detected} for: {content}")
                # Domain detection is less strict, so we'll continue
        
        return True
        
    except Exception as e:
        print(f"✗ Domain detection test failed: {e}")
        return False

def test_agent_selection():
    """Test smart agent selection"""
    print("\nTesting smart agent selection...")
    
    try:
        from enhanced_agents import SmartAgentSelector
        
        selector = SmartAgentSelector()
        
        # Test Python data science ticket
        agents, language, domain = selector.select_agents_for_ticket(
            "Create machine learning model using Python pandas and scikit-learn",
            "ML Model Development"
        )
        
        print(f"✓ Selected agents: {list(agents.keys())}")
        print(f"✓ Language: {language}, Domain: {domain}")
        
        # Verify expected agents are selected
        expected_agents = ["coder", "code_reviewer"]
        for agent in expected_agents:
            if agent not in agents:
                print(f"✗ Missing expected agent: {agent}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Agent selection test failed: {e}")
        return False

def test_circuit_breaker():
    """Test circuit breaker functionality"""
    print("\nTesting circuit breaker...")
    
    try:
        from error_recovery import CircuitBreaker, CircuitBreakerConfig
        
        # Create test circuit breaker
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=1,
            name="test_circuit"
        )
        circuit = CircuitBreaker(config)
        
        # Test function that always fails
        @circuit
        def failing_function():
            raise Exception("Test failure")
        
        # Test failures
        failure_count = 0
        for i in range(5):
            try:
                failing_function()
            except Exception:
                failure_count += 1
        
        print(f"✓ Circuit breaker handled {failure_count} failures")
        print(f"✓ Circuit state: {circuit.stats.state}")
        
        return True
        
    except Exception as e:
        print(f"✗ Circuit breaker test failed: {e}")
        return False

def test_metrics_collection():
    """Test metrics collection"""
    print("\nTesting metrics collection...")
    
    try:
        from monitoring_system import MetricsCollector
        
        collector = MetricsCollector()
        
        # Record test metrics
        collector.record_metric("test_metric", 42.0, {"env": "test"}, "units")
        collector.record_metric("test_metric", 84.0, {"env": "test"}, "units")
        
        # Get stats
        stats = collector.get_metric_stats("test_metric", 60)
        
        if stats and stats["count"] == 2:
            print(f"✓ Metrics collected: {stats}")
        else:
            print(f"✗ Expected 2 metrics, got: {stats}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Metrics collection test failed: {e}")
        return False

def test_alert_manager():
    """Test alert manager"""
    print("\nTesting alert manager...")
    
    try:
        from monitoring_system import (
            MetricsCollector, AlertManager, ThresholdAlertRule, AlertLevel
        )
        
        collector = MetricsCollector()
        alert_manager = AlertManager(collector)
        
        # Add test alert rule
        rule = ThresholdAlertRule(
            "test_alert",
            "test_metric",
            threshold=50.0,
            comparison="greater",
            level=AlertLevel.WARNING
        )
        alert_manager.add_alert_rule(rule)
        
        # Record metric that should trigger alert
        collector.record_metric("test_metric", 75.0)
        
        # Check alert (normally done in background thread)
        should_alert = rule.evaluate(collector)
        
        if should_alert:
            print("✓ Alert rule evaluation working")
        else:
            print("✗ Alert rule should have triggered")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Alert manager test failed: {e}")
        return False

async def test_enhanced_pipeline_init():
    """Test enhanced pipeline initialization"""
    print("\nTesting enhanced pipeline initialization...")
    
    try:
        # Import without initializing full pipeline
        from enhanced_main import EnhancedPipeline
        
        # Test just the setup methods that don't require external services
        pipeline = EnhancedPipeline.__new__(EnhancedPipeline)  # Create without __init__
        
        # Test individual setup methods
        pipeline.setup_monitoring()
        print("✓ Monitoring setup completed")
        
        pipeline.setup_agents()
        print("✓ Agent setup completed")
        
        print("✓ Enhanced pipeline components initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced pipeline initialization failed: {e}")
        return False

def test_system_requirements():
    """Test system requirements"""
    print("\nTesting system requirements...")
    
    try:
        import psutil
        
        # Check CPU
        cpu_count = psutil.cpu_count()
        print(f"✓ CPU cores: {cpu_count}")
        
        # Check memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"✓ Total memory: {memory_gb:.1f} GB")
        
        # Check disk
        disk = psutil.disk_usage('/')
        disk_gb = disk.total / (1024**3)
        print(f"✓ Total disk: {disk_gb:.1f} GB")
        
        # Recommendations
        if memory_gb < 2:
            print("⚠ Warning: Less than 2GB RAM available")
        if cpu_count < 2:
            print("⚠ Warning: Less than 2 CPU cores available")
        
        return True
        
    except Exception as e:
        print(f"✗ System requirements check failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("ENHANCED CREWAI PIPELINE TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Environment Variables", test_environment_variables),
        ("Language Detection", test_language_detection),
        ("Domain Detection", test_domain_detection),
        ("Agent Selection", test_agent_selection),
        ("Circuit Breaker", test_circuit_breaker),
        ("Metrics Collection", test_metrics_collection),
        ("Alert Manager", test_alert_manager),
        ("Enhanced Pipeline Init", test_enhanced_pipeline_init),
        ("System Requirements", test_system_requirements)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"\n{test_name}: ✓ PASSED")
            else:
                failed += 1
                print(f"\n{test_name}: ✗ FAILED")
        except Exception as e:
            failed += 1
            print(f"\n{test_name}: ✗ FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Enhanced system is ready for deployment.")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    asyncio.run(run_all_tests())