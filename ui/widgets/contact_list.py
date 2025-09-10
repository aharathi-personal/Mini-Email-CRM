"""
Contact List Widget for Mini Email CRM
Provides scrollable contact list with search functionality and selection events
Based on Screen 3 design - Review Personalized Emails
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QListWidget, QListWidgetItem, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette

from ui.styles.stylesheet import (
    INPUT_STYLE, CARD_STYLE, SUBTITLE_STYLE,
    PRIMARY_BLUE, BORDER_GREY, DARK_GREY, LIGHT_GREY,
    FONT_SIZE_SMALL
)


class ContactListWidget(QWidget):
    """
    Contact list widget with search functionality and contact selection
    Shows contacts in scrollable list with search/filter capabilities
    """
    
    # Signals
    contact_selected = pyqtSignal(dict)  # Emitted when a contact is selected
    search_changed = pyqtSignal(str)     # Emitted when search text changes
    contacts_filtered = pyqtSignal(int)  # Emitted with filtered contact count
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contacts = []  # List of contact dictionaries
        self.filtered_contacts = []  # Currently filtered/displayed contacts
        self.selected_contact = None
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the contact list UI based on Screen 3 design"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Search bar
        self.search_widget = self.create_search_bar()
        layout.addWidget(self.search_widget)
        
        # Contact list
        self.contact_list = self.create_contact_list()
        layout.addWidget(self.contact_list)
        
        self.setLayout(layout)
        
    def create_search_bar(self):
        """Create the search bar widget"""
        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                padding: 2px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        
        # Search icon (using Unicode character)
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {DARK_GREY};
                border: none;
                background: transparent;
            }}
        """)
        layout.addWidget(search_icon)
        
        # Search input field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                font-size: {FONT_SIZE_SMALL};
                color: {DARK_GREY};
                background: transparent;
                padding: 4px 0;
            }}
            QLineEdit::placeholder {{
                color: #999999;
            }}
        """)
        layout.addWidget(self.search_input)
        
        search_frame.setLayout(layout)
        return search_frame
        
    def create_contact_list(self):
        """Create the scrollable contact list"""
        contact_list = QListWidget()
        contact_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {BORDER_GREY};
                border-radius: 4px;
                background-color: white;
                selection-background-color: #E3F2FD;
                selection-color: {DARK_GREY};
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid #F0F0F0;
                color: {DARK_GREY};
            }}
            QListWidget::item:hover {{
                background-color: {LIGHT_GREY};
            }}
            QListWidget::item:selected {{
                background-color: #E3F2FD;
                color: {DARK_GREY};
            }}
            QListWidget::item:selected:hover {{
                background-color: #BBDEFB;
            }}
        """)
        
        # Enable single selection only
        contact_list.setSelectionMode(QListWidget.SingleSelection)
        
        return contact_list
        
    def connect_signals(self):
        """Connect internal signals"""
        # Search functionality with debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.contact_list.itemSelectionChanged.connect(self.on_contact_selection_changed)
        self.contact_list.itemClicked.connect(self.on_contact_clicked)
        
    def on_search_text_changed(self, text):
        """Handle search text changes with debouncing"""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms delay for debouncing
        
    def perform_search(self):
        """Perform the actual search/filter operation"""
        search_text = self.search_input.text().strip().lower()
        self.filter_contacts(search_text)
        self.search_changed.emit(search_text)
        
    def filter_contacts(self, search_text=""):
        """Filter contacts based on search text"""
        if not search_text:
            self.filtered_contacts = self.contacts.copy()
        else:
            self.filtered_contacts = []
            for contact in self.contacts:
                # Search in name and email
                name = f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip().lower()
                email = contact.get('email', '').lower()
                
                if search_text in name or search_text in email:
                    self.filtered_contacts.append(contact)
                    
        self.update_contact_list_display()
        self.contacts_filtered.emit(len(self.filtered_contacts))
        
    def update_contact_list_display(self):
        """Update the visual contact list display"""
        self.contact_list.clear()
        
        for contact in self.filtered_contacts:
            item = self.create_contact_list_item(contact)
            self.contact_list.addItem(item)
            
    def create_contact_list_item(self, contact):
        """Create a list widget item for a contact"""
        # Format: John Doe\njohn@email.com (as shown in Screen 3)
        firstname = contact.get('firstname', '')
        lastname = contact.get('lastname', '')
        email = contact.get('email', '')
        
        # Full name
        full_name = f"{firstname} {lastname}".strip()
        if not full_name:
            full_name = "Unknown Name"
            
        # Create display text
        display_text = f"{full_name}\n{email}"
        
        # Create list item
        item = QListWidgetItem(display_text)
        item.setData(Qt.UserRole, contact)  # Store contact data
        
        # Set item styling
        item.setFont(QFont("Arial", 11))
        
        return item
        
    def on_contact_selection_changed(self):
        """Handle contact selection changes"""
        selected_items = self.contact_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            contact = item.data(Qt.UserRole)
            self.selected_contact = contact
            self.contact_selected.emit(contact)
        else:
            self.selected_contact = None
            
    def on_contact_clicked(self, item):
        """Handle contact item clicks"""
        contact = item.data(Qt.UserRole)
        self.selected_contact = contact
        self.contact_selected.emit(contact)
        
    # Public API methods
    def set_contacts(self, contacts):
        """Set the list of contacts to display"""
        self.contacts = contacts.copy() if contacts else []
        self.filter_contacts()  # This will update the display
        
    def add_contact(self, contact):
        """Add a single contact to the list"""
        if contact not in self.contacts:
            self.contacts.append(contact)
            self.filter_contacts()  # Refresh display
            
    def remove_contact(self, contact):
        """Remove a contact from the list"""
        if contact in self.contacts:
            self.contacts.remove(contact)
            self.filter_contacts()  # Refresh display
            
    def clear_contacts(self):
        """Clear all contacts"""
        self.contacts = []
        self.filtered_contacts = []
        self.selected_contact = None
        self.contact_list.clear()
        
    def get_selected_contact(self):
        """Get the currently selected contact"""
        return self.selected_contact
        
    def get_all_contacts(self):
        """Get all contacts (unfiltered)"""
        return self.contacts.copy()
        
    def get_filtered_contacts(self):
        """Get currently filtered/displayed contacts"""
        return self.filtered_contacts.copy()
        
    def get_contact_count(self):
        """Get total number of contacts"""
        return len(self.contacts)
        
    def get_filtered_count(self):
        """Get number of currently filtered/displayed contacts"""
        return len(self.filtered_contacts)
        
    def select_contact_by_email(self, email):
        """Select a contact by email address"""
        for i in range(self.contact_list.count()):
            item = self.contact_list.item(i)
            contact = item.data(Qt.UserRole)
            if contact and contact.get('email') == email:
                self.contact_list.setCurrentItem(item)
                return True
        return False
        
    def select_contact_by_index(self, index):
        """Select a contact by list index"""
        if 0 <= index < self.contact_list.count():
            item = self.contact_list.item(index)
            self.contact_list.setCurrentItem(item)
            return True
        return False
        
    def clear_selection(self):
        """Clear the current selection"""
        self.contact_list.clearSelection()
        self.selected_contact = None
        
    def set_search_text(self, text):
        """Set the search text programmatically"""
        self.search_input.setText(text)
        self.perform_search()
        
    def clear_search(self):
        """Clear the search text"""
        self.search_input.clear()
        self.perform_search()
        
    def get_search_text(self):
        """Get the current search text"""
        return self.search_input.text()
        
    def set_enabled(self, enabled):
        """Enable or disable the widget"""
        super().setEnabled(enabled)
        self.search_input.setEnabled(enabled)
        self.contact_list.setEnabled(enabled)
        
    def focus_search(self):
        """Set focus to the search input"""
        self.search_input.setFocus()
        
    def load_contacts_from_csv_data(self, csv_data):
        """Load contacts from CSV data (list of dictionaries)"""
        contacts = []
        for row in csv_data:
            # Ensure required fields exist
            contact = {
                'firstname': row.get('firstname', '').strip(),
                'lastname': row.get('lastname', '').strip(), 
                'email': row.get('email', '').strip()
            }
            
            # Only add contacts with valid email
            if contact['email']:
                contacts.append(contact)
                
        self.set_contacts(contacts)
        return len(contacts)
        
    def export_contacts(self):
        """Export contacts in a format suitable for email sending"""
        export_data = []
        for contact in self.contacts:
            export_data.append({
                'firstname': contact.get('firstname', ''),
                'lastname': contact.get('lastname', ''),
                'email': contact.get('email', ''),
                'full_name': f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
            })
        return export_data


# Example usage and testing
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QLabel
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Contact List Widget Test")
    window.setGeometry(100, 100, 800, 600)
    
    # Create central widget
    central_widget = QWidget()
    layout = QHBoxLayout()
    
    # Create contact list
    contact_list = ContactListWidget()
    
    # Sample contacts
    sample_contacts = [
        {'firstname': 'John', 'lastname': 'Doe', 'email': 'john@email.com'},
        {'firstname': 'Jane', 'lastname': 'Smith', 'email': 'jane@email.com'},
        {'firstname': 'Edward', 'lastname': 'Johnson', 'email': 'edward@email.com'},
        {'firstname': 'Mary', 'lastname': 'Williams', 'email': 'mary@email.com'},
        {'firstname': 'James', 'lastname': 'Brown', 'email': 'james@email.com'},
        {'firstname': 'Robert', 'lastname': 'Garcia', 'email': 'robert@email.com'},
    ]
    
    contact_list.set_contacts(sample_contacts)
    
    # Info panel
    info_label = QLabel("Select a contact to see details here")
    info_label.setStyleSheet(f"""
        QLabel {{
            background-color: {LIGHT_GREY};
            border: 1px solid {BORDER_GREY};
            border-radius: 4px;
            padding: 20px;
            font-size: {FONT_SIZE_SMALL};
        }}
    """)
    
    # Connect signals for testing
    def on_contact_selected(contact):
        info_text = f"""
        Selected Contact:
        
        Name: {contact.get('firstname', '')} {contact.get('lastname', '')}
        Email: {contact.get('email', '')}
        """
        info_label.setText(info_text)
        print(f"Contact selected: {contact}")
    
    contact_list.contact_selected.connect(on_contact_selected)
    contact_list.search_changed.connect(lambda text: print(f"Search: '{text}'"))
    contact_list.contacts_filtered.connect(lambda count: print(f"Filtered count: {count}"))
    
    layout.addWidget(contact_list, 1)
    layout.addWidget(info_label, 1)
    
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    print("Contact List Widget Test Started!")
    print("Features:")
    print("- Search/filter contacts")
    print("- Click to select contacts")
    print("- View contact details")
    
    window.show()
    sys.exit(app.exec_())
