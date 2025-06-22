from Models.connection import get_connection

def register_user(first_name, last_name, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO userr (First_name, Last_name, Email, Pass) VALUES (%s, %s, %s, %s)"
    values = (first_name, last_name, email, password)
    cursor.execute(sql, values)
    conn.commit()
    user_id = cursor.lastrowid  # ✅ this is the missing line
    conn.close()
    return user_id


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM userr WHERE Email=%s AND Pass=%s"
    cursor.execute(sql, (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

