from Models.connection import get_connection

def add_settlement(from_user_id, to_user_id, amount, status="pending", group_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO settlements (From_UserID, To_UserID, Amount, Status, Settlement_Date, Group_ID)
    VALUES (%s, %s, %s, %s, NOW(), %s)
    """
    cursor.execute(sql, (from_user_id, to_user_id, amount, status, group_id))
    conn.commit()
    settlement_id = cursor.lastrowid
    conn.close()
    return settlement_id

def update_settlement_status(settlement_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "UPDATE settlements SET Status = %s, Settlement_Date = NOW() WHERE ID = %s"
    cursor.execute(sql, (status, settlement_id))
    conn.commit()
    conn.close()

