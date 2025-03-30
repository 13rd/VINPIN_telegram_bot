#!/bin/bash

# Имя контейнера
CONTAINER_NAME="log-generator"

# Проверяем, запущен ли контейнер
if ! docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Контейнер $CONTAINER_NAME не найден."
    exit 1
fi

# Остановка контейнера
echo "Остановка контейнера $CONTAINER_NAME..."
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

echo "Контейнер $CONTAINER_NAME остановлен и удален."