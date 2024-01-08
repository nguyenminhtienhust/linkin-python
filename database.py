
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# Connect to MySQL
def connect():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )



def initialize_db():
    conn = connect()
    cursor = conn.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        age INT
    )
    """
    cursor.execute(query)
    conn.close()

# Inside database.py
def create_user(name, age):
    conn = connect()
    cursor = conn.cursor()
    query = "INSERT INTO users (name, age) VALUES (%s, %s)"
    values = (name, age)
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return cursor.lastrowid
