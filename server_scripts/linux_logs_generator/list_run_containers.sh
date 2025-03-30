#!/bin/bash

# Выводим список запущенных контейнеров
echo "Список запущенных контейнеров:"
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}"