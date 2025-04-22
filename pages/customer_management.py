import tkinter as tk
from tkinter import ttk, messagebox
from gui_framework import BasePage
import mysql.connector

class CustomerManagement(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.create_customer_ui()
        self.load_customers()

    def create_customer_ui(self):
        header = ttk.Label(self.content, text="Customer Management", font=('Helvetica', 16))
        header.pack(pady=10)

        search_frame = ttk.Frame(self.content)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", lambda e: self.load_customers())

        columns = ("ID", "Name", "Contact", "Email", "Address")
        self.tree = ttk.Treeview(self.content, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120 if col != "Address" else 200)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add", command=self.add_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Edit", command=self.edit_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="View Sales", command=self.view_sales).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self.load_customers).pack(side=tk.LEFT, padx=2)

    def load_customers(self):
        search = self.search_var.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = "SELECT customer_id, name, contact, email, address FROM customers"
        params = ()
        if search:
            query += " WHERE name LIKE %s OR contact LIKE %s OR email LIKE %s OR address LIKE %s"
            like = f"%{search}%"
            params = (like, like, like, like)
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['customer_id'], row['name'], row['contact'], row['email'], row['address']))

    def add_customer(self):
        self.open_customer_form("Add Customer")

    def edit_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a customer to edit.")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_customer_form("Edit Customer", values)

    def delete_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a customer to delete.")
            return
        customer_id = self.tree.item(selected[0], 'values')[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))
                self.db.commit()
                self.load_customers()
                messagebox.showinfo("Deleted", "Customer deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete customer: {e}")

    def open_customer_form(self, title, customer=None):
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry("350x350")
        form.resizable(False, False)

        name_var = tk.StringVar(value=customer[1] if customer else "")
        phone_var = tk.StringVar(value=customer[2] if customer else "")
        email_var = tk.StringVar(value=customer[3] if customer else "")
        address_var = tk.StringVar(value=customer[4] if customer else "")

        ttk.Label(form, text="Name:").pack(anchor='w', padx=20, pady=(20, 2))
        name_entry = ttk.Entry(form, textvariable=name_var)
        name_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Phone:").pack(anchor='w', padx=20, pady=(10, 2))
        phone_entry = ttk.Entry(form, textvariable=phone_var)
        phone_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Email:").pack(anchor='w', padx=20, pady=(10, 2))
        email_entry = ttk.Entry(form, textvariable=email_var)
        email_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Address:").pack(anchor='w', padx=20, pady=(10, 2))
        address_entry = ttk.Entry(form, textvariable=address_var)
        address_entry.pack(fill=tk.X, padx=20)

        def save():
            name = name_var.get().strip()
            phone = phone_var.get().strip()
            email = email_var.get().strip()
            address = address_var.get().strip()
            if not name:
                messagebox.showerror("Input Error", "Name is required.")
                return
            try:
                if customer:
                    self.cursor.execute("""
                        UPDATE customers SET name=%s, phone=%s, email=%s, address=%s WHERE customer_id=%s
                    """, (name, phone, email, address, customer[0]))
                else:
                    self.cursor.execute("""
                        INSERT INTO customers (name, phone, email, address)
                        VALUES (%s, %s, %s, %s)
                    """, (name, phone, email, address))
                self.db.commit()
                self.load_customers()
                form.destroy()
                messagebox.showinfo("Success", "Customer saved successfully.")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save customer: {e}")

        btn_frame = ttk.Frame(form)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Save", command=save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=form.destroy).pack(side=tk.LEFT, padx=10)

    def view_sales(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a customer to view sales.")
            return
        customer_id = self.tree.item(selected[0], 'values')[0]
        self.cursor.execute("""
            SELECT s.sale_id, s.date, s.total_amount
            FROM sales s
            WHERE s.customer_id = %s
            ORDER BY s.date DESC
        """, (customer_id,))
        sales = self.cursor.fetchall()
        info = "Sales History:\n"
        if sales:
            for s in sales:
                info += f"ID: {s['sale_id']} | Date: {s['date']} | Amount: {s['total_amount']}\n"
        else:
            info += "No sales found."
        messagebox.showinfo("Customer Sales", info)