# Create virtual environment

uv venv

# Activate virtual environment

.\.venv\Scripts\activate

# Install requirments.txt

uv pip install -r requirements.txt

# Run docker

docker-compose -f docker-compose-dev.yaml up --build
