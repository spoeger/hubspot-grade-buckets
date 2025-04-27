# update_contact_from_phone.py

from trestle_reverse_phone import reverse_lookup
from hubspot_helpers import update_contact_address
from log_to_sheet import log_to_sheet  # ✅ NEW import to log steps
import time

def process_contact(contact_id, phone_number):
    print(f"Starting process for contact {contact_id} with phone {phone_number}")

    script_name = "Update Contact Script"

    # --- Trestle Lookup Step ---
    start_lookup = time.time()
    address_data = reverse_lookup(phone_number)
    lookup_duration = round(time.time() - start_lookup, 2)
    print(f"⏱️ Trestle reverse lookup took {lookup_duration:.2f} seconds")

    if not address_data:
        print(f"⚠️ No address found for {phone_number}")
        log_to_sheet(script_name, "Trestle Lookup", "Failed", f"No address found for {phone_number}", start_time=start_lookup)
        return {"success": False}

    log_to_sheet(script_name, "Trestle Lookup", "Success", f"Address found for {phone_number}", start_time=start_lookup)

    # --- HubSpot Update Step ---
    start_update = time.time()
    update_success = update_contact_address(contact_id, address_data)
    update_duration = round(time.time() - start_update, 2)
    print(f"⏱️ HubSpot address update took {update_duration:.2f} seconds")

    if update_success:
        print(f"✅ Successfully updated contact {contact_id} with address from Trestle.")
        log_to_sheet(script_name, "HubSpot Update", "Success", f"Updated contact {contact_id}", start_time=start_update)
        return {"success": True}
    else:
        print(f"❌ Failed to update contact {contact_id}")
        log_to_sheet(script_name, "HubSpot Update", "Failed", f"Failed to update contact {contact_id}", start_time=start_update)
        return {"success": False}
