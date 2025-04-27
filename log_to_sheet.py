import os
import json
import io
import gspread
from google.oauth2.service_account import Credentials
import datetime
import time
import traceback

# Define the scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Load service account info from environment variable
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

# Authenticate
credentials = Credentials.from_service_account_info(
    service_account_info,
    scopes=SCOPES
)
gc = gspread.authorize(credentials)

# Open your sheet
SPREADSHEET_NAME = 'Script Logs'  # Make sure your sheet matches this name
sheet = gc.open(SPREADSHEET_NAME).sheet1

def log_to_sheet(script_name, step, status, message, start_time=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if start_time:
        duration = round(time.time() - start_time, 2)
    else:
        duration = ""

    row = [now, script_name, step, status, message, duration]
    sheet.append_row(row)
    print("Logged to Google Sheet!")

# Wrapper for safe execution and error catching
def safe_execute(script_name, step_name, function_to_run):
    step_start = time.time()
    try:
        function_to_run()
        log_to_sheet(script_name, step_name, "Success", "Step completed successfully.", start_time=step_start)
    except Exception as e:
        error_message = traceback.format_exc()
        log_to_sheet(script_name, step_name, "Error", error_message, start_time=step_start)
        raise  # Re-raise if you want the script to stop on errors

# Example usage
def main():
    log_to_sheet("Test Script", "Script Start", "Info", "Script execution started.")

    # Example of successful step
    def dummy_success():
        time.sleep(1)  # Simulate work

    # Example of failing step
    def dummy_failure():
        time.sleep(0.5)
        raise Exception("Something went wrong!")

    safe_execute("Test Script", "Initialization", dummy_success)
    safe_execute("Test Script", "Critical Step", dummy_failure)

    log_to_sheet("Test Script", "Script End", "Info", "Script execution finished.")

if __name__ == "__main__":
    main()
