"""
Enhanced Validation Pipeline for Mini Email CRM
Task 22: Comprehensive validation system with edge case handling

This module provides advanced validation for files, attachments, and data
with robust error handling and recovery mechanisms.
"""

import os
import mimetypes
import hashlib
import zipfile
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

# Optional imports for enhanced validation
try:
    import magic  # python-magic for better MIME type detection
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

try:
    from PIL import Image  # Pillow for image validation
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from models.attachment import Attachment, AttachmentType
from core.integration_manager import ValidationResult

import logging
logger = logging.getLogger(__name__)


class FileCorruptionError(Exception):
    """Exception for corrupted or invalid files"""
    pass


class SecurityError(Exception):
    """Exception for security-related file issues"""
    pass


class EnhancedValidationPipeline:
    """
    Advanced validation pipeline with comprehensive checks
    Task 22: Handles edge cases, corruption detection, and security validation
    """
    
    # Dangerous file extensions and signatures
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.vbe', 
        '.js', '.jse', '.jar', '.msi', '.dll', '.sh', '.py', '.pl', '.php'
    }
    
    # Known malicious file signatures (magic numbers)
    DANGEROUS_SIGNATURES = {
        b'MZ': 'Windows Executable',
        b'\x7fELF': 'Linux Executable',
        b'\xca\xfe\xba\xbe': 'Java Class File',
        b'PK\x03\x04': 'ZIP Archive (potential script)',
    }
    
    # Maximum file sizes by type (bytes)
    MAX_FILE_SIZES = {
        AttachmentType.PDF: 25 * 1024 * 1024,      # 25MB for PDFs
        AttachmentType.IMAGE: 10 * 1024 * 1024,    # 10MB for images
        AttachmentType.DOCUMENT: 25 * 1024 * 1024, # 25MB for documents
        AttachmentType.OTHER: 5 * 1024 * 1024,     # 5MB for other files
    }
    
    def __init__(self):
        self.validation_cache = {}
        self.security_scanning_enabled = True
        
    def validate_file_comprehensive(self, file_path: str) -> ValidationResult:
        """
        Comprehensive file validation with security and corruption checks
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            ValidationResult with detailed validation information
        """
        result = ValidationResult()
        
        try:
            # Basic existence and accessibility checks
            basic_result = self._validate_basic_file_properties(file_path)
            result.errors.extend(basic_result.errors)
            result.warnings.extend(basic_result.warnings)
            result.info.extend(basic_result.info)
            
            if not basic_result.is_valid:
                result.is_valid = False
                return result
            
            # Security validation
            security_result = self._validate_file_security(file_path)
            result.errors.extend(security_result.errors)
            result.warnings.extend(security_result.warnings)
            
            if not security_result.is_valid:
                result.is_valid = False
                return result
            
            # Corruption and integrity checks
            integrity_result = self._validate_file_integrity(file_path)
            result.errors.extend(integrity_result.errors)
            result.warnings.extend(integrity_result.warnings)
            result.info.extend(integrity_result.info)
            
            if not integrity_result.is_valid:
                result.is_valid = False
                return result
            
            # Content validation based on file type
            content_result = self._validate_file_content(file_path)
            result.errors.extend(content_result.errors)
            result.warnings.extend(content_result.warnings)
            result.info.extend(content_result.info)
            
            if not content_result.is_valid:
                result.is_valid = False
            
        except Exception as e:
            logger.error(f"Validation pipeline error for {file_path}: {e}")
            result.add_error(f"Validation failed: {str(e)}")
        
        return result
    
    def _validate_basic_file_properties(self, file_path: str) -> ValidationResult:
        """Validate basic file properties"""
        result = ValidationResult()
        
        # Check file exists
        if not os.path.exists(file_path):
            result.add_error(f"File not found: {file_path}")
            return result
        
        # Check if it's actually a file
        if not os.path.isfile(file_path):
            result.add_error(f"Path is not a file: {file_path}")
            return result
        
        # Check file permissions
        if not os.access(file_path, os.R_OK):
            result.add_error(f"File is not readable: {file_path}")
            return result
        
        # Check file size
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                result.add_error("File is empty")
                return result
            
            if file_size > 100 * 1024 * 1024:  # 100MB absolute limit
                result.add_error(f"File too large: {file_size / (1024*1024):.1f}MB (max 100MB)")
                return result
                
            result.add_info(f"File size: {self._format_file_size(file_size)}")
            
        except OSError as e:
            result.add_error(f"Cannot access file: {e}")
            return result
        
        return result
    
    def _validate_file_security(self, file_path: str) -> ValidationResult:
        """Validate file security and detect potential threats"""
        result = ValidationResult()
        
        if not self.security_scanning_enabled:
            return result
        
        file_name = os.path.basename(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # Check dangerous extensions
        if file_ext in self.DANGEROUS_EXTENSIONS:
            result.add_error(f"Dangerous file type: {file_ext}")
            return result
        
        # Check file signature
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
                
            for signature, description in self.DANGEROUS_SIGNATURES.items():
                if header.startswith(signature):
                    # Special handling for ZIP files
                    if signature == b'PK\x03\x04':
                        zip_result = self._validate_zip_file(file_path)
                        if not zip_result.is_valid:
                            result.add_error(f"Suspicious ZIP file: {zip_result.errors[0]}")
                        else:
                            result.add_info("ZIP file validated")
                    else:
                        result.add_error(f"Dangerous file detected: {description}")
                        return result
                        
        except Exception as e:
            result.add_warning(f"Could not scan file signature: {e}")
        
        # Check for hidden or system files
        if file_name.startswith('.') and not file_name.endswith(('.pdf', '.doc', '.docx')):
            result.add_warning("Hidden file detected")
        
        # Check for suspicious patterns in filename
        suspicious_patterns = ['script', 'macro', 'autorun', 'payload']
        if any(pattern in file_name.lower() for pattern in suspicious_patterns):
            result.add_warning(f"Suspicious filename pattern: {file_name}")
        
        return result
    
    def _validate_zip_file(self, file_path: str) -> ValidationResult:
        """Validate ZIP file contents for security"""
        result = ValidationResult()
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Check for suspicious files in ZIP
                for name in zip_file.namelist():
                    name_lower = name.lower()
                    ext = Path(name).suffix.lower()
                    
                    if ext in self.DANGEROUS_EXTENSIONS:
                        result.add_error(f"ZIP contains dangerous file: {name}")
                        return result
                    
                    # Check for directory traversal
                    if '..' in name or name.startswith('/'):
                        result.add_error(f"ZIP contains path traversal: {name}")
                        return result
                
                result.add_info(f"ZIP contains {len(zip_file.namelist())} files")
                
        except zipfile.BadZipFile:
            result.add_error("Corrupted ZIP file")
        except Exception as e:
            result.add_error(f"ZIP validation error: {e}")
        
        return result
    
    def _validate_file_integrity(self, file_path: str) -> ValidationResult:
        """Validate file integrity and detect corruption"""
        result = ValidationResult()
        
        try:
            # Basic read test
            with open(file_path, 'rb') as f:
                # Try to read the entire file in chunks
                chunk_size = 8192
                total_read = 0
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    total_read += len(chunk)
                
                result.add_info(f"Successfully read {self._format_file_size(total_read)}")
            
            # Calculate file hash for integrity
            file_hash = self._calculate_file_hash(file_path)
            result.add_info(f"File hash: {file_hash[:16]}...")
            
        except PermissionError:
            result.add_error("Permission denied reading file")
        except IOError as e:
            result.add_error(f"IO error reading file: {e}")
        except Exception as e:
            result.add_error(f"Integrity check failed: {e}")
        
        return result
    
    def _validate_file_content(self, file_path: str) -> ValidationResult:
        """Validate file content based on type"""
        result = ValidationResult()
        
        try:
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                # Fallback to basic detection
                mime_type = self._detect_mime_type_basic(file_path)
            
            result.add_info(f"MIME type: {mime_type}")
            
            # Type-specific validation
            if mime_type:
                if mime_type.startswith('image/'):
                    content_result = self._validate_image_file(file_path)
                elif mime_type == 'application/pdf':
                    content_result = self._validate_pdf_file(file_path)
                elif mime_type.startswith('application/'):
                    content_result = self._validate_document_file(file_path, mime_type)
                elif mime_type.startswith('text/'):
                    content_result = self._validate_text_file(file_path)
                else:
                    result.add_warning(f"Unknown file type: {mime_type}")
                    return result
                
                result.errors.extend(content_result.errors)
                result.warnings.extend(content_result.warnings)
                result.info.extend(content_result.info)
                
                if not content_result.is_valid:
                    result.is_valid = False
            
        except Exception as e:
            result.add_warning(f"Content validation error: {e}")
        
        return result
    
    def _validate_image_file(self, file_path: str) -> ValidationResult:
        """Validate image file"""
        result = ValidationResult()
        
        try:
            # Try to open as image if PIL is available
            if HAS_PIL:
                from PIL import Image
                with Image.open(file_path) as img:
                    result.add_info(f"Image: {img.size[0]}x{img.size[1]} pixels, {img.mode}")
                    
                    # Check for reasonable dimensions
                    if img.size[0] > 10000 or img.size[1] > 10000:
                        result.add_warning("Very large image dimensions")
            else:
                # PIL not available, basic validation
                result.add_info("Image validation limited (PIL not available)")
                # Basic header check for common formats
                with open(file_path, 'rb') as f:
                    header = f.read(16)
                    if header.startswith(b'\xff\xd8\xff'):
                        result.add_info("JPEG image detected")
                    elif header.startswith(b'\x89PNG'):
                        result.add_info("PNG image detected")
                    elif header.startswith(b'GIF8'):
                        result.add_info("GIF image detected")
                    else:
                        result.add_warning("Unknown image format")
                
        except Exception as e:
            result.add_error(f"Invalid image file: {e}")
        
        return result
    
    def _validate_pdf_file(self, file_path: str) -> ValidationResult:
        """Validate PDF file"""
        result = ValidationResult()
        
        try:
            # Check PDF header
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF-'):
                    result.add_error("Invalid PDF header")
                    return result
                
                # Try to find PDF version
                version_info = header.decode('ascii', errors='ignore')
                result.add_info(f"PDF version info: {version_info}")
                
                # Basic structure check - look for EOF marker
                f.seek(-1024, 2)  # Go to near end of file
                tail = f.read()
                if b'%%EOF' not in tail:
                    result.add_warning("PDF may be truncated (no EOF marker)")
                
        except Exception as e:
            result.add_error(f"PDF validation error: {e}")
        
        return result
    
    def _validate_document_file(self, file_path: str, mime_type: str) -> ValidationResult:
        """Validate document file (Word, Excel, etc.)"""
        result = ValidationResult()
        
        try:
            if mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                           'application/vnd.openxmlformats-officedocument.presentationml.presentation']:
                # Office Open XML format - check as ZIP
                zip_result = self._validate_zip_file(file_path)
                if zip_result.is_valid:
                    result.add_info("Valid Office document structure")
                else:
                    result.add_error("Corrupted Office document")
            
            elif mime_type in ['application/msword', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint']:
                # Legacy Office format - basic validation
                with open(file_path, 'rb') as f:
                    header = f.read(8)
                    # Check for OLE compound document signature
                    if header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
                        result.add_info("Valid legacy Office document")
                    else:
                        result.add_warning("Unexpected Office document format")
            
            else:
                result.add_info(f"Document type: {mime_type}")
                
        except Exception as e:
            result.add_error(f"Document validation error: {e}")
        
        return result
    
    def _validate_text_file(self, file_path: str) -> ValidationResult:
        """Validate text file"""
        result = ValidationResult()
        
        try:
            # Try to read as text with different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            text_content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text_content = f.read(1024)  # Read first 1KB
                    result.add_info(f"Text encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if text_content is None:
                result.add_error("Cannot decode text file")
                return result
            
            # Check for suspicious content
            suspicious_keywords = ['<script', 'javascript:', 'vbscript:', 'onload=', 'eval(']
            for keyword in suspicious_keywords:
                if keyword.lower() in text_content.lower():
                    result.add_warning(f"Suspicious content detected: {keyword}")
            
        except Exception as e:
            result.add_error(f"Text validation error: {e}")
        
        return result
    
    def _detect_mime_type_basic(self, file_path: str) -> str:
        """Basic MIME type detection based on file extension"""
        ext = Path(file_path).suffix.lower()
        
        mime_map = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf'
        }
        
        return mime_map.get(ext, 'application/octet-stream')
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def validate_attachment_collection(self, attachments: List[Attachment]) -> ValidationResult:
        """Validate collection of attachments with enhanced checks"""
        result = ValidationResult()
        
        if not attachments:
            return result
        
        total_size = 0
        file_hashes = set()
        file_names_lower = set()
        
        for i, attachment in enumerate(attachments):
            # Individual file validation
            file_result = self.validate_file_comprehensive(attachment.filepath)
            if not file_result.is_valid:
                result.errors.extend([f"Attachment {i+1} ({attachment.filename}): {err}" for err in file_result.errors])
                result.is_valid = False
            
            result.warnings.extend([f"Attachment {i+1} ({attachment.filename}): {warn}" for warn in file_result.warnings])
            
            # Check for duplicate files by hash
            if os.path.exists(attachment.filepath):
                file_hash = self._calculate_file_hash(attachment.filepath)
                if file_hash in file_hashes:
                    result.add_warning(f"Duplicate file content detected: {attachment.filename}")
                file_hashes.add(file_hash)
                
                total_size += attachment.file_size
            
            # Check for case-insensitive duplicate names
            name_lower = attachment.filename.lower()
            if name_lower in file_names_lower:
                result.add_error(f"Duplicate filename: {attachment.filename}")
            file_names_lower.add(name_lower)
        
        # Collection-level validation
        if total_size > Attachment.MAX_TOTAL_SIZE:
            total_mb = total_size / (1024 * 1024)
            max_mb = Attachment.MAX_TOTAL_SIZE / (1024 * 1024)
            result.add_error(f"Total size ({total_mb:.1f}MB) exceeds limit ({max_mb}MB)")
        
        # Check for reasonable number of attachments
        if len(attachments) > 20:
            result.add_warning(f"Large number of attachments: {len(attachments)}")
        
        result.add_info(f"Validated {len(attachments)} attachments, {self._format_file_size(total_size)} total")
        
        return result
    
    def clean_filename(self, filename: str) -> str:
        """Clean filename to prevent issues"""
        # Remove or replace problematic characters
        import re
        
        # Replace unsafe characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # Ensure reasonable length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        # Ensure it's not empty
        if not filename.strip():
            filename = "unnamed_file"
        
        return filename
    
    def quarantine_file(self, file_path: str, reason: str) -> str:
        """Move suspicious file to quarantine directory"""
        quarantine_dir = tempfile.mkdtemp(prefix="crm_quarantine_")
        
        filename = os.path.basename(file_path)
        quarantine_path = os.path.join(quarantine_dir, f"QUARANTINED_{filename}")
        
        try:
            shutil.move(file_path, quarantine_path)
            logger.warning(f"File quarantined: {file_path} -> {quarantine_path} (Reason: {reason})")
            return quarantine_path
        except Exception as e:
            logger.error(f"Failed to quarantine file: {e}")
            raise
    
    def disable_security_scanning(self):
        """Disable security scanning (for testing only)"""
        self.security_scanning_enabled = False
        logger.warning("Security scanning disabled")
    
    def enable_security_scanning(self):
        """Enable security scanning"""
        self.security_scanning_enabled = True
        logger.info("Security scanning enabled")