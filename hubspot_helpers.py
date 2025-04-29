import os
import requests
from dotenv import load_dotenv
import traceback
from log_to_sheet import log_to_sheet  # ✅ NEW import to log to Google Sheets

load_dotenv()

# Load your HubSpot API key from environment variable
HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")
HUBSPOT_BASE_URL = "https://api.hubapi.com"

def update_contact_address(contact_id, address_data):
    """
    Updates the HubSpot contact with the address returned by Trestle.
    
    Parameters:
        contact_id (str): The internal ID of the HubSpot contact to update.
        address_data (dict): Dictionary with keys 'street', 'city', 'state', and 'zip'.

    Returns:
        bool: True if the update was successful, False otherwise.
    """

    script_name = "HubSpot Update Contact"

    if not HUBSPOT_API_KEY:
        print("❌ HUBSPOT_API_KEY is not set.")
        log_to_sheet(script_name, "API Key Check", "Failed", "HUBSPOT_API_KEY is not set.")
        return False

    if not contact_id or not address_data:
        print("❌ Missing contact_id or address_data.")
        log_to_sheet(script_name, "Input Validation", "Failed", "Missing contact_id or address_data.")
        return False

    # Ensure all required address fields are present
    if not all(k in address_data for k in ["street", "city", "state", "zip"]):
        print("❌ Incomplete address data:", address_data)
        log_to_sheet(script_name, "Input Validation", "Failed", f"Incomplete address data: {address_data}")
        return False

    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts/{contact_id}"

    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }

    properties = {
        "address": address_data.get("street"),
        "city": address_data.get("city"),
        "state": address_data.get("state"),
        "zip": address_data.get("zip"),
        "lead_source": "Trestle"
    }

    payload = {
        "properties": properties
    }

    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"✅ Updated contact {contact_id} with address.")
        log_to_sheet(script_name, "Update Contact", "Success", f"Updated contact {contact_id}")
        return True

    except requests.exceptions.HTTPError as err:
        error_message = f"❌ HubSpot update failed: {err.response.status_code} - {err.response.text}"
        print(error_message)
        log_to_sheet(script_name, "Update Contact", "Error", error_message)
        return False
    except Exception as e:
        full_error = traceback.format_exc()
        print(f"❌ Unexpected HubSpot error: {str(e)}")
        log_to_sheet(script_name, "Update Contact", "Error", full_error)
        return False
