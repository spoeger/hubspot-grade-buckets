from flask import Flask, request, jsonify
from update_contact_from_phone import process_contact

app = Flask(__name__)

@app.route("/webhook/update-contact", methods=["POST"])
def webhook_update_contact():
    data = request.get_json()

    # Validate inputs
    contact_id = data.get("contact_id")
    phone_number = data.get("phone_number")

    if not contact_id or not phone_number:
        return jsonify({
            "success": False,
            "error": "Missing contact_id or phone_number in request body"
        }), 400

    # Call the main logic
    result = process_contact(contact_id, phone_number)

    if not result.get("success"):
        return jsonify({
            "success": False,
            "error": result.get("error", "Unknown failure occurred")
        }), 500

    return jsonify({
        "success": True,
        "message": f"Contact {contact_id} updated successfully."
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
