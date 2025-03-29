from scripts import *
import database


def main():
    database.add_user(1028701092)
    print(database.get_user_by_id(1028701092))
    database.add_user(7897593957)
    print(database.get_user_by_id(7897593957))

if __name__ == '__main__':
    main()
