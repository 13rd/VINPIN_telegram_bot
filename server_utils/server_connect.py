import paramiko
import winrm

def execute_command_on_linux(host, port, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, port=port, username=username, password=password)
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()
    return output, error


def execute_command_on_windows(host, username, password, command):
    session = winrm.Session(f"http://{host}:5985/wsman", auth=(username, password))
    result = session.run_cmd(command)
    return result.std_out.decode(), result.std_err.decode()


if __name__ == '__main__':
    output, error = execute_command_on_linux("localhost",22, "linuxserver.io", "pass", "cat /etc/os-release")
    print(output)
    print(error)

