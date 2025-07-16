# 1) Build the frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build         # outputs to /app/frontend/dist

# 2) Build the backend
FROM python:3.11-slim AS backend-build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 3) Final image
FROM python:3.11-slim
WORKDIR /app

# Copy Python dependencies
COPY --from=backend-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Copy backend code
COPY --from=backend-build /app /app
# Copy built frontend
COPY --from=frontend-build /app/frontend/dist /app/frontend_dist

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "agent_caddie.app:app", "--host", "0.0.0.0", "--port", "8080"]
