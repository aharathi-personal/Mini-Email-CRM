"""
Enhanced Attachment Widget for Phase 8 Task 24
Features: Drag-drop visual feedback, loading indicators, better error messages, tooltips
"""

import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QProgressBar, QToolTip, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSignal as Signal
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent, QPixmap, QIcon

# Import themed error dialogs
from ui.error_dialogs import ThemedMessageBox

from ui.styles.stylesheet import (
    BUTTON_STYLE, SUBTITLE_STYLE, CARD_STYLE, SUCCESS_GREEN, ERROR_RED,
    DARK_GREY, LIGHT_GREY, BORDER_GREY, FONT_SIZE_SMALL, PRIMARY_BLUE,
    WARNING_ORANGE, SURFACE, SURFACE_ELEVATED, TEXT_SECONDARY, PRIMARY_HOVER
)
from models.attachment import Attachment, AttachmentManager, AttachmentType


class AttachmentProcessingThread(QThread):
    """Background thread for processing attachment files"""
    processing_complete = Signal(dict)
    progress_update = Signal(int, str)
    
    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths if isinstance(file_paths, list) else [file_paths]
        
    def run(self):
        """Process attachment files in background"""
        results = []
        total_files = len(self.file_paths)
        
        for i, file_path in enumerate(self.file_paths):
            try:
                progress = int((i / total_files) * 100)
                self.progress_update.emit(progress, f"Processing {Path(file_path).name}...")
                
                # Simulate processing time for demonstration
                self.msleep(500)
                
                # Create attachment object
                file_size = os.path.getsize(file_path)
                file_name = Path(file_path).name
                
                # Determine attachment type
                extension = Path(file_path).suffix.lower()
                if extension == '.pdf':
                    attachment_type = AttachmentType.PDF
                    mime_type = 'application/pdf'
                elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    attachment_type = AttachmentType.IMAGE
                    mime_type = f'image/{extension[1:]}'
                elif extension in ['.doc', '.docx', '.txt', '.rtf']:
                    attachment_type = AttachmentType.DOCUMENT
                    mime_type = 'application/octet-stream'
                else:
                    attachment_type = AttachmentType.OTHER
                    mime_type = 'application/octet-stream'
                
                attachment = Attachment(
                    filename=file_name,
                    filepath=file_path,
                    file_size=file_size,
                    mime_type=mime_type,
                    attachment_type=attachment_type
                )
                
                results.append({
                    'success': True,
                    'attachment': attachment,
                    'file_path': file_path
                })
                
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'file_path': file_path
                })
        
        self.progress_update.emit(100, "Processing complete")
        self.processing_complete.emit({'results': results})


class AttachmentItemWidget(QWidget):
    """Individual attachment item with enhanced visual feedback"""
    
    remove_requested = pyqtSignal(str)  # filename
    
    def __init__(self, attachment, parent=None):
        super().__init__(parent)
        self.attachment = attachment
        self.setup_ui()
        self.setup_tooltips()
        
    def setup_ui(self):
        """Set up attachment item UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # File type icon
        icon_label = QLabel(self.get_file_icon())
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.get_icon_color()};
                color: white;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(icon_label)
        
        # File info
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # File name
        name_label = QLabel(self.attachment.filename)
        name_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                font-weight: bold;
                color: {DARK_GREY};
            }}
        """)
        # Truncate long names
        if len(self.attachment.filename) > 25:
            name_label.setText(self.attachment.filename[:22] + "...")
        info_layout.addWidget(name_label)
        
        # File size and type
        size_text = self.format_file_size(self.attachment.file_size)
        type_text = self.attachment.attachment_type.value.upper()
        details_label = QLabel(f"{size_text} • {type_text}")
        details_label.setStyleSheet(f"""
            QLabel {{
                font-size: 9px;
                color: {TEXT_SECONDARY};
            }}
        """)
        info_layout.addWidget(details_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ERROR_RED};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
        """)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.attachment.filename))
        layout.addWidget(remove_btn)
        
        # Set main widget style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {SURFACE};
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                margin: 2px;
            }}
            QWidget:hover {{
                border-color: {PRIMARY_BLUE};
                background-color: {SURFACE_ELEVATED};
            }}
        """)
        
        self.setLayout(layout)
        
    def get_file_icon(self):
        """Get appropriate icon for file type"""
        if self.attachment.attachment_type == AttachmentType.PDF:
            return "PDF"
        elif self.attachment.attachment_type == AttachmentType.IMAGE:
            return "IMG"
        elif self.attachment.attachment_type == AttachmentType.DOCUMENT:
            return "DOC"
        else:
            return "FILE"
    
    def get_icon_color(self):
        """Get color for file type icon"""
        if self.attachment.attachment_type == AttachmentType.PDF:
            return ERROR_RED
        elif self.attachment.attachment_type == AttachmentType.IMAGE:
            return PRIMARY_BLUE
        elif self.attachment.attachment_type == AttachmentType.DOCUMENT:
            return SUCCESS_GREEN
        else:
            return BORDER_GREY
    
    def format_file_size(self, size_bytes):
        """Format file size for display"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def setup_tooltips(self):
        """Set up tooltips for the attachment item"""
        tooltip_text = (
            f"Filename: {self.attachment.filename}\\n"
            f"Size: {self.format_file_size(self.attachment.file_size)}\\n"
            f"Type: {self.attachment.attachment_type.value}\\n"
            f"Path: {self.attachment.filepath}"
        )
        self.setToolTip(tooltip_text)


class EnhancedAttachmentWidget(QWidget):
    """
    Enhanced attachment widget with:
    - Drag-drop visual feedback
    - Loading indicators for file processing
    - Better error messages with suggestions
    - Tooltips and help text
    - Attachment count and size summary
    - Responsive layout
    """
    
    # Signals
    attachments_changed = pyqtSignal(int, int)  # count, total_size
    attachment_added = pyqtSignal(str)  # filename
    attachment_removed = pyqtSignal(str)  # filename
    attachment_error = pyqtSignal(str, list)  # error_type, messages
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.attachment_manager = AttachmentManager()
        self.processing_thread = None
        self.drag_active = False
        self.setup_ui()
        self.setup_tooltips()
        
    def setup_ui(self):
        """Set up the enhanced attachment UI"""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Header with summary
        header_layout = self.create_header()
        layout.addLayout(header_layout)
        
        # Drag-drop zone (collapsible)
        self.drop_zone = self.create_drop_zone()
        layout.addWidget(self.drop_zone)
        
        # Action buttons
        button_layout = self.create_action_buttons()
        layout.addLayout(button_layout)
        
        # Processing indicator (hidden by default)
        self.processing_widget = self.create_processing_widget()
        layout.addWidget(self.processing_widget)
        
        # Attachment list
        self.attachment_list = self.create_attachment_list()
        layout.addWidget(self.attachment_list)
        
        # Summary footer
        self.summary_widget = self.create_summary_widget()
        layout.addWidget(self.summary_widget)
        
        self.setLayout(layout)
        self.update_ui_state()
        
    def create_header(self):
        """Create header with title and attachment summary"""
        layout = QVBoxLayout()
        
        # Title row
        title_row = QHBoxLayout()
        
        title_label = QLabel("📎 Email Attachments")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {DARK_GREY};
            }}
        """)
        title_row.addWidget(title_label)
        
        title_row.addStretch()
        
        # Attachment count and size
        self.summary_label = QLabel("No attachments")
        self.summary_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: {TEXT_SECONDARY};
                font-style: italic;
            }}
        """)
        title_row.addWidget(self.summary_label)
        
        layout.addLayout(title_row)
        
        # Help text
        help_label = QLabel("Add files to send along with your email (PDF, images, documents)")
        help_label.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: {TEXT_SECONDARY};
                margin-bottom: 4px;
            }}
        """)
        layout.addWidget(help_label)
        
        return layout
        
    def create_drop_zone(self):
        """Create enhanced drag-drop zone"""
        drop_frame = QFrame()
        drop_frame.setFixedHeight(120)
        drop_frame.setAcceptDrops(True)
        drop_frame.setObjectName("attachmentDropZone")
        
        # Install event handlers
        drop_frame.dragEnterEvent = self.dragEnterEvent
        drop_frame.dragLeaveEvent = self.dragLeaveEvent
        drop_frame.dropEvent = self.dropEvent
        
        self.update_drop_zone_style(drop_frame, False)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(6)
        
        # Icon
        icon_label = QLabel("📎")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 32px; border: none; background: transparent;")
        content_layout.addWidget(icon_label)
        
        # Instructions
        instruction_label = QLabel("Drop files here or click Add Files")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: {DARK_GREY};
                border: none;
                background: transparent;
            }}
        """)
        content_layout.addWidget(instruction_label)
        
        # Limits
        limits_label = QLabel("Max 25MB per file, 25MB total")
        limits_label.setAlignment(Qt.AlignCenter)
        limits_label.setStyleSheet(f"""
            QLabel {{
                font-size: 9px;
                color: #999;
                border: none;
                background: transparent;
            }}
        """)
        content_layout.addWidget(limits_label)
        
        drop_frame.setLayout(content_layout)
        return drop_frame
        
    def update_drop_zone_style(self, drop_zone, is_drag_active, is_error=False):
        """Update drop zone styling"""
        if is_error:
            border_color = ERROR_RED
            bg_color = SURFACE_ELEVATED
        elif is_drag_active:
            border_color = PRIMARY_BLUE
            bg_color = SURFACE_ELEVATED
        else:
            border_color = BORDER_GREY
            bg_color = SURFACE
        
        border_style = "solid" if is_drag_active else "dashed"
        
        drop_zone.setStyleSheet(f"""
            QFrame#attachmentDropZone {{
                border: 2px {border_style} {border_color};
                border-radius: 6px;
                background-color: {bg_color};
            }}
        """)
        
    def create_action_buttons(self):
        """Create action buttons"""
        layout = QHBoxLayout()
        
        # Add files button
        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.setStyleSheet(f"""
            QPushButton {{
                {BUTTON_STYLE}
                min-width: 100px;
                padding: 6px 12px;
            }}
        """)
        self.add_files_btn.clicked.connect(self.browse_files)
        layout.addWidget(self.add_files_btn)
        
        # Clear all button
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {WARNING_ORANGE};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #e68a00;
            }}
            QPushButton:disabled {{
                background-color: {BORDER_GREY};
                color: #999;
            }}
        """)
        self.clear_all_btn.clicked.connect(self.clear_all_attachments)
        layout.addWidget(self.clear_all_btn)
        
        layout.addStretch()
        return layout
        
    def create_processing_widget(self):
        """Create processing indicator widget"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {PRIMARY_BLUE};
                border-radius: 6px;
                background-color: {SURFACE_ELEVATED};
                padding: 8px;
            }}
        """)
        widget.hide()
        
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Processing icon (simple text for now)
        self.processing_icon = QLabel("⏳")
        self.processing_icon.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.processing_icon)
        
        # Processing text
        self.processing_label = QLabel("Processing files...")
        self.processing_label.setStyleSheet(f"""
            QLabel {{
                font-size: {FONT_SIZE_SMALL};
                color: {PRIMARY_BLUE};
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.processing_label)
        
        layout.addStretch()
        
        # Progress bar
        self.processing_progress = QProgressBar()
        self.processing_progress.setFixedWidth(100)
        self.processing_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {BORDER_GREY};
                border-radius: 3px;
                text-align: center;
                height: 16px;
            }}
            QProgressBar::chunk {{
                background-color: {PRIMARY_BLUE};
                border-radius: 2px;
            }}
        """)
        layout.addWidget(self.processing_progress)
        
        widget.setLayout(layout)
        return widget
        
    def create_attachment_list(self):
        """Create scrollable attachment list"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                background-color: {SURFACE};
            }}
        """)
        
        # Container widget for attachments
        self.attachment_container = QWidget()
        self.attachment_layout = QVBoxLayout()
        self.attachment_layout.setContentsMargins(4, 4, 4, 4)
        self.attachment_layout.setSpacing(2)
        self.attachment_container.setLayout(self.attachment_layout)
        
        scroll_area.setWidget(self.attachment_container)
        scroll_area.hide()  # Initially hidden
        
        return scroll_area
        
    def create_summary_widget(self):
        """Create attachment summary widget"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {BORDER_GREY};
                border-radius: 6px;
                background-color: {SURFACE_ELEVATED};
                padding: 6px;
            }}
        """)
        widget.hide()  # Initially hidden
        
        layout = QHBoxLayout()
        
        # Summary info
        self.detailed_summary = QLabel()
        self.detailed_summary.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: {TEXT_SECONDARY};
            }}
        """)
        layout.addWidget(self.detailed_summary)
        
        layout.addStretch()
        
        # Limits warning
        self.limits_warning = QLabel()
        self.limits_warning.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: {WARNING_ORANGE};
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.limits_warning)
        
        widget.setLayout(layout)
        return widget
        
    def setup_tooltips(self):
        """Set up tooltips"""
        self.add_files_btn.setToolTip(
            "Add files to attach to your email.\\n"
            "Supported: PDF, images (JPG, PNG, GIF), documents (DOC, TXT)"
        )
        
        self.drop_zone.setToolTip(
            "Drag files from your computer and drop them here.\\n"
            "Multiple files can be selected at once."
        )
        
        self.clear_all_btn.setToolTip("Remove all attached files")
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasUrls():
            # Check if all files are valid
            valid_files = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    valid_files.append(file_path)
            
            if valid_files:
                event.acceptProposedAction()
                self.drag_active = True
                self.update_drop_zone_style(self.drop_zone, True)
                return
        
        event.ignore()
        self.update_drop_zone_style(self.drop_zone, False, True)
        
    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        self.drag_active = False
        self.update_drop_zone_style(self.drop_zone, False)
        
    def dropEvent(self, event: QDropEvent):
        """Handle file drop"""
        self.drag_active = False
        self.update_drop_zone_style(self.drop_zone, False)
        
        file_paths = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                file_paths.append(file_path)
        
        if file_paths:
            self.process_files(file_paths)
            event.acceptProposedAction()
        
    def browse_files(self):
        """Open file browser"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Attachment Files",
            "",
            "All Supported (*.pdf *.jpg *.jpeg *.png *.gif *.doc *.docx *.txt);;"
            "PDF Files (*.pdf);;"
            "Images (*.jpg *.jpeg *.png *.gif);;"
            "Documents (*.doc *.docx *.txt);;"
            "All Files (*)"
        )
        
        if file_paths:
            self.process_files(file_paths)
            
    def process_files(self, file_paths):
        """Process selected files"""
        # Show processing widget
        self.processing_widget.show()
        self.processing_progress.setRange(0, 100)
        self.processing_progress.setValue(0)
        
        # Start processing thread
        self.processing_thread = AttachmentProcessingThread(file_paths)
        self.processing_thread.progress_update.connect(self.update_processing)
        self.processing_thread.processing_complete.connect(self.handle_processing_complete)
        self.processing_thread.start()
        
    def update_processing(self, progress, message):
        """Update processing progress"""
        self.processing_progress.setValue(progress)
        self.processing_label.setText(message)
        
    def handle_processing_complete(self, result):
        """Handle processing completion"""
        self.processing_widget.hide()
        
        successful = 0
        failed = 0
        error_messages = []
        
        for item in result['results']:
            if item['success']:
                # Add attachment
                errors = self.attachment_manager.add_attachment(item['attachment'])
                if not errors:
                    self.add_attachment_to_ui(item['attachment'])
                    successful += 1
                    self.attachment_added.emit(item['attachment'].filename)
                else:
                    failed += 1
                    error_messages.extend(errors)
            else:
                failed += 1
                error_messages.append(f"{Path(item['file_path']).name}: {item['error']}")
        
        # Show results
        if successful > 0:
            self.update_ui_state()
            
        if failed > 0:
            self.attachment_error.emit("Processing errors", error_messages)
            
    def add_attachment_to_ui(self, attachment):
        """Add attachment widget to UI"""
        item_widget = AttachmentItemWidget(attachment)
        item_widget.remove_requested.connect(self.remove_attachment)
        self.attachment_layout.addWidget(item_widget)
        
    def remove_attachment(self, filename):
        """Remove attachment"""
        # Remove from manager
        self.attachment_manager.remove_attachment(filename)
        
        # Remove from UI
        for i in range(self.attachment_layout.count()):
            widget = self.attachment_layout.itemAt(i).widget()
            if isinstance(widget, AttachmentItemWidget) and widget.attachment.filename == filename:
                widget.setParent(None)
                break
        
        self.attachment_removed.emit(filename)
        self.update_ui_state()
        
    def clear_all_attachments(self):
        """Clear all attachments"""
        if self.attachment_manager.get_attachment_count() == 0:
            return
            
        # Ask for confirmation
        reply = ThemedMessageBox.question(
            self,
            "Clear All Attachments",
            "Are you sure you want to remove all attachments?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear manager
            self.attachment_manager.clear()
            
            # Clear UI
            for i in range(self.attachment_layout.count()):
                widget = self.attachment_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
                    
            self.update_ui_state()
            
    def update_ui_state(self):
        """Update UI based on current state"""
        count = self.attachment_manager.get_attachment_count()
        total_size = self.attachment_manager.get_total_size()
        
        # Update summary label
        if count == 0:
            self.summary_label.setText("No attachments")
            self.attachment_list.hide()
            self.summary_widget.hide()
            self.clear_all_btn.setEnabled(False)
        else:
            size_mb = total_size / (1024 * 1024)
            self.summary_label.setText(f"{count} file{'s' if count != 1 else ''} ({size_mb:.1f} MB)")
            self.attachment_list.show()
            self.summary_widget.show()
            self.clear_all_btn.setEnabled(True)
            
            # Update detailed summary
            file_types = {}
            for attachment in self.attachment_manager.attachments:
                file_type = attachment.attachment_type.value
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            type_summary = ", ".join([f"{count} {type}" for type, count in file_types.items()])
            self.detailed_summary.setText(f"Files: {type_summary}")
            
            # Check limits
            max_total = Attachment.MAX_TOTAL_SIZE
            if total_size > max_total * 0.8:  # Warning at 80%
                remaining_mb = (max_total - total_size) / (1024 * 1024)
                if remaining_mb <= 0:
                    self.limits_warning.setText("⚠️ Size limit exceeded!")
                    self.limits_warning.setStyleSheet(f"color: {ERROR_RED}; font-weight: bold;")
                else:
                    self.limits_warning.setText(f"⚠️ {remaining_mb:.1f} MB remaining")
                    self.limits_warning.setStyleSheet(f"color: {WARNING_ORANGE}; font-weight: bold;")
            else:
                self.limits_warning.setText("")
        
        # Emit signal
        self.attachments_changed.emit(count, total_size)
        
    def get_attachment_manager(self):
        """Get the attachment manager"""
        return self.attachment_manager
        
    def has_attachments(self):
        """Check if there are attachments"""
        return self.attachment_manager.get_attachment_count() > 0