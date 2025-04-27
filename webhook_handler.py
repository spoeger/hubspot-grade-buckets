from flask import Flask, request, jsonify
from update_contact_from_phone import process_contact
import os
import requests
import time
from log_to_sheet import log_to_sheet  # ✅ NEW import for logging steps to Google Sheets

app = Flask(__name__)

# --- TRESTLE ROUTE ---
@app.route("/webhook/update-contact", methods=["POST"])
def webhook_update_contact():
    try:
        data = request.get_json()

        # Validate inputs
        contact_id = data.get("contact_id")
        phone_number = data.get("phone_number")

        if not contact_id or not phone_number:
            return jsonify({
                "success": False,
                "error": "Missing contact_id or phone_number in request body"
            }), 400

        print(f"📞 Received update request for contact {contact_id} with phone {phone_number}")

        script_name = "Update Contact Script"
        start_processing = time.time()

        # Call the main logic
        result = process_contact(contact_id, phone_number)

        elapsed_processing = round(time.time() - start_processing, 2)

        if not result.get("success"):
            log_to_sheet(script_name, "Update Contact", "Failed", f"Failed updating contact {contact_id}", start_time=start_processing)
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown failure occurred")
            }), 500

        log_to_sheet(script_name, "Update Contact", "Success", f"Successfully updated contact {contact_id}", start_time=start_processing)
        return jsonify({
            "success": True,
            "message": f"Contact {contact_id} updated successfully."
        }), 200

    except Exception as e:
        import traceback
        error_message = traceback.format_exc()
        log_to_sheet("Update Contact Script", "Webhook Error", "Error", error_message)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# --- MORTGAGE STRENGTH ROUTE ---
@app.route("/receive-grade", methods=["POST"])
def receive_grade():
    data = request.get_json()
    print("📥 Received grade payload:", data)

    unique_id = data.get("unique_id")
    grade = data.get("grade")

    if not unique_id or not grade:
        return jsonify({"error": "Missing unique_id or grade"}), 400

    try:
        start_update = time.time()

        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{unique_id}"
        headers = {
            "Authorization": f"Bearer {os.environ.get('HUBSPOT_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "properties": {
                "grade": grade
            }
        }

        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()

        elapsed_update = time.time() - start_update
        print(f"✅ Grade '{grade}' added to contact {unique_id} (⏱️ {elapsed_update:.2f}s)")
        return jsonify({"status": "success", "updated": unique_id}), 200

    except requests.exceptions.RequestException as e:
        print("❌ HubSpot update failed:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
