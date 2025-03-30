from scripts import *
import database
from cryptography.fernet import Fernet




def main():
    # database.add_user(1028701092)
    # print(database.get_user_by_id(1028701092))
    # database.add_user(7897593957)
    print(database.delete_cluster(1028701092, "first"))
    database.delete_cluster(1028701092, "second")
    database.delete_cluster(1028701092, "aaa")
    database.delete_cluster(1028701092, "third")

if __name__ == '__main__':
    main()
