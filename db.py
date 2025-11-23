import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='PetAdoptionDB',
            user='root',
            password=''  # <-- change if needed
        )
        if conn.is_connected():
            print("Connected to PetAdoptionDB database successfully!")
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        print("Please check:")
        print("1. MySQL server is running")
        print("2. Database 'PetAdoptionDB' exists")
        print("3. Username and password are correct")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
