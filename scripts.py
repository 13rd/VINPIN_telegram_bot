import os
import paramiko
import winrm
import shutil


def create_server_scripts_folder(server_name):
    """Создание папки для скриптов сервера."""
    script_folder = f"server_scripts/{server_name}"
    os.makedirs(script_folder, exist_ok=True)

    # Определение источника скриптов в зависимости от типа сервера
    if "linux" in server_name.lower():
        source_folder = "scripts/linux"
    elif "windows" in server_name.lower():
        source_folder = "scripts/windows"
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
    script_folder = f"server_scripts/{server_name}"
    if os.path.exists(script_folder):
        shutil.rmtree(script_folder)


def list_scripts(server_name):
    """Получение списка скриптов для сервера."""
    script_folder = f"server_scripts/{server_name}"
    return [f for f in os.listdir(script_folder) if os.path.isfile(os.path.join(script_folder, f))]


def execute_script(server_name, script_name, connection_string):
    """Выполнение скрипта на удаленном сервере."""
    script_path = f"server_scripts/{server_name}/{script_name}"
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
        ssh.close()
        return output

    elif "windows" in connection_string.lower():
        print()
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