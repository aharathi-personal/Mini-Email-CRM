"""
Attachment Cleanup System for Mini Email CRM
Task 22: Automatic cleanup of attachments and temporary files

This module provides comprehensive cleanup management for attachments,
temporary files, and campaign resources with safety mechanisms.
"""

import os
import shutil
import tempfile
import atexit
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable, Any
from pathlib import Path
from contextlib import contextmanager

import logging
logger = logging.getLogger(__name__)


class CleanupPolicy:
    """Policy for cleanup operations"""
    
    def __init__(self):
        self.cleanup_on_completion = True
        self.cleanup_on_cancellation = True
        self.cleanup_on_error = True
        self.preserve_logs = True
        self.max_temp_age_hours = 24
        self.max_log_age_days = 30
        self.cleanup_interval_minutes = 60
        self.dry_run = False  # For testing
    
    def should_cleanup(self, reason: str) -> bool:
        """Check if cleanup should be performed for given reason"""
        if reason == "completion":
            return self.cleanup_on_completion
        elif reason == "cancellation":
            return self.cleanup_on_cancellation
        elif reason == "error":
            return self.cleanup_on_error
        return False


class AttachmentCleanupManager:
    """
    Manages cleanup of attachments and temporary files
    Task 22: Provides automatic cleanup with safety mechanisms
    """
    
    def __init__(self, policy: CleanupPolicy = None):
        self.policy = policy or CleanupPolicy()
        self.temp_directories = set()
        self.tracked_files = {}  # file_path -> metadata
        self.active_campaigns = set()
        self.cleanup_handlers = []
        self.cleanup_lock = threading.Lock()
        self.background_cleanup_running = False
        self.background_thread = None
        
        # Register cleanup on exit
        atexit.register(self.emergency_cleanup)
        
        logger.info("Attachment cleanup manager initialized")
    
    def register_temp_directory(self, temp_dir: str, campaign_id: str = None) -> str:
        """
        Register a temporary directory for tracking
        
        Args:
            temp_dir: Path to temporary directory
            campaign_id: Optional campaign identifier
            
        Returns:
            The registered directory path
        """
        with self.cleanup_lock:
            self.temp_directories.add(temp_dir)
            
            if campaign_id:
                self.active_campaigns.add(campaign_id)
            
            logger.info(f"Registered temp directory: {temp_dir} (campaign: {campaign_id})")
            
        return temp_dir
    
    def register_file(self, file_path: str, metadata: Dict = None, temp: bool = False):
        """
        Register a file for tracking and cleanup
        
        Args:
            file_path: Path to file
            metadata: Additional metadata about the file
            temp: Whether this is a temporary file
        """
        with self.cleanup_lock:
            self.tracked_files[file_path] = {
                'registered_at': datetime.now(),
                'metadata': metadata or {},
                'temp': temp,
                'size': self._get_file_size_safe(file_path)
            }
            
            logger.debug(f"Registered file: {file_path} (temp: {temp})")
    
    def unregister_file(self, file_path: str):
        """Unregister a file from tracking"""
        with self.cleanup_lock:
            if file_path in self.tracked_files:
                del self.tracked_files[file_path]
                logger.debug(f"Unregistered file: {file_path}")
    
    def cleanup_campaign(self, campaign_id: str, reason: str = "completion") -> Dict[str, Any]:
        """
        Clean up resources for a specific campaign
        
        Args:
            campaign_id: Campaign identifier
            reason: Reason for cleanup (completion, cancellation, error)
            
        Returns:
            Cleanup results
        """
        logger.info(f"Starting campaign cleanup: {campaign_id} (reason: {reason})")
        
        if not self.policy.should_cleanup(reason):
            logger.info(f"Cleanup skipped for reason: {reason}")
            return {"skipped": True, "reason": reason}
        
        results = {
            "campaign_id": campaign_id,
            "reason": reason,
            "files_removed": 0,
            "directories_removed": 0,
            "space_freed": 0,
            "errors": [],
            "dry_run": self.policy.dry_run
        }
        
        with self.cleanup_lock:
            # Remove campaign from active list
            self.active_campaigns.discard(campaign_id)
            
            # Find and clean files associated with this campaign
            files_to_remove = []
            for file_path, metadata in self.tracked_files.items():
                if metadata.get('metadata', {}).get('campaign_id') == campaign_id:
                    files_to_remove.append(file_path)
            
            # Clean up files
            for file_path in files_to_remove:
                try:
                    if self._remove_file_safe(file_path, results):
                        self.unregister_file(file_path)
                except Exception as e:
                    results["errors"].append(f"Failed to remove {file_path}: {e}")
                    logger.error(f"Cleanup error for {file_path}: {e}")
            
            # Clean up temp directories (only if no other campaigns are using them)
            if not self.active_campaigns:
                dirs_to_remove = list(self.temp_directories)
                for temp_dir in dirs_to_remove:
                    try:
                        if self._remove_directory_safe(temp_dir, results):
                            self.temp_directories.discard(temp_dir)
                    except Exception as e:
                        results["errors"].append(f"Failed to remove directory {temp_dir}: {e}")
                        logger.error(f"Directory cleanup error for {temp_dir}: {e}")
        
        logger.info(f"Campaign cleanup completed: {results}")
        return results
    
    def cleanup_all_temp_files(self, max_age_hours: int = None) -> Dict[str, Any]:
        """
        Clean up all temporary files older than specified age
        
        Args:
            max_age_hours: Maximum age in hours (uses policy default if None)
            
        Returns:
            Cleanup results
        """
        max_age = max_age_hours or self.policy.max_temp_age_hours
        cutoff_time = datetime.now() - timedelta(hours=max_age)
        
        logger.info(f"Starting temp file cleanup (max age: {max_age} hours)")
        
        results = {
            "max_age_hours": max_age,
            "files_removed": 0,
            "directories_removed": 0,
            "space_freed": 0,
            "errors": [],
            "dry_run": self.policy.dry_run
        }
        
        with self.cleanup_lock:
            # Clean tracked temp files
            files_to_remove = []
            for file_path, metadata in self.tracked_files.items():
                if (metadata.get('temp', False) and 
                    metadata.get('registered_at', datetime.now()) < cutoff_time):
                    files_to_remove.append(file_path)
            
            for file_path in files_to_remove:
                try:
                    if self._remove_file_safe(file_path, results):
                        self.unregister_file(file_path)
                except Exception as e:
                    results["errors"].append(f"Failed to remove {file_path}: {e}")
                    logger.error(f"Temp cleanup error for {file_path}: {e}")
        
        # Clean up system temp directories with CRM prefixes
        self._cleanup_system_temp_files(results, cutoff_time)
        
        logger.info(f"Temp file cleanup completed: {results}")
        return results
    
    def _cleanup_system_temp_files(self, results: Dict, cutoff_time: datetime):
        """Clean up system temporary files with CRM prefixes"""
        temp_dir = tempfile.gettempdir()
        
        try:
            for item in os.listdir(temp_dir):
                if item.startswith(('mini_crm_', 'crm_temp_', 'crm_quarantine_')):
                    item_path = os.path.join(temp_dir, item)
                    
                    try:
                        # Check modification time
                        mtime = datetime.fromtimestamp(os.path.getmtime(item_path))
                        if mtime < cutoff_time:
                            if os.path.isdir(item_path):
                                self._remove_directory_safe(item_path, results)
                            else:
                                self._remove_file_safe(item_path, results)
                    
                    except Exception as e:
                        results["errors"].append(f"Failed to process {item_path}: {e}")
                        logger.error(f"System temp cleanup error for {item_path}: {e}")
        
        except Exception as e:
            results["errors"].append(f"Failed to scan temp directory: {e}")
            logger.error(f"Temp directory scan error: {e}")
    
    def _remove_file_safe(self, file_path: str, results: Dict) -> bool:
        """Safely remove a file with error handling"""
        
        if not os.path.exists(file_path):
            return True  # Already removed
        
        # Get file size before removal
        file_size = self._get_file_size_safe(file_path)
        
        if self.policy.dry_run:
            logger.info(f"DRY RUN: Would remove file {file_path} ({file_size} bytes)")
            results["files_removed"] += 1
            results["space_freed"] += file_size
            return True
        
        try:
            # Make file writable if needed
            os.chmod(file_path, 0o666)
            os.remove(file_path)
            
            results["files_removed"] += 1
            results["space_freed"] += file_size
            
            logger.debug(f"Removed file: {file_path} ({file_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove file {file_path}: {e}")
            raise
    
    def _remove_directory_safe(self, dir_path: str, results: Dict) -> bool:
        """Safely remove a directory with error handling"""
        
        if not os.path.exists(dir_path):
            return True  # Already removed
        
        if not os.path.isdir(dir_path):
            return False  # Not a directory
        
        # Calculate directory size
        dir_size = self._get_directory_size_safe(dir_path)
        
        if self.policy.dry_run:
            logger.info(f"DRY RUN: Would remove directory {dir_path} ({dir_size} bytes)")
            results["directories_removed"] += 1
            results["space_freed"] += dir_size
            return True
        
        try:
            # Make all files writable
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.chmod(file_path, 0o666)
                    except:
                        pass  # Ignore chmod errors
            
            shutil.rmtree(dir_path)
            
            results["directories_removed"] += 1
            results["space_freed"] += dir_size
            
            logger.debug(f"Removed directory: {dir_path} ({dir_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove directory {dir_path}: {e}")
            raise
    
    def _get_file_size_safe(self, file_path: str) -> int:
        """Safely get file size"""
        try:
            return os.path.getsize(file_path)
        except:
            return 0
    
    def _get_directory_size_safe(self, dir_path: str) -> int:
        """Safely get directory size"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += self._get_file_size_safe(file_path)
        except:
            pass  # Ignore errors
        return total_size
    
    def start_background_cleanup(self):
        """Start background cleanup thread"""
        if self.background_cleanup_running:
            return
        
        self.background_cleanup_running = True
        self.background_thread = threading.Thread(
            target=self._background_cleanup_worker,
            daemon=True
        )
        self.background_thread.start()
        
        logger.info("Background cleanup started")
    
    def stop_background_cleanup(self):
        """Stop background cleanup thread"""
        self.background_cleanup_running = False
        if self.background_thread:
            self.background_thread.join(timeout=5)
        
        logger.info("Background cleanup stopped")
    
    def _background_cleanup_worker(self):
        """Background cleanup worker thread"""
        while self.background_cleanup_running:
            try:
                # Perform periodic cleanup
                self.cleanup_all_temp_files()
                
                # Sleep for cleanup interval
                sleep_time = self.policy.cleanup_interval_minutes * 60
                for _ in range(sleep_time):
                    if not self.background_cleanup_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def emergency_cleanup(self):
        """Emergency cleanup on application exit"""
        logger.info("Emergency cleanup triggered")
        
        try:
            # Quick cleanup of temp directories
            with self.cleanup_lock:
                for temp_dir in list(self.temp_directories):
                    try:
                        if os.path.exists(temp_dir):
                            shutil.rmtree(temp_dir)
                            logger.info(f"Emergency cleanup: removed {temp_dir}")
                    except Exception as e:
                        logger.error(f"Emergency cleanup error for {temp_dir}: {e}")
        
        except Exception as e:
            logger.error(f"Emergency cleanup error: {e}")
    
    def register_cleanup_handler(self, handler: Callable):
        """Register custom cleanup handler"""
        self.cleanup_handlers.append(handler)
        logger.info("Custom cleanup handler registered")
    
    def execute_cleanup_handlers(self, context: str = "manual"):
        """Execute all registered cleanup handlers"""
        logger.info(f"Executing {len(self.cleanup_handlers)} cleanup handlers ({context})")
        
        for i, handler in enumerate(self.cleanup_handlers):
            try:
                handler()
                logger.debug(f"Cleanup handler {i+1} executed successfully")
            except Exception as e:
                logger.error(f"Cleanup handler {i+1} failed: {e}")
    
    def get_cleanup_status(self) -> Dict[str, Any]:
        """Get current cleanup status"""
        with self.cleanup_lock:
            total_tracked_size = sum(
                metadata.get('size', 0) 
                for metadata in self.tracked_files.values()
            )
            
            temp_files_count = sum(
                1 for metadata in self.tracked_files.values()
                if metadata.get('temp', False)
            )
            
            status = {
                "temp_directories": len(self.temp_directories),
                "tracked_files": len(self.tracked_files),
                "temp_files": temp_files_count,
                "active_campaigns": len(self.active_campaigns),
                "total_tracked_size": total_tracked_size,
                "background_cleanup_running": self.background_cleanup_running,
                "cleanup_handlers": len(self.cleanup_handlers),
                "policy": {
                    "cleanup_on_completion": self.policy.cleanup_on_completion,
                    "cleanup_on_cancellation": self.policy.cleanup_on_cancellation,
                    "cleanup_on_error": self.policy.cleanup_on_error,
                    "max_temp_age_hours": self.policy.max_temp_age_hours,
                    "dry_run": self.policy.dry_run
                }
            }
        
        return status
    
    @contextmanager
    def temporary_file(self, prefix: str = "crm_temp_", suffix: str = ""):
        """Context manager for temporary files with automatic cleanup"""
        
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(
                prefix=prefix, 
                suffix=suffix, 
                delete=False
            )
            temp_path = temp_file.name
            temp_file.close()
            
            # Register for tracking
            self.register_file(temp_path, temp=True)
            
            logger.debug(f"Created temporary file: {temp_path}")
            yield temp_path
            
        finally:
            if temp_file:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        self.unregister_file(temp_path)
                        logger.debug(f"Cleaned up temporary file: {temp_path}")
                except Exception as e:
                    logger.error(f"Failed to cleanup temporary file {temp_path}: {e}")
    
    @contextmanager
    def temporary_directory(self, prefix: str = "crm_temp_", campaign_id: str = None):
        """Context manager for temporary directories with automatic cleanup"""
        
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix)
            self.register_temp_directory(temp_dir, campaign_id)
            
            logger.debug(f"Created temporary directory: {temp_dir}")
            yield temp_dir
            
        finally:
            if temp_dir:
                try:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                        self.temp_directories.discard(temp_dir)
                        logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.error(f"Failed to cleanup temporary directory {temp_dir}: {e}")


# Global cleanup manager instance
cleanup_manager = AttachmentCleanupManager()


def cleanup_on_completion(campaign_id: str) -> Dict[str, Any]:
    """Convenience function for completion cleanup"""
    return cleanup_manager.cleanup_campaign(campaign_id, "completion")


def cleanup_on_cancellation(campaign_id: str) -> Dict[str, Any]:
    """Convenience function for cancellation cleanup"""
    return cleanup_manager.cleanup_campaign(campaign_id, "cancellation")


def cleanup_on_error(campaign_id: str) -> Dict[str, Any]:
    """Convenience function for error cleanup"""
    return cleanup_manager.cleanup_campaign(campaign_id, "error")


def register_campaign_file(file_path: str, campaign_id: str):
    """Register a file for campaign-specific cleanup"""
    cleanup_manager.register_file(
        file_path, 
        metadata={"campaign_id": campaign_id},
        temp=True
    )


def safe_temp_directory(prefix: str = "mini_crm_", campaign_id: str = None):
    """Create a temporary directory with automatic cleanup registration"""
    return cleanup_manager.temporary_directory(prefix, campaign_id)


def safe_temp_file(prefix: str = "mini_crm_", suffix: str = ""):
    """Create a temporary file with automatic cleanup registration"""
    return cleanup_manager.temporary_file(prefix, suffix)