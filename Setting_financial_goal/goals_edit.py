from db import get_connection

def edit_goal():
    try:
        goal_id = input("Enter the Goal ID you want to edit: ").strip()
        print("\nWhat do you want to edit?")
        print("1. Target Amount")
        print("2. Current Amount")
        print("3. Priority")
        print("4. Status")
        choice = input("Enter choice: ").strip()

        update_sql = None
        new_value = None

        if choice == "1":
            new_value = float(input("Enter new target amount: "))
            update_sql = "UPDATE financial_goals SET target_amount = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2"
        elif choice == "2":
            new_value = float(input("Enter new current amount: "))
            update_sql = "UPDATE financial_goals SET current_amount = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2"
        elif choice == "3":
            new_value = input("Enter new priority (High/Medium/Low): ").capitalize()
            update_sql = "UPDATE financial_goals SET priority = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2"
        elif choice == "4":
            new_value = input("Enter new status (In Progress/Completed/On Hold): ").capitalize()
            update_sql = "UPDATE financial_goals SET status = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2"
        else:
            print("❌ Invalid choice.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(update_sql, (new_value, goal_id))
        if cursor.rowcount == 0:
            print("❌ No goal found with that ID.")
        else:
            conn.commit()
            print("✅ Goal updated successfully.")

    except Exception as e:
        print("❌ Error updating goal:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
