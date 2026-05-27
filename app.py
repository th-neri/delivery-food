import database
import bcrypt

def menu():
    connection = database.connect()
    database.create_tables(connection)
    current_user = None
    is_admin = False

    database.make_admin(connection, "neri123@gmail.com")

    while True:
        if current_user is None:
            print("\n     OPTIONS   ")
            print("-----------------")
            print("1- Create your account")
            print("2- Sign in")
            print("3- Exit")

            choice = input("Enter your choice here: ").strip()

            if choice == "1":
                print("\n---CREATE YOUR ACCOUNT---")
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
            print("\n     OPTIONS   ")
            print("-----------------")
            print("1- Show menu")
            print("2- Buy here")
            print("3- Account settings")
            print("4- Log out")
            if is_admin:
                print("5- ADMIN OPTIONS")
            choice = input("Enter your choice here: ")

            if choice == "1":
                print("\n   MENU   ")

                restaurants = database.get_menu(connection)

                if not restaurants:
                    print("\nNo restaurants available.")
                    continue

                for restaurant in restaurants:
                    restaurant_id = restaurant[0]
                    restaurant_name = restaurant[1]

                    print(f'{restaurant_name}')
                    print("-" * len(restaurant_name))

                    dishes = database.get_dish_by_restaurant(connection, restaurant_id)

                    if not dishes:
                        print("\nNo dishes available.")

                    for dish in dishes:
                        dish_id = dish[0]
                        name = dish[1]
                        type = dish[2]
                        price = dish[3]

                        print(f'ID NUMBER: {dish_id} | NAME: {name} | TYPE: {type} | ${price}')

            elif choice == "2":
                while True:
                    print("\n   BUY HERE   ")
                    print("------------------")
                    print("1- Add item(s) to the cart")
                    print("2- View your cart")
                    print("3- Remove item from the cart")
                    print("4- Checkout")
                    print("5- Go back to the main page")

                    choice = input("Enter your choice here: ").strip()

                    if choice == "1":
                        print("\n---MENU---")

                        restaurants = database.get_menu(connection)

                        if not restaurants:
                            print("\nNo restaurants available.")
                            continue

                        for restaurant in restaurants:
                            restaurant_id = restaurant[0]
                            restaurant_name = restaurant[1]

                            print(f'{restaurant_name}')
                            print("-" * len(restaurant_name))

                        dishes = database.get_dish_by_restaurant(connection, restaurant_id)

                        if not dishes:
                            print("\nNo dishes available.")
                        
                        for dish in dishes:
                            dish_id = dish[0]
                            name = dish[1]
                            type = dish[2]
                            price = dish[3]

                            print(f'ID NUMBER: {dish_id} | NAME: {name} | TYPE: {type} | ${price}')

                        try:
                            dish_id = int(input("\nEnter the ID number of your choice: "))
                            quantity = int(input("Enter the quantity: "))

                            if not dish_id:
                                print("\nID not found.")
                        except ValueError:
                            print("\nInvalid input.")
                            continue

                        database.add_to_the_cart(connection, current_user, dish_id, quantity)
                        print(f'{dish_name} added to the cart!')
            elif choice == "3":
                while True:
                    print("\n     SETTINGS   ")
                    print("------------------")
                    print("1- Change username")
                    print("2- Change password")
                    print("3- Delete your account")
                    print("4- Go back to the main page")

                    choice = input("Enter your choice here: ")

                    if choice == "1":
                        print("\n---Change your username---")

                        password = input("Enter with your password: ")

                        result = database.get_user_password(connection, current_user)

                        if result:
                            stored_password = result[0]
                            
                            if bcrypt.checkpw(password.encode(), stored_password.encode()):
                                new_name = input("Write your new username: ")

                                confirm = input("Are you sure you want to change your username? (Y/N): ").strip().lower()

                                if confirm == "n":
                                    print("\nCancelled.")
                                elif confirm == "y":
                                    database.change_username(connection, current_user, new_name)
                                    print(f'\nYou changed your username, {new_name}!')
                                else:
                                    print("\nInvalid input. You have to use (Y) for yes or (N) for no.")
                            else:
                                print("\nWrong password. Try again.")                     
                        else:
                            print("\nUser not found.")

                    elif choice == "2":
                        print("\n---Change your password---")
                        password = input("Write your current password: ")
                        
                        result = database.get_user_password(connection, current_user)

                        if result:
                            stored_password = result[0]

                            if bcrypt.checkpw(password.encode(), stored_password.encode()):
                                new_password = input("Write your new password: ")

                                confirm = input("Are you sure you want to change the password of your account? (Y/N): ").strip().lower()

                                if confirm == "n":
                                    print("\nCancelled.")
                                elif confirm == "y":
                                    database.change_password(connection, current_user, new_password)
                                    print("\nYou changed your password!")
                                else:
                                    print("\nInvalid input. You have to use (Y) for yes or (N) for no.")
                            else:
                                print("\nWrong password. Try again.")
                        else:
                            print("\nUser not found.")

                    elif choice == "3":
                        print("\n---Delete your account---")

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
                while True:
                    print("\n   ADM OPTIONS   ")
                    print("-----------------")
                    print("1- Add Restaurant")
                    print("2- Remove restaurant from the app")
                    print("3- Add a dish")
                    print("4- Remove dish from the app")
                    print("5- Statistics")
                    print("6- Go back to the main page")

                    choice = input("Enter your choice here: ")  

                    if choice == "1":
                        print("\n---Add restaurant---")

                        restaurant_name = input("Write the restaurant name: ")               
                        location = input("Restaurant location: ")   

                        if not restaurant_name or not location:
                            print("\nYou have to fill all the fields.\n")  
                            continue

                        database.add_restaurant(connection, restaurant_name, location)   
                        print("\nRestaurant added succesfully!")  

                    elif choice == "2": 
                        print("\n---Remove restaurant---")

                        restaurant_id = input("Enter the restaurant ID number to remove it: ").strip()

                        if not database.restaurant_exists(connection, restaurant_id):
                            print("\nID number does not exist.")
                            continue

                        confirm = input("Are you sure you want to remove the restaurant? (Y/N): ").strip().lower()

                        if confirm == "n":
                            print("\nCancelled.")
                            continue
                        elif confirm == "y":
                            database.delete_restaurant(connection, restaurant_id)
                            print("\nRestaurant removed successfully!")
                        else:
                            print("\nInvalid input. You have to use (Y) for yes or (N) for no.")   

                    elif choice == "3":
                        print("\n---Add a new dish---")

                        restaurants = database.get_menu(connection)

                        print("\nRestaurants IDs")
                        for restaurant in restaurants:
                            print(f'ID: {restaurant[0]} | Restaurant name: {restaurant[1]}\n')

                        try:
                            restaurant_id = int(input("Write the ID number of the restaurant: "))
                            dish_name = input("Write the item name: ")
                            type = input("Write the type: ")
                            price = float(input("Write the price: "))
                        except:
                            print("\nInvalid input(s).")
                            continue

                        if not restaurant_id or not dish_name or not type or not price:
                            print("\nYou have to fill all the fields.\n")
                            continue        

                        if database.restaurant_exists(connection, restaurant_id):
                            database.add_dish(connection, dish_name, restaurant_id, type, price)    
                            print(f'\n{dish_name} added!')    
                        else:
                            print("\nRestaurant ID does not exist. Use a valid ID.")

                    elif choice == "4":
                        print("\n---Remove dish---")

                        dish_id = input("Enter the dish ID number to remove it: ").strip()

                        if not database.dish_exists(connection, dish_id):
                            print("\nID number does not exist.")
                            continue

                        confirm = input("Are you sure you want to remove it? (Y/N): ").strip().lower()

                        if confirm == "n":
                            print("\nCancelled.")
                            continue
                        elif confirm == "y":
                            database.delete_dish(connection, dish_id)
                            print("\nDish removed successfully!")
                        else:
                            print("\nInvalid input. You have to use (Y) for yes or (N) for no.")    
                    elif choice == "5":
                        pass
                    elif choice == "6":   
                        break
            else:
                print("\nInvalid choice, Pick a valid number.")

menu()