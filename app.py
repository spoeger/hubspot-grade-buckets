from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Webhook receiver is live!"

@app.route("/receive-grade", methods=["POST"])
def receive_grade():
    data = request.json
    print("Received:", data)

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(debug=True)
