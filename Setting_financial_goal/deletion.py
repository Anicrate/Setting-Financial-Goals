from db import get_connection
from datetime import datetime
import random

def delete_goal(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT goal_id, goal_name, current_amount
            FROM financial_goals
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """, {"user_id": user_id})

        goals = cursor.fetchall()

        if not goals:
            print("No financial goals found for your user ID.")
            return

        print("\nYour Financial Goals:")
        print(f"{'Goal ID':<8} {'Goal Name':<30} {'Current Amount':<15}")
        print("-" * 50)

        for goal_id, goal_name, current_amount in goals:
            print(f"{goal_id:<8} {goal_name:<30} {current_amount:<15}")

        goal_id_to_delete = input("\nEnter the Goal ID you want to delete: ").strip()

        if not goal_id_to_delete.isdigit():
            print("Invalid Goal ID. Must be a number.")
            return
        
        goal_id_to_delete = int(goal_id_to_delete)

        cursor.execute("""
            SELECT goal_name 
            FROM financial_goals
            WHERE user_id = :user_id AND goal_id = :goal_id
        """, {"user_id": user_id, "goal_id": goal_id_to_delete})

        row = cursor.fetchone()
        if not row:
            print(f"Goal ID {goal_id_to_delete} not found for your user ID.")
            return

        goal_name = row[0]

        confirm = input(f"Are you sure you want to delete '{goal_name}' (ID: {goal_id_to_delete})? (Enter 'CONFIRM'): ").strip().upper()
        if confirm != 'CONFIRM':
            print("Deletion cancelled.")
            return

        cursor.execute("""
            DELETE FROM financial_goals
            WHERE user_id = :user_id AND goal_id = :goal_id
        """, {"user_id": user_id, "goal_id": goal_id_to_delete})

        # transaction_id = f"FG{datetime.now().strftime('%H%M%S')}"
        transaction_id = f"FG{random.randint(100, 999)}"
        category_id = 8 # Savings $ Investments
        cursor.execute("""
            INSERT INTO transactions (
                transaction_id, user_id, amount, description, category_id,
                timestamp, payment_mode, payment_to, transaction_type
            ) VALUES (
                :transaction_id, :user_id, :amount, :description, :category_id,
                CURRENT_TIMESTAMP, 'Self', 'Self', 'CREDIT'
            )
        """, {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "category_id": category_id,
            "amount": float(current_amount),
            "description": f"Credited from FG"
        })

        conn.commit()
        print(f"Goal '{goal_name}' (ID: {goal_id_to_delete}) has been deleted successfully.")
        print(f"Credited amount {current_amount} to account.")

    except Exception as e:
        print("Error during deletion:", e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()