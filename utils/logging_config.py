"""
Logging configuration for Med42 service
Centralized logging setup with medical data sanitization
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from .validation import sanitize_medical_text


class MedicalDataFilter(logging.Filter):
    """Logging filter to sanitize PHI from log messages"""

    def __init__(self, enable_phi_filtering: bool = True):
        self.enable_phi_filtering = enable_phi_filtering

    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            if self.enable_phi_filtering:
                record.msg = sanitize_medical_text(record.msg)
        return True


class Med42Formatter(logging.Formatter):
    """Custom formatter for Med42 service logs"""

    def format(self, record):
        # Add service identifier
        if not hasattr(record, 'service'):
            record.service = 'med42'

        # Format the message
        message = super().format(record)

        # Add additional context for medical logs
        if hasattr(record, 'request_id'):
            message = f"[{record.request_id}] {message}"

        return message


def setup_logging(log_dir: str, log_level: str = "INFO",
                 enable_phi_filtering: bool = True) -> logging.Logger:
    """Setup comprehensive logging for Med42 service"""

    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger('med42')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatters
    formatter = Med42Formatter(
        '%(asctime)s | %(levelname)s | %(service)s | %(name)s | %(message)s'
    )

    # File handler for all logs
    all_log_file = os.path.join(log_dir, "med42_service.log")
    file_handler = logging.handlers.RotatingFileHandler(
        all_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(MedicalDataFilter(enable_phi_filtering))
    logger.addHandler(file_handler)

    # Access log handler
    access_log_file = os.path.join(log_dir, "access.log")
    access_handler = logging.handlers.RotatingFileHandler(
        access_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    access_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s'
    )
    access_handler.setFormatter(access_formatter)
    access_handler.setLevel(logging.INFO)
    logger.addHandler(access_handler)

    # Error log handler
    error_log_file = os.path.join(log_dir, "error.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.WARNING)
    error_handler.addFilter(MedicalDataFilter(enable_phi_filtering))
    logger.addHandler(error_handler)

    # Console handler for development
    if os.environ.get('FLASK_ENV') == 'development':
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.addFilter(MedicalDataFilter(enable_phi_filtering))
        logger.addHandler(console_handler)

    return logger


def get_request_logger(request_id: str) -> logging.LoggerAdapter:
    """Get a logger adapter with request ID context"""
    logger = logging.getLogger('med42')
    return logging.LoggerAdapter(logger, {'request_id': request_id})


def log_analysis_request(logger, request_data: dict, remote_addr: str):
    """Log analysis request with sanitized data"""
    sanitized_prompt = sanitize_medical_text(request_data.get('prompt', ''))
    analysis_type = request_data.get('analysis_type', 'unknown')
    text_length = len(request_data.get('text', ''))

    logger.info(
        f"Analysis request from {remote_addr} - Type: {analysis_type}, "
        f"Text length: {text_length} chars, Prompt: {sanitized_prompt[:100]}..."
    )


def log_analysis_result(logger, request_id: str, result: dict, execution_time: float):
    """Log analysis completion with key metrics"""
    tokens_generated = result.get('tokens_generated', 0)
    model_used = result.get('model_used', 'unknown')

    logger.info(
        f"Analysis completed in {execution_time:.2f}s - "
        f"Tokens: {tokens_generated}, Model: {model_used}"
    )


def log_analysis_request(logger, request_data: dict, remote_addr: str):
    """Log analysis request with sanitized data"""
    from .validation import sanitize_medical_text

    sanitized_prompt = sanitize_medical_text(request_data.get('prompt', ''))
    analysis_type = request_data.get('analysis_type', 'unknown')
    text_length = len(request_data.get('text', ''))

    logger.info(
        f"Analysis request from {remote_addr} - Type: {analysis_type}, "
        f"Text length: {text_length} chars, Prompt: {sanitized_prompt[:100]}..."
    )
