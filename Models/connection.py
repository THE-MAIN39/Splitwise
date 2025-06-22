import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="bsgpfm7hjvrfuuctqhaa-mysql.services.clever-cloud.com",
            user="u25tcgnb0dpj2a3t",
            password="jtQuCd4lNzhLl3qirC4e",
            database="bsgpfm7hjvrfuuctqhaa",
            port=3306
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ DB Connection Error: {err}")
        return None
