import mysql.connector  # Correct import

def get_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='MEHARZ499206',
        database='splitwise2'
    )
    return conn


print("Successfully done")
