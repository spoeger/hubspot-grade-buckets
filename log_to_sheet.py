import gspread
from google.oauth2.service_account import Credentials
import datetime
import time
import traceback

# Path to your service account JSON key
SERVICE_ACCOUNT_FILE = 'gentle-cinema-384316-79f0543373bc.json'  # Update if needed

# Define the scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Authenticate
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)
gc = gspread.authorize(credentials)

# Open your sheet
SPREADSHEET_NAME = 'Script Logs'  # Make sure your sheet name matches
sheet = gc.open(SPREADSHEET_NAME).sheet1

def log_to_sheet(script_name, step, status, message, start_time=None):
    """Logs an entry to the Google Sheet."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if start_time:
        duration = round(time.time() - start_time, 2)
    else:
        duration = ""

    row = [now, script_name, step, status, message, duration]
    sheet.append_row(row)
    print(f"✅ Logged to Google Sheet: {step} - {status}")

def safe_execute(script_name, step_name, function_to_run):
    """Executes a function and logs success or error."""
    step_start = time.time()
    try:
        result = function_to_run()
        log_to_sheet(script_name, step_name, "Success", "Step completed successfully.", start_time=step_start)
        return result
    except Exception as e:
        error_message = traceback.format_exc()
        log_to_sheet(script_name, step_name, "Error", error_message, start_time=step_start)
        raise

# No main() or test code here — this is purely a helper module now.
