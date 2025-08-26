from datetime import datetime
from db import get_connection
import oracledb as cx_Oracle
import random

def create_new_goal():
    conn = None
    cursor = None
    try:                                # Establish database connection and cursor
        conn = get_connection()
        cursor = conn.cursor()

# Loop to get valid logged-in user_id
        while True:
            user_id = input("Enter your User ID: ").strip()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, email_id FROM users WHERE user_id = :1 AND is_loggedin = 1", (user_id,))
            user = cursor.fetchone()
            if not user:
                print("User is not logged in.")
                return

            print(f"\nLogged in as: {user[1]} (User ID: {user[0]})")
            
# Verify if user exists in the users table
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = :1", (user_id,))
            user_exists = cursor.fetchone()[0]

            if user_exists == 0:
                print("You are not registered. Please register before creating a goal.")
                return
            else:
                break

# Input category for the financial goal
        category_name = input("Enter the category of your goal (e.g., Savings, Investment): ").strip()

        # Goal Name
        while True:
            goal_name = input("Enter the name of your goal: ").strip()
            if goal_name:
                break
            print("Goal name cannot be empty.")


        while True:
            try:
                target_amount = float(input("Enter the target amount (positive number): "))
                if target_amount > 0:
                    break
                else:
                    print("Target amount must be greater than zero.")
            except ValueError:
                print("Invalid input. Target amount must be a number.")


        while True:
            try:
                current_amount = float(input("Enter the current saved amount: "))
                if current_amount < 0:
                    print("Current amount cannot be negative.")
                elif current_amount > target_amount:
                    print(f"Current amount cannot exceed target amount of ₹{target_amount}.")
                elif current_amount == target_amount:
                    print(f"Current amount cannot be equal to target amount of ₹{target_amount}.")
                else:
                    break
            except ValueError:
                print("Invalid input. Current amount must be a number.")

# Calculate total credited amount for the user
        cursor.execute("""
            SELECT NVL(SUM(amount), 0) 
            FROM transactions 
            WHERE user_id = :1 
              AND TRIM(LOWER(transaction_type)) = 'credit'
        """, (user_id,))
        total_credit = cursor.fetchone()[0]

# Calculate total debited amount for the user
        cursor.execute("""
            SELECT NVL(SUM(amount), 0) 
            FROM transactions 
            WHERE user_id = :1 
              AND TRIM(LOWER(transaction_type)) = 'debit'
        """, (user_id,))
        total_debit = cursor.fetchone()[0]

 # Calculate available balance (credit - debit)
        available_balance = total_credit - total_debit
        print(f"Available Balance: ₹{available_balance}")

 # Check if current amount exceeds available balance
        if current_amount > available_balance:
            print(f"Insufficient balance. Available: ₹{available_balance}")
            return


        while True:
            priority = input("Enter priority (High/Medium/Low): ").strip().capitalize()
            if priority in ["High", "Medium", "Low"]:
                break
            print("Invalid priority. Choose from High, Medium, or Low.")


        status = "In Progress"
        start_date_str = datetime.now().strftime("%Y-%m-%d")

# Input and validate target date (cannot be in the past)
        while True:
            target_date_str = input("Enter the target date (YYYY-MM-DD): ").strip()
            try:
                target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                if target_date >= datetime.now().date():
                    break
                else:
                    print("Target date cannot be in the past.")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")

        # --- Call stored procedure to insert goal ---
        cursor.callproc("create_goal", [
            user_id,
            category_name,
            goal_name,
            target_amount,
            current_amount,
            start_date_str,
            target_date_str,
            status,
            priority
        ])

# Insert new financial goal into the database
        # insert_goal_sql = """
        #     INSERT INTO financial_goals
        #     (user_id, category_name, goal_name, target_amount, current_amount, 
        #     start_date, target_date, status, priority)
        #     VALUES (:1, :2, :3, :4, :5, 
        #     TO_DATE(:6, 'YYYY-MM-DD'), TO_DATE(:7, 'YYYY-MM-DD'), :8, :9)
        # """
        # cursor.execute(insert_goal_sql, (
        #     user_id, category_name, goal_name, target_amount, current_amount,
        #     start_date_str, target_date_str, status, priority
        # ))


        if current_amount > 0:
            transaction_id = f"FG{random.randint(100, 999)}"
            category_id = 8  # Savings & Investments

            cursor.execute("""
                INSERT INTO transactions (
                    transaction_id, user_id, amount, description, category_id,
                    timestamp, payment_mode, payment_to, transaction_type
                ) VALUES (
                    :transaction_id, :user_id, :amount, :description, :category_id,
                    CURRENT_TIMESTAMP, :payment_mode, :payment_to, :transaction_type
                )
            """, {
                "transaction_id": transaction_id,
                "user_id": user_id,
                "amount": current_amount,
                "description": "Debit to FG",
                "category_id": category_id,
                "payment_mode": "Bank",
                "payment_to": "Self",
                "transaction_type": "Debit"
            })

# Insert new financial goal into the database
        conn.commit()

        print(f"\n Financial goal created successfully for User {user_id}.")
        print(f"   Goal '{goal_name}' of ₹{target_amount} is set for {target_date_str}.")
        if current_amount > 0:
            print(f"   Transaction recorded: {transaction_id} - Debit ₹{current_amount} to Self.\n")

# Handle database integrity errors (like foreign key violations)
    except cx_Oracle.IntegrityError as e:
        if "ORA-02291" in str(e):
            print("You are not registered. Please register before creating a goal.")
        else:
            print("Database Integrity Error:", e)
# Handle any unexpected exceptions
    except Exception as e:
        print("Unexpected Error:", e)
    finally:
        # Close cursor and connection if they were opened
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


