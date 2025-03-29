from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("mongo_uri")
DB_NAME = os.getenv("db_name")

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


def add_server(user_id, server_name, connection_string, scripts: list):
    """Добавление сервера в базу данных."""
    server_data = {
        "user_id": user_id,
        "server_name": server_name,
        "connection_string": connection_string,
        "scripts": scripts
    }
    servers_collection.insert_one(server_data)


def get_servers(user_id):
    """Получение списка серверов пользователя."""
    return list(servers_collection.find({"user_id": user_id}))


def delete_server(server_id):
    """Удаление сервера из базы данных."""
    result = servers_collection.delete_one({"_id": server_id})
    return result.deleted_count > 0


def get_server_by_id(server_id):
    """Получение сервера по его ID."""
    return servers_collection.find_one({"_id": server_id})


def get_server_by_server_name(server_name):
    """Получение сервера по его NAME."""
    return servers_collection.find_one({"server_name": server_name})