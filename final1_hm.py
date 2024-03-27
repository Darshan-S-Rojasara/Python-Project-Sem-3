import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import re
from fpdf import FPDF

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Restaurant:
    def __init__(self):
        self.menu = {}

    def load_menu(self, filename="menu.txt"):
        try:
            with open(filename, "r") as file:
                for line in file:
                    name, price = line.strip().split("|")
                    self.menu[name] = float(price)
        except FileNotFoundError:
            print("Menu file not found. Starting with an empty menu.")

    def view_menu(self):
        print("--------------")
        print("      Menu")
        print("--------------")
        print("Item\t\t\tPrice")
        print("--------------")
        for name, price in self.menu.items():
            print(f"{name.ljust(20)}\t₹{price}")
        print("--------------")

    def save_menu(self, filename="menu.txt"):
        with open(filename, "w") as file:
            for name, price in self.menu.items():
                file.write(f"{name}|{price}\n")

    def add_menu_item(self, item):
        self.menu[item.name] = item.price
        self.save_menu()

    def remove_menu_item(self, name):
        if not self.menu:
            print("The menu is already empty.")
            return
        
        if name in self.menu:
            del self.menu[name]
            self.save_menu()
            print(f"{name} has been removed from the menu.")
        else:
            print(f"{name} is not in the menu.")

class Order:
    def __init__(self):
        self.items = []
        self.days_stay = 0  # Number of days stayed
        self.daily_rate = 100  # Daily rate for stay

    def add_item(self, item, quantity=1):
        self.items.append((item, quantity))

    def calculate_total(self, menu):
        total = 0
        for item, quantity in self.items:  # Access item name and quantity from tuple
            if item in menu:  # Check if item name is in the menu
                total += menu[item] * quantity  # Calculate total price for the item
            else:
                print(f"{item} is not available in the menu.")
        return total

    def calculate_stay_charges(self):
        return self.days_stay * self.daily_rate

    def make_payment(self, total, customer_email, customer_username, hotel_name, menu):
        subject_bill = f'{hotel_name} - Your Bill'
        body_bill = f'''
        Dear {customer_username},

        Thank you for dining at {hotel_name}. Below is the summary of your order:

--------------------------------------------------------------------------------------------------------------
        
                                               Order Summary:
        
--------------------------------------------------------------------------------------------------------------      
        Item                   Quantity                   Price
--------------------------------------------------------------------------------------------------------------
        '''
        for item, quantity in self.items:  # Use tuple unpacking to get item and quantity
         body_bill += f"{item.ljust(20)}         *         {quantity}                   ₹{menu[item]}\n"  # Use menu dictionary to get item price
        
        body_bill += f'''
_____________________________________________________________________________________________________
        Total Amount: ₹{total}
_____________________________________________________________________________________________________

        Thanks for visiting {hotel_name}. We look forward to serving you again soon!

        Best regards,
        {hotel_name}
        '''
        
        pdf_filename = generate_pdf_bill(customer_username, hotel_name, body_bill)
        send_email_with_attachment(customer_email, subject_bill, body_bill, pdf_filename)
        print("Bill sent successfully.")

def send_email_with_attachment(receiver_email, subject, body, attachment_filename):
    sender_email = 'mywork.rds111.2030@gmail.com'  # Update with your email address
    sender_password = 'loulqncslbreljxh'  # Update with your email password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    with open(attachment_filename, "rb") as attachment:
        part = MIMEApplication(attachment.read(), Name=attachment_filename)

    part['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
    message.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def generate_pdf_bill(customer_username, hotel_name, body_bill):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_left_margin(10)  # Set left margin
    pdf.set_right_margin(10)  # Set right margin
    pdf.add_font('DejaVuSans', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVuSans', 'I', 'DejaVuSerif-Italic.ttf', uni=True)
    pdf.add_font('DejaVuSans-Bold', '', 'DejaVuSans-Bold.ttf', uni=True)
    
    # Set font styles
    pdf.set_font('DejaVuSans', '', 12)
    pdf.set_font('DejaVuSans-Bold', '', 16)
    
    # Add hotel name as title
    pdf.cell(0, 10, f'{hotel_name} - Your Bill', ln=True, align='C')
    pdf.ln(10)  # Add new line after title

    # Add body of the bill
    pdf.set_font('DejaVuSans', '', 12)
    pdf.multi_cell(0, 10, body_bill)

    # Add footer
    pdf.set_font('DejaVuSans', 'I', 10)
    pdf.cell(0, 10, 'Thanks for visiting.', ln=True, align='C')
    
    pdf_filename = f"{customer_username}_{hotel_name}_Bill.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

def send_email(receiver_email, subject, body):
    sender_email = 'mywork.rds111.2030@gmail.com'  # Update with your email address
    sender_password = 'loulqncslbreljxh'  # Update with your email password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def register_customer():
    username = input("Enter username: ")
    password = input("Enter password: ")
    email = input("Enter email: ")
    phonenumber = input("Enter phone number (10 digits): ")

    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("Invalid email format. Please enter a valid email address.")
        return None, None, None

    if len(phonenumber) != 10:
        print("Invalid phone number. Please enter a 10-digit phone number.")
        return None, None, None

    # Check if email is already registered
    if email_registered(email):
        print("Email is already registered. Please use a different email or go for Login.")
        return None, None, None

    # Generate OTP
    otp = ''.join(random.choices('0123456789', k=6))
    subject_otp = 'OTP for Registration'
    body_otp = f'Your OTP for registration is: {otp}.'
    send_email(email, subject_otp, body_otp)

    # Verify OTP
    entered_otp = input("Enter OTP received on your email: ")
    if entered_otp == otp:
        # Send registration successful email
        subject_success = 'Registration Successful'
        body_success = f'Hello {username},\n\nYour registration is successful. Thank you for joining us!'
        send_email(email, subject_success, body_success)

        # Store customer details
        with open("registered_customers.txt", "a") as file:
            file.write(f"{username}|{password}|{email}|{phonenumber}\n")
        return username, password, email  # Return email address
    else:
        print("Invalid OTP. Registration failed.")
        return None, None, None

def email_registered(email):
    with open("registered_customers.txt", "r") as file:
        for line in file:
            values = line.strip().split("|")
            if len(values) >= 3:  # Ensure there are at least 3 values (username, password, email)
                _, _, stored_email = values[:3]
                if stored_email == email:
                    return True
    return False

def login_customer():
    username = input("Enter username: ")
    password = input("Enter password: ")
    with open("registered_customers.txt", "r") as file:
        for line in file:
            stored_values = line.strip().split("|")
            if len(stored_values) >= 2:  # Ensure there are at least 2 values (username, password)
                stored_username, stored_password = stored_values[:2]
                if stored_username == username and stored_password == password:
                    return True, stored_username, stored_values[2] if len(stored_values) >= 3 else None
    return False, None, None
def main():
    restaurant = Restaurant()
    order = Order()
    restaurant.load_menu()
    
    admin_username = "darshan"
    admin_password = "rds"
    hotel_name = "Saffron Sunset"  # Specify the hotel name

    customer_email = None  # Initialize customer_email variable
    username = None  # Initialize username variable

    while True:
        print("\n1. Register as Customer")
        print("2. Login as Admin")
        print("3. Login as Customer")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            print("Customer Registration:")
            username, password, customer_email = register_customer()
            if customer_email is not None:
                print("Registration successful!")

        elif choice == '3':
            print("Customer Login:")
            login_success, username, customer_email = login_customer()
            if login_success:
                print("Login successful. You are now logged in as customer.")
                while True:
                    print("\n1. View Menu")
                    print("2. Place Order")
                    print("3. Reorder Items")
                    print("4. Pay Bill")
                    print("5. Logout")
                    customer_choice = input("Enter your choice: ")

                    if customer_choice == '1':
                        restaurant.view_menu()
                        
                    elif customer_choice == '2':
                        item_name = input("Enter item name to order (type 'done' to finish): ")
                        while item_name.lower() != 'done':
                            quantity = int(input("Enter quantity: "))
                            order.add_item(item_name, quantity)
                            item_name = input("Enter next item name to order (type 'done' to finish): ")
                        total = order.calculate_total(restaurant.menu)
                        print(f"Total bill: ₹{total}")

                    elif customer_choice == '3':
                        # Reorder items
                        if order.items:
                            print("Reordering items:")
                            restaurant.view_menu()
                            reorder_item = input("Enter item name to reorder: ")
                            if reorder_item in restaurant.menu:
                                quantity = int(input("Enter quantity: "))
                                order.add_item(reorder_item, quantity)
                                print(f"{reorder_item} added to the order.")
                                total = order.calculate_total(restaurant.menu)
                                print(f"Updated total bill: ₹{total}")
                            else:
                                print(f"{reorder_item} is not available in the menu.")
                        else:
                            print("No items in the order to reorder.")

                    elif customer_choice == '4':
                        # Pay bill
                        if order.items:
                            order.make_payment(total, customer_email, username, hotel_name, restaurant.menu)  # Pass menu dictionary
                        else:
                            print("No items in the order to pay the bill.")
                        break

                    elif customer_choice == '5':
                        print("Logging out from customer account.")
                        break

                    else:
                        print("Invalid choice. Please try again.")

            else:
                print("Invalid username or password. Please try again.")

        elif choice == '2':
            print("Admin Login:")
            admin_username_input = input("Enter username: ")
            admin_password_input = input("Enter password: ")
            if admin_username_input == admin_username and admin_password_input == admin_password:
                print("Login successful. You are now logged in as admin.")
                restaurant.load_menu()
                while True:
                    print("\n1. Add Menu Item")
                    print("2. Remove Menu Item")
                    print("3. View Menu")
                    print("4. Logout")
                    admin_choice = input("Enter your choice: ")

                    if admin_choice == '1':
                        name = input("Enter item name: ")
                        price = float(input("Enter item price: "))
                        item = MenuItem(name, price)
                        restaurant.add_menu_item(item)

                    elif admin_choice == '2':
                        name = input("Enter item name to remove: ")
                        restaurant.remove_menu_item(name)

                    elif admin_choice == '3':
                        restaurant.view_menu()

                    elif admin_choice == '4':
                        restaurant.save_menu()
                        print("Logging out from admin account.")
                        break

                    else:
                        print("Invalid choice. Please try again.")

            else:
                print("Invalid username or password. Please try again.")

        elif choice == '4':
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
