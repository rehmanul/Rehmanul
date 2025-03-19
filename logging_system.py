"""Logging system module"""
import time
from functools import wraps
from typing import Optional, Callable, Any

class LogRepository:
    def log_error(self, url: str, extraction_id: str, error_type: str, message: str, stack_trace: str = None):
        """Log an error"""
        print(f"ERROR [{error_type}] {url} ({extraction_id}): {message}")
        if stack_trace:
            print(f"Stack trace: {stack_trace}")
    
    def log_operation(self, url: str, extraction_id: str, operation: str, status: str, message: str, duration_ms: int = None):
        """Log an operation"""
        duration_info = f" ({duration_ms}ms)" if duration_ms is not None else ""
        print(f"{operation} {status}: {url} ({extraction_id}){duration_info} - {message}")

def log_execution_time() -> Callable:
    """Decorator to log execution time of functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)
            print(f"{func.__name__} executed in {duration_ms}ms")
            return result
        return wrapper
    return decorator

# Create singleton instance
log_repository = LogRepository()
