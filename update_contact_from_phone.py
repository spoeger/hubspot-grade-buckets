from trestle_reverse_phone import reverse_lookup
from hubspot_helpers import update_contact_address

def process_contact(contact_id, phone_number):
    """
    Runs the full flow:
    - Looks up address via Trestle using phone number
    - Updates HubSpot contact with the returned address

    Returns:
        dict: {success: bool, error: optional str}
    """

    print(f"🔄 Starting process for contact {contact_id} with phone {phone_number}")

    address = reverse_lookup(phone_number)

    if not address:
        error_msg = f"❌ No valid address found for {phone_number}"
        print(error_msg)
        return {"success": False, "error": error_msg}

    success = update_contact_address(contact_id, address)

    if not success:
        error_msg = f"❌ Failed to update HubSpot contact {contact_id}"
        print(error_msg)
        return {"success": False, "error": error_msg}

    print(f"✅ Successfully updated contact {contact_id} with address from Trestle.")
    return {"success": True}
