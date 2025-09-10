"""
Logger utility for Django applications.
Adapted from Node.js winston-based logger to Python logging.
"""

import logging
import os
import sys
from typing import Any, Optional


class Logger:
    """Singleton logger class for consistent logging across the application."""
    
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup the logger based on environment."""
        if os.getenv('DJANGO_ENV') == 'production':
            self._logger = self._get_production_logger()
        else:
            self._logger = self._get_development_logger()
    
    def _get_production_logger(self) -> logging.Logger:
        """Create a production logger with structured formatting."""
        logger = logging.getLogger('backend')
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(name)s]%(origin)s %(levelname)s: %(message)s',
            defaults={'origin': ''}
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def _get_development_logger(self) -> logging.Logger:
        """Create a development logger using Python's built-in logging."""
        logger = logging.getLogger('backend')
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create console handler with color formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        
        # Create formatter with colors
        formatter = logging.Formatter(
            '\033[36m[%(name)s]\033[0m%(origin)s \033[32m%(levelname)s\033[0m: %(message)s',
            defaults={'origin': ''}
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._logger.info(message, *args, **kwargs)
    
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._logger.error(message, *args, **kwargs)
    
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._logger.warning(message, *args, **kwargs)
    
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._logger.debug(message, *args, **kwargs)


def get_logger() -> Logger:
    """
    Get the singleton logger instance.
    
    Returns:
        Logger: The logger instance
    """
    return Logger()


# Convenience functions for direct logging
def log_info(message: str, *args: Any, **kwargs: Any) -> None:
    """Log an info message."""
    get_logger().info(message, *args, **kwargs)


def log_error(message: str, *args: Any, **kwargs: Any) -> None:
    """Log an error message."""
    get_logger().error(message, *args, **kwargs)


def log_warning(message: str, *args: Any, **kwargs: Any) -> None:
    """Log a warning message."""
    get_logger().warning(message, *args, **kwargs)


def log_debug(message: str, *args: Any, **kwargs: Any) -> None:
    """Log a debug message."""
    get_logger().debug(message, *args, **kwargs)