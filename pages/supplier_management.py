import tkinter as tk
from tkinter import ttk, messagebox
from gui_framework import BasePage
import mysql.connector

class SupplierManagement(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.create_supplier_ui()
        self.load_suppliers()

    def create_supplier_ui(self):
        header_frame = ttk.Frame(self.content)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame, text="Supplier Management", font=('Helvetica', 16)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Search:").pack(side=tk.LEFT, padx=(30, 2))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(header_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", lambda e: self.load_suppliers())

        columns = ("ID", "Name", "Contact", "Email", "Address")
        self.tree = ttk.Treeview(self.content, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120 if col != "Address" else 200)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add", width=10, command=self.add_supplier).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Edit", width=10, command=self.edit_supplier).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", width=10, command=self.delete_supplier).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="View Info", width=10, command=self.view_supplier_info).pack(side=tk.LEFT, padx=2)
        self.tree.bind("<Double-1>", lambda e: self.view_supplier_info())

    def view_supplier_info(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a supplier to view info.")
            return
        supplier_id = self.tree.item(selected[0], 'values')[0]
        self.cursor.execute("SELECT * FROM suppliers WHERE supplier_id=%s", (supplier_id,))
        supplier = self.cursor.fetchone()
        self.cursor.execute("""
            SELECT p.purchase_id, p.date, p.total_amount
            FROM purchases p
            WHERE p.supplier_id = %s
            ORDER BY p.date DESC
        """, (supplier_id,))
        purchases = self.cursor.fetchall()
        info = f"Name: {supplier['name']}\nContact: {supplier['contact']}\nEmail: {supplier['email']}\nAddress: {supplier['address']}\n\nPurchase History:\n"
        if purchases:
            for p in purchases:
                info += f"ID: {p['purchase_id']} | Date: {p['date']} | Amount: {p['total_amount']}\n"
        else:
            info += "No purchases found."
        messagebox.showinfo("Supplier Info", info)

    def load_suppliers(self):
        search = self.search_var.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = "SELECT supplier_id, name, contact, email, address FROM suppliers"
        params = ()
        if search:
            query += " WHERE name LIKE %s OR contact LIKE %s OR email LIKE %s OR address LIKE %s"
            like = f"%{search}%"
            params = (like, like, like, like)
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['supplier_id'], row['name'], row['contact'], row['email'], row['address']))

    def add_supplier(self):
        self.open_supplier_form("Add Supplier")

    def edit_supplier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a supplier to edit.")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_supplier_form("Edit Supplier", values)

    def delete_supplier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a supplier to delete.")
            return
        supplier_id = self.tree.item(selected[0], 'values')[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this supplier?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM suppliers WHERE supplier_id=%s", (supplier_id,))
                self.db.commit()
                self.load_suppliers()
                messagebox.showinfo("Deleted", "Supplier deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete supplier: {e}")

    def open_supplier_form(self, title, supplier=None):
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry("350x400")
        form.resizable(False, False)

        name_var = tk.StringVar(value=supplier[1] if supplier else "")
        contact_var = tk.StringVar(value=supplier[2] if supplier else "")
        email_var = tk.StringVar(value=supplier[3] if supplier else "")
        address_var = tk.StringVar(value=supplier[4] if supplier else "")

        ttk.Label(form, text="Name:").pack(anchor='w', padx=20, pady=(20, 2))
        name_entry = ttk.Entry(form, textvariable=name_var)
        name_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Contact:").pack(anchor='w', padx=20, pady=(10, 2))
        contact_entry = ttk.Entry(form, textvariable=contact_var)
        contact_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Email:").pack(anchor='w', padx=20, pady=(10, 2))
        email_entry = ttk.Entry(form, textvariable=email_var)
        email_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Address:").pack(anchor='w', padx=20, pady=(10, 2))
        address_entry = ttk.Entry(form, textvariable=address_var)
        address_entry.pack(fill=tk.X, padx=20)

        def save():
            name = name_var.get().strip()
            contact = contact_var.get().strip()
            email = email_var.get().strip()
            address = address_var.get().strip()

            if not all([name, contact, email, address]):
                messagebox.showerror("Input Error", "Please fill all required fields.")
                return

            try:
                if supplier:
                    self.cursor.execute("""
                        UPDATE suppliers SET name=%s, contact=%s, email=%s, address=%s
                        WHERE supplier_id=%s
                    """, (name, contact, email, address, supplier[0]))
                else:
                    self.cursor.execute("""
                        INSERT INTO suppliers (name, contact, email, address)
                        VALUES (%s, %s, %s, %s)
                    """, (name, contact, email, address))
                self.db.commit()
                self.load_suppliers()
                form.destroy()
                messagebox.showinfo("Success", "Supplier saved successfully.")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save supplier: {e}")

        btn_frame = ttk.Frame(form)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Save", command=save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=form.destroy).pack(side=tk.LEFT, padx=10)