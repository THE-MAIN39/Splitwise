from Models.connection import get_connection
def add_feedback(from_user_id, description, rating):
    conn = get_connection()
    cursor = conn.cursor()

    # Only insert if not exists
    cursor.execute("SELECT ID FROM feedback WHERE From_UserID = %s", (from_user_id,))
    if cursor.fetchone():
        raise Exception("Feedback already exists.")

    sql = """
        INSERT INTO feedback (From_UserID, Description, Rating, Feedback_Date)
        VALUES (%s, %s, %s, NOW())
    """
    cursor.execute(sql, (from_user_id, description, rating))
    conn.commit()
    conn.close()
