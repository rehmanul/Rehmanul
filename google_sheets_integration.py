import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List

class GoogleSheetsIntegration:
    def __init__(self, creds_file: str, sheet_name: str):
        """Initialize Google Sheets integration.
        
        Args:
            creds_file (str): Path to the credentials JSON file
            sheet_name (str): Name of the Google Sheet to access
        """
        self.creds_file = creds_file
        self.sheet_name = sheet_name
        self.client = self.authenticate()
        self.sheet = self.client.open(sheet_name).sheet1
        
        # Set up headers if sheet is empty
        if not self.sheet.get_all_values():
            self.setup_headers()

    def authenticate(self):
        """Authenticate with Google Sheets API."""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, scope)
        return gspread.authorize(creds)

    def setup_headers(self):
        """Set up the headers in the sheet."""
        headers = [
            'URL',
            'Company Name',
            'Company Type',
            'Company Description',
            'Contact Emails',
            'Contact Phones',
            'Contact Addresses',
            'Product Name',
            'Product Category',
            'Product Price',
            'Product Description',
            'Product Features',
            'Product Specifications',
            'Additional Products',
            'Extraction Date'
        ]
        self.sheet.append_row(headers)

    def add_row(self, data: List[str]):
        """Add a new row to the sheet.
        
        Args:
            data (List[str]): List of values to add as a new row
        """
        try:
            self.sheet.append_row(data)
        except Exception as e:
            print(f"Error writing to Google Sheet: {str(e)}")

    def clear_sheet(self, keep_headers: bool = True):
        """Clear all data from the sheet.
        
        Args:
            keep_headers (bool): Whether to keep the header row
        """
        if keep_headers:
            headers = self.sheet.row_values(1)
            self.sheet.clear()
            self.sheet.append_row(headers)
        else:
            self.sheet.clear()