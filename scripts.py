import base64
import os
import socket
import sys
from concurrent.futures import ThreadPoolExecutor
import paramiko
import winrm
import shutil
import subprocess
from pypsrp.client import Client

bot_absolute_path = os.path.abspath(__file__).replace("\\\\", "/").replace("scripts.py", "")

def create_server_scripts_folder(server_name):
    """Создание папки для скриптов сервера."""
    script_folder = f"{bot_absolute_path}server_scripts/{server_name}"
    os.makedirs(script_folder, exist_ok=True)

    # Определение источника скриптов в зависимости от типа сервера
    if "linux" in server_name.lower():
        source_folder = bot_absolute_path+"scripts/linux"
    elif "windows" in server_name.lower():
        source_folder = bot_absolute_path+"scripts/windows"
    else:
        return

    # Копирование всех файлов из исходной папки в папку сервера
    for filename in os.listdir(source_folder):
        source_file = os.path.join(source_folder, filename)
        destination_file = os.path.join(script_folder, filename)
        if os.path.isfile(source_file):  # Копируем только файлы
            shutil.copy(source_file, destination_file)


def delete_server_scripts_folder(server_name):
    """Удаление папки с файлами скриптов сервера."""
    script_folder = f"{bot_absolute_path}server_scripts/{server_name}"
    if os.path.exists(script_folder):
        shutil.rmtree(script_folder)


def list_scripts(server_name):
    """Получение списка скриптов для сервера."""
    script_folder = f"{bot_absolute_path}server_scripts/{server_name}"
    return [f for f in os.listdir(script_folder) if os.path.isfile(os.path.join(script_folder, f))]


def execute_script(server_name, script_name, connection_string):
    """Выполнение скрипта на удаленном сервере."""
    script_path = f"{bot_absolute_path}server_scripts/{server_name}/{script_name}"
    print(script_path, connection_string)

    if "linux" in server_name.lower():
        print("linux")
        # Разбор строки подключения
        user, password = connection_string.split(":")[0], connection_string.split(":")[1].split("@")[0]
        ip, port = connection_string.split("@")[1].split(":")
        port = int(port)

        # SSH-подключение
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=user, password=password)
        stdin, stdout, stderr = ssh.exec_command(f"bash {script_path}")
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        return output, error


    elif "windows" in connection_string.lower():
        print("windows")
        # Разбор строки подключения
        user, password = connection_string.split(":")[0], connection_string.split(":")[1].split("@")[0]
        ip = connection_string.split("@")[1]

        # Чтение содержимого скрипта
        with open(script_path, "r") as f:
            script_content = f.read()

        # Подключение к Windows Server через WinRM
        session = winrm.Session(
            f"http://{ip}:5985/wsman",
            auth=(user, password),
            transport="ntlm"
        )
        result = session.run_ps(script_content)  # Выполнение PowerShell-скрипта
        if result.status_code == 0:
            return result.std_out.decode()
        else:
            return result.std_err.decode()

    return "Unsupported server type."


def copy_and_execute_script(server_name, script_name, connection_string):
    """
    Копирует скрипт на удаленный сервер, выполняет его и удаляет после завершения.
    """
    script_path = f"{bot_absolute_path}server_scripts/{server_name}/{script_name}"
    if "linux" in server_name:
        # Разбор строки подключения
        user, password = connection_string.split(":")[0], connection_string.split(":")[1].split("@")[0]
        ip, port = connection_string.split("@")[1].split(":")
        port = int(port)

        # Создание SSH-клиента
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=port, username=user, password=password)

            # Копирование файла через SFTP
            sftp = ssh.open_sftp()
            remote_path = f"/tmp/{os.path.basename(script_path)}"
            sftp.put(script_path, remote_path)
            sftp.close()

            # Выполнение скрипта
            stdin, stdout, stderr = ssh.exec_command(f"bash {remote_path}")
            output = stdout.read().decode().replace("\n", " \n")
            error = stderr.read().decode()
            # Удаление файла
            ssh.exec_command(f"rm {remote_path}")
            ssh.close()
            return output, error

        except paramiko.SSHException as e:
            # Обработка ошибок SSH (например, проблемы с аутентификацией)
            print(f"SSHException: {e}")
            return "", "Ошибка подключения SSH"

        except socket.timeout as e:
            # Обработка таймаутов при подключении
            print(f"Socket timeout: {e}")
            return "", "Сервер не отвечает (таймаут)"

        except Exception as e:
            print(e)
            return "", "Ошибка строки подключения"

    elif "windows" in server_name:
        # Разбор строки подключения
        user, password = connection_string.split(":")[0], connection_string.split(":")[1].split("@")[0]
        ip, port = connection_string.split("@")[1].split(":")
        # port = int(port)

        try:
            session = winrm.Session(ip, auth=(user, password), transport='ntlm', read_timeout_sec=60)
            result = session.run_cmd("ipconfig")

            # return result.std_out.decode('utf-8'), result.std_err.decode('utf-8')

            # Путь к локальному файлу
            local_file_path = script_path
            remote_file_path = f'C:\\Windows\\Temp\\{os.path.basename(script_path)}'

            # Чтение файла и кодирование в Base64
            with open(local_file_path, 'rb') as file:
                file_content = file.read()
                encoded_content = base64.b64encode(file_content).decode('utf-8')

            # Команда для создания файла на удалённом сервере
            create_file_command = f'''
            $base64Content = "{encoded_content}"
            $content = [System.Convert]::FromBase64String($base64Content)
            Set-Content -Path "{remote_file_path}" -Value $content -Encoding Byte
            '''

            # Выполнение команды для создания файла
            result = session.run_ps(create_file_command)
            if result.status_code != 0:
                print("Ошибка при создании файла на сервере:")
                print(result.std_err.decode('utf-8'))
                exit(1)

            print("Файл успешно передан на сервер.")

            # Выполнение скрипта на удалённом сервере
            execute_command = f'cmd.exe /c "{remote_file_path}"'
            result = session.run_ps(execute_command)
            output = "Вывод: "
            errors = "Ошибки: "
            if result.status_code == 0:
                print("Скрипт выполнен успешно:")
                output = result.std_out.decode('utf-8')
            else:
                print("Ошибка при выполнении скрипта:")
                errors = result.std_err.decode('utf-8')

            # Удаление файла на удалённом сервере
            delete_command = f'Remove-Item -Path "{remote_file_path}" -Force'
            result = session.run_ps(delete_command)
            if result.status_code == 0:
                print("Файл успешно удалён с сервера.")
            else:
                print("Ошибка при удалении файла:")
                print(result.std_err.decode('utf-8'))


            return output, errors
        except Exception as e:
            print(e)
            return "", "Ошибка строки подключения"

    else:
        return "", "Unsupported server type."

def folder_is_available(server_name):
    return not os.path.exists(f"{bot_absolute_path}server_scripts/{server_name}")

def execute_script_on_cluster(servers, script_name):
    """
    Выполняет команду на всех серверах в кластере параллельно.
    """
    results = {}
    print(servers)

    for server in servers:
        try:
            output, errors = copy_and_execute_script(server["server_name"], script_name, server["connection_string"])
            results[server["server_name"]] = [output, errors]
            print(server)
        except Exception as e:
            results[server["server_name"]] = ["", f"Ошибка: {str(e)}"]


    return results

def create_cluster_scripts_folder(cluster_name):
    """Создание папки для скриптов сервера."""
    cluster_folder = f"{bot_absolute_path}cluster_scripts/{cluster_name}"
    os.makedirs(cluster_folder, exist_ok=True)

    source_folder = bot_absolute_path+"clusters_default_script/"

    # Копирование всех файлов из исходной папки в папку сервера
    for filename in os.listdir(source_folder):
        source_file = os.path.join(source_folder, filename)
        destination_file = os.path.join(cluster_folder, filename)
        if os.path.isfile(source_file):  # Копируем только файлы
            shutil.copy(source_file, destination_file)

def delete_cluster_scripts_folder(cluster_name):
    """Удаление папки с файлами скриптов сервера."""
    script_folder = f"{bot_absolute_path}cluster_scripts/{cluster_name}"
    if os.path.exists(script_folder):
        shutil.rmtree(script_folder)

def list_scripts_cluster(cluster_name):
    """Получение списка скриптов для сервера."""
    script_folder = f"{bot_absolute_path}cluster_scripts/{cluster_name}"
    return [f for f in os.listdir(script_folder) if os.path.isfile(os.path.join(script_folder, f))]