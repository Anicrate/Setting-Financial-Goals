from goals_create import create_new_goal
from goals_edit import update_goal
from goals_view import view_goals
from deletion import delete_goal   

def create_financial_goal():
    while True:
        print("\n ..... Welcome to WealthWizard: Financial Goals Menu.....\n")
        print("1. Create a New Goal")
        print("2. Update Goal")
        print("3. View Goals")
        print("4. Delete Goal")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            create_new_goal()
        elif choice == "2":
            update_goal()
        elif choice == "3":
            view_goals()
        elif choice == "4":
            user_id = input("Enter your User ID to delete a goal: ").strip()
            delete_goal(user_id)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    create_financial_goal()
