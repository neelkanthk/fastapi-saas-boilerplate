from fastapi import BackgroundTasks, Request
import app.config.email as email_config
import requests


def send_email(receiver_email: str, subject: str, body: str):
    url = email_config.email_api_endpoint
    api_token = email_config.email_api_key
    headers = {
        "Host": email_config.email_api_host,
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": {
            "email": email_config.email_from,
            "name": email_config.email_from_name
        },
        "to": [
            {
                "email": receiver_email
            }
        ],
        "subject": subject,
        "text": body,
        "category": "Testing"
    }

    response = requests.post(url, json=payload, headers=headers)
    print("Email sent:", response.status_code, response.text)


def send_signup_verification_email(to: str, token: str, background_tasks: BackgroundTasks, request: Request):
    verification_link = str(request.url_for("verify_email")) + f"?token={token}"
    subject = "Webscan || Verify your email"
    body = f"Please click the following link to verify your email: {verification_link}"

    # Sending email in the background
    background_tasks.add_task(send_email, to, subject, body)


def send_password_reset_verification_email(to: str, token: str, background_tasks: BackgroundTasks, request: Request):
    verification_link = str(request.url_for("reset_password")) + f"?token={token}"
    subject = "Webscan || Reset your password"
    body = f"Please click the following link to reset your password: {verification_link}"

    # Sending email in the background
    background_tasks.add_task(send_email, to, subject, body)
