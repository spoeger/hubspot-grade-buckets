import os
import requests
from dotenv import load_dotenv
import traceback
from log_to_sheet import log_to_sheet  # ✅ New import to allow error logging

load_dotenv()

TRESTLE_API_KEY = os.environ.get("TRESTLE_API_KEY")
API_URL = "https://api.trestleiq.com/3.2/phone"

def reverse_lookup(phone_number):
    script_name = "Trestle Reverse Lookup"

    if not TRESTLE_API_KEY:
        print("❌ TRESTLE_API_KEY is not set.")
        log_to_sheet(script_name, "API Key Check", "Failed", "TRESTLE_API_KEY is not set.")
        return None

    headers = {
        "x-api-key": TRESTLE_API_KEY
    }

    params = {
        "phone": phone_number,
        "phone.country_hint": "US"
    }

    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("owners"):
            warning_message = f"⚠️ No owners found for phone number: {phone_number}"
            print(warning_message)
            log_to_sheet(script_name, "Reverse Lookup", "Failed", warning_message)
            return None

        owner = data["owners"][0]
        address = owner.get("current_addresses", [{}])[0]

        if not address.get("street_line_1"):
            warning_message = f"⚠️ No valid address found for phone number: {phone_number}"
            print(warning_message)
            log_to_sheet(script_name, "Reverse Lookup", "Failed", warning_message)
            return None

        address_result = {
            "street": address.get("street_line_1"),
            "city": address.get("city"),
            "state": address.get("state_code"),
            "zip": address.get("postal_code")
        }

        success_message = f"✅ Address found for {phone_number}: {address_result}"
        print(success_message)
        log_to_sheet(script_name, "Reverse Lookup", "Success", success_message)
        return address_result

    except requests.exceptions.HTTPError as err:
        error_message = f"❌ Trestle API HTTP error: {err.response.status_code} - {err.response.text}"
        print(error_message)
        log_to_sheet(script_name, "Reverse Lookup", "Error", error_message)
        return None
    except Exception as e:
        full_error = traceback.format_exc()
        print(f"❌ Trestle API unexpected error: {str(e)}")
        log_to_sheet(script_name, "Reverse Lookup", "Error", full_error)
        return None
