# Import necessary modules
import tkinter as tk  # For GUI
import pickle         # For saving and loading data
import os             # For file operations

# ======================
# Class Definitions
# ======================

# Account base class
class Account:
    def _init_(self, username, password, email):
        self.username = username
        self.__password = password  # Private password attribute
        self.email = email
        self.purchase_history = []  # List to store user's bookings

    def get_password(self):
        return self.__password  # Getter for password

    def make_booking(self, booking):
        self.purchase_history.append(booking)  # Add booking to user's history

# Guest class inherits from Account and adds more personal details
class Guest(Account):
    def _init_(self, username, password, email, name, phone, address):
        super()._init_(username, password, email)
        self.name = name
        self.phone = phone
        self.address = address

# Ticket class represents ticket type and price
class Ticket:
    def _init_(self, ticket_type, price):
        self.ticket_type = ticket_type
        self.price = price

# Payment class represents payment method and amount
class Payment:
    def _init_(self, method, amount):
        self.method = method
        self.amount = amount

# Booking class represents a complete booking
class Booking:
    def _init_(self, ticket, date, payment):
        self.ticket = ticket
        self.date = date
        self.payment = payment

    def to_dict(self):
        # Convert booking to dictionary for saving
        return {
            "ticket_type": self.ticket.ticket_type,
            "price": self.ticket.price,
            "date": self.date,
            "payment_method": self.payment.method,
            "payment_amount": self.payment.amount
        }

    @staticmethod
    def from_dict(data):
        # Reconstruct Booking object from dictionary
        ticket = Ticket(data["ticket_type"], data["price"])
        payment = Payment(data["payment_method"], data["payment_amount"])
        return Booking(ticket, data["date"], payment)

# ======================
# Data Functions
# ======================

DATA_FILE = "accounts.pkl"  # File to store account data

def load_accounts():
    # Load accounts from file
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "rb") as f:
            data = pickle.load(f)
        reconstructed_accounts = {}
        for username, user_data in data.items():
            user = Guest(
                user_data["username"],
                user_data["password"],
                user_data["email"],
                user_data.get("name", ""),
                user_data.get("phone", ""),
                user_data.get("address", "")
            )
            user.purchase_history = [Booking.from_dict(b) for b in user_data.get("purchase_history", [])]
            reconstructed_accounts[username] = user
        return reconstructed_accounts
    except:
        return {}  # Return empty if error occurs

# ======================
# Admin Features
# ======================

def open_admin_login_window():
    # Admin login window
    win = tk.Toplevel(root)
    tk.Label(win, text="Admin Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()

    def validate_admin():
        # Validate admin password
        if pass_entry.get() == "admin123":  # Admin password (can be changed)
            win.destroy()
            open_admin_dashboard()
        else:
            tk.Label(win, text="Invalid password.", fg="red").pack()

    tk.Button(win, text="Login", command=validate_admin).pack()

def open_admin_dashboard():
    # Admin dashboard with options
    win = tk.Toplevel(root)
    win.title("Admin Dashboard")

    tk.Button(win, text="View All Bookings", command=lambda: view_all_bookings(win)).pack(pady=5)
    tk.Button(win, text="Apply Discount", command=lambda: apply_discount(win)).pack(pady=5)
    tk.Button(win, text="Close", command=win.destroy).pack(pady=5)

def view_all_bookings(dashboard_win):
    # Display all bookings
    win = tk.Toplevel(dashboard_win)
    win.title("All User Bookings")
    found = False
    for user in accounts.values():
        if user.purchase_history:
            tk.Label(win, text=f"User: {user.username}").pack()
            for b in user.purchase_history:
                summary = f" - {b.ticket.ticket_type}, {b.date}, AED {b.payment.amount} via {b.payment.method}"
                tk.Label(win, text=summary).pack()
            found = True
    if not found:
        tk.Label(win, text="No bookings found.").pack()
    tk.Button(win, text="Back", command=win.destroy).pack(pady=5)

def apply_discount(dashboard_win):
    # Apply discount to all bookings
    win = tk.Toplevel(dashboard_win)
    win.title("Apply Discount")

    tk.Label(win, text="Enter discount percentage (e.g., 10 for 10%):").pack()
    discount_entry = tk.Entry(win)
    discount_entry.pack()

    def apply():
        try:
            discount = float(discount_entry.get())
            for user in accounts.values():
                for b in user.purchase_history:
                    original_price = b.ticket.price
                    discounted_price = round(original_price * (1 - discount / 100), 2)
                    b.ticket.price = discounted_price
                    b.payment.amount = discounted_price
            save_accounts(accounts)
            tk.Label(win, text=f"Applied {discount}% discount to all bookings.", fg="green").pack()
        except ValueError:
            tk.Label(win, text="Please enter a valid number.", fg="red").pack()

    tk.Button(win, text="Apply Discount", command=apply).pack()
    tk.Button(win, text="Back", command=win.destroy).pack(pady=5)

def save_accounts(accounts):
    # Save accounts to file
    data = {}
    for username, user in accounts.items():
        data[username] = {
            "username": user.username,
            "password": user.get_password(),
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "address": user.address,
            "purchase_history": [b.to_dict() for b in user.purchase_history]
        }
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

# ======================
# User Interface Setup
# ======================

accounts = load_accounts()  # Load existing accounts
root = tk.Tk()              # Main application window
root.title("Grand Prix Ticket Booking System")
root.geometry("600x400")

# ======================
# GUI Functions for Users
# ======================

def open_register_window():
    # User registration window
    win = tk.Toplevel(root)
    labels = ["Username", "Password", "Email", "Full Name", "Phone", "Address"]
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(win, text=label).grid(row=i, column=0)
        entry = tk.Entry(win, show="*" if "Password" in label else None)
        entry.grid(row=i, column=1)
        entries[label] = entry
    feedback = tk.Label(win, text="", fg="red")
    feedback.grid(row=len(labels), columnspan=2)

    def submit():
        username = entries["Username"].get()
        if username in accounts:
            feedback.config(text="Username already exists.")
            return
        guest = Guest(username, entries["Password"].get(), entries["Email"].get(),
                      entries["Full Name"].get(), entries["Phone"].get(), entries["Address"].get())
        accounts[username] = guest
        save_accounts(accounts)
        feedback.config(text="Account created successfully! Please login.", fg="green")

    tk.Button(win, text="Register", command=submit).grid(row=len(labels)+1, columnspan=2)

def open_login_window():
    # User login window
    win = tk.Toplevel(root)
    tk.Label(win, text="Username").grid(row=0, column=0)
    tk.Label(win, text="Password").grid(row=1, column=0)
    user_entry = tk.Entry(win)
    pass_entry = tk.Entry(win, show="*")
    user_entry.grid(row=0, column=1)
    pass_entry.grid(row=1, column=1)
    feedback = tk.Label(win, text="")
    feedback.grid(row=2, columnspan=2)

    def attempt_login():
        username = user_entry.get()
        password = pass_entry.get()
        user = accounts.get(username)
        if user and user.get_password() == password:
            win.destroy()
            open_dashboard(user)
        else:
            feedback.config(text="Invalid credentials.")

    tk.Button(win, text="Login", command=attempt_login).grid(row=3, columnspan=2)

def open_dashboard(user):
    # User dashboard window
    win = tk.Toplevel(root)
    win.title("Dashboard")
    tk.Label(win, text=f"Welcome {user.username}").pack()
    tk.Button(win, text="My Reservations", command=lambda: view_reservations(user, win)).pack(pady=5)
    tk.Button(win, text="Make a New Reservation", command=lambda: open_ticket_selection_window(user)).pack(pady=5)
    tk.Button(win, text="View Account Details", command=lambda: show_account_details(user)).pack(pady=5)
    tk.Button(win, text="Logout", command=win.destroy).pack(pady=5)

def show_account_details(user):
    # Display user account details
    win = tk.Toplevel(root)
    win.title("Account Details")
    details = f"Username: {user.username}\nName: {user.name}\nEmail: {user.email}\nPhone: {user.phone}\nAddress: {user.address}"
    tk.Label(win, text=details).pack(pady=10)
    tk.Button(win, text="Close", command=win.destroy).pack(pady=5)

def view_reservations(user, dashboard_win):
    # Display user's bookings
    win = tk.Toplevel(dashboard_win)
    win.title("My Reservations")
    if not user.purchase_history:
        tk.Label(win, text="No reservations found.").pack()
    else:
        for b in user.purchase_history:
            summary = f"{b.ticket.ticket_type}, {b.date}, AED {b.payment.amount} via {b.payment.method}"
            tk.Label(win, text=summary).pack()
    tk.Button(win, text="Back", command=win.destroy).pack(pady=5)

def open_ticket_selection_window(user):
    # Ticket selection window
    win = tk.Toplevel(root)
    tickets = [
        Ticket("Single Race Pass", 200),
        Ticket("Weekend Package", 650),
        Ticket("Season Membership", 2000),
        Ticket("Group Discount (5 People)", 900)
    ]
    choice = tk.StringVar(value=tickets[0].ticket_type)
    tk.Label(win, text="Choose Ticket Type:").pack()
    for t in tickets:
        tk.Radiobutton(win, text=f"{t.ticket_type} - AED {t.price}", variable=choice, value=t.ticket_type).pack()

    def next_step():
        selected_ticket = next(t for t in tickets if t.ticket_type == choice.get())
        win.destroy()
        open_date_selection_window(user, selected_ticket)

    tk.Button(win, text="Next: Select Date", command=next_step).pack()
    tk.Button(win, text="Back", command=lambda: open_dashboard(user) or win.destroy()).pack()

def open_date_selection_window(user, ticket):
    # Date selection window based on ticket type
    win = tk.Toplevel(root)
    win.title("Select Date")

    if ticket.ticket_type == "Single Race Pass":
        tk.Label(win, text="Choose Weekend:").pack()
        weekends = {
            "Weekend 1 (Dec 5-7)": ["2025-12-05", "2025-12-06", "2025-12-07"],
            "Weekend 2 (Dec 12-14)": ["2025-12-12", "2025-12-13", "2025-12-14"],
            "Weekend 3 (Dec 19-21)": ["2025-12-19", "2025-12-20", "2025-12-21"]
        }
        weekend_choice = tk.StringVar(value=list(weekends.keys())[0])
        for w in weekends:
            tk.Radiobutton(win, text=w, variable=weekend_choice, value=w).pack(anchor="w")

        def next_step():
            win.destroy()
            open_day_selection_window(user, ticket, weekends[weekend_choice.get()])

        tk.Button(win, text="Next: Choose Day", command=next_step).pack()
        tk.Button(win, text="Back", command=lambda: open_ticket_selection_window(user) or win.destroy()).pack()

    else:
        dates = (
            ["Weekend 1 (Dec 5-7)", "Weekend 2 (Dec 12-14)", "Weekend 3 (Dec 19-21)"] if ticket.ticket_type == "Weekend Package" else
            ["Full Season 2025"] if ticket.ticket_type == "Season Membership" else
            ["Group Day 1 (Dec 8)", "Group Day 2 (Dec 15)", "Group Day 3 (Dec 22)"]
        )
        choice = tk.StringVar(value=dates[0])
        for d in dates:
            tk.Radiobutton(win, text=d, variable=choice, value=d).pack(anchor="w")

        def next_step_other():
            win.destroy()
            open_payment_window(user, ticket, choice.get())

        tk.Button(win, text="Next: Payment", command=next_step_other).pack()
        tk.Button(win, text="Back", command=lambda: open_ticket_selection_window(user) or win.destroy()).pack()

def open_day_selection_window(user, ticket, days):
    # Day selection window
    win = tk.Toplevel(root)
    win.title("Select Day")
    tk.Label(win, text="Choose Day:").pack()
    choice = tk.StringVar(value=days[0])
    for d in days:
        tk.Radiobutton(win, text=d, variable=choice, value=d).pack(anchor="w")

    def confirm_day():
        win.destroy()
        open_payment_window(user, ticket, choice.get())

    tk.Button(win, text="Next: Payment", command=confirm_day).pack()
    tk.Button(win, text="Back", command=lambda: open_date_selection_window(user, ticket) or win.destroy()).pack()

def open_payment_window(user, ticket, date):
    # Payment window
    win = tk.Toplevel(root)
    tk.Label(win, text=f"Confirm {ticket.ticket_type} on {date} for AED {ticket.price}").pack()
    methods = ["Credit Card", "Digital Wallet"]
    choice = tk.StringVar(value=methods[0])
    for m in methods:
        tk.Radiobutton(win, text=m, variable=choice, value=m).pack()

    def confirm():
        booking = Booking(ticket, date, Payment(choice.get(), ticket.price))
        user.make_booking(booking)
        accounts[user.username] = user
        save_accounts(accounts)
        win.destroy()
        show_booking_summary(user, booking)

    def show_booking_summary(user, booking):
        # Booking summary window
        summary_win = tk.Toplevel(root)
        summary_win.title("Booking Summary")
        summary = f"Ticket: {booking.ticket.ticket_type}\nDate: {booking.date}\nAmount: AED {booking.payment.amount}\nPayment Method: {booking.payment.method}"
        tk.Label(summary_win, text="Booking Summary").pack(pady=5)
        tk.Label(summary_win, text=summary).pack(pady=5)
        tk.Label(summary_win, text="Booking confirmed! Thank you.", fg="green").pack(pady=10)
        tk.Button(summary_win, text="Return to Dashboard",
                  command=lambda: [summary_win.destroy(), open_dashboard(user)]).pack(pady=5)

    tk.Button(win, text="Confirm Booking", command=confirm).pack()
    tk.Button(win, text="Back", command=lambda: open_date_selection_window(user, ticket) or win.destroy()).pack()

# ======================
# Main Menu Buttons
# ======================

tk.Label(root, text="Welcome to the Grand Prix Ticket Booking System").pack(pady=10)
tk.Button(root, text="Register", command=open_register_window).pack(pady=5)
tk.Button(root, text="Login", command=open_login_window).pack(pady=5)
tk.Button(root, text="Admin Login", command=open_admin_login_window).pack(pady=5)
tk.Button(root, text="Exit", command=root.destroy).pack(pady=5)

# Start the GUI loop
root.mainloop()