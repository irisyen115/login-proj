from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
from flask_cors import CORS
import re
import os

app = Flask(__name__)
load_dotenv()
CORS(app)

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

def is_valid_email(email):
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None

@app.route("/send-mail", methods=["POST"])
def send_mail():
    data = request.json
    subject = data.get("subject", "No Subject")[:100]
    recipient = data.get("recipient")
    body = data.get("body", "")[:5000]
    html_body = data.get("html_body", None)

    if not recipient or not is_valid_email(recipient):
        app.logger.error({"error": f"Invalid {recipient} email"})
        return jsonify({"error": "Invalid recipient email"}), 400

    try:
        msg = Message(subject, sender=app.config["MAIL_USERNAME"], recipients=[recipient])
        msg.body = body
        if html_body:
            msg.html = html_body
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        app.logger.error(f"Email sending failed: {str(e)}")
        app.logger.error(f"Email sending failed: {app.config}")
        return jsonify({"error": "Failed to send email"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)