from scripts import *
import database


def main():
    print(database.get_servers(1028701092))
    database.delete_server(database.get_servers(1028701092)[0]["_id"])
    print(database.get_servers(1028701092))

if __name__ == '__main__':
    main()
