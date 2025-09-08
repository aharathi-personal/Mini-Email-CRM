"""
Core package for Mini Email CRM
Business logic and processing components
"""

from .csv_handler import CSVHandler, CSVValidationError

__all__ = [
    'CSVHandler',
    'CSVValidationError'
]