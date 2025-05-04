import tkinter as tk
from tkinter import ttk
import pickle
import os

class Account:
    """Class to represent an account"""
    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.purchase_history = []

    def view_purchase_history(self):
        return self.purchase_history

class Discount:
    """Class to represent the discounts"""
    def __init__(self, code, percentage):
        self.code = code
        self.percentage = percentage

class Guest(Account):
    """Class to represent a guest account"""
    def __init__(self, username, password, email, name, phone, address):
        super().__init__(username, password, email)
        self.name = name
        self.phone = phone
        self.address = address
        self.discounts = []

    def add_discount(self, discount):
        self.discounts.append(discount)

    def make_booking(self, booking):
        self.purchase_history.append(booking)

class Administrator(Account):
    """Class to represent an admin account"""
    def __init__(self, username, password, email, admin_id):
        super().__init__(username, password, email)
        self.admin_id = admin_id

class Event:
    """Class to represent an event"""
    def __init__(self, name, date, location):
        self.name = name
        self.date = date
        self.location = location

class Ticket:
    """Class to represent a ticket"""
    def __init__(self, ticket_type, price, event_date, availability_status):
        self.ticket_type = ticket_type
        self.price = price
        self.event_date = event_date
        self.availability_status = availability_status
        self.event = event

    def __str__(self):
        return f"{self.ticket_type} | AED {self.price} | {self.event_date}"

class Payment:
    """Class to represent a payment"""
    def __init__(self, method, amount, date):
        self.method = method
        self.amount = amount
        self.date = date
        self.payments = []

class Booking:
    """Class to represent a booking for the event"""
    def __init__(self, booking_number, date, tickets, guest):
        self.booking_number = booking_number
        self.date = date
        self.tickets = tickets
        self.guest = guest
        self.total_price = sum(ticket.price for ticket in tickets)

    def add_payment(self, payment):
        self.payments.append(payment)

DATA_FILE = "accounts.pkl" # File to save the accounts information

def load_accounts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            return pickle.load(f)
    return {} # Loads the data of the account if it exists in the pickl file

def save_accounts(data):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f) # Saves the data in binary format into the pickl file

accounts = load_accounts()

root = tk.Tk()
root.title("Grand Prix Ticket Booking System")
root.geometry("600x400")

def open_register_window():
    register_window = tk.Toplevel(root)
    register_window.title("Register")
    labels = ["Username", "Password", "Email", "Full Name", "Phone", "Address"]
    entries = {}

    for i, label_text in enumerate(labels):
        tk.Label(register_window, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        entry = tk.Entry(register_window, show="*" if "Password" in label_text else None)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label_text] = entry

    feedback = tk.Label(register_window, text="", fg="red")
    feedback.grid(row=len(labels), columnspan=2)

    def submit_register():
        username = entries["Username"].get()
        if username in accounts:
            feedback.config(text="Username already exists.")
            return

        guest = Guest(
            username,
            entries["Password"].get(),
            entries["Email"].get(),
            entries["Full Name"].get(),
            entries["Phone"].get(),
            entries["Address"].get()
        )
        accounts[username] = guest
        save_accounts(accounts)
        feedback.config(text="Account created successfully!", fg="green")

    tk.Button(register_window, text="Register", command=submit_register).grid(row=len(labels)+1, columnspan=2, pady=10)


def open_login_window():
    login_window = tk.Toplevel(root)
    login_window.title("Login")

    tk.Label(login_window, text="Username").grid(row=0, column=0, padx=10, pady=5)
    tk.Label(login_window, text="Password").grid(row=1, column=0, padx=10, pady=5)

    username_entry = tk.Entry(login_window)
    password_entry = tk.Entry(login_window, show="*")
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    feedback = tk.Label(login_window, text="", fg="red")
    feedback.grid(row=3, columnspan=2)

    def attempt_login():
        username = username_entry.get()
        password = password_entry.get()
        user = accounts.get(username)
        if user and user.password == password:
            feedback.config(text=f"Welcome, {username}!", fg="green")
            open_booking_window(user)
        else:
            feedback.config(text="Invalid credentials.", fg="red")

    tk.Button(login_window, text="Login", command=attempt_login).grid(row=2, columnspan=2, pady=10)

def open_booking_window(user):
    booking_window = tk.Toplevel(root)
    booking_window.title("Book Your Tickets")

    tk.Label(booking_window, text="Choose your ticket:").pack(pady=10)

    tickets = [
        Ticket("Single Race", 200.0, "2025-12-01", "Available"),
        Ticket("Weekend Package", 650.0, "2025-12-01", "Available"),
        Ticket("Season Pass", 2000.0, "All Dates", "Available")
    ]

    selected = tk.StringVar(value=tickets[0].ticket_type)

    for ticket in tickets:
        tk.Radiobutton(booking_window, text=str(ticket), variable=selected, value=ticket.ticket_type).pack(anchor='w')

    feedback = tk.Label(booking_window, text="", fg="green")
    feedback.pack()

    def confirm_booking():
        chosen_ticket = next(t for t in tickets if t.ticket_type == selected.get())
        booking = Booking(
            booking_number=len(user.purchase_history) + 1,
            date="2025-05-03",
            tickets=[chosen_ticket]
        )
        user.make_booking(booking)
        save_accounts(accounts)
        feedback.config(text=f"Booking confirmed! AED {booking.total_price}")

    tk.Button(booking_window, text="Confirm Booking", command=confirm_booking).pack(pady=20)


tk.Label(root, text="Welcome to the Grand Prix Ticket Booking System", font=("Arial", 14)).pack(pady=30)
tk.Button(root, text="Register", width=20, command=open_register_window).pack(pady=10)
tk.Button(root, text="Login", width=20, command=open_login_window).pack(pady=10)
tk.Button(root, text="Exit", width=20, command=root.destroy).pack(pady=10)

root.mainloop()