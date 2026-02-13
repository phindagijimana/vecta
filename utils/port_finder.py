"""
Port Finder Utility for Vecta AI
Finds free port between 8085-8150
"""
import socket
import logging

logger = logging.getLogger("vectaai.port")


def is_port_free(port: int) -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.bind(('0.0.0.0', port))
            return True
    except (socket.error, OSError):
        return False


def find_free_port(start_port: int = 8085, end_port: int = 8150) -> int:
    """
    Find a free port in the specified range
    
    Args:
        start_port: Starting port number (default: 8085)
        end_port: Ending port number (default: 8150)
    
    Returns:
        Free port number, or start_port if none found
    """
    # Try the start port first
    if is_port_free(start_port):
        logger.info(f"Port {start_port} is available")
        return start_port
    
    logger.warning(f"Port {start_port} is in use, searching for free port...")
    
    # Search for free port in range
    for port in range(start_port + 1, end_port + 1):
        if is_port_free(port):
            logger.info(f"Found free port: {port}")
            return port
    
    # If no free port found, return start port anyway
    logger.error(f"No free ports found in range {start_port}-{end_port}")
    return start_port


if __name__ == "__main__":
    # Test port finder
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Port Finder...")
    print(f"Default port (8085) free: {is_port_free(8085)}")
    
    free_port = find_free_port(8085, 8150)
    print(f"Found free port: {free_port}")
