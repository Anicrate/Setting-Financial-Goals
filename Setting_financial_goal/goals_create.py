from datetime import datetime
from db import get_connection
import oracledb as cx_Oracle

def create_new_goal():
    try:
        user_id = input("Enter your User ID: ").strip()
        category_name = input("Enter the category of your goal: ").strip()
        goal_name = input("Enter the name of your goal: ").strip()
        target_amount = float(input("Enter the target amount (positive number): "))
        current_amount = float(input("Enter the current saved amount: "))
        priority = input("Enter priority (High/Medium/Low): ").strip().capitalize()
        status = "In Progress"
        start_date_str = datetime.now().strftime("%Y-%m-%d")
        target_date_str = input("Enter the target date (YYYY-MM-DD): ").strip()

        if not goal_name or target_amount <= 0:
            print("❌ Invalid amount or empty goal name.")
            return

        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD.")
            return

        if target_date < datetime.now().date():
            print("❌ Target date cannot be in the past.")
            return

        conn = get_connection()
        cursor = conn.cursor()

        insert_sql = """
            INSERT INTO financial_goals
            (user_id, category_name, goal_name, target_amount, current_amount, 
             start_date, target_date, status, priority)
            VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), 
                    TO_DATE(:7, 'YYYY-MM-DD'), :8, :9)
        """
        values = (
            user_id, category_name, goal_name, target_amount, current_amount,
            start_date_str, target_date_str, status, priority
        )

        cursor.execute(insert_sql, values)
        conn.commit()

        print(f"\n✅ Financial goal created successfully for User {user_id}.")
        print(f"   Goal '{goal_name}' of ₹{target_amount} is set for {target_date_str}.\n")

    except cx_Oracle.IntegrityError as e:
        if "ORA-02291" in str(e):
            print("❌ You are not registered. Please register before creating a goal.")
        else:
            print("❌ Database Integrity Error:", e)
    except Exception as e:
        print("❌ Unexpected Error:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
