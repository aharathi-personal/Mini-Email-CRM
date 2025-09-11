"""
Attachment data model for Mini Email CRM
Handles file attachments with validation and management
"""

import os
import mimetypes
from enum import Enum
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class AttachmentType(Enum):
    """Supported attachment file types"""
    PDF = "pdf"
    IMAGE = "image"
    DOCUMENT = "document"
    OTHER = "other"


@dataclass
class Attachment:
    """
    File attachment with validation and metadata
    
    Stores filename, filepath, file size, mime type and provides validation
    """
    
    filename: str
    filepath: str
    file_size: int  # Size in bytes
    mime_type: str
    attachment_type: AttachmentType
    added_at: Optional[datetime] = None
    
    # File size limits (in bytes)
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB per file
    MAX_TOTAL_SIZE = 25 * 1024 * 1024  # 25MB total attachments
    
    # Allowed file extensions by type
    ALLOWED_EXTENSIONS = {
        AttachmentType.PDF: {'.pdf'},
        AttachmentType.IMAGE: {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'},
        AttachmentType.DOCUMENT: {'.doc', '.docx', '.txt', '.rtf', '.odt', '.xlsx', '.xls', '.ppt', '.pptx'},
        AttachmentType.OTHER: set()  # Will be determined by other validations
    }
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp',
        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain', 'application/rtf', 'application/vnd.oasis.opendocument.text',
        'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    }
    
    def __post_init__(self):
        """Validate attachment on initialization"""
        if self.added_at is None:
            self.added_at = datetime.now()
        
        # Validate required fields
        if not self.filename or not self.filename.strip():
            raise ValueError("Filename is required")
        
        if not self.filepath or not self.filepath.strip():
            raise ValueError("File path is required")
        
        if self.file_size < 0:
            raise ValueError("File size cannot be negative")
    
    @classmethod
    def from_file_path(cls, filepath: str) -> 'Attachment':
        """
        Create attachment from file path with automatic metadata detection
        
        Args:
            filepath: Path to the file
            
        Returns:
            Attachment instance with detected metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        file_path = Path(filepath)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {filepath}")
        
        # Get file metadata
        filename = file_path.name
        file_size = file_path.stat().st_size
        mime_type, _ = mimetypes.guess_type(filepath)
        
        if mime_type is None:
            mime_type = 'application/octet-stream'  # Default for unknown types
        
        # Determine attachment type
        attachment_type = cls._determine_attachment_type(filename, mime_type)
        
        return cls(
            filename=filename,
            filepath=str(file_path.absolute()),
            file_size=file_size,
            mime_type=mime_type,
            attachment_type=attachment_type
        )
    
    @classmethod
    def _determine_attachment_type(cls, filename: str, mime_type: str) -> AttachmentType:
        """Determine attachment type from filename and MIME type"""
        file_ext = Path(filename).suffix.lower()
        
        for att_type, extensions in cls.ALLOWED_EXTENSIONS.items():
            if file_ext in extensions:
                return att_type
        
        # Fallback to MIME type detection
        if mime_type.startswith('image/'):
            return AttachmentType.IMAGE
        elif mime_type == 'application/pdf':
            return AttachmentType.PDF
        elif mime_type.startswith('application/') or mime_type.startswith('text/'):
            return AttachmentType.DOCUMENT
        
        return AttachmentType.OTHER
    
    def validate(self) -> List[str]:
        """
        Validate attachment file
        
        Returns:
            List of validation error messages, empty if valid
        """
        errors = []
        
        # Check if file exists
        if not os.path.exists(self.filepath):
            errors.append(f"File not found: {self.filepath}")
            return errors  # Can't continue validation without file
        
        # Validate file size
        if self.file_size > self.MAX_FILE_SIZE:
            errors.append(f"File size ({self.get_file_size_mb():.1f}MB) exceeds maximum limit ({self.MAX_FILE_SIZE // (1024*1024)}MB)")
        
        if self.file_size == 0:
            errors.append("File is empty")
        
        # Validate file extension
        file_ext = Path(self.filename).suffix.lower()
        if not self._is_extension_allowed(file_ext):
            errors.append(f"File type '{file_ext}' is not supported")
        
        # Validate MIME type
        if not self._is_mime_type_allowed(self.mime_type):
            errors.append(f"MIME type '{self.mime_type}' is not supported")
        
        # Additional security checks
        if self._is_potentially_dangerous_file():
            errors.append("File type may be dangerous and is not allowed")
        
        return errors
    
    def _is_extension_allowed(self, extension: str) -> bool:
        """Check if file extension is allowed"""
        for allowed_extensions in self.ALLOWED_EXTENSIONS.values():
            if extension in allowed_extensions:
                return True
        return False
    
    def _is_mime_type_allowed(self, mime_type: str) -> bool:
        """Check if MIME type is allowed"""
        return mime_type in self.ALLOWED_MIME_TYPES
    
    def _is_potentially_dangerous_file(self) -> bool:
        """Check for potentially dangerous file types"""
        dangerous_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.jar',
            '.js', '.jse', '.vbs', '.vbe', '.ps1', '.sh', '.msi'
        }
        
        file_ext = Path(self.filename).suffix.lower()
        return file_ext in dangerous_extensions
    
    def get_file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.file_size / (1024 * 1024)
    
    def get_file_size_formatted(self) -> str:
        """Get human-readable file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def get_file_icon_type(self) -> str:
        """Get file icon type for UI display"""
        return self.attachment_type.value
    
    def is_image(self) -> bool:
        """Check if attachment is an image"""
        return self.attachment_type == AttachmentType.IMAGE
    
    def is_pdf(self) -> bool:
        """Check if attachment is a PDF"""
        return self.attachment_type == AttachmentType.PDF
    
    def is_document(self) -> bool:
        """Check if attachment is a document"""
        return self.attachment_type == AttachmentType.DOCUMENT
    
    def to_dict(self) -> Dict:
        """Convert attachment to dictionary for storage/export"""
        return {
            'filename': self.filename,
            'filepath': self.filepath,
            'file_size': self.file_size,
            'file_size_formatted': self.get_file_size_formatted(),
            'mime_type': self.mime_type,
            'attachment_type': self.attachment_type.value,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'is_valid': len(self.validate()) == 0
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Attachment':
        """Create attachment from dictionary"""
        attachment_type = AttachmentType(data['attachment_type'])
        added_at = None
        if data.get('added_at'):
            added_at = datetime.fromisoformat(data['added_at'])
        
        return cls(
            filename=data['filename'],
            filepath=data['filepath'],
            file_size=data['file_size'],
            mime_type=data['mime_type'],
            attachment_type=attachment_type,
            added_at=added_at
        )
    
    def __str__(self) -> str:
        """String representation for logging"""
        return f"Attachment({self.filename}, {self.get_file_size_formatted()})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return (f"Attachment(filename='{self.filename}', "
                f"size={self.file_size}, type={self.attachment_type})")


class AttachmentManager:
    """
    Manager class for handling multiple attachments with collective validation
    """
    
    def __init__(self):
        self.attachments: List[Attachment] = []
    
    def add_attachment(self, attachment: Attachment) -> List[str]:
        """
        Add attachment with validation
        
        Returns:
            List of validation errors, empty if successful
        """
        errors = []
        
        # Validate individual attachment
        attachment_errors = attachment.validate()
        if attachment_errors:
            errors.extend(attachment_errors)
            return errors
        
        # Check for duplicate filenames
        if self.has_attachment(attachment.filename):
            errors.append(f"File '{attachment.filename}' is already attached")
            return errors
        
        # Check total size limit
        new_total_size = self.get_total_size() + attachment.file_size
        if new_total_size > Attachment.MAX_TOTAL_SIZE:
            total_mb = new_total_size / (1024 * 1024)
            max_mb = Attachment.MAX_TOTAL_SIZE / (1024 * 1024)
            errors.append(f"Total attachment size ({total_mb:.1f}MB) would exceed limit ({max_mb}MB)")
            return errors
        
        # Add attachment if all validations pass
        self.attachments.append(attachment)
        return errors
    
    def add_attachment_from_file(self, filepath: str) -> List[str]:
        """
        Add attachment from file path
        
        Returns:
            List of validation errors, empty if successful
        """
        try:
            attachment = Attachment.from_file_path(filepath)
            return self.add_attachment(attachment)
        except (FileNotFoundError, ValueError) as e:
            return [str(e)]
    
    def remove_attachment(self, filename: str) -> bool:
        """
        Remove attachment by filename
        
        Returns:
            True if removed, False if not found
        """
        for i, attachment in enumerate(self.attachments):
            if attachment.filename == filename:
                del self.attachments[i]
                return True
        return False
    
    def has_attachment(self, filename: str) -> bool:
        """Check if attachment with filename exists"""
        return any(att.filename == filename for att in self.attachments)
    
    def get_attachment(self, filename: str) -> Optional[Attachment]:
        """Get attachment by filename"""
        for attachment in self.attachments:
            if attachment.filename == filename:
                return attachment
        return None
    
    def get_attachments(self) -> List[Attachment]:
        """Get all attachments"""
        return self.attachments.copy()
    
    def get_attachment_count(self) -> int:
        """Get number of attachments"""
        return len(self.attachments)
    
    def get_total_size(self) -> int:
        """Get total size of all attachments in bytes"""
        return sum(att.file_size for att in self.attachments)
    
    def get_total_size_formatted(self) -> str:
        """Get human-readable total size"""
        total_size = self.get_total_size()
        if total_size < 1024:
            return f"{total_size} B"
        elif total_size < 1024 * 1024:
            return f"{total_size / 1024:.1f} KB"
        else:
            return f"{total_size / (1024 * 1024):.1f} MB"
    
    def validate_all(self) -> List[str]:
        """
        Validate all attachments
        
        Returns:
            List of all validation errors across attachments
        """
        errors = []
        
        for attachment in self.attachments:
            attachment_errors = attachment.validate()
            if attachment_errors:
                errors.extend([f"{attachment.filename}: {error}" for error in attachment_errors])
        
        # Check total size
        total_size = self.get_total_size()
        if total_size > Attachment.MAX_TOTAL_SIZE:
            total_mb = total_size / (1024 * 1024)
            max_mb = Attachment.MAX_TOTAL_SIZE / (1024 * 1024)
            errors.append(f"Total attachment size ({total_mb:.1f}MB) exceeds limit ({max_mb}MB)")
        
        return errors
    
    def clear_attachments(self) -> None:
        """Remove all attachments"""
        self.attachments.clear()
    
    def get_attachments_by_type(self, attachment_type: AttachmentType) -> List[Attachment]:
        """Get attachments filtered by type"""
        return [att for att in self.attachments if att.attachment_type == attachment_type]
    
    def get_summary(self) -> Dict:
        """Get attachment summary for display"""
        return {
            'count': self.get_attachment_count(),
            'total_size': self.get_total_size(),
            'total_size_formatted': self.get_total_size_formatted(),
            'types': {
                'pdf': len(self.get_attachments_by_type(AttachmentType.PDF)),
                'image': len(self.get_attachments_by_type(AttachmentType.IMAGE)),
                'document': len(self.get_attachments_by_type(AttachmentType.DOCUMENT)),
                'other': len(self.get_attachments_by_type(AttachmentType.OTHER))
            }
        }
    
    def to_dict(self) -> Dict:
        """Convert attachment manager to dictionary"""
        return {
            'attachments': [att.to_dict() for att in self.attachments],
            'summary': self.get_summary()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AttachmentManager':
        """Create attachment manager from dictionary"""
        manager = cls()
        for att_data in data.get('attachments', []):
            attachment = Attachment.from_dict(att_data)
            manager.attachments.append(attachment)  # Direct append to avoid validation
        return manager
    
    def __str__(self) -> str:
        """String representation for logging"""
        return f"AttachmentManager({self.get_attachment_count()} files, {self.get_total_size_formatted()})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"AttachmentManager(count={self.get_attachment_count()}, total_size={self.get_total_size()})"
