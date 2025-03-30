#!/bin/bash

# Имя контейнера
CONTAINER_NAME="log-generator"

# Проверяем, запущен ли контейнер
if docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Контейнер $CONTAINER_NAME уже существует. Остановите его перед запуском."
    exit 1
fi

# Сборка и запуск контейнера
echo "Сборка и запуск контейнера..."
#docker build -t  nnikitchenko/log-generator .
docker run -d --name $CONTAINER_NAME nnikitchenko/log-generator

echo "Контейнер $CONTAINER_NAME запущен."