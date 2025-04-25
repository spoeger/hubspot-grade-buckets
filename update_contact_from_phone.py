# update_contact_from_phone.py

from trestle_reverse_phone import reverse_lookup
from hubspot_helpers import update_contact_address
import time

def process_contact(contact_id, phone_number):
    print(f"Starting process for contact {contact_id} with phone {phone_number}")
    
    start_lookup = time.time()
    address_data = reverse_lookup(phone_number)
    print(f"⏱️ Trestle reverse lookup took {time.time() - start_lookup:.2f} seconds")

    if not address_data:
        print(f"⚠️ No address found for {phone_number}")
        return {"success": False}

    start_update = time.time()
    update_success = update_contact_address(contact_id, address_data)
    print(f"⏱️ HubSpot address update took {time.time() - start_update:.2f} seconds")

    if update_success:
        print(f"✅ Successfully updated contact {contact_id} with address from Trestle.")
        return {"success": True}
    else:
        return {"success": False}
