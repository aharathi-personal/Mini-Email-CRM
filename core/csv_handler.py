"""
CSV Handler for Mini Email CRM
Handles CSV file processing with pandas, validation, and error handling
"""

import os
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
import logging
from pathlib import Path

from models.contact import Contact
from config.settings import FILE_SETTINGS


class CSVValidationError(Exception):
    """Custom exception for CSV validation errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}


class CSVHandler:
    """
    CSV file processor with validation and error handling
    
    Features:
    - Multiple encoding support (UTF-8, Latin-1, CP1252)
    - Flexible column mapping (handles variations in column names)
    - Comprehensive validation (file, structure, data)
    - Detailed error reporting with line numbers
    - Large file handling with memory efficiency
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Column mapping for flexible CSV import
        self.column_mappings = {
            'email': ['email', 'email_address', 'e_mail', 'e-mail', 'mail'],
            'firstname': ['firstname', 'first_name', 'fname', 'first', 'given_name'],
            'lastname': ['lastname', 'last_name', 'lname', 'last', 'surname', 'family_name'],
            'phone': ['phone', 'phone_number', 'telephone', 'tel', 'mobile'],
            'company': ['company', 'organization', 'org', 'business', 'employer'],
            'title': ['title', 'job_title', 'position', 'role', 'job']
        }
        
        # Supported encodings to try in order
        self.encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate file before processing
        
        Returns:
            Dict with validation results and file info
        """
        result = {
            'valid': False,
            'file_size': 0,
            'file_extension': '',
            'errors': []
        }
        
        try:
            # Check file exists
            if not os.path.exists(file_path):
                result['errors'].append(f"File not found: {file_path}")
                return result
            
            # Get file info
            file_path_obj = Path(file_path)
            result['file_size'] = file_path_obj.stat().st_size
            result['file_extension'] = file_path_obj.suffix.lower()
            
            # Check file extension
            allowed_extensions = FILE_SETTINGS['allowed_extensions']
            if result['file_extension'] not in allowed_extensions:
                result['errors'].append(
                    f"Unsupported file type: {result['file_extension']}. "
                    f"Allowed types: {', '.join(allowed_extensions)}"
                )
                return result
            
            # Check file size
            max_size = FILE_SETTINGS['max_file_size_mb'] * 1024 * 1024  # Convert to bytes
            if result['file_size'] > max_size:
                result['errors'].append(
                    f"File too large: {result['file_size'] / 1024 / 1024:.1f}MB. "
                    f"Maximum allowed: {FILE_SETTINGS['max_file_size_mb']}MB"
                )
                return result
            
            # Check if file is readable
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Try to read first 100 characters
            except UnicodeDecodeError:
                # This is okay, we'll handle encoding detection later
                pass
            except Exception as e:
                result['errors'].append(f"File is not readable: {str(e)}")
                return result
            
            result['valid'] = True
            self.logger.info(f"File validation passed: {file_path}")
            
        except Exception as e:
            result['errors'].append(f"File validation error: {str(e)}")
            self.logger.error(f"File validation failed: {str(e)}")
        
        return result
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding by trying common encodings
        
        Returns:
            Best encoding found, defaults to 'utf-8'
        """
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()  # Try to read entire file
                self.logger.info(f"Detected encoding: {encoding}")
                return encoding
            except UnicodeDecodeError:
                continue
            except Exception:
                break
        
        # Default fallback
        self.logger.warning("Could not detect encoding, using utf-8")
        return 'utf-8'
    
    def read_csv_file(self, file_path: str, encoding: Optional[str] = None) -> pd.DataFrame:
        """
        Read CSV file with automatic encoding detection
        
        Args:
            file_path: Path to CSV file
            encoding: Specific encoding to use, auto-detect if None
            
        Returns:
            pandas DataFrame with CSV data
            
        Raises:
            CSVValidationError: If file cannot be read
        """
        if encoding is None:
            encoding = self.detect_encoding(file_path)
        
        try:
            # Try different CSV parsing approaches
            separators = [',', ';', '\t']  # Common separators
            
            for separator in separators:
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        sep=separator,
                        dtype=str,  # Read all as strings initially
                        na_values=['', 'NULL', 'null', 'N/A', 'n/a', 'NA'],
                        keep_default_na=False,
                        skipinitialspace=True
                    )
                    
                    # Check if we got reasonable columns (more than 1 column usually means correct separator)
                    if len(df.columns) > 1:
                        self.logger.info(f"Successfully read CSV with separator '{separator}', encoding '{encoding}'")
                        return df
                        
                except Exception as e:
                    self.logger.debug(f"Failed to read with separator '{separator}': {str(e)}")
                    continue
            
            # If all separators failed, raise error
            raise CSVValidationError(
                "Could not parse CSV file. Please ensure it uses comma (,), semicolon (;), or tab separation.",
                {'encoding_used': encoding, 'separators_tried': separators}
            )
            
        except Exception as e:
            if isinstance(e, CSVValidationError):
                raise
            raise CSVValidationError(f"Failed to read CSV file: {str(e)}")
    
    def map_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Map CSV columns to standard field names
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dict mapping standard field names to actual column names
            
        Raises:
            CSVValidationError: If required columns not found
        """
        columns_lower = {col.lower().strip(): col for col in df.columns}
        mapping = {}
        
        # Map each standard field to actual column
        for standard_field, variations in self.column_mappings.items():
            found_column = None

            for variation in variations:
                if variation.lower() in columns_lower:
                    found_column = columns_lower[variation.lower()]
                    break

            if found_column:
                mapping[standard_field] = found_column

        # Validate required columns (lastname optional)
        required_fields = ['email', 'firstname']
        missing_fields = []

        for field in required_fields:
            if field not in mapping:
                missing_fields.append(field)

        if missing_fields:
            available_columns = list(df.columns)
            raise CSVValidationError(
                f"Required columns not found: {', '.join(missing_fields)}",
                {
                    'missing_fields': missing_fields,
                    'available_columns': available_columns,
                    'column_mappings': self.column_mappings
                }
            )

        self.logger.info(f"Column mapping successful: {mapping}")
        return mapping
    
    def validate_data_quality(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate data quality and report issues
        
        Returns:
            Dict with validation results and statistics
        """
        result = {
            'total_rows': len(df),
            'valid_rows': 0,
            'invalid_rows': [],
            'warnings': [],
            'statistics': {}
        }
        
        email_col = column_mapping['email']
        firstname_col = column_mapping['firstname']
        lastname_col = column_mapping.get('lastname')
        
        # Statistics tracking
        empty_emails = 0
        invalid_emails = 0
        empty_firstnames = 0
        empty_lastnames = 0
        
        for idx, row in df.iterrows():
            row_errors = []
            
            # Check email
            email = str(row[email_col]).strip() if pd.notna(row[email_col]) else ''
            if not email:
                empty_emails += 1
                row_errors.append("Missing email address")
            else:
                # Basic email validation
                if '@' not in email or '.' not in email.split('@')[-1]:
                    invalid_emails += 1
                    row_errors.append(f"Invalid email format: {email}")
            
            # Check firstname
            firstname = str(row[firstname_col]).strip() if pd.notna(row[firstname_col]) else ''
            if not firstname:
                empty_firstnames += 1
                row_errors.append("Missing first name")
            
            # Check lastname
            lastname = ''
            if lastname_col:
                lastname = str(row[lastname_col]).strip() if pd.notna(row[lastname_col]) else ''
                if not lastname:
                    empty_lastnames += 1
            
            if row_errors:
                result['invalid_rows'].append({
                    'row_number': idx + 2,  # +2 because pandas is 0-indexed and CSV has header
                    'errors': row_errors,
                    'data': dict(row)
                })
            else:
                result['valid_rows'] += 1
        
        # Generate statistics
        result['statistics'] = {
            'total_rows': result['total_rows'],
            'valid_rows': result['valid_rows'],
            'invalid_rows': len(result['invalid_rows']),
            'empty_emails': empty_emails,
            'invalid_emails': invalid_emails,
            'empty_firstnames': empty_firstnames,
            'empty_lastnames': empty_lastnames
        }
        
        # Generate warnings
        if empty_emails > 0:
            result['warnings'].append(f"{empty_emails} rows have missing email addresses")
        if invalid_emails > 0:
            result['warnings'].append(f"{invalid_emails} rows have invalid email formats")
        if empty_firstnames > 0:
            result['warnings'].append(f"{empty_firstnames} rows have missing first names")
        if lastname_col and empty_lastnames > 0:
            result['warnings'].append(f"{empty_lastnames} rows have missing last names (optional field)")
        
        return result
    
    def process_csv_file(self, file_path: str) -> Dict[str, Any]:
        """
        Main method to process CSV file and convert to contacts
        
        Returns:
            Dict with processing results, contacts, and statistics
        """
        result = {
            'success': False,
            'contacts': [],
            'file_info': {},
            'statistics': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Step 1: Validate file
            self.logger.info(f"Processing CSV file: {file_path}")
            file_validation = self.validate_file(file_path)
            result['file_info'] = file_validation
            
            if not file_validation['valid']:
                result['errors'].extend(file_validation['errors'])
                return result
            
            # Step 2: Read CSV file
            df = self.read_csv_file(file_path)
            self.logger.info(f"Read {len(df)} rows from CSV")
            
            # Step 3: Map columns
            column_mapping = self.map_columns(df)
            
            # Step 4: Validate data quality
            data_validation = self.validate_data_quality(df, column_mapping)
            result['statistics'] = data_validation['statistics']
            result['warnings'] = data_validation['warnings']
            
            # Step 5: Convert valid rows to Contact objects
            contacts = []
            for idx, row in df.iterrows():
                try:
                    # Skip rows that failed validation
                    if any(invalid['row_number'] == idx + 2 for invalid in data_validation['invalid_rows']):
                        continue
                    
                    # Create contact data dictionary
                    contact_data = {}
                    for standard_field, csv_column in column_mapping.items():
                        value = row[csv_column]
                        contact_data[standard_field] = str(value).strip() if pd.notna(value) else None
                    
                    # Create Contact object
                    contact = Contact.from_dict(contact_data)
                    contacts.append(contact)
                    
                except Exception as e:
                    self.logger.error(f"Failed to create contact from row {idx + 2}: {str(e)}")
                    result['warnings'].append(f"Row {idx + 2}: Failed to create contact - {str(e)}")
            
            result['contacts'] = contacts
            result['success'] = True
            
            # Add total_rows for accurate reporting
            result['total_rows'] = len(df)
            
            self.logger.info(f"Successfully processed {len(contacts)} contacts from CSV")
            
            # Add summary to statistics
            result['statistics']['contacts_created'] = len(contacts)
            result['statistics']['processing_success_rate'] = (
                len(contacts) / len(df) * 100 if len(df) > 0 else 0
            )
            
        except CSVValidationError as e:
            result['errors'].append(str(e))
            if hasattr(e, 'details'):
                result['file_info'].update(e.details)
            self.logger.error(f"CSV validation error: {str(e)}")
            
        except Exception as e:
            result['errors'].append(f"Unexpected error processing CSV: {str(e)}")
            self.logger.error(f"Unexpected error: {str(e)}")
        
        return result
    
    def validate_csv_structure(self, file_path: str) -> Dict[str, Any]:
        """
        Quick validation of CSV structure without full processing
        Useful for UI feedback before full import
        """
        result = {
            'valid': False,
            'columns': [],
            'row_count': 0,
            'required_columns_found': [],
            'missing_columns': [],
            'errors': []
        }
        
        try:
            # Validate file first
            file_validation = self.validate_file(file_path)
            if not file_validation['valid']:
                result['errors'] = file_validation['errors']
                return result
            
            # Read just the header and a few rows
            df = self.read_csv_file(file_path)
            result['columns'] = list(df.columns)
            result['row_count'] = len(df)
            
            # Check column mapping
            try:
                column_mapping = self.map_columns(df)
                result['required_columns_found'] = list(column_mapping.keys())
                result['valid'] = True
            except CSVValidationError as e:
                if hasattr(e, 'details') and 'missing_fields' in e.details:
                    result['missing_columns'] = e.details['missing_fields']
                result['errors'].append(str(e))
            
        except Exception as e:
            result['errors'].append(f"Structure validation error: {str(e)}")
        
        return result
    
    def get_sample_data(self, file_path: str, num_rows: int = 5) -> Dict[str, Any]:
        """
        Get sample data from CSV for preview
        """
        result = {
            'success': False,
            'sample_data': [],
            'columns': [],
            'errors': []
        }
        
        try:
            df = self.read_csv_file(file_path)
            result['columns'] = list(df.columns)
            
            # Get sample rows
            sample_df = df.head(num_rows)
            result['sample_data'] = sample_df.to_dict('records')
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(f"Failed to get sample data: {str(e)}")
        
        return result