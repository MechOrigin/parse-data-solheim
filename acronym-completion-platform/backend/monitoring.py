import time
import logging
import psutil
import os
from functools import wraps
from typing import Callable, Any
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("acronym-platform")

# Performance metrics storage
metrics = {
    "api_calls": {},
    "processing_times": {},
    "memory_usage": [],
    "cpu_usage": [],
    "errors": []
}

def log_metrics():
    """Log current system metrics"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    metrics["memory_usage"].append({
        "timestamp": datetime.now().isoformat(),
        "rss": memory_info.rss / 1024 / 1024,  # MB
        "vms": memory_info.vms / 1024 / 1024   # MB
    })
    
    metrics["cpu_usage"].append({
        "timestamp": datetime.now().isoformat(),
        "percent": process.cpu_percent(interval=1)
    })
    
    # Keep only the last 1000 measurements
    if len(metrics["memory_usage"]) > 1000:
        metrics["memory_usage"] = metrics["memory_usage"][-1000:]
    if len(metrics["cpu_usage"]) > 1000:
        metrics["cpu_usage"] = metrics["cpu_usage"][-1000:]

def track_performance(func: Callable) -> Callable:
    """Decorator to track function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        func_name = func.__name__
        
        try:
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Update metrics
            if func_name not in metrics["processing_times"]:
                metrics["processing_times"][func_name] = []
            
            metrics["processing_times"][func_name].append(execution_time)
            
            # Log performance
            logger.info(f"Function {func_name} executed in {execution_time:.4f} seconds")
            
            return result
        except Exception as e:
            # Log error
            error_info = {
                "timestamp": datetime.now().isoformat(),
                "function": func_name,
                "error": str(e)
            }
            metrics["errors"].append(error_info)
            logger.error(f"Error in {func_name}: {str(e)}")
            raise
    
    return wrapper

def track_api_call(endpoint: str):
    """Decorator to track API endpoint calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if endpoint not in metrics["api_calls"]:
                metrics["api_calls"][endpoint] = 0
            
            metrics["api_calls"][endpoint] += 1
            logger.info(f"API call to {endpoint}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def get_performance_metrics():
    """Get current performance metrics"""
    # Log current system metrics
    log_metrics()
    
    # Calculate averages
    avg_processing_times = {}
    for func_name, times in metrics["processing_times"].items():
        if times:
            avg_processing_times[func_name] = sum(times) / len(times)
    
    # Get latest memory and CPU usage
    latest_memory = metrics["memory_usage"][-1] if metrics["memory_usage"] else None
    latest_cpu = metrics["cpu_usage"][-1] if metrics["cpu_usage"] else None
    
    # Get recent errors
    recent_errors = metrics["errors"][-10:] if metrics["errors"] else []
    
    return {
        "api_calls": metrics["api_calls"],
        "avg_processing_times": avg_processing_times,
        "memory_usage": latest_memory,
        "cpu_usage": latest_cpu,
        "recent_errors": recent_errors
    }

def save_metrics_to_file():
    """Save metrics to a JSON file"""
    with open("performance_metrics.json", "w") as f:
        json.dump(get_performance_metrics(), f, indent=2)
    
    logger.info("Performance metrics saved to file") 