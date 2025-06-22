from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from Models.user import register_user, login_user
from Models.group import create_group, add_member_to_group, get_group_info, get_group_summary
from Models.expense import add_expense, share_expense
from Models.feedback import add_feedback
from Models.settlement import add_settlement, update_settlement_status
from Models.connection import get_connection
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'



# DB Connection
def get_connection():
    return mysql.connector.connect(
        host="bsgpfm7hjvrfuuctqhaa-mysql.services.clever-cloud.com",
        user="u25tcgnb0dpj2a3t",
        password="jtQuCd4lNzhLl3qirC4e",
        database="bsgpfm7hjvrfuuctqhaa",
        port=3306
    )













# Your routes (add here or import them)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)

# Set the admin ID here
ADMIN_ID = 68  # You can change this to any admin user ID

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return redirect('/login')

# ------------------ Login ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = login_user(data['email'], data['password'])
        if user:
            session['user_id'] = user['ID']
            flash("✅ Logged in successfully! Welcome, " + user['First_name'] + "!", "success")  
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# ------------------ Register ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        user_id = register_user(data['first_name'], data['last_name'], data['email'], data['password'])
        
        flash("✅ Account registered successfully! Please log in.", "success")  # 🔔 Flash message here
        return redirect('/login')
    
    return render_template('register.html')
#-------------------------------------------------------

# ------------------ Dashboard ------------------
# ------------------ Dashboard ------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = int(session['user_id'])  # Ensure integer
    ADMIN_ID = 68  # 👑 Admin ID

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Get full user info including username & email
    cursor.execute("SELECT ID, First_name, Last_name, Email, Wallet FROM userr WHERE ID = %s", (user_id,))
    user = cursor.fetchone()

    if user_id == ADMIN_ID:
        # ✅ Admin views
        cursor.execute("SELECT * FROM groups")
        all_groups = cursor.fetchall()

        cursor.execute("SELECT * FROM members")
        all_members = cursor.fetchall()

        cursor.execute("SELECT * FROM feedback")
        all_feedbacks = cursor.fetchall()

        cursor.execute("SELECT * FROM settlements")
        all_settlements = cursor.fetchall()

        conn.close()

        return render_template(
            'admin_dashboard.html',
            user=user,
            all_groups=all_groups,
            all_members=all_members,
            all_feedbacks=all_feedbacks,
            all_settlements=all_settlements
        )

    conn.close()
    # ✅ Normal user dashboard
    return render_template('dashboard.html', user=user)



#====================================================
@app.route('/settle-wallet/<int:group_id>', methods=['POST'])
def settle_with_wallet(group_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Step 1: Get user's wallet balance
        cursor.execute("SELECT Wallet FROM userr WHERE ID = %s", (user_id,))
        wallet = cursor.fetchone()['Wallet']

        # Step 2: Get all pending settlements in this group for this user
        cursor.execute("""
            SELECT ID, To_UserID, Amount
            FROM settlements
            WHERE From_UserID = %s AND Group_ID = %s AND Status = 'pending'
        """, (user_id, group_id))
        pending_settlements = cursor.fetchall()

        total_amount = sum([s['Amount'] for s in pending_settlements])

        if wallet < total_amount:
            return render_template("error.html", error_message="❌ Not enough Wallet balance to settle all debts in this group.")

        # Step 3: Update wallet balances and mark settlements as complete
        for s in pending_settlements:
            to_user = s['To_UserID']
            amount = s['Amount']

            # Deduct from current user
            cursor.execute("UPDATE userr SET Wallet = Wallet - %s WHERE ID = %s", (amount, user_id))
            # Add to receiver
            cursor.execute("UPDATE userr SET Wallet = Wallet + %s WHERE ID = %s", (amount, to_user))
            # Mark settlement as complete
            cursor.execute("UPDATE settlements SET Status = 'complete', Settlement_Date = NOW() WHERE ID = %s", (s['ID'],))

        conn.commit()
        conn.close()
        return render_template("message.html", message="✅ All pending settlements in this group have been paid using your Wallet!")

    except Exception as e:
        conn.rollback()
        conn.close()
        return render_template("error.html", error_message="❌ " + str(e))


# ------------------ Logout ------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
##################################################
@app.route('/group/<int:group_id>/summary')
def group_summary(group_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get group info
    cursor.execute("SELECT * FROM groups WHERE ID = %s", (group_id,))
    group = cursor.fetchone()

    # Get members
    cursor.execute("""
        SELECT u.ID, u.First_name, u.Last_name 
        FROM members gm 
        JOIN userr u ON gm.User_ID = u.ID 
        WHERE gm.Group_ID = %s
    """, (group_id,))
    members = cursor.fetchall()
    member_ids = [str(member['ID']) for member in members]

    # Get expenses
    cursor.execute("""
        SELECT e.ID, e.Description, e.Amount, u.First_name AS Paid_by
        FROM expenses e
        JOIN userr u ON e.Pair_ID = u.ID
        WHERE e.Group_ID = %s
    """, (group_id,))
    expenses = cursor.fetchall()

    # Get settlements related to these members
    if member_ids:
        ids_str = ",".join(member_ids)
        cursor.execute("""
    SELECT s.*, 
           uf.First_name AS From_Name, 
           ut.First_name AS To_Name
    FROM settlements s
    JOIN userr uf ON s.From_UserID = uf.ID
    JOIN userr ut ON s.To_UserID = ut.ID
    WHERE s.Group_ID = %s
""", (group_id,))
        settlements = cursor.fetchall()
    else:
        settlements = []

    conn.close()

    return render_template('group_summary.html',
                           group=group,
                           members=members,
                           expenses=expenses,
                           settlements=settlements)

##################################################
@app.route('/add-expense/<int:group_id>', methods=['GET', 'POST'])
def handle_add_expense(group_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch group info and creator
        cursor.execute("SELECT Group_name, Created_by FROM Groups WHERE ID = %s", (group_id,))
        group = cursor.fetchone()

        if not group:
            conn.close()
            return render_template("error.html", error_message="❌ Group not found.")

        # ❌ If not the creator, deny access
        if int(group['Created_by']) != int(user_id):
            conn.close()
            return render_template("error.html", error_message="❌ Only the group creator can add expenses.")

        if request.method == 'GET':
            # Load members to show in form
            cursor.execute("""
                SELECT u.ID, u.First_name
                FROM members m
                JOIN userr u ON u.ID = m.User_ID
                WHERE m.Group_ID = %s
            """, (group_id,))
            members = cursor.fetchall()
            conn.close()
            return render_template("add_expense.html", group=group, members=members, group_id=group_id)

        elif request.method == 'POST':
            desc = request.form['description']
            amount = float(request.form['amount'])
            pair_id = int(request.form['pair_id'])
            type = request.form['type']
            involved_users = request.form.getlist('involved_users')

            expense_id = add_expense(group_id, pair_id, amount, desc)
            share_amount = round(amount / len(involved_users), 2)

            for uid in involved_users:
                uid = int(uid)
                share_expense(expense_id, uid, share_amount)

                if uid != pair_id:
                    add_settlement(
                        from_user_id=uid,
                        to_user_id=pair_id,
                        amount=share_amount,
                        status='pending',
                        group_id=group_id
                    )

            conn.close()
            flash("✅ Expense added successfully!")
            return redirect('/groups')

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()

        return render_template("error.html", error_message=f"❌ Error: {str(e)}")


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ------------------ View Groups ------------------
@app.route('/groups')
def groups():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT distinct  g.* FROM Groups g
        JOIN Members m ON g.ID = m.Group_ID
        WHERE m.User_ID = %s
    """, (session['user_id'],))
    group_list = cursor.fetchall()
    conn.close()
    
    return render_template('groups.html', group_list=group_list)

# ------------------ Create Group Page ------------------
@app.route('/create-group')
def create_group_page():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template("create_group.html", user_id=session['user_id'])
#################################
@app.route('/group/<int:group_id>')
def view_group(group_id):
    if 'user_id' not in session:
        return redirect('/login')
    try:
        group_data = get_group_info(group_id)
        group = get_group_info(group_id) 
        return render_template('group_details.html', group=group_data)
    except Exception as e:
        return render_template('error.html', error_message=str(e))

# ------------------ API: Create Group ------------------
@app.route('/api/create-group', methods=['POST'])
def group():
    try:
        group_id = create_group(request.form['group_name'], request.form['created_by'])
        flash("Group created successfully!", "success")
        return redirect('/groups')
    except Exception as e:
        return render_template('error.html', error_message=str(e))

# ------------------ Join Group Page ------------------
@app.route('/join-group', methods=['GET', 'POST'])
def join_group():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        try:
            group_id = request.form['group_id']
            conn = get_connection()
            cursor = conn.cursor()

            # Check if group exists
            cursor.execute("SELECT ID FROM Groups WHERE ID = %s", (group_id,))
            if not cursor.fetchone():
                raise Exception("Group not found")

            # Check if user is already a member
            cursor.execute("SELECT * FROM Members WHERE Group_ID = %s AND User_ID = %s", (group_id, session['user_id']))
            if cursor.fetchone():
                raise Exception("Already a member of this group")

            # Add member
            cursor.execute("INSERT INTO Members (Group_ID, User_ID, Joined_at) VALUES (%s, %s, NOW())", (group_id, session['user_id']))
            conn.commit()
            conn.close()

            return render_template('join_group.html', message="✅ Successfully joined the group!")
        except Exception as e:
            return render_template('join_group.html', message="❌ " + str(e))

    return render_template('join_group.html')

# ------------------ API: Add Member to Group ------------------
@app.route('/group/member', methods=['POST'])
def add_member():
    try:
        data = request.get_json(force=True)
        group_id = data['group_id']
        user_id = data['user_id']

        conn = get_connection()
        cursor = conn.cursor()

        # Check for duplicate
        cursor.execute("SELECT 1 FROM Members WHERE Group_ID = %s AND User_ID = %s", (group_id, user_id))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "User already a member of this group"}), 400

        # Add if not exists
        cursor.execute("INSERT INTO Members (Group_ID, User_ID, Joined_at) VALUES (%s, %s, NOW())", (group_id, user_id))
        conn.commit()
        conn.close()

        return jsonify({"message": "Member added to group", "status": "success"})
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500


# ------------------ API: Add Expense ------------------
@app.route('/expense', methods=['POST'])
def expense():
    data = request.json
    try:
        expense_id = add_expense(data['group_id'], data['pair_id'], data['amount'], data['description'])
        return jsonify({"status": "success", "expense_id": expense_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------ API: Share Expense ------------------
@app.route('/expense/share', methods=['POST'])
def share():
    data = request.json
    try:
        share_expense(data['expense_id'], data['user_id'], data['share_amount'])
        return jsonify({"status": "shared successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------ API: Submit Feedback ------------------


# ------------------ API: Add Settlement ------------------
@app.route('/settle', methods=['POST'])
def settle():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "❌ Unauthorized"}), 401

    data = request.json
    try:
        from_user = session['user_id']  # secure: use session, not frontend
        to_user = data['to_user_id']
        amount = data['amount']
        group_id = data.get('group_id')

        if not group_id:
            return jsonify({"status": "error", "message": "❌ Missing group ID"}), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Check if requester is the group creator
        cursor.execute("SELECT Created_by FROM Groups WHERE ID = %s", (group_id,))
        group = cursor.fetchone()

        if not group:
            return jsonify({"status": "error", "message": "❌ Group not found"}), 404

        if int(group['Created_by']) != int(from_user):
            return jsonify({
                "status": "error",
                "message": "❌ Permission denied. Only the group creator can add settlements."
            }), 403

        # ✅ Add the settlement
        settlement_id = add_settlement(
            from_user_id=from_user,
            to_user_id=to_user,
            amount=amount,
            status=data.get('status', 'pending'),
            group_id=group_id
        )

        conn.close()
        return jsonify({"status": "settlement recorded", "settlement_id": settlement_id})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500



# ------------------ API: Update Settlement Status ------------------
@app.route('/settle/<int:settlement_id>', methods=['PUT'])
def update_settle(settlement_id):
    data = request.json
    try:
        update_settlement_status(settlement_id, data['status'])
        return jsonify({"status": "settlement updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------ API: View Group ------------------
@app.route('/settlement/delete/<int:settlement_id>', methods=['POST'])
def delete_settlement(settlement_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if settlement exists and is owned by the logged-in user
        cursor.execute("SELECT * FROM settlements WHERE ID = %s", (settlement_id,))
        settlement = cursor.fetchone()

        if not settlement:
            return render_template("error.html", error_message="❌ Settlement not found.")

        if settlement['From_UserID'] != user_id:
            return render_template("error.html", error_message="❌ You are not allowed to delete this settlement.")

        # Delete settlement
        cursor.execute("DELETE FROM settlements WHERE ID = %s", (settlement_id,))
        conn.commit()

        return render_template("message.html", message="✅ Settlement deleted successfully.")
    
    except Exception as e:
        conn.rollback()
        return render_template("error.html", error_message=f"❌ Error deleting settlement: {str(e)}")
    
    finally:
        conn.close()
#---------------------------------------------------------------------------------
@app.route('/group/delete/<int:group_id>', methods=['POST'])
def delete_group(group_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if user is creator
        cursor.execute("SELECT Created_by FROM Groups WHERE ID = %s", (group_id,))
        group = cursor.fetchone()

        if not group or int(group[0]) != int(user_id):
            conn.close()
            return render_template("error.html", error_message="❌ You are not authorized to delete this group.")

        # Step 1: Delete expense shares
        cursor.execute("""
            DELETE es FROM expense_share es
            JOIN expenses e ON es.Expense_ID = e.ID
            WHERE e.Group_ID = %s
        """, (group_id,))

        # Step 2: Delete settlements
        cursor.execute("DELETE FROM settlements WHERE Group_ID = %s", (group_id,))

        # Step 3: Delete expenses
        cursor.execute("DELETE FROM expenses WHERE Group_ID = %s", (group_id,))

        # Step 4: Delete group members
        cursor.execute("DELETE FROM members WHERE Group_ID = %s", (group_id,))

        # Step 5: Delete group
        cursor.execute("DELETE FROM groups WHERE ID = %s", (group_id,))

        conn.commit()
        conn.close()
        return redirect('/groups')

    except Exception as e:
        conn.rollback()
        conn.close()
        return render_template("error.html", error_message=f"❌ Error deleting group: {str(e)}")
#------------------------------------------------------------------
@app.route('/feedback', methods=['GET', 'POST'])
def feed_back():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            # Check if already submitted
            cursor.execute("SELECT * FROM feedback WHERE From_UserID = %s", (user_id,))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                return render_template("feedback.html", feedback=existing)

            description = request.form['description']
            rating = int(request.form['rating'])

            cursor.execute("""
                INSERT INTO feedback (From_UserID, Description, Rating, Created_At)
                VALUES (%s, %s, %s, NOW())
            """, (user_id, description, rating))
            conn.commit()

            cursor.execute("SELECT * FROM feedback WHERE From_UserID = %s", (user_id,))
            feedback = cursor.fetchone()
            conn.close()
            return render_template("feedback.html", feedback=feedback)

        except Exception as e:
            conn.rollback()
            conn.close()
            return render_template("error.html", error_message="❌ " + str(e))

    # GET request
    cursor.execute("SELECT * FROM feedback WHERE From_UserID = %s", (user_id,))
    feedback = cursor.fetchone()
    conn.close()
    return render_template("feedback.html", feedback=feedback)





if __name__ == '__main__':
    print("Successfully done")
    app.run(debug=True)
