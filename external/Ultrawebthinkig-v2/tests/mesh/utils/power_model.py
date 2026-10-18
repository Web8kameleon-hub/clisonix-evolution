"""
EuroWeb Ultra - Power Model Utilities
Calculates storage requirements for mesh offline operations
"""

def estimate_storage_bytes(hours: int, rate_per_minute: int, avg_msg_bytes: int) -> int:
    """
    Estimate storage bytes needed for offline operation
    
    Args:
        hours: Hours of offline operation (typically 72h for aviation)
        rate_per_minute: Messages per minute
        avg_msg_bytes: Average message size in bytes
    
    Returns:
        Total bytes needed for storage
    """
    minutes = hours * 60
    total_messages = minutes * rate_per_minute
    total_bytes = total_messages * avg_msg_bytes
    
    # Add 20% buffer for headers, metadata, and safety margin
    buffer_multiplier = 1.2
    return int(total_bytes * buffer_multiplier)

def mb(bytes_value: int) -> float:
    """Convert bytes to megabytes"""
    return bytes_value / (1024 * 1024)

def gb(bytes_value: int) -> float:
    """Convert bytes to gigabytes"""
    return bytes_value / (1024 * 1024 * 1024)

def format_storage(bytes_value: int) -> str:
    """Format storage size in human readable format"""
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024 * 1024:
        return f"{bytes_value / 1024:.2f} KB"
    elif bytes_value < 1024 * 1024 * 1024:
        return f"{mb(bytes_value):.2f} MB"
    else:
        return f"{gb(bytes_value):.2f} GB"
