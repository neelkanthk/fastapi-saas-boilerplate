import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file if present

# OAuth2 configuration
oauth2_secret_key = os.getenv("OAUTH2_SECRET_KEY")
oauth2_algorithm = os.getenv("OAUTH2_ALGORITHM")
oauth2_access_token_expiry = int(os.getenv("OAUTH2_ACCESS_TOKEN_EXPIRE_MINUTES"))
