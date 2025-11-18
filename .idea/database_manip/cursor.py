import os
import psycopg2 as pg2
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder


load_dotenv()


def query(sql_query, vars=(), fetch=False):
    db_name = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    connection = None
    try:
        with SSHTunnelForwarder(
            ('starbug.cs.rit.edu', 22),
            ssh_username = username,
            ssh_password = password,
            remote_bind_address=('127.0.0.1', 5432)
            ) as tunnel:
           
            tunnel.start()
            params = {
                'database' : db_name,
                'user' : username,
                'password' : password,
                'host' : 'localhost',
                'port' : tunnel.local_bind_port
            }
            connection = pg2.connect(**params)
            cursor = connection.cursor()
            if vars:
                cursor.execute(sql_query, vars)
            else:
                cursor.execute(sql_query)
            if fetch:
                result = cursor.fetchall()
            else:
                result = None
            connection.commit()
            cursor.close()
            connection.close()
            return result
    except Exception as e:
        print(e)
        if connection != None:
            connection.close()

