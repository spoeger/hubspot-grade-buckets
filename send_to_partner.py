import requests
import json
import os

HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")
TRESTLE_API_KEY = os.environ.get("TRESTLE_API_KEY")
PARTNER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/582745/2xlxuhn/"  # Replace with your partner's real URL

PROCESSED_FILE = "processed_contacts.json"

def load_processed_ids():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_ids(processed_ids):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(list(processed_ids), f)

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

def enrich_with_trestle(contact):
    props = contact.get("properties", {})
    phone = props.get("phone")
    name = f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()

    if not phone or not name:
        return None  # Not enough info to enrich

    params = {
        "phone": phone,
        "phone.country_hint": "US",
        "phone.name_hint": name
    }

    headers = {
        "accept": "application/json",
        "x-api-key": TRESTLE_API_KEY
    }

    try:
        response = requests.get("https://api.trestleiq.com/3.2/phone", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Try to extract address
        match = data.get("matches", [{}])[0]
        enriched = {
            "address": match.get("address_line1"),
            "city": match.get("city"),
            "state": match.get("state_code"),
            "zip": match.get("postal_code")
        }

        if all(enriched.values()):
            print(f"🏡 Enriched address for {contact['id']}: {enriched}")
            return enriched

    except Exception as e:
        print(f"❌ Trestle enrichment failed for {contact['id']}: {e}")

    return None

def update_hubspot_address(contact_id, address_data):
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"properties": address_data}
    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()
    print(f"✅ Updated HubSpot contact {contact_id} with address.")

def send_to_partner(contact):
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

    res = requests.post(PARTNER_WEBHOOK_URL, json=payload)
    if res.status_code == 200:
        print(f"📤 Sent to partner: contact {contact['id']}")
        return True
    else:
        print(f"❌ Failed to send {contact['id']} to partner: {res.status_code} - {res.text}")
        return False

def main():
    print("🔄 Starting contact enrichment + delivery process...")
    processed_ids = load_processed_ids()
    new_processed = set()

    contacts = get_recent_contacts()

    for contact in contacts:
        contact_id = contact["id"]
        if contact_id in processed_ids:
            continue

        props = contact.get("properties", {})

        # If no address yet, try to enrich
        if not is_address_complete(contact):
            enriched = enrich_with_trestle(contact)
            if enriched:
                update_hubspot_address(contact_id, enriched)
                # Refresh local contact data
                props.update(enriched)

        # Now check again if address is complete
        if is_address_complete(contact):
            success = send_to_partner(contact)
            if success:
                new_processed.add(contact_id)

    all_processed = processed_ids.union(new_processed)
    save_processed_ids(all_processed)
    print("✅ Done.")

if __name__ == "__main__":
    main()
