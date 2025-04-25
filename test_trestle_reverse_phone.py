import os
import requests

# Set your Trestle API key here or pull from environment variable
TRESTLE_API_KEY = os.environ.get("TRESTLE_API_KEY", "ap9VkN5nAf34M6UxRnamyaAAtPwBKBIj5CRmpcZL")

# The phone number you want to test (E.164 format preferred)
phone_number = "+16199220905"  # or "6199220905"

url = "https://api.trestleiq.com/3.2/phone"

headers = {
    "x-api-key": TRESTLE_API_KEY
}

params = {
    "phone": phone_number,
    "phone.country_hint": "US"
    # Optional: add these if needed
    # "phone.name_hint": "John Doe",
    # "phone.postal_code_hint": "92101"
}

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    print("\n✅ SUCCESSFUL RESPONSE:\n")
    print(data)

except requests.exceptions.HTTPError as err:
    print("\n❌ HTTP ERROR:\n", err.response.status_code, err.response.text)
except Exception as e:
    print("\n❌ ERROR:\n", str(e))
