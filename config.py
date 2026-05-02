import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="task_manager"
    )

def get_secret_key():
    return "secret123"