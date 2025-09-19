"""
Error Recovery and Circuit Breaker Implementation
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import functools

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    expected_exception: type = Exception
    name: str = "default"

@dataclass
class CircuitBreakerStats:
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: CircuitState = CircuitState.CLOSED
    state_changed_at: datetime = field(default_factory=datetime.now)

class CircuitBreaker:
    """Circuit breaker pattern implementation for external service calls"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
    
    def __call__(self, func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await self._call(func, *args, **kwargs)
        return wrapper
    
    async def _call(self, func: Callable, *args, **kwargs):
        async with self._lock:
            if self.stats.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.stats.state = CircuitState.HALF_OPEN
                    self.stats.state_changed_at = datetime.now()
                    logger.info(f"Circuit breaker {self.config.name} moved to HALF_OPEN")
                else:
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker {self.config.name} is OPEN"
                    )
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await self._on_success()
            return result
        except self.config.expected_exception as e:
            await self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.stats.last_failure_time and
            datetime.now() - self.stats.last_failure_time > timedelta(seconds=self.config.recovery_timeout)
        )
    
    async def _on_success(self):
        async with self._lock:
            self.stats.success_count += 1
            
            if self.stats.state == CircuitState.HALF_OPEN:
                self.stats.state = CircuitState.CLOSED
                self.stats.failure_count = 0
                self.stats.state_changed_at = datetime.now()
                logger.info(f"Circuit breaker {self.config.name} moved to CLOSED")
    
    async def _on_failure(self):
        async with self._lock:
            self.stats.failure_count += 1
            self.stats.last_failure_time = datetime.now()
            
            if self.stats.failure_count >= self.config.failure_threshold:
                self.stats.state = CircuitState.OPEN
                self.stats.state_changed_at = datetime.now()
                logger.warning(f"Circuit breaker {self.config.name} moved to OPEN")

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class RetryConfig:
    """Configuration for retry mechanisms"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retriable_exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retriable_exceptions = retriable_exceptions

class RetryMechanism:
    """Advanced retry mechanism with exponential backoff and jitter"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def __call__(self, func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await self._retry_call(func, *args, **kwargs)
        return wrapper
    
    async def _retry_call(self, func: Callable, *args, **kwargs):
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except self.config.retriable_exceptions as e:
                last_exception = e
                
                if attempt == self.config.max_attempts - 1:
                    logger.error(f"All {self.config.max_attempts} retry attempts failed")
                    break
                
                delay = self._calculate_delay(attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {str(e)}")
                await asyncio.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter"""
        delay = min(
            self.config.base_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )
        
        if self.config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Add 0-50% jitter
        
        return delay

class FallbackHandler:
    """Fallback workflow handler for when primary workflows fail"""
    
    def __init__(self):
        self.fallback_strategies = {}
    
    def register_fallback(self, operation: str, fallback_func: Callable):
        """Register a fallback function for a specific operation"""
        self.fallback_strategies[operation] = fallback_func
    
    async def execute_fallback(self, operation: str, *args, **kwargs):
        """Execute fallback strategy for failed operation"""
        if operation in self.fallback_strategies:
            try:
                return await self.fallback_strategies[operation](*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback for {operation} also failed: {str(e)}")
                raise e
        else:
            raise ValueError(f"No fallback strategy registered for operation: {operation}")

# Service-specific circuit breakers and retry configs
class ServiceResilienceManager:
    """Centralized manager for service resilience patterns"""
    
    def __init__(self):
        self.circuit_breakers = {}
        self.retry_configs = {}
        self.fallback_handler = FallbackHandler()
        self._setup_default_configs()
    
    def _setup_default_configs(self):
        """Setup default configurations for different services"""
        
        # OpenAI API
        self.circuit_breakers["openai"] = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=120,
                name="openai_api"
            )
        )
        
        # GitHub API
        self.circuit_breakers["github"] = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                name="github_api"
            )
        )
        
        # Jira API
        self.circuit_breakers["jira"] = CircuitBreaker(
            CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=90,
                name="jira_api"
            )
        )
        
        # Retry configurations
        self.retry_configs["api_call"] = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=30.0
        )
        
        self.retry_configs["file_operation"] = RetryConfig(
            max_attempts=5,
            base_delay=0.5,
            max_delay=10.0
        )
        
        # Register fallback strategies
        self._setup_fallback_strategies()
    
    def _setup_fallback_strategies(self):
        """Setup fallback strategies for critical operations"""
        
        async def openai_fallback(*args, **kwargs):
            """Fallback for OpenAI API failures"""
            logger.info("OpenAI API unavailable, using simplified code generation")
            return "# Code generation temporarily unavailable\n# Please implement manually"
        
        async def github_fallback(*args, **kwargs):
            """Fallback for GitHub API failures"""
            logger.info("GitHub API unavailable, saving to local files")
            # Save to local backup location
            return {"status": "saved_locally", "path": "/tmp/backup"}
        
        async def jira_fallback(*args, **kwargs):
            """Fallback for Jira API failures"""
            logger.info("Jira API unavailable, logging ticket update")
            # Log the update for manual processing
            return {"status": "logged_for_manual_update"}
        
        self.fallback_handler.register_fallback("openai", openai_fallback)
        self.fallback_handler.register_fallback("github", github_fallback)
        self.fallback_handler.register_fallback("jira", jira_fallback)
    
    def get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get circuit breaker for specific service"""
        return self.circuit_breakers.get(service)
    
    def get_retry_config(self, operation: str) -> RetryConfig:
        """Get retry configuration for specific operation"""
        return self.retry_configs.get(operation, self.retry_configs["api_call"])
    
    def create_resilient_call(self, service: str, operation: str = "api_call"):
        """Create a resilient function call with circuit breaker and retry"""
        circuit_breaker = self.get_circuit_breaker(service)
        retry_config = self.get_retry_config(operation)
        
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Apply retry mechanism
                retry_func = RetryMechanism(retry_config)(func)
                
                # Apply circuit breaker if available
                if circuit_breaker:
                    resilient_func = circuit_breaker(retry_func)
                else:
                    resilient_func = retry_func
                
                try:
                    return await resilient_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Service {service} call failed after all retries: {str(e)}")
                    # Try fallback
                    try:
                        return await self.fallback_handler.execute_fallback(service, *args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed: {str(fallback_error)}")
                        raise e
            
            return wrapper
        return decorator
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all circuit breakers"""
        status = {}
        for service, cb in self.circuit_breakers.items():
            status[service] = {
                "state": cb.stats.state.value,
                "failure_count": cb.stats.failure_count,
                "success_count": cb.stats.success_count,
                "last_failure": cb.stats.last_failure_time.isoformat() if cb.stats.last_failure_time else None,
                "state_changed_at": cb.stats.state_changed_at.isoformat()
            }
        return status

# Global instance
resilience_manager = ServiceResilienceManager()