import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file if present

# Email configuration
email_api_host = os.getenv("EMAIL_API_HOST")
email_api_key = os.getenv("EMAIL_API_KEY")
email_api_endpoint = f"https://{email_api_host}/api/send/4030462"
email_from = os.getenv("EMAIL_FROM")
email_from_name = os.getenv("EMAIL_FROM_NAME")
email_reply_to = os.getenv("EMAIL_REPLY_TO", email_from)
email_reply_to_name = os.getenv("EMAIL_REPLY_TO_NAME", email_from_name)
