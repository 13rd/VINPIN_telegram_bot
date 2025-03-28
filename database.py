from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv
import hashlib
from cryptography.fernet import Fernet

import scripts

load_dotenv()

MONGO_URI = os.getenv("mongo_uri")
DB_NAME = os.getenv("db_name")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

cipher_suite = Fernet(ENCRYPTION_KEY)

# Подключение к MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
servers_collection = db["servers"]

def add_user(user_id: int):
    users_collection.insert_one({"user_id": user_id})

def delete_user(user_id: int):
    result = users_collection.delete_one({"user_id": user_id})
    return result.deleted_count > 0

def get_user_by_id(user_id: int):
    user = users_collection.find_one({"user_id": user_id})
    return user


def add_server(user_id, server_name, connection_string):
    """Добавление сервера в базу данных."""
    encrypted_data = cipher_suite.encrypt(connection_string.encode("utf-8"))
    server_data = {
        "user_id": user_id,
        "server_name": server_name,
        "connection_string": encrypted_data,
    }
    servers_collection.insert_one(server_data)


def get_servers(user_id):
    """Получение списка серверов пользователя."""
    servers = list(servers_collection.find({"user_id": user_id}))
    for server in servers:
        server["connection_string"] = cipher_suite.decrypt(server["connection_string"]).decode('utf-8')
    return servers


def delete_server(server_name):
    """Удаление сервера из базы данных."""
    scripts.delete_server_scripts_folder(server_name)
    result = servers_collection.delete_one({"server_name": server_name})
    return result.deleted_count > 0


def get_server_by_id(server_id):
    """Получение сервера по его ID."""
    return servers_collection.find_one({"_id": server_id})


def get_server_by_server_name(server_name):
    """Получение сервера по его NAME."""
    server = servers_collection.find_one({"server_name": server_name})
    server["connection_string"] = cipher_suite.decrypt(server["connection_string"]).decode('utf-8')
    return server