import psycopg2
from dotenv import load_dotenv
import os
from sshtunnel import SSHTunnelForwarder

username = "YOUR_CS_USERNAME"
password = "YOUR_CS_PASSWORD"
dbName = "YOUR_DB_NAME"

load_dotenv()

def connection():
    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=username,
                                ssh_password=password,
                                remote_bind_address=('127.0.0.1', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            params = {
                'dbname': dbName,
                'user': username,
                'password': password,
                'host': 'localhost',
                'port': server.local_bind_port
            }


            conn = psycopg.connect(**params)
            curs = conn.cursor()
            print("Database connection established")


            conn.close()
    except Exception as e:
        print("Connection failed:", e)
