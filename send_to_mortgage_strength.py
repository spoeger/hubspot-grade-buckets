# send_to_mortgage_strength.py

import requests
import json
import os
import sys
import time

HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")
TRESTLE_API_KEY = os.environ.get("TRESTLE_API_KEY")
PARTNER_WEBHOOK_URL = "# Replace"
PROCESSED_FILE = "processed_contacts.json"

def load_processed_ids():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_ids(processed_ids):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed_ids), f)

def get_contact_by_id(contact_id):
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    params = {
        "properties": "firstname,lastname,phone,address,city,state,zip"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_recent_contacts(limit=50):
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    params = {
        "limit": limit,
        "properties": "firstname,lastname,phone,address,city,state,zip",
        "sort": "-lastmodifieddate"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("results", [])

def is_address_complete(contact):
    props = contact.get("properties", {})
    return all(props.get(field) for field in ["address", "city", "state", "zip"])

def send_to_mortgage_strength(contact):
    props = contact["properties"]
    payload = {
        "unique_id": contact["id"],
        "first_name": props.get("firstname"),
        "last_name": props.get("lastname"),
        "address": props.get("address"),
        "city": props.get("city"),
        "state": props.get("state"),
        "zip": props.get("zip")
    }

    start_send = time.time()
    response = requests.post(PARTNER_WEBHOOK_URL, json=payload)
    elapsed_send = time.time() - start_send

    if response.status_code == 200:
        print(f"📤 Sent to Mortgage Strength: contact {contact['id']} (⏱️ {elapsed_send:.2f}s)")
        return True
    else:
        print(f"❌ Failed to send {contact['id']} to partner: {response.status_code} - {response.text}")
        return False

def main():
    contact_id = sys.argv[1] if len(sys.argv) > 1 else None

    if contact_id:
        print(f"🔎 Sending single contact ID {contact_id} to Mortgage Strength")
        try:
            contact = get_contact_by_id(contact_id)
            if is_address_complete(contact):
                send_to_mortgage_strength(contact)
            else:
                print("⚠️ Address incomplete, skipping.")
        except Exception as e:
            print("❌ Error with specific contact:", e)
        return

    print("🔄 Starting batch send to Mortgage Strength...")
    processed_ids = load_processed_ids()
    new_processed = set()

    contacts = get_recent_contacts()

    for contact in contacts:
        contact_id = contact["id"]
        if contact_id in processed_ids:
            continue

        if is_address_complete(contact):
            success = send_to_mortgage_strength(contact)
            if success:
                new_processed.add(contact_id)

    all_processed = processed_ids.union(new_processed)
    save_processed_ids(all_processed)
    print("✅ Batch send complete.")

if __name__ == "__main__":
    main()
