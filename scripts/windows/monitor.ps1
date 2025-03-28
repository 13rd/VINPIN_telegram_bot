Write-Host "CPU Usage:"
Get-WmiObject Win32_Processor | Select-Object LoadPercentage
Write-Host "Memory Usage:"
Get-WmiObject Win32_OperatingSystem | Select-Object FreePhysicalMemory, TotalVisibleMemorySize
Write-Host "Disk Usage:"
Get-PSDrive C | Select-Object Used, Free