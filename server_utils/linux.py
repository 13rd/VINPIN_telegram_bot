import paramiko

def get_linux_command(distribution):
    if "ubuntu" in distribution.lower() or "debian" in distribution.lower():
        return {
            "check_disk": "df -h",
            "check_memory": "free -h",
            "list_processes": "ps aux",
            "service_status": "systemctl status",
        }
    else:
        return {
            "check_disk": "df -h",
            "check_memory": "free -h",
            "list_processes": "ps aux",
            "service_status": "rc-service",

        }

def execute_command_on_linux(host, username, password, command_type):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)

    # Определение дистрибутива
    stdin, stdout, stderr = client.exec_command("cat /etc/os-release")
    os_info = stdout.read().decode().lower()

    # Получение команды в зависимости от дистрибутива
    commands = get_linux_command(os_info)
    command = commands.get(command_type, "echo 'Unknown command'")

    # Выполнение команды
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()
    return output, error


def main():
    output, error = execute_command_on_linux("localhost", "linuxserver.io", "pass", "check_memory")
    print(output)
    print(error)


if __name__ == '__main__':
    main()
