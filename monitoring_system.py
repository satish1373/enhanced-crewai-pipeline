"""
Comprehensive Monitoring & Alerting System
"""

import time
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import psutil
import threading
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"

@dataclass
class Metric:
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

@dataclass
class Alert:
    name: str
    level: AlertLevel
    message: str
    timestamp: datetime
    source: str
    labels: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False

class MetricsCollector:
    """Collects and stores metrics for monitoring"""
    
    def __init__(self, retention_hours: int = 24):
        self.metrics = defaultdict(lambda: deque(maxlen=retention_hours * 60))  # Store minute-level data
        self.retention_hours = retention_hours
        self._lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None, unit: str = ""):
        """Record a metric value"""
        with self._lock:
            metric = Metric(
                name=name,
                value=value,
                timestamp=datetime.now(),
                labels=labels or {},
                unit=unit
            )
            self.metrics[name].append(metric)
    
    def get_metric_history(self, name: str, duration_minutes: int = 60) -> List[Metric]:
        """Get metric history for specified duration"""
        with self._lock:
            if name not in self.metrics:
                return []
            
            cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
            return [m for m in self.metrics[name] if m.timestamp >= cutoff_time]
    
    def get_metric_stats(self, name: str, duration_minutes: int = 60) -> Dict[str, float]:
        """Get statistical summary of metric"""
        history = self.get_metric_history(name, duration_minutes)
        if not history:
            return {}
        
        values = [m.value for m in history]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "median": statistics.median(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0
        }

class SystemMetricsCollector:
    """Collects system-level metrics"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.collection_interval = 30  # seconds
        self.running = False
        self.collection_thread = None
    
    def start_collection(self):
        """Start collecting system metrics"""
        if self.running:
            return
        
        self.running = True
        self.collection_thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.collection_thread.start()
        logger.info("System metrics collection started")
    
    def stop_collection(self):
        """Stop collecting system metrics"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("System metrics collection stopped")
    
    def _collect_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                self._collect_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_metrics(self):
        """Collect current system metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics_collector.record_metric("system_cpu_usage", cpu_percent, unit="percent")
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics_collector.record_metric("system_memory_usage", memory.percent, unit="percent")
        self.metrics_collector.record_metric("system_memory_available", memory.available / (1024**3), unit="GB")
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.metrics_collector.record_metric("system_disk_usage", disk_percent, unit="percent")
        
        # Network metrics
        network = psutil.net_io_counters()
        self.metrics_collector.record_metric("system_network_bytes_sent", network.bytes_sent, unit="bytes")
        self.metrics_collector.record_metric("system_network_bytes_recv", network.bytes_recv, unit="bytes")

class PipelineMetricsCollector:
    """Collects pipeline-specific metrics"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.active_tickets = {}
        self.ticket_start_times = {}
        self.agent_performance = defaultdict(list)
    
    def record_ticket_started(self, ticket_key: str):
        """Record when ticket processing starts"""
        self.ticket_start_times[ticket_key] = datetime.now()
        self.active_tickets[ticket_key] = True
        self.metrics_collector.record_metric("pipeline_active_tickets", len(self.active_tickets))
        self.metrics_collector.record_metric("pipeline_tickets_started", 1)
    
    def record_ticket_completed(self, ticket_key: str, success: bool = True):
        """Record when ticket processing completes"""
        if ticket_key in self.ticket_start_times:
            duration = (datetime.now() - self.ticket_start_times[ticket_key]).total_seconds()
            self.metrics_collector.record_metric("pipeline_ticket_duration", duration, unit="seconds")
            del self.ticket_start_times[ticket_key]
        
        if ticket_key in self.active_tickets:
            del self.active_tickets[ticket_key]
        
        self.metrics_collector.record_metric("pipeline_active_tickets", len(self.active_tickets))
        
        if success:
            self.metrics_collector.record_metric("pipeline_tickets_success", 1)
        else:
            self.metrics_collector.record_metric("pipeline_tickets_failed", 1)
    
    def record_agent_performance(self, agent_name: str, duration: float, success: bool):
        """Record agent performance metrics"""
        self.metrics_collector.record_metric(
            f"agent_{agent_name}_duration", 
            duration, 
            labels={"agent": agent_name}, 
            unit="seconds"
        )
        
        if success:
            self.metrics_collector.record_metric(f"agent_{agent_name}_success", 1, labels={"agent": agent_name})
        else:
            self.metrics_collector.record_metric(f"agent_{agent_name}_failure", 1, labels={"agent": agent_name})
    
    def record_api_call(self, service: str, endpoint: str, duration: float, status_code: int):
        """Record API call metrics"""
        labels = {"service": service, "endpoint": endpoint, "status": str(status_code)}
        
        self.metrics_collector.record_metric("api_call_duration", duration, labels=labels, unit="seconds")
        self.metrics_collector.record_metric("api_calls_total", 1, labels=labels)
        
        if 200 <= status_code < 300:
            self.metrics_collector.record_metric("api_calls_success", 1, labels=labels)
        else:
            self.metrics_collector.record_metric("api_calls_error", 1, labels=labels)

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_rules = []
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.notification_handlers = []
        self.check_interval = 60  # seconds
        self.running = False
        self.check_thread = None
    
    def add_alert_rule(self, rule: 'AlertRule'):
        """Add an alert rule"""
        self.alert_rules.append(rule)
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """Add a notification handler"""
        self.notification_handlers.append(handler)
    
    def start_monitoring(self):
        """Start alert monitoring"""
        if self.running:
            return
        
        self.running = True
        self.check_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.check_thread.start()
        logger.info("Alert monitoring started")
    
    def stop_monitoring(self):
        """Stop alert monitoring"""
        self.running = False
        if self.check_thread:
            self.check_thread.join(timeout=5)
        logger.info("Alert monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_alerts()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
                time.sleep(self.check_interval)
    
    def _check_alerts(self):
        """Check all alert rules"""
        for rule in self.alert_rules:
            try:
                should_alert = rule.evaluate(self.metrics_collector)
                alert_key = f"{rule.name}_{rule.metric_name}"
                
                if should_alert and alert_key not in self.active_alerts:
                    # New alert
                    alert = Alert(
                        name=rule.name,
                        level=rule.level,
                        message=rule.get_message(self.metrics_collector),
                        timestamp=datetime.now(),
                        source="pipeline_monitor",
                        labels=rule.labels
                    )
                    self._fire_alert(alert, alert_key)
                
                elif not should_alert and alert_key in self.active_alerts:
                    # Resolve alert
                    self._resolve_alert(alert_key)
            
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule.name}: {e}")
    
    def _fire_alert(self, alert: Alert, alert_key: str):
        """Fire a new alert"""
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        
        logger.warning(f"ALERT FIRED: {alert.name} - {alert.message}")
        
        # Send notifications
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error sending alert notification: {e}")
    
    def _resolve_alert(self, alert_key: str):
        """Resolve an active alert"""
        if alert_key in self.active_alerts:
            alert = self.active_alerts[alert_key]
            alert.resolved = True
            del self.active_alerts[alert_key]
            
            logger.info(f"ALERT RESOLVED: {alert.name}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]

class AlertRule:
    """Base class for alert rules"""
    
    def __init__(self, name: str, metric_name: str, level: AlertLevel = AlertLevel.WARNING, labels: Dict[str, str] = None):
        self.name = name
        self.metric_name = metric_name
        self.level = level
        self.labels = labels or {}
    
    def evaluate(self, metrics_collector: MetricsCollector) -> bool:
        """Evaluate if alert should fire"""
        raise NotImplementedError
    
    def get_message(self, metrics_collector: MetricsCollector) -> str:
        """Get alert message"""
        return f"Alert: {self.name}"

class ThresholdAlertRule(AlertRule):
    """Alert rule based on threshold comparison"""
    
    def __init__(self, name: str, metric_name: str, threshold: float, 
                 comparison: str = "greater", duration_minutes: int = 5, 
                 level: AlertLevel = AlertLevel.WARNING, labels: Dict[str, str] = None):
        super().__init__(name, metric_name, level, labels)
        self.threshold = threshold
        self.comparison = comparison  # "greater", "less", "equal"
        self.duration_minutes = duration_minutes
    
    def evaluate(self, metrics_collector: MetricsCollector) -> bool:
        stats = metrics_collector.get_metric_stats(self.metric_name, self.duration_minutes)
        if not stats:
            return False
        
        current_value = stats.get("avg", 0)
        
        if self.comparison == "greater":
            return current_value > self.threshold
        elif self.comparison == "less":
            return current_value < self.threshold
        elif self.comparison == "equal":
            return abs(current_value - self.threshold) < 0.001
        
        return False
    
    def get_message(self, metrics_collector: MetricsCollector) -> str:
        stats = metrics_collector.get_metric_stats(self.metric_name, self.duration_minutes)
        current_value = stats.get("avg", 0) if stats else 0
        return f"{self.metric_name} is {current_value:.2f}, threshold is {self.threshold}"

class HealthChecker:
    """Health check system for pipeline components"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.health_checks = {}
        self.last_check_results = {}
    
    def register_health_check(self, name: str, check_func: Callable[[], bool], interval_seconds: int = 60):
        """Register a health check"""
        self.health_checks[name] = {
            "func": check_func,
            "interval": interval_seconds,
            "last_check": 0
        }
    
    def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        current_time = time.time()
        
        for name, check_config in self.health_checks.items():
            if current_time - check_config["last_check"] >= check_config["interval"]:
                try:
                    is_healthy = check_config["func"]()
                    results[name] = {
                        "healthy": is_healthy,
                        "last_check": datetime.now().isoformat(),
                        "error": None
                    }
                    self.metrics_collector.record_metric(f"health_check_{name}", 1 if is_healthy else 0)
                    check_config["last_check"] = current_time
                except Exception as e:
                    results[name] = {
                        "healthy": False,
                        "last_check": datetime.now().isoformat(),
                        "error": str(e)
                    }
                    self.metrics_collector.record_metric(f"health_check_{name}", 0)
            else:
                # Use cached result
                results[name] = self.last_check_results.get(name, {"healthy": False, "error": "Not yet checked"})
        
        self.last_check_results = results
        return results

class DashboardData:
    """Provides data for monitoring dashboards"""
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager, health_checker: HealthChecker):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.health_checker = health_checker
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        return {
            "system_metrics": self._get_system_metrics(),
            "pipeline_metrics": self._get_pipeline_metrics(),
            "active_alerts": [self._serialize_alert(alert) for alert in self.alert_manager.get_active_alerts()],
            "health_status": self.health_checker.run_health_checks(),
            "performance_summary": self._get_performance_summary(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics summary"""
        return {
            "cpu_usage": self.metrics_collector.get_metric_stats("system_cpu_usage", 60),
            "memory_usage": self.metrics_collector.get_metric_stats("system_memory_usage", 60),
            "disk_usage": self.metrics_collector.get_metric_stats("system_disk_usage", 60)
        }
    
    def _get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get pipeline metrics summary"""
        return {
            "tickets_processed": self.metrics_collector.get_metric_stats("pipeline_tickets_success", 1440),  # 24 hours
            "tickets_failed": self.metrics_collector.get_metric_stats("pipeline_tickets_failed", 1440),
            "average_processing_time": self.metrics_collector.get_metric_stats("pipeline_ticket_duration", 1440),
            "active_tickets": self.metrics_collector.get_metric_stats("pipeline_active_tickets", 60)
        }
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        agents = ["router", "coder", "reviewer", "qa_agent"]
        agent_performance = {}
        
        for agent in agents:
            agent_performance[agent] = {
                "avg_duration": self.metrics_collector.get_metric_stats(f"agent_{agent}_duration", 1440),
                "success_rate": self._calculate_success_rate(agent)
            }
        
        return {
            "agent_performance": agent_performance,
            "api_performance": self._get_api_performance()
        }
    
    def _calculate_success_rate(self, agent: str) -> float:
        """Calculate success rate for an agent"""
        success_stats = self.metrics_collector.get_metric_stats(f"agent_{agent}_success", 1440)
        failure_stats = self.metrics_collector.get_metric_stats(f"agent_{agent}_failure", 1440)
        
        total_success = success_stats.get("count", 0)
        total_failure = failure_stats.get("count", 0)
        total = total_success + total_failure
        
        return (total_success / total * 100) if total > 0 else 0
    
    def _get_api_performance(self) -> Dict[str, Any]:
        """Get API performance metrics"""
        return {
            "openai_api": self.metrics_collector.get_metric_stats("api_call_duration", 1440),
            "github_api": self.metrics_collector.get_metric_stats("api_call_duration", 1440),
            "jira_api": self.metrics_collector.get_metric_stats("api_call_duration", 1440)
        }
    
    def _serialize_alert(self, alert: Alert) -> Dict[str, Any]:
        """Serialize alert for JSON output"""
        return {
            "name": alert.name,
            "level": alert.level.value,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "source": alert.source,
            "labels": alert.labels,
            "resolved": alert.resolved
        }

# Notification handlers
def slack_notification_handler(webhook_url: str):
    """Create Slack notification handler"""
    def handler(alert: Alert):
        try:
            import requests
            
            color_map = {
                AlertLevel.INFO: "good",
                AlertLevel.WARNING: "warning", 
                AlertLevel.ERROR: "danger",
                AlertLevel.CRITICAL: "danger"
            }
            
            payload = {
                "attachments": [{
                    "color": color_map.get(alert.level, "warning"),
                    "title": f"Pipeline Alert: {alert.name}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Level", "value": alert.level.value, "short": True},
                        {"title": "Source", "value": alert.source, "short": True},
                        {"title": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    return handler

def email_notification_handler(smtp_config: Dict[str, str]):
    """Create email notification handler"""
    def handler(alert: Alert):
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from']
            msg['To'] = smtp_config['to']
            msg['Subject'] = f"Pipeline Alert: {alert.name} ({alert.level.value.upper()})"
            
            body = f"""
Pipeline Alert Notification

Alert: {alert.name}
Level: {alert.level.value.upper()}
Message: {alert.message}
Source: {alert.source}
Time: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Labels: {alert.labels}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_config['host'], int(smtp_config['port']))
            server.starttls()
            server.login(smtp_config['user'], smtp_config['password'])
            server.sendmail(smtp_config['from'], smtp_config['to'], msg.as_string())
            server.quit()
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    return handler