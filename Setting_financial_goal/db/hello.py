import oracledb as cx_Oracle
from datetime import datetime

# ---------------- Connection ----------------
def get_connection():
    conn = cx_Oracle.connect(
        user="system",
        password="dbms",
        dsn="localhost/XE"
    )
    return conn

# ---------------- Create Goal ----------------
def create_new_goal():
    try:
        user_id = input("Enter your User ID: ").strip()
        category_name = input("Enter the category of your goal: ").strip()
        goal_name = input("Enter the name of your goal: ").strip()
        target_amount = float(input("Enter the target amount (positive number): "))
        current_amount = float(input("Enter the current saved amount: "))
        priority = input("Enter priority (High/Medium/Low): ").strip().capitalize()
        status = "In Progress"  # Default for new goals
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

# ---------------- Update Goal ----------------
def update_goal():
    try:
        goal_id = input("Enter the Goal ID you want to update: ").strip()
        print("\nWhat do you want to update?")
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

# ---------------- View Goals ----------------
def view_goals():
    try:
        user_id = input("Enter your User ID to view your goals: ").strip()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT goal_id, category_name, goal_name, target_amount, current_amount,
                   TO_CHAR(start_date, 'YYYY-MM-DD'),
                   TO_CHAR(target_date, 'YYYY-MM-DD'),
                   status, priority
            FROM financial_goals
            WHERE user_id = :1
            ORDER BY start_date
        """, (user_id,))

        rows = cursor.fetchall()

        if not rows:
            print("⚠️ No goals found for this user.")
            return

        # Print in table format
        print("\n" + "-" * 95)
        print(f"{'Goal ID':<8} {'Category':<15} {'Goal Name':<20} {'Target Amt':<12} {'Current Amt':<12} {'Start Date':<12} {'Target Date':<12} {'Status':<12} {'Priority':<10}")
        print("-" * 95)
        for row in rows:
            print(f"{row[0]:<8} {row[1]:<15} {row[2]:<20} {row[3]:<12} {row[4]:<12} {row[5]:<12} {row[6]:<12} {row[7]:<12} {row[8]:<10}")
        print("-" * 95)

    except Exception as e:
        print("❌ Error fetching goals:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ---------------- Main Menu ----------------
def create_financial_goal():
    while True:
        print("\n |||||  Welcome to WealthWizard: Financial Goals Menu    ||||| \n")
        print("1. Create a New Goal")
        print("2. Update Goal")
        print("3. View Goals")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            create_new_goal()
        elif choice == "2":
            update_goal()
        elif choice == "3":
            view_goals()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1, 2, 3, or 4.")

# ---------------- Run ----------------
if __name__ == "__main__":
    create_financial_goal()
