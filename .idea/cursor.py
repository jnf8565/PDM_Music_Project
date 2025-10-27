import os
import psycopg2 as pg2
from dotenv import load_dotenv

connection = pg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=os.getenv("DB_PORT")
    )

cursor = connection.cursor()