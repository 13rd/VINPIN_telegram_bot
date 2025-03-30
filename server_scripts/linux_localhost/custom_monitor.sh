#!/bin/bash

# Получаем данные о CPU
cpu_usage=$(top -bn1 | grep '%Cpu(s)' | awk '{print "CPU Usage: " $2 " us, " $4 " sy, " $8 " id"}')

# Получаем данные о памяти
memory_usage=$(free -h | awk 'NR==2 {print "Memory Usage: Total: " $2 ", Used: " $3 ", Free: " $4 ", Available: " $7}')

# Получаем данные о дисковом пространстве
disk_usage=$(df -h | awk 'NR==2 {print "Disk Usage: Total: " $2 ", Used: " $3 ", Free: " $4 ", Usage: " $5}')

echo "Системная информация:"
echo $cpu_usage
echo $memory_usage
echo $disk_usage