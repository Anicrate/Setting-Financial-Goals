import matplotlib.pyplot as plt
import oracledb
from db import get_connection


def view_goals():

    conn = None
    cursor = None

    try:
        user_id = input("Enter your User ID to view your goals: ").strip()


        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT is_loggedIn
            FROM users
            WHERE user_id = :1
        """, (user_id,))
        login_status = cursor.fetchone()

        if not login_status:
            print("User ID not found.")
            return
        if login_status[0] != 1:
            print("You must log in first to view your goals.")
            return

        cursor.execute("""
            SELECT goal_id, category_name, goal_name, target_amount, NVL(current_amount, 0),
                   TO_CHAR(start_date, 'YYYY-MM-DD'),
                   TO_CHAR(target_date, 'YYYY-MM-DD'),
                   status, priority
            FROM financial_goals
            WHERE user_id = :1
            ORDER BY start_date
        """, (user_id,))
        goals = cursor.fetchall()

        if not goals:
            print("No goals found for this user.")
            return


        print("\n" + "-" * 95)
        print(f"{'Goal ID':<8} {'Category':<15} {'Goal Name':<20} {'Target Amt':<12} "
              f"{'Current Amt':<12} {'Start Date':<12} {'Target Date':<12} {'Status':<12} {'Priority':<10}")
        print("-" * 95)
        for goal in goals:
            print(f"{goal[0]:<8} {goal[1]:<15} {goal[2]:<20} {goal[3]:<12} {goal[4]:<12} "
                  f"{goal[5]:<12} {goal[6]:<12} {goal[7]:<12} {goal[8]:<10}")
        print("-" * 95)


        try:
            selected_goal_id = int(input("\nEnter the Goal ID to view as pie chart (or 0 to skip): ").strip())
            if selected_goal_id != 0:
                cursor.execute("""
                    SELECT goal_name, target_amount, NVL(current_amount, 0)
                    FROM financial_goals
                    WHERE goal_id = :1 AND user_id = :2
                """, (selected_goal_id, user_id))
                goal_data = cursor.fetchone()

                if goal_data:
                    goal_name, target_amount, current_amount = goal_data
                    remaining_amount = max(target_amount - current_amount, 0)


                    labels = ['Completed', 'Remaining']
                    sizes = [current_amount, remaining_amount]
                    colors = ['#4CAF50', '#FF9800']
                    explode = (0.1, 0)

                    plt.figure(figsize=(5, 5))
                    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                            startangle=140, explode=explode)
                    plt.title(f"Progress for '{goal_name}'")
                    plt.axis('equal')
                    plt.show()
                else:
                    print("Invalid Goal ID or goal not found.")
        except ValueError:
            print("Invalid input for Goal ID.")

    except oracledb.DatabaseError as db_err:
        error_obj, = db_err.args
        print(f"Database error: {error_obj.message}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
