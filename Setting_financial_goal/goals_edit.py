from datetime import datetime
from db import get_connection
import oracledb as cx_Oracle
import random

def update_goal():
    try:
        print("Welcome to the Goal Update System!")

        user_id = input("Enter your User ID: ").strip()
        conn = get_connection()
        if not conn:
            print("Could not connect to database.")
            return
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, email_id FROM users WHERE user_id = :1 AND is_loggedin = 1", (user_id,))
        user = cursor.fetchone()
        if not user:
            print("User is not logged in.")
            return
        print(f"\nLogged in as: {user[1]} (User ID: {user[0]})")
        cursor.execute("SELECT goal_id, goal_name, target_amount, current_amount, status FROM financial_goals WHERE user_id = :1", (user_id,))
        goals = cursor.fetchall()
        if goals:
            print("\nYour Goals:")
            for g in goals:
                print(f"ID: {g[0]}, Name: {g[1]}, Target: {g[2]}, Current: {g[3]}, Status: {g[4]}")
        else:
            print("\nNo goals found for this user.")
        cursor.close()
        conn.close()
        conn = get_connection()
        if not conn:
            return
        cursor = conn.cursor()

        goal_id = input("Enter the Goal ID you want to edit: ").strip()
        cursor.execute("SELECT * FROM financial_goals WHERE goal_id = :1 AND user_id = :2", (goal_id, user_id))
        goal_info = cursor.fetchone()
        if not goal_info:
            print("No goal found with that ID for this user.")
            cursor.close()
            conn.close()
            return
        print("\nGoal Details:")
        columns = [desc[0] for desc in cursor.description]
        for col, val in zip(columns, goal_info):
            print(f"{col}: {val}")

        print("\nWhat do you want to edit?")
        print("1. Target Amount")
        print("2. Add Amount to Goal")
        print("3. Priority")
        print("4. Status")
        print("5. Category Name")
        print("6. Goal Name")
        print("7. Start Date")
        print("8. Target Date")
        choice = input("Enter choice: ").strip()

        update_sql = None
        new_value = None

        if choice == "1":
            new_value = float(input("Enter new target amount: "))
            
            cursor.execute("SELECT current_amount FROM financial_goals WHERE goal_id = :1 AND user_id = :2", (goal_id, user_id))
            row = cursor.fetchone()
            if row is None:
                print("Goal not found.")
                return
            current_amount = row[0]
            
            if new_value < current_amount:
                print(f"Target Amount can't be less than current amount (₹{current_amount}).")
                return
            
            update_sql = "UPDATE financial_goals SET target_amount = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2 AND user_id = :3"
            cursor.execute(update_sql, (new_value, goal_id, user_id))
            conn.commit()

        elif choice == "2":

            add_amount = float(input("Enter amount to add to your goal: "))

            cursor.execute("SELECT current_amount, target_amount FROM financial_goals WHERE goal_id = :1 AND user_id = :2", (goal_id, user_id))
            amounts = cursor.fetchone()
            if not amounts:
                print("Goal not found.")
                return
            current_amount, target_amount = amounts

            cursor.execute("SELECT NVL(SUM(amount), 0) FROM transactions WHERE user_id = :1 AND TRIM(LOWER(transaction_type)) = 'credit'", (user_id,))
            total_credit = cursor.fetchone()[0]
            print("=====================================")
            print(f"Total Credit: ₹{total_credit}")
            cursor.execute("SELECT NVL(SUM(amount), 0) FROM transactions WHERE user_id = :1 AND TRIM(LOWER(transaction_type)) = 'debit'", (user_id,))
            total_debit = cursor.fetchone()[0]
            available_balance = total_credit - total_debit
            print(f"Available Balance: ₹{available_balance}")
            if add_amount > available_balance:
                print(f"Insufficient balance. Available: ₹{available_balance}")
                return
            new_current_amount = current_amount + add_amount
            if new_current_amount > target_amount:
                print(f"Cannot add. Final amount ₹{new_current_amount} exceeds target ₹{target_amount}.")
                return

            cursor.execute("UPDATE financial_goals SET current_amount = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2 AND user_id = :3", (new_current_amount, goal_id, user_id))

            transaction_id = f"FG{random.randint(100, 999)}"
            category_id = 8  # Savings & Investments

            cursor.execute("""
                INSERT INTO transactions (
                    transaction_id, user_id, amount, description, category_id,
                    timestamp, payment_mode, payment_to, transaction_type
                ) VALUES (
                    :transaction_id, :user_id, :amount, :description, :category_id,
                    CURRENT_TIMESTAMP, 'Self', 'Financial Goal', 'DEBIT'
                )
            """, {
                "transaction_id": transaction_id,
                "user_id": user_id,
                "amount": float(add_amount),  
                "description": f"Added to goal {goal_id}",
                "category_id": category_id
            })

            conn.commit()
            print(f"₹{add_amount} added to goal. New saved amount: ₹{new_current_amount}. Transaction recorded.")
            return
        elif choice == "3":
            new_value = input("Enter new priority (High/Medium/Low): ").capitalize()
            update_sql = "UPDATE financial_goals SET priority = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2 AND user_id = :3"
        elif choice == "4":
            new_value = input("Enter new status (In Progress/Completed/On Hold): ").capitalize()
            update_sql = "UPDATE financial_goals SET status = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2 AND user_id = :3"
        elif choice == "5":
            new_value = input("Enter new category name: ").strip()
            update_sql = "UPDATE financial_goals SET category_name = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2 AND user_id = :3"
        elif choice == "6":
            new_value = input("Enter new goal name: ").strip()
            update_sql = "UPDATE financial_goals SET goal_name = :1, updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2 AND user_id = :3"
        elif choice == "7":
            new_value = input("Enter new start date (YYYY-MM-DD): ").strip()
            try:
                start_date = datetime.strptime(new_value, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format.")
                return
            today = datetime.now().date()

            cursor.execute("SELECT target_date FROM financial_goals WHERE goal_id = :1 AND user_id = :2", (goal_id, user_id))
            result = cursor.fetchone()
            if result:
                target_date = result[0]
                if start_date >= target_date:
                    print("Start date cannot be greater than or equal to target date.")
                    return
                if start_date < today:
                    print("Start date cannot be less than today.")
                    return
            update_sql = "UPDATE financial_goals SET start_date = TO_DATE(:1, 'YYYY-MM-DD'), updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2 AND user_id = :3"
        elif choice == "8":
            new_value = input("Enter new target date (YYYY-MM-DD): ").strip()
            try:
                target_date = datetime.strptime(new_value, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format.")
                return
            today = datetime.now().date()

            cursor.execute("SELECT start_date FROM financial_goals WHERE goal_id = :1 AND user_id = :2", (goal_id, user_id))
            result = cursor.fetchone()
            if result:
                start_date = result[0]
                if target_date <= today:
                    print("Target date cannot be less than or equal to today.")
                    return
                if start_date and start_date >= target_date:
                    print("Start date cannot be greater than or equal to target date.")
                    return
            update_sql = "UPDATE financial_goals SET target_date = TO_DATE(:1, 'YYYY-MM-DD'), updated_at = CURRENT_TIMESTAMP WHERE goal_id = :2 AND user_id = :3"
        else:
            print("Invalid choice.")
            return

        if update_sql:
            cursor.execute(update_sql, (new_value, goal_id, user_id))
            if cursor.rowcount == 0:
                print("No goal found with that ID for this user.")
            else:
                conn.commit()
                print("Goal updated successfully.")
    except Exception as e:
        print("Error updating goal:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
