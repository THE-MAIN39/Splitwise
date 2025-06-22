import mysql.connector

def get_connection():
    
        ssl_disabled=False,  # ✅ Required for Clever Cloud
        ssl_verify_cert=False  # ✅ Since they disabled SSL verification
    )
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    print("📋 Tables in DB:", cursor.fetchall())  # ← Add this for confirmation

print("✅ Successfully connected to Clever Cloud")
return conn
