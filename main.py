from scripts import *


def main():
    server_name = "server1_linux"
    # create_server_scripts_folder(server_name)
    # delete_server_scripts_folder(server_name)
    list_scr = list_scripts(server_name)
    print(list_scr)
    output = execute_script(server_name, list_scr[1], "linuxserver.io:pass@localhost:22")
    print(output)

if __name__ == '__main__':
    main()
