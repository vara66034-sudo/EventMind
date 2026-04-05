#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] git pull"
git pull

echo "[2/4] Остановка контейнеров проекта"
docker compose down --remove-orphans

echo "[3/4] Сборка без кэша"
docker compose build --no-cache

echo "[4/4] Запуск контейнеров заново"
docker compose up -d --force-recreate

echo "Готово."
