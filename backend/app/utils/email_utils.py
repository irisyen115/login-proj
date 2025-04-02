import requests

def trigger_email(url, recipient, subject, body_str):
    data = {
        "recipient": recipient,
        "subject": subject,
        "body": body_str
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to send email, status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
