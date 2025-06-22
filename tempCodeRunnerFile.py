import mysql.connector

conn = mysql.connector.connect(
    host="bsgpfm7hjvrfuuctqhaa-mysql.services.clever-cloud.com",
    user="u25tcgnb0dpj2a3t",
    password="jtQuCd4lNzhLl3qirC4e",
    database="bsgpfm7hjvrfuuctqhaa",
    port=3306
)

print("✅ Connected successfully!")
conn.close()