def record_settlement(from_user_id, to_user_id, amount, status):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO Settlements (From_UserID, To_UserID, Amount, Settlement_Date, Statuss) VALUES (%s, %s, %s, NOW(), %s)"
    cursor.execute(sql, (from_user_id, to_user_id, amount, status))
    conn.commit()
    conn.close()
