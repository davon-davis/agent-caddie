# Dockerfile (put this at your repo root)
FROM python:3.11-slim

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Expose the port Fly uses by default
ENV PORT 8080
CMD ["uvicorn", "agent_caddie.app:app", "--host", "0.0.0.0", "--port", "8080"]
