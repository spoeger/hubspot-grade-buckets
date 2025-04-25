import os
import requests
from dotenv import load_dotenv

load_dotenv()

TRESTLE_API_KEY = os.environ.get("TRESTLE_API_KEY")
API_URL = "https://api.trestleiq.com/3.2/phone"

def reverse_lookup(phone_number):
    if not TRESTLE_API_KEY:
        print("❌ TRESTLE_API_KEY is not set.")
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
            print(f"⚠️ No owners found for phone number: {phone_number}")
            return None

        owner = data["owners"][0]
        address = owner.get("current_addresses", [{}])[0]

        if not address.get("street_line_1"):
            print(f"⚠️ No valid address found for phone number: {phone_number}")
            return None

        address_result = {
            "street": address.get("street_line_1"),
            "city": address.get("city"),
            "state": address.get("state_code"),
            "zip": address.get("postal_code")
        }

        print(f"✅ Address found for {phone_number}: {address_result}")
        return address_result

    except requests.exceptions.HTTPError as err:
        print(f"❌ Trestle API HTTP error: {err.response.status_code} - {err.response.text}")
        return None
    except Exception as e:
        print(f"❌ Trestle API unexpected error: {str(e)}")
        return None
