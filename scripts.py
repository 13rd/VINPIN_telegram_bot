import os
import paramiko
import winrm


def create_server_scripts_folder(server_name):
    """Создание папки для скриптов сервера."""
    os.makedirs(f"server_scripts/{server_name}", exist_ok=True)
    # Копирование стандартных скриптов
    if "linux" in server_name.lower():
        os.system(f"cp scripts/linux/* server_scripts/{server_name}/")
    elif "windows" in server_name.lower():
        os.system(f"cp scripts/windows/* server_scripts/{server_name}/")


def list_scripts(server_name):
    """Получение списка скриптов для сервера."""
    script_folder = f"server_scripts/{server_name}"
    return [f for f in os.listdir(script_folder) if os.path.isfile(os.path.join(script_folder, f))]


def execute_script(server_name, script_name, connection_string):
    """Выполнение скрипта на удаленном сервере."""
    script_path = f"server_scripts/{server_name}/{script_name}"

    if "linux" in connection_string.lower():
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