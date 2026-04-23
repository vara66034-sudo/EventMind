FROM node:24-alpine3.22 AS frontend-builder

WORKDIR /app/frontend

COPY frontend /app/frontend/

RUN npm ci

RUN npm run build

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY backend /app/backend/

RUN pip install --no-cache-dir -r ./backend/requirements.txt

COPY --from=frontend-builder /app/frontend/build ./frontend/build

WORKDIR /app/backend

EXPOSE 8099

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8099"]
