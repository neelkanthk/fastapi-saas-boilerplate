import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file if present

# Application configuration
api_name = os.getenv("API_NAME")

# Other configurations can be added here as needed
# For example, email server settings, logging settings, etc.

force_email_verification = os.getenv("FORCE_EMAIL_VERIFICATION", "True").lower() == "true"
force_https = os.getenv("FORCE_HTTPS", "False").lower() == "true"
base_url = os.getenv("BASE_URL", "http://localhost:8000")
allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
