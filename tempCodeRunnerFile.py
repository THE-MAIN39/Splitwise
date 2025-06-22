from Models.user import register_user
from Models.group import create_group, add_member_to_group
from Models.expense import add_expense, share_expense
from Models.feedback import add_feedback
from Models.settlement import add_settlement, update_settlement_status

print("=== Registering Users ===")
user1_id = register_user("Umer", "Mehar", "setdrgwtle.com", "pass1")
user2_id = register_user("Isha", "Ikhlaq", "@sedfwdttle.com", "pass2")
print(f"Users created: {user1_id}, {user2_id}")

print("\n=== Creating Group ===")
group_id = create_group("Beach Trip", created_by=user1_id)
print(f"Group created with ID: {group_id}")

print("\n=== Adding Members to Group ===")
add_member_to_group(group_id, user1_id)
add_member_to_group(group_id, user2_id)
print("Members added successfully")

print("\n=== Adding Expense ===")
expense_id = add_expense(group_id, user1_id, 3000, "Resort Booking")
print(f"Expense added with ID: {expense_id}")

print("\n=== Sharing Expense ===")
share_expense(expense_id, user1_id, 1500)
share_expense(expense_id, user2_id, 1500)
print("Expense shared between users")

print("\n=== Adding Feedback ===")
add_feedback(user2_id, "Amazing trip!", 5)
print("Feedback submitted")

print("\n=== Recording Settlement ===")
settlement_id = add_settlement(from_user_id=user2_id, to_user_id=user1_id, amount=1500, status="pending")
print(f"Settlement recorded with ID: {settlement_id}")

print("\n=== Updating Settlement Status ===")
update_settlement_status(settlement_id, "completed")
print("Settlement marked as completed")

from Models.group import get_group_info

if __name__ == "__main__":
    print("=== Checking Group Info ===")
    try:
        group_id_to_check = 8  # ✅ Replace with the actual group ID you want to test
        group_info = get_group_info(group_id_to_check)
        print("Group Info:")
        print(group_info)
    except Exception as e:
        print("Error:", e)
