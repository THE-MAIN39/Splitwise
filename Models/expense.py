from Models.connection import get_connection
def add_expense(group_id, paid_by_user_id, amount, description):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO Expenses (Group_ID, Pair_ID, Amount, Expense_Date, Description) VALUES (%s, %s, %s, NOW(), %s)"
    cursor.execute(sql, (group_id, paid_by_user_id, amount, description))
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return expense_id

def share_expense(expense_id, user_id, share_amount):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO Expense_share (Expense_ID, User_ID, Share_Amount) VALUES (%s, %s, %s)"
    cursor.execute(sql, (expense_id, user_id, share_amount))
    conn.commit()
    conn.close()
