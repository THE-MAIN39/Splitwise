from Models.connection import get_connection

def create_group(group_name, created_by):
    conn = get_connection()
    cursor = conn.cursor()

    # Insert the group
    sql = "INSERT INTO Groups (Group_name, Created_by, Created_at) VALUES (%s, %s, NOW())"
    cursor.execute(sql, (group_name, created_by))
    group_id = cursor.lastrowid

    # Auto-add the creator as a member
    cursor.execute("INSERT INTO Members (Group_ID, User_ID, Joined_at) VALUES (%s, %s, NOW())",
                   (group_id, created_by))

    conn.commit()
    conn.close()
    return group_id

def add_member_to_group(group_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO Members (Group_ID, User_ID, Joined_at) VALUES (%s, %s, NOW())"
    cursor.execute(sql, (group_id, user_id))
    conn.commit()
    conn.close()

def get_group_info(group_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Groups WHERE ID = %s", (group_id,))
    group = cursor.fetchone()
    if not group:
        raise Exception("Group not found")

    cursor.execute("""
        SELECT u.ID, u.First_name, u.Last_name, u.Email
        FROM Members m
        JOIN Userr u ON u.ID = m.User_ID
        WHERE m.Group_ID = %s
    """, (group_id,))
    members = cursor.fetchall()
    conn.close()

    group["members"] = members
    return group

def get_groups_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT ID, Group_name, Created_at
        FROM Groups
        WHERE Created_by = %s
    """
    cursor.execute(sql, (user_id,))
    groups = cursor.fetchall()
    conn.close()
    return groups


def get_group_summary(group_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Group info
    cursor.execute("SELECT * FROM groups WHERE ID = %s", (group_id,))
    group = cursor.fetchone()

    # Members
    cursor.execute("""
        SELECT u.ID, u.First_name, u.Last_name
        FROM group_members gm
        JOIN users u ON gm.User_ID = u.ID
        WHERE gm.Group_ID = %s
    """, (group_id,))
    members = cursor.fetchall()

    # Expenses
    cursor.execute("""
        SELECT * FROM expenses
        WHERE Group_ID = %s
        ORDER BY Created_at DESC
    """, (group_id,))
    expenses = cursor.fetchall()

    # Settlements
    cursor.execute("""
        SELECT * FROM settlements
        WHERE From_UserID IN (
            SELECT User_ID FROM group_members WHERE Group_ID = %s
        ) AND To_UserID IN (
            SELECT User_ID FROM group_members WHERE Group_ID = %s
        )
    """, (group_id, group_id))
    settlements = cursor.fetchall()

    conn.close()
    return {
        "group": group,
        "members": members,
        "expenses": expenses,
        "settlements": settlements
    }

