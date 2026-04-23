FROM node:22-bookworm-slim AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

COPY backend ./backend
COPY config ./config
COPY --from=frontend-builder /app/frontend/build ./frontend/build

WORKDIR /app/backend

EXPOSE 8069

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8069"]
