import os
import paramiko
import winrm
import shutil
import subprocess

bot_absolute_path = "C:/Python/VINPIN_telegram_bot/"

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
    if "linux" in connection_string.lower():
        # Разбор строки подключения
        user, password = connection_string.split(":")[0], connection_string.split(":")[1].split("@")[0]
        ip, port = connection_string.split("@")[1].split(":")
        port = int(port)

        # Создание SSH-клиента
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
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Удаление файла
        ssh.exec_command(f"rm {remote_path}")
        ssh.close()

        return output, error

    elif "windows" in connection_string.lower():
        # Разбор строки подключения
        user, password = connection_string.split(":")[0], connection_string.split(":")[1].split("@")[0]
        ip, port = connection_string.split("@")[1].split(":")
        port = int(port)

        # Копирование файла через SCP
        remote_path = f"C:\\temp\\{os.path.basename(script_path)}"
        scp_command = f"scp -P {port} {script_path} {user}@{ip}:{remote_path}"
        subprocess.run(scp_command, shell=True, check=True)

        # Выполнение скрипта через PowerShell
        ps_command = f"powershell.exe -Command Invoke-Expression {remote_path}"
        output = subprocess.check_output(ps_command, shell=True).decode()

        # Удаление файла
        del_command = f"powershell.exe -Command Remove-Item {remote_path}"
        subprocess.run(del_command, shell=True, check=True)

        return output

    else:
        return "Unsupported server type."