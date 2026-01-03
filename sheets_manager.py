"""
Google Sheets Manager for Leads/Contacts Database
Handles all interactions with the Google Sheet
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
import os
import unicodedata


class SheetsManager:
    """Manages Google Sheets operations for leads and contacts"""
    
    # Column mapping for the sheet
    COLUMNS = {
        'Nombre': 0,
        'Teléfono': 1,
        'Email': 2,
        'Telegram': 3,
        'Empresa': 4,
        'Rol': 5,
        'bio': 6,
        'bitácora': 7
    }
    
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        """
        Initialize the sheets manager
        
        Args:
            credentials_file: Path to the service account JSON file
            spreadsheet_id: The ID of the Google Spreadsheet
        """
        # Define the scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Authenticate using the service account
        creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
        self.client = gspread.authorize(creds)
        
        # Open the spreadsheet
        self.spreadsheet = self.client.open_by_key(spreadsheet_id)
        self.sheet = self.spreadsheet.sheet1  # Use the first sheet
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for fuzzy matching by removing accents and converting to lowercase
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text without accents and in lowercase
        """
        # Normalize unicode characters (NFD = decompose accents from letters)
        nfd = unicodedata.normalize('NFD', text)
        # Filter out accent marks (category 'Mn' = nonspacing marks)
        without_accents = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
        # Convert to lowercase
        return without_accents.lower().strip()
        
    def get_all_records(self) -> List[Dict]:
        """
        Get all records from the sheet
        
        Returns:
            List of dictionaries with all records
        """
        try:
            records = self.sheet.get_all_records()
            return records
        except Exception as e:
            print(f"Error fetching records: {e}")
            return []
    
    def search_by_name(self, name: str) -> List[Dict]:
        """
        Search for records by name (fuzzy match: case-insensitive, accent-insensitive)
        
        Args:
            name: The name to search for
            
        Returns:
            List of matching records
        """
        all_records = self.get_all_records()
        name_normalized = self.normalize_text(name)
        
        matches = [
            record for record in all_records 
            if name_normalized in self.normalize_text(record.get('Nombre', ''))
        ]
        
        return matches
    
    def search_by_field(self, field: str, value: str) -> List[Dict]:
        """
        Search for records by any field (fuzzy match: case-insensitive, accent-insensitive)
        
        Args:
            field: The field name to search in
            value: The value to search for
            
        Returns:
            List of matching records
        """
        all_records = self.get_all_records()
        value_normalized = self.normalize_text(value)
        
        matches = [
            record for record in all_records 
            if value_normalized in self.normalize_text(str(record.get(field, '')))
        ]
        
        return matches
    
    def update_field(self, name: str, field: str, new_value: str, append: bool = False) -> bool:
        """
        Update a specific field for a contact by name
        
        Args:
            name: The name of the contact to update
            field: The field to update
            new_value: The new value for the field
            append: If True, append to existing value; if False, replace
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the row with the matching name
            all_values = self.sheet.get_all_values()
            
            # Find the header row
            headers = all_values[0]
            
            # Find the column index for the field
            if field not in headers:
                print(f"Field '{field}' not found in headers")
                return False
            
            field_col_idx = headers.index(field) + 1  # gspread uses 1-based indexing
            name_col_idx = headers.index('Nombre') + 1
            
            # Find the row with the matching name (fuzzy match: case-insensitive, accent-insensitive)
            name_normalized = self.normalize_text(name)
            target_row = None
            
            for row_idx, row in enumerate(all_values[1:], start=2):  # Start from row 2 (skip header)
                row_name_normalized = self.normalize_text(row[name_col_idx - 1])
                if name_normalized == row_name_normalized or name_normalized in row_name_normalized:
                    target_row = row_idx
                    break
            
            if target_row is None:
                print(f"No record found with name '{name}'")
                return False
            
            # Get current value if appending
            if append:
                current_value = self.sheet.cell(target_row, field_col_idx).value or ""
                if current_value:
                    new_value = f"{current_value}\n{new_value}"
            
            # Update the cell
            self.sheet.update_cell(target_row, field_col_idx, new_value)
            print(f"Successfully updated {field} for {name}")
            return True
            
        except Exception as e:
            print(f"Error updating field: {e}")
            return False
    
    def add_record(self, record: Dict) -> bool:
        """
        Add a new record to the sheet
        
        Args:
            record: Dictionary with the record data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the headers from the sheet to know the column order
            headers = self.sheet.row_values(1)
            
            # Prepare the row data in the correct order based on headers
            row = []
            for header in headers:
                row.append(record.get(header, ''))
            
            self.sheet.append_row(row)
            
            # Get identifier for log message (try 'Nombre' first, then 'Fecha', then first field)
            identifier = record.get('Nombre') or record.get('Fecha') or record.get(headers[0], 'Unknown')
            print(f"Successfully added new record for {identifier}")
            return True
            
        except Exception as e:
            print(f"Error adding record: {e}")
            return False
    
    def get_record_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a single record by fuzzy name match
        
        Args:
            name: The name to search for
            
        Returns:
            Dictionary with the record data or None if not found
        """
        matches = self.search_by_name(name)
        
        if not matches:
            return None
        
        # If exact normalized match found, return it
        name_normalized = self.normalize_text(name)
        for match in matches:
            if self.normalize_text(match.get('Nombre', '')) == name_normalized:
                return match
        
        # Otherwise return the first match
        return matches[0] if matches else None

