import matplotlib.pyplot as plt
from db import get_connection

def view_goals():
    try:
        user_id = input("Enter your User ID to view your goals: ").strip()

        conn = get_connection()
        cursor = conn.cursor()

        # Step 1: Check login status
        cursor.execute("""
            SELECT is_loggedIn
            FROM users
            WHERE user_id = :1
        """, (user_id,))
        login_status = cursor.fetchone()

        if not login_status:
            print("❌ User ID not found.")
            return
        elif login_status[0] != 1:
            print("⚠️ You must log in first to view your goals.")
            return

        # Step 2: Retrieve financial goals
        cursor.execute("""
            SELECT goal_id, category_name, goal_name, target_amount, NVL(current_amount, 0),
                   TO_CHAR(start_date, 'YYYY-MM-DD'),
                   TO_CHAR(target_date, 'YYYY-MM-DD'),
                   status, priority
            FROM financial_goals
            WHERE user_id = :1
            ORDER BY start_date
        """, (user_id,))

        rows = cursor.fetchall()

        # Step 3: Handle no goals
        if not rows:
            print("⚠️ No goals found for this user.")
            return

        # Step 4: Display table
        print("\n" + "-" * 95)
        print(f"{'Goal ID':<8} {'Category':<15} {'Goal Name':<20} {'Target Amt':<12} {'Current Amt':<12} {'Start Date':<12} {'Target Date':<12} {'Status':<12} {'Priority':<10}")
        print("-" * 95)
        for row in rows:
            print(f"{row[0]:<8} {row[1]:<15} {row[2]:<20} {row[3]:<12} {row[4]:<12} {row[5]:<12} {row[6]:<12} {row[7]:<12} {row[8]:<10}")
        print("-" * 95)

        # Step 5: Ask for pie chart view
        try:
            goal_id = int(input("\nEnter the Goal ID to view as pie chart (or 0 to skip): ").strip())
            if goal_id != 0:
                cursor.execute("""
                    SELECT goal_name, target_amount, NVL(current_amount, 0)
                    FROM financial_goals
                    WHERE goal_id = :1 AND user_id = :2
                """, (goal_id, user_id))
                goal_data = cursor.fetchone()

                if goal_data:
                    goal_name, target_amount, current_amount = goal_data
                    remaining_amount = max(target_amount - current_amount, 0)

                    # Create pie chart
                    labels = ['Completed', 'Remaining']
                    sizes = [current_amount, remaining_amount]
                    colors = ['#4CAF50', '#FF9800']
                    explode = (0.1, 0)  # highlight completed part

                    plt.figure(figsize=(5, 5))
                    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                            startangle=140, explode=explode)
                    plt.title(f"Progress for '{goal_name}'")
                    plt.axis('equal')
                    plt.show()
                else:
                    print("⚠️ Invalid Goal ID or goal not found.")
        except ValueError:
            print("⚠️ Invalid input.")

    except Exception as e:
        print("❌ Error fetching goals:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
