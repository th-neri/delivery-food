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

            choice = input("Enter your choice here: ").strip()

            if choice == "1":
                name = input("Write your name: ")
                email = input("Write your email: ")
                password = input("Write your password: ")

                if not name or not email or not password:
                    print("\nYou have to fill all the fields.\n")
                    continue

                result = database.add_user(connection, name, email, password)

                if result == "success":
                    print(f'\nYou account has been successfully created, {name}!')
                elif result == "already_exists":
                    print("\nYou used an email that is already in use. Please, try to use a different email or use it to sign in.")
            elif choice == "2":
                print("\n---SIGN IN---")
                email = input("Enter with your email: ")
                password = input("Enter with your password: ")

                user = database.login_user(connection, email, password)

                if user:
                    current_user = user[0]
                    name = user[1]
                    is_admin = user[3] == "admin"
                    print(f'\nYou are logged in {name}, welcome to our app!')
                else:
                    print("\nWrong email or password, try again or create your own account.")
            elif choice == "3":
                print("\nHave a good day!\n")
                break
            else:
                print("\nInvalid choice. Pick a valid number.")

        else:
            print("\n---OPTIONS---")
            print("1- Show menu")
            print("2- Buy here")
            print("3- Account settings")
            print("4- Log out")
            if is_admin:
                print("5- ADMIN OPTIONS")
            choice = input("Enter your choice here: ")

            if choice == "1":
                print("\n---MENU---")
            elif choice == "2":
                pass
            elif choice == "3":
                while True:
                    print("\n---SETTINGS---")
                    print("1- Change user name")
                    print("2- Change password")
                    print("3- Delete your account")
                    print("4- Go back to the main page")

                    choice = input("Enter your choice here: ")

                    if choice == "1":
                        name = input("Write your new name: ")
                        password = input("Enter with your password: ")

                        result = database.get_user_password(connection, current_user)

                        if result:
                            stored_password = result[0]

                            confirm = input("Are you sure you want to change the username of your account? (Y/N): ").strip().lower()
                            if confirm == "n":
                                print("\nCancelled.")    
                                continue      
                            elif confirm == "y":
                                if bcrypt.checkpw(password.encode(), stored_password.encode()):
                                    database.change_username(connection, current_user, name)   
                                    print(f'\nYou changed your username, {name}!')     
                                else:
                                    print("\nIncorrect password. Try again.")  
                            else:
                                print("\nInvalid input. You have to use (Y) for yes or (N) for no.")   
                        else:
                            print("\nUser not found.\n")
                    elif choice == "2":
                        new_password = input("Write your new password: ")
                        password = input("Write your current password: ")
                        
                        result = database.get_user_password(connection, current_user)

                        if result:
                            stored_password = result[0]

                            confirm = input("Are you sure you want to change the password of your account? (Y/N): ").strip().lower()

                            if confirm == "n":
                                print("\nCancelled")
                            elif confirm == "y":
                                if bcrypt.checkpw(password.encode(), stored_password.encode()):
                                    database.change_password(connection, current_user, new_password)
                                    print("\nYou changed your password!")
                                else:
                                    print("\nIncorrect password. Try again.")
                            else:
                                print("\nInvalid input. You have to use (Y) for yes or (N) for no.")
                        else:
                            print("\nUser not found.\n")
                    elif choice == "3":
                        password = input("Write your password: ")

                        result = database.get_user_password(connection, current_user)

                        if result:
                            stored_password = result[0]

                            confirm = input("Before we proceed with the process we need to know if you are sure you want to delete your account (Y/N): ").strip().lower()

                            if confirm == "n":
                                print("\nCancelled.")
                            elif confirm == "y":
                                if bcrypt.checkpw(password.encode(), stored_password.encode()):
                                    database.delete_account_by_id(connection, current_user)
                                    current_user = None
                                    print("\nYour account has been deleted successfully!")
                                    break
                                else:
                                    print("\nIncorrect password. Try again.")
                            else:
                                print("\nInvalid input. You have to use (Y) for yes or (N) for no.")
                        else:
                            print("\nUser not found.\n")
                    elif choice == "4":
                        break
            elif choice == "4":
                print("\nHave a good day!\n")
                current_user = None
                is_admin = False
                continue
            elif choice == "5":
                pass
            else:
                print("\nInvalid choice, Pick a valid number.")

menu()