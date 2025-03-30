#!/bin/bash

# Имя контейнера
CONTAINER_NAME="log-generator"

# Путь к файлу логов на хосте
LOG_FILE="app.log"

# Копируем логи из контейнера на хост
echo "Получение логов из контейнера..."
docker cp $CONTAINER_NAME:/app/logs/app.log $LOG_FILE

echo "Логи сохранены в файл: $LOG_FILE"
cat $LOG_FILE