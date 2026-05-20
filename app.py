import database
import bcrypt

def menu():
    connection = database.connect()
    database.create_tables(connection)

    current_user = None
    is_admin = False

    while True:
        if current_user is None:
            print("\n---OPTIONS---")
            print("1- Create your account")
            print("2- Sign in")
            print("3- Exit")

            choice = input("Enter with your choice here: ").strip()

            if choice == "1":
                name = input("Write your name: ")
                email = input("Write your email: ")
                password = input("Write your password: ")

                if not name or not email or not password:
                    print("\nYou have to fill all the fields.\n")

                result = database.add_user(connection, name, email, password)

                if result == "success":
                    print(f'\nYou account has been successfully created, {name}!')
                elif result == "already_exists":
                    print("\nYou used an email that is already in use. Please, try to use a different email or use it to sign in.")
            elif choice == "2":
                pass
            elif choice == "3":
                print("\nHave a good day!\n")
                break
            else:
                print("Invalid choice. Pick a valid number.")
menu()