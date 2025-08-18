from db import get_connection
import oracledb as cx_Oracle

def delete_goal(user_id):
    try:
        # Establish DB connection
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch all financial goals for the user
        cursor.execute("""
            SELECT *
            FROM financial_goals
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """, {"user_id": user_id})
        goals = cursor.fetchall()

        if not goals:
            print("You don't have any financial goals.")
            return

        print("\nYour Financial Goals:")
        print(
            f"{'Goal ID':<8} {'Goal Name':<25} {'Category':<15} {'Target Amount':<15} {'Current Amount':<15} "
            f"{'Start Date':<12} {'Target Date':<12} {'Status':<12} {'Priority':<10} {'Created At':<15} {'Updated At':<15}"
        )
        print("-" * 160)

        for goal in goals:
            goal_id, user_id, category_name, goal_name, target_amount, current_amount, start_date, \
                target_date, status, priority, created_at, updated_at = goal

            start_date_str = start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else str(start_date)
            target_date_str = target_date.strftime('%Y-%m-%d') if hasattr(target_date, 'strftime') else str(target_date)
            created_at_str = created_at.strftime('%Y-%m-%d') if hasattr(created_at, 'strftime') else str(created_at)
            updated_at_str = updated_at.strftime('%Y-%m-%d') if hasattr(updated_at, 'strftime') else str(updated_at)

            print(
                f"{goal_id:<8} {goal_name:<25} {category_name:<15} {target_amount:<15} {current_amount:<15} "
                f"{start_date_str:<12} {target_date_str:<12} {status:<12} {priority:<10} {created_at_str:<15} {updated_at_str:<15}"
            )

        goal_id_to_delete = input("\nEnter the Goal ID you want to delete: ").strip()
        if not goal_id_to_delete.isdigit():
            print("Invalid Goal ID. Must be a number.")
            return

        goal_id_to_delete = int(goal_id_to_delete)

        # Ask for confirmation
        confirm = input(f"Are you sure you want to delete Goal ID {goal_id_to_delete}? Type 'CONFIRM' to proceed: ").strip().upper()
        if confirm != 'CONFIRM':
            print("Deletion cancelled.")
            return

        # Prepare OUT parameter
        result_msg = cursor.var(cx_Oracle.STRING)

        # Call the stored procedure
        cursor.callproc("delete_goal", [
            user_id,
            goal_id_to_delete,
            confirm,
            result_msg
        ])

        # Show result
        print(result_msg.getvalue())

        conn.commit()

    except Exception as e:
        print("Error during deletion:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()