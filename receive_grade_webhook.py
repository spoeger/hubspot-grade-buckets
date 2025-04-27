# receive_grade_webhook.py

import os
import requests
from flask import Flask, request, jsonify
import time

app = Flask(__name__)
HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY")

@app.route("/")
def home():
    return "Grade webhook is live!"

@app.route("/receive-grade", methods=["POST"])
def receive_grade():
    data = request.json
    print("📥 Received grade payload:", data)

    unique_id = data.get("unique_id")
    grade = data.get("grade")

    if not unique_id or not grade:
        return jsonify({"error": "Missing unique_id or grade"}), 400

    try:
        start_update = time.time()

        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{unique_id}"
        headers = {
            "Authorization": f"Bearer {HUBSPOT_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "properties": {
                "grade": grade,
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
