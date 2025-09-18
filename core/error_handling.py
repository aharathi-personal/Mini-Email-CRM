"""
Enhanced Error Handling System for Mini Email CRM
Task 22: Robust error handling with recovery mechanisms

This module provides comprehensive error handling for edge cases,
recovery mechanisms, and graceful failure handling.
"""

import os
import traceback
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum

import logging
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better handling"""
    FILE_ACCESS = "file_access"
    NETWORK = "network"
    VALIDATION = "validation"
    CORRUPTION = "corruption"
    PERMISSION = "permission"
    RESOURCE = "resource"
    SECURITY = "security"
    EMAIL = "email"
    ATTACHMENT = "attachment"
    SYSTEM = "system"


class RecoveryAction(Enum):
    """Available recovery actions"""
    RETRY = "retry"
    SKIP = "skip"
    ABORT = "abort"
    IGNORE = "ignore"
    QUARANTINE = "quarantine"
    REPLACE = "replace"
    MANUAL = "manual"


class ErrorContext:
    """Context information for errors"""
    
    def __init__(self, operation: str, file_path: str = None, email: str = None):
        self.operation = operation
        self.file_path = file_path
        self.email = email
        self.timestamp = datetime.now()
        self.additional_info = {}
    
    def add_info(self, key: str, value: Any):
        """Add additional context information"""
        self.additional_info[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'operation': self.operation,
            'file_path': self.file_path,
            'email': self.email,
            'timestamp': self.timestamp.isoformat(),
            'additional_info': self.additional_info
        }


class CRMError(Exception):
    """Base exception for CRM-specific errors"""
    
    def __init__(self, message: str, category: ErrorCategory, severity: ErrorSeverity,
                 context: ErrorContext = None, recoverable: bool = True,
                 suggested_actions: List[RecoveryAction] = None):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.context = context
        self.recoverable = recoverable
        self.suggested_actions = suggested_actions or []
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/display"""
        return {
            'message': str(self),
            'category': self.category.value,
            'severity': self.severity.value,
            'recoverable': self.recoverable,
            'suggested_actions': [action.value for action in self.suggested_actions],
            'timestamp': self.timestamp.isoformat(),
            'context': self.context.to_dict() if self.context else None
        }


class FileAccessError(CRMError):
    """File access related errors"""
    
    def __init__(self, message: str, file_path: str, operation: str):
        context = ErrorContext(operation, file_path=file_path)
        super().__init__(
            message, 
            ErrorCategory.FILE_ACCESS, 
            ErrorSeverity.MEDIUM,
            context,
            recoverable=True,
            suggested_actions=[RecoveryAction.RETRY, RecoveryAction.REPLACE, RecoveryAction.SKIP]
        )


class NetworkError(CRMError):
    """Network related errors"""
    
    def __init__(self, message: str, operation: str, email: str = None):
        context = ErrorContext(operation, email=email)
        super().__init__(
            message,
            ErrorCategory.NETWORK,
            ErrorSeverity.HIGH,
            context,
            recoverable=True,
            suggested_actions=[RecoveryAction.RETRY, RecoveryAction.SKIP]
        )


class AttachmentError(CRMError):
    """Attachment specific errors"""
    
    def __init__(self, message: str, file_path: str, operation: str):
        context = ErrorContext(operation, file_path=file_path)
        super().__init__(
            message,
            ErrorCategory.ATTACHMENT,
            ErrorSeverity.MEDIUM,
            context,
            recoverable=True,
            suggested_actions=[RecoveryAction.QUARANTINE, RecoveryAction.SKIP, RecoveryAction.REPLACE]
        )


class SecurityError(CRMError):
    """Security related errors"""
    
    def __init__(self, message: str, file_path: str, operation: str):
        context = ErrorContext(operation, file_path=file_path)
        super().__init__(
            message,
            ErrorCategory.SECURITY,
            ErrorSeverity.CRITICAL,
            context,
            recoverable=False,
            suggested_actions=[RecoveryAction.QUARANTINE, RecoveryAction.ABORT]
        )


class ErrorHandler:
    """
    Comprehensive error handling system
    Task 22: Provides robust error handling with recovery mechanisms
    """
    
    def __init__(self):
        self.error_history = []
        self.retry_policies = {}
        self.recovery_handlers = {}
        self.max_history = 1000
        self.setup_default_policies()
    
    def setup_default_policies(self):
        """Setup default retry and recovery policies"""
        
        # Network retry policy - exponential backoff
        self.retry_policies[ErrorCategory.NETWORK] = {
            'max_attempts': 3,
            'base_delay': 1.0,
            'max_delay': 30.0,
            'exponential': True
        }
        
        # File access retry policy
        self.retry_policies[ErrorCategory.FILE_ACCESS] = {
            'max_attempts': 2,
            'base_delay': 0.5,
            'max_delay': 5.0,
            'exponential': False
        }
        
        # Attachment retry policy
        self.retry_policies[ErrorCategory.ATTACHMENT] = {
            'max_attempts': 1,
            'base_delay': 0.0,
            'max_delay': 0.0,
            'exponential': False
        }
        
        # No retry for security issues
        self.retry_policies[ErrorCategory.SECURITY] = {
            'max_attempts': 0,
            'base_delay': 0.0,
            'max_delay': 0.0,
            'exponential': False
        }
    
    def handle_error(self, error: Exception, context: ErrorContext = None) -> Dict[str, Any]:
        """
        Handle error with appropriate recovery strategy
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            
        Returns:
            Dictionary with error information and suggested recovery
        """
        
        # Convert to CRM error if needed
        if not isinstance(error, CRMError):
            crm_error = self._convert_to_crm_error(error, context)
        else:
            crm_error = error
        
        # Log the error
        self._log_error(crm_error)
        
        # Add to history
        self.error_history.append(crm_error)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Determine recovery strategy
        recovery_info = self._determine_recovery_strategy(crm_error)
        
        return {
            'error': crm_error.to_dict(),
            'recovery': recovery_info
        }
    
    def _convert_to_crm_error(self, error: Exception, context: ErrorContext = None) -> CRMError:
        """Convert generic exception to CRM error"""
        
        error_msg = str(error)
        error_type = type(error).__name__
        
        # Determine category based on error type and message
        category = ErrorCategory.SYSTEM
        severity = ErrorSeverity.MEDIUM
        suggested_actions = [RecoveryAction.RETRY, RecoveryAction.ABORT]
        
        if isinstance(error, (OSError, IOError, FileNotFoundError, PermissionError)):
            category = ErrorCategory.FILE_ACCESS
            if isinstance(error, PermissionError):
                category = ErrorCategory.PERMISSION
                severity = ErrorSeverity.HIGH
                suggested_actions = [RecoveryAction.MANUAL, RecoveryAction.SKIP]
        
        elif isinstance(error, (ConnectionError, TimeoutError)):
            category = ErrorCategory.NETWORK
            severity = ErrorSeverity.HIGH
            suggested_actions = [RecoveryAction.RETRY, RecoveryAction.SKIP]
        
        elif "attachment" in error_msg.lower() or "file" in error_msg.lower():
            category = ErrorCategory.ATTACHMENT
            
        elif "email" in error_msg.lower() or "smtp" in error_msg.lower():
            category = ErrorCategory.EMAIL
            severity = ErrorSeverity.HIGH
            
        elif "security" in error_msg.lower() or "dangerous" in error_msg.lower():
            category = ErrorCategory.SECURITY
            severity = ErrorSeverity.CRITICAL
            suggested_actions = [RecoveryAction.QUARANTINE, RecoveryAction.ABORT]
        
        elif "corrupt" in error_msg.lower() or "invalid" in error_msg.lower():
            category = ErrorCategory.CORRUPTION
            suggested_actions = [RecoveryAction.QUARANTINE, RecoveryAction.REPLACE, RecoveryAction.SKIP]
        
        return CRMError(
            f"{error_type}: {error_msg}",
            category,
            severity,
            context,
            recoverable=True,
            suggested_actions=suggested_actions
        )
    
    def _log_error(self, error: CRMError):
        """Log error with appropriate level"""
        
        message = getattr(error, 'message', str(error))
        log_msg = f"[{error.category.value}] {message}"
        if error.context:
            log_msg += f" (Operation: {error.context.operation}"
            if error.context.file_path:
                log_msg += f", File: {error.context.file_path}"
            if error.context.email:
                log_msg += f", Email: {error.context.email}"
            log_msg += ")"
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_msg)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_msg)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
    
    def _determine_recovery_strategy(self, error: CRMError) -> Dict[str, Any]:
        """Determine recovery strategy for error"""
        
        recovery_info = {
            'can_retry': error.recoverable and error.category in self.retry_policies,
            'retry_policy': self.retry_policies.get(error.category, {}),
            'suggested_actions': error.suggested_actions,
            'user_message': self._generate_user_message(error),
            'technical_details': error.to_dict()
        }
        
        # Add specific recovery suggestions based on error category
        if error.category == ErrorCategory.FILE_ACCESS:
            recovery_info['suggestions'] = [
                "Check if the file still exists",
                "Verify file permissions",
                "Try selecting the file again",
                "Contact system administrator if problem persists"
            ]
        
        elif error.category == ErrorCategory.NETWORK:
            recovery_info['suggestions'] = [
                "Check internet connection",
                "Verify email server settings",
                "Try again in a few moments",
                "Contact IT support if problem continues"
            ]
        
        elif error.category == ErrorCategory.ATTACHMENT:
            recovery_info['suggestions'] = [
                "Try removing and re-adding the attachment",
                "Check if file is corrupted",
                "Verify file is not too large",
                "Use a different file format if possible"
            ]
        
        elif error.category == ErrorCategory.SECURITY:
            recovery_info['suggestions'] = [
                "File has been flagged as potentially dangerous",
                "Do not proceed with this file",
                "Contact security team if file is business-critical",
                "Use a different file or scan with antivirus"
            ]
        
        elif error.category == ErrorCategory.EMAIL:
            recovery_info['suggestions'] = [
                "Check recipient email address",
                "Verify email server configuration",
                "Reduce attachment size if possible",
                "Try sending to a different email first"
            ]
        
        return recovery_info
    
    def _generate_user_message(self, error: CRMError) -> str:
        """Generate user-friendly error message"""
        
        error_message = str(error)  # Use str() instead of error.message
        
        if error.category == ErrorCategory.FILE_ACCESS:
            return f"Unable to access file. Please check if the file exists and you have permission to read it."
        
        elif error.category == ErrorCategory.NETWORK:
            return f"Network connection problem. Please check your internet connection and try again."
        
        elif error.category == ErrorCategory.ATTACHMENT:
            return f"Problem with attachment file. The file may be corrupted or in an unsupported format."
        
        elif error.category == ErrorCategory.SECURITY:
            return f"Security issue detected. This file type may be dangerous and cannot be processed."
        
        elif error.category == ErrorCategory.EMAIL:
            return f"Email sending failed. Please check the recipient address and email settings."
        
        elif error.category == ErrorCategory.CORRUPTION:
            return f"File appears to be corrupted or in an invalid format."
        
        elif error.category == ErrorCategory.PERMISSION:
            return f"Permission denied. You may not have sufficient rights to perform this operation."
        
        else:
            return f"An unexpected error occurred: {error_message}"
    
    def retry_with_backoff(self, operation: Callable, error_category: ErrorCategory,
                          context: ErrorContext = None, *args, **kwargs) -> Any:
        """
        Retry operation with backoff policy
        
        Args:
            operation: Function to retry
            error_category: Category for retry policy
            context: Error context
            *args, **kwargs: Arguments for operation
            
        Returns:
            Result of successful operation
            
        Raises:
            Last exception if all retries failed
        """
        
        policy = self.retry_policies.get(error_category, {'max_attempts': 1})
        max_attempts = policy['max_attempts']
        base_delay = policy.get('base_delay', 1.0)
        max_delay = policy.get('max_delay', 30.0)
        exponential = policy.get('exponential', True)
        
        last_exception = None
        
        for attempt in range(max_attempts + 1):
            try:
                return operation(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                if attempt < max_attempts:
                    # Calculate delay
                    if exponential:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                    else:
                        delay = base_delay
                    
                    logger.info(f"Retry {attempt + 1}/{max_attempts} after {delay}s delay")
                    time.sleep(delay)
                else:
                    # Final attempt failed
                    error_info = self.handle_error(e, context)
                    logger.error(f"All retry attempts failed: {error_info}")
        
        raise last_exception
    
    def handle_large_file_error(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Handle large file specific errors"""
        
        context = ErrorContext("large_file_handling", file_path=file_path)
        context.add_info("file_size", file_size)
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            error = CRMError(
                f"File too large: {file_size / (1024*1024):.1f}MB (maximum: 100MB)",
                ErrorCategory.RESOURCE,
                ErrorSeverity.HIGH,
                context,
                recoverable=False,
                suggested_actions=[RecoveryAction.REPLACE, RecoveryAction.SKIP]
            )
        else:
            error = CRMError(
                f"File size warning: {file_size / (1024*1024):.1f}MB",
                ErrorCategory.RESOURCE,
                ErrorSeverity.MEDIUM,
                context,
                recoverable=True,
                suggested_actions=[RecoveryAction.IGNORE, RecoveryAction.REPLACE]
            )
        
        return self.handle_error(error, context)
    
    def handle_corrupt_file_error(self, file_path: str, corruption_details: str) -> Dict[str, Any]:
        """Handle corrupted file errors"""
        
        context = ErrorContext("corruption_detection", file_path=file_path)
        context.add_info("corruption_details", corruption_details)
        
        error = AttachmentError(
            f"File corruption detected: {corruption_details}",
            file_path,
            "corruption_detection"
        )
        
        return self.handle_error(error, context)
    
    def handle_network_timeout_error(self, operation: str, email: str = None, timeout_duration: float = None) -> Dict[str, Any]:
        """Handle network timeout errors"""
        
        context = ErrorContext(operation, email=email)
        if timeout_duration:
            context.add_info("timeout_duration", timeout_duration)
        
        error = NetworkError(
            f"Network timeout during {operation}",
            operation,
            email
        )
        
        return self.handle_error(error, context)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        
        if not self.error_history:
            return {"total_errors": 0}
        
        stats = {
            "total_errors": len(self.error_history),
            "by_category": {},
            "by_severity": {},
            "recent_errors": len([e for e in self.error_history 
                                if e.timestamp > datetime.now() - timedelta(hours=1)]),
            "recoverable_errors": len([e for e in self.error_history if e.recoverable]),
            "critical_errors": len([e for e in self.error_history 
                                  if e.severity == ErrorSeverity.CRITICAL])
        }
        
        # Count by category
        for error in self.error_history:
            category = error.category.value
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        # Count by severity
        for error in self.error_history:
            severity = error.severity.value
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
        
        return stats
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        logger.info("Error history cleared")
    
    def register_recovery_handler(self, category: ErrorCategory, handler: Callable):
        """Register custom recovery handler for error category"""
        self.recovery_handlers[category] = handler
        logger.info(f"Recovery handler registered for {category.value}")


# Global error handler instance
error_handler = ErrorHandler()


def handle_crm_error(func):
    """Decorator for automatic error handling"""
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = ErrorContext(func.__name__)
            error_info = error_handler.handle_error(e, context)
            
            # Re-raise with additional context
            raise CRMError(
                f"Error in {func.__name__}: {str(e)}",
                ErrorCategory.SYSTEM,
                ErrorSeverity.MEDIUM,
                context
            ) from e
    
    return wrapper


def safe_file_operation(operation: Callable, file_path: str, *args, **kwargs) -> Any:
    """Safely execute file operation with error handling"""
    
    context = ErrorContext("file_operation", file_path=file_path)
    
    try:
        return error_handler.retry_with_backoff(
            operation,
            ErrorCategory.FILE_ACCESS,
            context,
            *args,
            **kwargs
        )
    except Exception as e:
        error_info = error_handler.handle_error(e, context)
        raise CRMError(
            f"File operation failed: {str(e)}",
            ErrorCategory.FILE_ACCESS,
            ErrorSeverity.MEDIUM,
            context
        ) from e


def safe_network_operation(operation: Callable, operation_name: str, *args, **kwargs) -> Any:
    """Safely execute network operation with error handling"""
    
    context = ErrorContext(operation_name)
    
    try:
        return error_handler.retry_with_backoff(
            operation,
            ErrorCategory.NETWORK,
            context,
            *args,
            **kwargs
        )
    except Exception as e:
        error_info = error_handler.handle_error(e, context)
        raise NetworkError(
            f"Network operation failed: {str(e)}",
            operation_name
        ) from e