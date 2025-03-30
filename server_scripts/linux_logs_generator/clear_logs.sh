#!/bin/bash

# Имя контейнера
CONTAINER_NAME="log-generator"

# Удаление файла логов внутри контейнера
echo "Удаление логов в контейнере..."
docker exec $CONTAINER_NAME sh -c "> /app/logs/app.log"

echo "Логи в контейнере удалены."