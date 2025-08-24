"""
Common exception handling for TTS API
"""

from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class TTSError(Exception):
    """Base TTS exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def handle_validation_error(message: str, detail: str = None) -> HTTPException:
    """Handle validation errors with consistent logging and response"""
    logger.warning(f"Validation error: {message}")
    return HTTPException(status_code=400, detail=detail or message)

def handle_not_found_error(message: str, detail: str = None) -> HTTPException:
    """Handle not found errors with consistent logging and response"""
    logger.warning(f"Not found error: {message}")
    return HTTPException(status_code=404, detail=detail or message)

def handle_auth_error(message: str, detail: str = None) -> HTTPException:
    """Handle authentication errors with consistent logging and response"""
    logger.warning(f"Auth error: {message}")
    return HTTPException(status_code=401, detail=detail or message)

def handle_rate_limit_error(message: str, detail: str = None) -> HTTPException:
    """Handle rate limit errors with consistent logging and response"""
    logger.warning(f"Rate limit error: {message}")
    return HTTPException(status_code=429, detail=detail or message)

def handle_service_error(message: str, detail: str = None) -> HTTPException:
    """Handle service unavailable errors with consistent logging and response"""
    logger.error(f"Service error: {message}")
    return HTTPException(status_code=503, detail=detail or message)

def handle_internal_error(message: str, detail: str = None) -> HTTPException:
    """Handle internal server errors with consistent logging and response"""
    logger.error(f"Internal error: {message}")
    return HTTPException(status_code=500, detail=detail or "An unexpected error occurred. Please try again.")

def handle_file_error(error: Exception, operation: str) -> HTTPException:
    """Handle file system errors with consistent logging and response"""
    if isinstance(error, FileNotFoundError):
        logger.error(f"File not found during {operation}: {str(error)}")
        return HTTPException(status_code=500, detail=f"Failed to {operation}. Please check server configuration.")
    elif isinstance(error, PermissionError):
        logger.error(f"Permission error during {operation}: {str(error)}")
        return HTTPException(status_code=500, detail=f"Permission denied when {operation}. Please check server permissions.")
    else:
        logger.error(f"Unexpected file error during {operation}: {str(error)}")
        return HTTPException(status_code=500, detail=f"An unexpected error occurred during {operation}. Please try again.")