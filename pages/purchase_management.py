import tkinter as tk
from tkinter import ttk, messagebox
from gui_framework import BasePage
import mysql.connector
from datetime import datetime

class PurchaseManagement(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.create_purchase_ui()
        self.load_purchases()

    def create_purchase_ui(self):
        header = ttk.Label(self.content, text="Purchase Management", font=('Helvetica', 16))
        header.pack(pady=10)

        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Record Purchase", command=self.record_purchase).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_purchases).pack(side=tk.LEFT, padx=5)

        columns = ("Purchase ID", "Supplier", "Date", "Total Amount")
        self.tree = ttk.Treeview(self.content, columns=columns, show='headings', height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree.bind("<Double-1>", self.show_purchase_items)

    def load_purchases(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.cursor.execute("""
            SELECT p.purchase_id, s.name AS supplier, p.date, p.total_amount
            FROM purchases p
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            ORDER BY p.date DESC
        """)
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['purchase_id'], row['supplier'], row['date'], row['total_amount']))

    def record_purchase(self):
        form = tk.Toplevel(self)
        form.title("Record Purchase")
        form.geometry("400x500")
        form.resizable(False, False)

        # Supplier selection
        self.cursor.execute("SELECT supplier_id, name FROM suppliers")
        suppliers = self.cursor.fetchall()
        supplier_dict = {s['name']: s['supplier_id'] for s in suppliers}
        supplier_names = list(supplier_dict.keys())
        supplier_var = tk.StringVar(value=supplier_names[0] if supplier_names else "")

        ttk.Label(form, text="Supplier:").pack(anchor='w', padx=20, pady=(20, 2))
        supplier_combo = ttk.Combobox(form, textvariable=supplier_var, values=supplier_names, state='readonly')
        supplier_combo.pack(fill=tk.X, padx=20)

        # Product selection
        self.cursor.execute("SELECT product_id, name FROM products")
        products = self.cursor.fetchall()
        product_dict = {p['name']: p['product_id'] for p in products}
        product_names = list(product_dict.keys())

        items = []

        def add_item_row():
            row_frame = ttk.Frame(form)
            row_frame.pack(fill=tk.X, padx=20, pady=5)
            prod_var = tk.StringVar(value=product_names[0] if product_names else "")
            qty_var = tk.StringVar(value="1")
            price_var = tk.StringVar(value="0.0")
            ttk.Combobox(row_frame, textvariable=prod_var, values=product_names, state='readonly', width=15).pack(side=tk.LEFT)
            ttk.Entry(row_frame, textvariable=qty_var, width=5).pack(side=tk.LEFT, padx=5)
            ttk.Entry(row_frame, textvariable=price_var, width=8).pack(side=tk.LEFT, padx=5)
            items.append((prod_var, qty_var, price_var))

        ttk.Label(form, text="Products (Name, Quantity, Price):").pack(anchor='w', padx=20, pady=(10, 2))
        for _ in range(1):
            add_item_row()

        ttk.Button(form, text="Add Another Product", command=add_item_row).pack(pady=5)

        def save_purchase():
            supplier_name = supplier_var.get()
            supplier_id = supplier_dict.get(supplier_name)
            if not supplier_id:
                messagebox.showerror("Input Error", "Please select a supplier.")
                return

            purchase_items = []
            total_amount = 0.0
            for prod_var, qty_var, price_var in items:
                prod_name = prod_var.get()
                product_id = product_dict.get(prod_name)
                try:
                    qty = int(qty_var.get())
                    price = float(price_var.get())
                except ValueError:
                    messagebox.showerror("Input Error", "Quantity must be integer and price must be number.")
                    return
                if not product_id or qty <= 0 or price < 0:
                    messagebox.showerror("Input Error", "Invalid product, quantity, or price.")
                    return
                purchase_items.append((product_id, qty, price))
                total_amount += qty * price

            if not purchase_items:
                messagebox.showerror("Input Error", "Add at least one product.")
                return

            try:
                # Insert into purchases
                self.cursor.execute(
                    "INSERT INTO purchases (supplier_id, date, total_amount) VALUES (%s, %s, %s)",
                    (supplier_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total_amount)
                )
                purchase_id = self.cursor.lastrowid

                # Insert into purchase_items and update stock
                for product_id, qty, price in purchase_items:
                    self.cursor.execute(
                        "INSERT INTO purchase_items (purchase_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                        (purchase_id, product_id, qty, price)
                    )
                    self.cursor.execute(
                        "UPDATE products SET quantity = quantity + %s WHERE product_id = %s",
                        (qty, product_id)
                    )
                self.db.commit()
                self.load_purchases()
                form.destroy()
                messagebox.showinfo("Success", "Purchase recorded and stock updated.")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to record purchase: {e}")

        ttk.Button(form, text="Save Purchase", command=save_purchase).pack(pady=15)
        ttk.Button(form, text="Cancel", command=form.destroy).pack()

    def show_purchase_items(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        purchase_id = self.tree.item(selected[0], 'values')[0]
        self.cursor.execute("""
            SELECT p.name, pi.quantity, pi.price
            FROM purchase_items pi
            JOIN products p ON pi.product_id = p.product_id
            WHERE pi.purchase_id = %s
        """, (purchase_id,))
        items = self.cursor.fetchall()
        info = "\n".join([f"{item['name']}: {item['quantity']} x {item['price']}" for item in items])
        messagebox.showinfo("Purchase Items", info if info else "No items found.")