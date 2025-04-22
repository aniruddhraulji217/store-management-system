import tkinter as tk
from tkinter import ttk, messagebox
from gui_framework import BasePage
import mysql.connector
from datetime import datetime

class SalesManagement(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.create_sales_ui()
        self.load_sales()

    def create_sales_ui(self):
        header = ttk.Label(self.content, text="Sales Management", font=('Helvetica', 16))
        header.pack(pady=10)

        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Record Sale", command=self.record_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_sales).pack(side=tk.LEFT, padx=5)

        columns = ("Sale ID", "Customer", "Date", "Total Amount")
        self.tree = ttk.Treeview(self.content, columns=columns, show='headings', height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree.bind("<Double-1>", self.show_sale_items)

    def load_sales(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.cursor.execute("""
            SELECT s.sale_id, c.name AS customer, s.sale_date, s.total_amount
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            ORDER BY s.sale_date DESC
        """)
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['sale_id'], row['customer'], row['sale_date'], row['total_amount']))
    def record_sale(self):
        form = tk.Toplevel(self)
        form.title("Record Sale")
        form.geometry("500x600")
        form.resizable(False, False)

        # Customer selection (with add new)
        self.cursor.execute("SELECT customer_id, name FROM customers")
        customers = self.cursor.fetchall()
        customer_dict = {c['name']: c['customer_id'] for c in customers}
        customer_names = list(customer_dict.keys())
        customer_var = tk.StringVar(value=customer_names[0] if customer_names else "")

        ttk.Label(form, text="Customer:").pack(anchor='w', padx=20, pady=(20, 2))
        customer_combo = ttk.Combobox(form, textvariable=customer_var, values=customer_names, state='readonly')
        customer_combo.pack(fill=tk.X, padx=20)

        # Product selection
        self.cursor.execute("SELECT product_id, name, quantity, price, cost_price FROM products")
        products = self.cursor.fetchall()
        product_dict = {p['name']: p for p in products}
        product_names = list(product_dict.keys())

        items = []

        def add_item_row():
            row_frame = ttk.Frame(form)
            row_frame.pack(fill=tk.X, padx=20, pady=5)
            prod_var = tk.StringVar(value=product_names[0] if product_names else "")
            qty_var = tk.StringVar(value="1")
            price_var = tk.StringVar()
            cost_var = tk.StringVar()
            total_var = tk.StringVar()
            profit_var = tk.StringVar()

            def update_fields(*args):
                prod_name = prod_var.get()
                if prod_name in product_dict:
                    prod = product_dict[prod_name]
                    price_var.set(str(prod['price']))
                    cost_var.set(str(prod['cost_price']))
                    try:
                        qty = int(qty_var.get())
                    except:
                        qty = 1
                    total = qty * prod['price']
                    profit = (prod['price'] - prod['cost_price']) * qty
                    total_var.set(f"{total:.2f}")
                    profit_var.set(f"{profit:.2f}")

            prod_var.trace('w', update_fields)
            qty_var.trace('w', update_fields)

            ttk.Combobox(row_frame, textvariable=prod_var, values=product_names, state='readonly', width=15).pack(side=tk.LEFT)
            ttk.Entry(row_frame, textvariable=qty_var, width=5).pack(side=tk.LEFT, padx=5)
            ttk.Entry(row_frame, textvariable=price_var, width=8, state='readonly').pack(side=tk.LEFT, padx=5)
            ttk.Entry(row_frame, textvariable=cost_var, width=8, state='readonly').pack(side=tk.LEFT, padx=5)
            ttk.Entry(row_frame, textvariable=total_var, width=10, state='readonly').pack(side=tk.LEFT, padx=5)
            ttk.Entry(row_frame, textvariable=profit_var, width=10, state='readonly').pack(side=tk.LEFT, padx=5)
            items.append((prod_var, qty_var, price_var, cost_var, total_var, profit_var))
            update_fields()

        # Table headers
        header_frame = ttk.Frame(form)
        header_frame.pack(fill=tk.X, padx=20, pady=(10, 2))
        for text, w in zip(["Product", "Qty", "Price", "Cost", "Total", "Profit"], [15, 5, 8, 8, 10, 10]):
            ttk.Label(header_frame, text=text, width=w).pack(side=tk.LEFT, padx=2)

        for _ in range(1):
            add_item_row()

        ttk.Button(form, text="Add Another Product", command=add_item_row).pack(pady=5)

        total_sale_var = tk.StringVar(value="0.00")
        total_profit_var = tk.StringVar(value="0.00")

        def update_totals():
            total_sale = 0.0
            total_profit = 0.0
            for prod_var, qty_var, price_var, cost_var, total_var, profit_var in items:
                try:
                    total_sale += float(total_var.get())
                    total_profit += float(profit_var.get())
                except:
                    pass
            total_sale_var.set(f"{total_sale:.2f}")
            total_profit_var.set(f"{total_profit:.2f}")

        # Update totals whenever any item changes
        for item in items:
            for var in item:
                var.trace('w', lambda *args: update_totals())

        ttk.Label(form, text="Total Sale Amount:").pack(anchor='w', padx=20, pady=(10, 2))
        ttk.Entry(form, textvariable=total_sale_var, state='readonly').pack(fill=tk.X, padx=20)
        ttk.Label(form, text="Total Profit:").pack(anchor='w', padx=20, pady=(5, 2))
        ttk.Entry(form, textvariable=total_profit_var, state='readonly').pack(fill=tk.X, padx=20)

        def save_sale():
            customer_name = customer_var.get()
            customer_id = customer_dict.get(customer_name)
            if not customer_id:
                messagebox.showerror("Input Error", "Please select a customer.")
                return

            sale_items = []
            total_amount = 0.0
            total_profit = 0.0
            total_discount = 0.0
            tax_rate = 0.05  # Example: 5% tax
            total_tax = 0.0
            for prod_var, qty_var, price_var, cost_var, total_var, profit_var, discount_var in items:
                prod_name = prod_var.get()
                prod = product_dict.get(prod_name)
                if not prod:
                    messagebox.showerror("Input Error", "Invalid product selected.")
                    return
                product_id = prod['product_id']
                available_qty = prod['quantity']
                try:
                    qty = int(qty_var.get())
                    price = float(price_var.get())
                    cost = float(cost_var.get())
                    profit = float(profit_var.get())
                except ValueError:
                    messagebox.showerror("Input Error", "Invalid quantity or price.")
                    return
                if qty <= 0 or price < 0:
                    messagebox.showerror("Input Error", "Invalid quantity or price.")
                    return
                if qty > available_qty:
                    messagebox.showerror("Stock Error", f"Not enough stock for {prod_name}. Available: {available_qty}")
                    return
                sale_items.append((product_id, qty, price, cost, profit))
                subtotal = qty * price - discount
                tax = subtotal * tax_rate
                profit = (price - cost) * qty - discount
                total_amount += subtotal + tax
                total_profit += profit
                total_discount += discount
                total_tax += tax

            if not sale_items:
                messagebox.showerror("Input Error", "Add at least one product.")
                return

            try:
                # Insert into sales
                self.cursor.execute(
                    "INSERT INTO sales (customer_id, user_id, total_amount, total_profit, total_discount, sale_date) VALUES (%s, %s, %s, %s, %s, NOW())",
                    (customer_id, self.controller.current_user['user_id'], total_amount, total_profit, total_discount)
                )
                sale_id = self.cursor.lastrowid

                # Insert into sale_items and update stock
                for product_id, qty, price, cost, profit in sale_items:
                    self.cursor.execute(
                        "INSERT INTO sale_items (sale_id, product_id, quantity, price, profit) VALUES (%s, %s, %s, %s, %s)",
                        (sale_id, product_id, qty, price, profit)
                    )
                    self.cursor.execute(
                        "UPDATE products SET quantity = quantity - %s WHERE product_id = %s",
                        (qty, product_id)
                    )

                self.db.commit()
                self.load_sales()
                form.destroy()
                messagebox.showinfo("Success", "Sale recorded and stock updated.")
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Database Error", f"Failed to record sale: {e}")

        ttk.Button(form, text="Save Sale", command=save_sale).pack(pady=15)
        ttk.Button(form, text="Cancel", command=form.destroy).pack()

    def show_sale_items(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        sale_id = self.tree.item(selected[0], 'values')[0]
        self.cursor.execute("""
            SELECT p.name, si.quantity, si.price
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            WHERE si.sale_id = %s
        """, (sale_id,))
        items = self.cursor.fetchall()
        info = "\n".join([f"{item['name']}: {item['quantity']} x {item['price']}" for item in items])
        messagebox.showinfo("Sale Items", info if info else "No items found.")