@echo off

:: Отображение загрузки CPU
echo CPU Usage:
wmic cpu get LoadPercentage /value | find "LoadPercentage"

:: Отображение использования памяти
echo Memory Usage:
wmic OS get FreePhysicalMemory, TotalVisibleMemorySize /value | findstr "FreePhysicalMemory TotalVisibleMemorySize"

:: Отображение использования диска
echo Disk Usage:
for /f "tokens=3" %%A in ('fsutil volume diskfree C: ^| find "Total # of bytes"') do (
    set total=%%A
)
for /f "tokens=3" %%B in ('fsutil volume diskfree C: ^| find "Total # of free bytes"') do (
    set free=%%B
)

:: Проверка, что переменные установлены
if not defined total set total=0
if not defined free set free=0

:: Преобразование байтов в гигабайты
set /a used_gb=%total%/1073741824
set /a free_gb=%free%/1073741824

:: Вывод результата
echo Used: %used_gb% GB
echo Free: %free_gb% GB

pause