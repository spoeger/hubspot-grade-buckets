import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")

@app.route("/")
def home():
    return "Webhook receiver is live!"

@app.route("/receive-grade", methods=["POST"])
def receive_grade():
    data = request.json
    print("Received:", data)

    # Map external field names to HubSpot default fields
    hs_object_id = data.get("unique_id")
    hubspot_fields = {
        "firstname": data.get("first_name"),
        "lastname": data.get("last_name"),
        "address": data.get("address"),
        "city": data.get("city"),
        "state": data.get("state"),
        "zip": data.get("zip")
    }

    if not hs_object_id:
        return jsonify({"error": "Missing unique_id / hs_object_id"}), 400

    try:
        # Update the contact directly using hs_object_id
        update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{hs_object_id}"
        headers = {
            "Authorization": f"Bearer {HUBSPOT_API_KEY}",
            "Content-Type": "application/json"
        }
        update_payload = {
            "properties": hubspot_fields
        }

        update_res = requests.patch(update_url, headers=headers, json=update_payload)
        update_res.raise_for_status()

        return jsonify({
            "status": "contact updated",
            "hs_object_id": hs_object_id,
            "fields_updated": hubspot_fields
        }), 200

    except requests.exceptions.RequestException as e:
        print("Error updating HubSpot:", e)
        return jsonify({"error": str(e)}), 500
