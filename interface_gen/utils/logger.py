"""Logging utilities for the interface test case generator."""

import logging
import sys
from typing import Optional
from pathlib import Path

class Logger:
    """Custom logger with configurable output."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._logger = None
        return cls._instance
    
    def setup(
        self,
        log_level: int = logging.INFO,
        log_file: Optional[str] = None,
        debug: bool = False
    ):
        """Setup logger configuration."""
        if self._logger is not None:
            return
        
        # Create logger
        self._logger = logging.getLogger("interface_gen")
        self._logger.setLevel(logging.DEBUG if debug else log_level)
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)
        
        # File handler (if log_file specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)
    
    @property
    def logger(self) -> logging.Logger:
        """Get the logger instance."""
        if self._logger is None:
            self.setup()
        return self._logger

logger = Logger().logger 