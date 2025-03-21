from flask import Flask, request, jsonify
from flask_mail import Mail, Message
import config

app = Flask(__name__)
app.config.from_object(config)

mail = Mail(app)

@app.route("/send-mail", methods=["POST"])
def send_mail():
    data = request.json
    subject = data.get("subject", "No Subject")
    recipient = data.get("recipient")
    body = data.get("body", "")

    if not recipient:
        return jsonify({"error": "Recipient is required"}), 400

    try:
        msg = Message(subject, sender=app.config["MAIL_USERNAME"], recipients=[recipient])
        msg.body = body
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)