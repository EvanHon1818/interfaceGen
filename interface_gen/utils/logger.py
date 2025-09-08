"""Logging utilities for the interface test case generator."""

import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with the given name"""
    logger = logging.getLogger(name)
    
    # Set default level to INFO
    logger.setLevel(logging.INFO)
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create formatters and add them to the handlers
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(detailed_formatter)
    
    # Add handlers to logger if they haven't been added already
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger 