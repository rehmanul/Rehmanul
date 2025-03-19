import json
import gspread
from google_sheets_integration import GoogleSheetsIntegration

def test_connection():
    try:
        # First, verify the credentials file can be read
        print("Testing credentials file...")
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        print("Credentials file loaded successfully!")
        
        print("\nTesting Google Sheets connection...")
        # Initialize the Google Sheets integration
        sheets = GoogleSheetsIntegration('credentials.json', 'Web Stryker Pro+')
        
        # Try to add a test row
        test_data = ['Test', 'Connection', 'Successful']
        sheets.add_row(test_data)
        print("Successfully connected to Google Sheets and added test data!")
        
        # Clear the test data
        sheets.clear_sheet()
        print("Successfully cleared test data!")
        
    except json.JSONDecodeError as e:
        print(f"Error reading credentials file: {str(e)}")
        print("Please check if the credentials.json file is properly formatted")
    except gspread.exceptions.APIError as e:
        print(f"Google Sheets API Error: {str(e)}")
        print("\nTo fix this error:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com")
        print("2. Select project: knowledge-grapgh-searches")
        print("3. Enable the following APIs:")
        print("   - Google Drive API")
        print("   - Google Sheets API")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_connection()