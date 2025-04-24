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
        # Only show Record Purchase for admin
        if getattr(self.controller, "current_user", {}).get("role") == "admin":
            ttk.Button(btn_frame, text="Record Purchase", command=self.record_purchase).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_purchases).pack(side=tk.LEFT, padx=5)

        columns = ("Purchase ID", "Supplier", "Date", "Total Amount")
        self.tree = ttk.Treeview(self.content, columns=columns, show='headings', height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree.bind("<Double-1>", self.show_purchase_items)

    def record_purchase(self):
        form = tk.Toplevel(self)
        form.title("Purchase Products")
        form.geometry("600x750")
        form.resizable(False, False)

        # --- Add scrollable frame setup ---
        canvas = tk.Canvas(form, borderwidth=0, background="#f0f0f0", height=700)
        scroll_frame = ttk.Frame(canvas)
        vscrollbar = ttk.Scrollbar(form, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscrollbar.set)

        vscrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scroll_frame.bind("<Configure>", on_frame_configure)

        # --- Use scroll_frame instead of form for widgets below ---
        self.cursor.execute("SELECT supplier_id, name FROM suppliers")
        suppliers = self.cursor.fetchall()
        supplier_dict = {s['name']: s['supplier_id'] for s in suppliers}
        supplier_names = list(supplier_dict.keys())
        supplier_var = tk.StringVar(value=supplier_names[0] if supplier_names else "")

        ttk.Label(scroll_frame, text="Supplier:").pack(anchor='w', padx=20, pady=(20, 2))
        supplier_combo = ttk.Combobox(scroll_frame, textvariable=supplier_var, values=supplier_names, state='readonly')
        supplier_combo.pack(fill=tk.X, padx=20)

        def add_supplier_popup():
            popup = tk.Toplevel(form)
            popup.title("Add New Supplier")
            popup.geometry("350x300")
            popup.resizable(False, False)

            name_var = tk.StringVar()
            contact_var = tk.StringVar()
            email_var = tk.StringVar()
            address_var = tk.StringVar()

            ttk.Label(popup, text="Name:").pack(anchor='w', padx=10, pady=(10, 2))
            ttk.Entry(popup, textvariable=name_var).pack(fill=tk.X, padx=10)
            ttk.Label(popup, text="Contact:").pack(anchor='w', padx=10, pady=(10, 2))
            ttk.Entry(popup, textvariable=contact_var).pack(fill=tk.X, padx=10)
            ttk.Label(popup, text="Email:").pack(anchor='w', padx=10, pady=(10, 2))
            ttk.Entry(popup, textvariable=email_var).pack(fill=tk.X, padx=10)
            ttk.Label(popup, text="Address:").pack(anchor='w', padx=10, pady=(10, 2))
            ttk.Entry(popup, textvariable=address_var).pack(fill=tk.X, padx=10)

            def save_supplier():
                name = name_var.get().strip()
                contact = contact_var.get().strip()
                email = email_var.get().strip()
                address = address_var.get().strip()
                if not name:
                    messagebox.showerror("Input Error", "Supplier name is required.", parent=popup)
                    return
                try:
                    self.cursor.execute(
                        "INSERT INTO suppliers (name, contact, email, address) VALUES (%s, %s, %s, %s)",
                        (name, contact, email, address)
                    )
                    self.db.commit()
                    supplier_dict[name] = self.cursor.lastrowid
                    supplier_names.append(name)
                    supplier_combo['values'] = supplier_names
                    supplier_var.set(name)
                    popup.destroy()
                except Exception as e:
                    self.db.rollback()
                    messagebox.showerror("Database Error", f"Failed to add supplier: {e}", parent=popup)

            ttk.Button(popup, text="Save Supplier", command=save_supplier).pack(pady=10)
            ttk.Button(popup, text="Cancel", command=popup.destroy).pack()

        ttk.Button(scroll_frame, text="Add New Supplier", command=add_supplier_popup).pack(pady=5)

        # Product selection or add new product
        self.cursor.execute("SELECT product_id, name FROM products")
        products = self.cursor.fetchall()
        product_dict = {p['name']: p['product_id'] for p in products}
        product_names = list(product_dict.keys())

        items = []

        def add_item_row():
            row_frame = ttk.Frame(scroll_frame)
            row_frame.pack(fill=tk.X, padx=20, pady=5)
            prod_var = tk.StringVar(value=product_names[0] if product_names else "")
            is_new_var = tk.BooleanVar(value=False)
            ttk.Combobox(row_frame, textvariable=prod_var, values=product_names, state='readonly', width=15).pack(side=tk.LEFT)
            ttk.Checkbutton(row_frame, text="New Product", variable=is_new_var).pack(side=tk.LEFT, padx=5)

            # For new product details
            name_var = tk.StringVar()
            desc_var = tk.StringVar()
            price_var = tk.StringVar()
            quantity_var = tk.StringVar(value="1")
            category_var = tk.StringVar()
            cost_price_var = tk.StringVar()
            supplier_id_var = tk.StringVar()
            # Only show these if is_new_var is True
            def toggle_new_fields(*args):
                if is_new_var.get():
                    new_fields_frame.pack(fill=tk.X, padx=10, pady=2)
                else:
                    new_fields_frame.pack_forget()
            is_new_var.trace_add('write', toggle_new_fields)

            new_fields_frame = ttk.Frame(row_frame)
            ttk.Label(new_fields_frame, text="Name:").pack(anchor='w')
            ttk.Entry(new_fields_frame, textvariable=name_var).pack(fill=tk.X)
            ttk.Label(new_fields_frame, text="Description:").pack(anchor='w')
            ttk.Entry(new_fields_frame, textvariable=desc_var).pack(fill=tk.X)
            ttk.Label(new_fields_frame, text="Category:").pack(anchor='w')
            ttk.Entry(new_fields_frame, textvariable=category_var).pack(fill=tk.X)
            ttk.Label(new_fields_frame, text="Selling Price:").pack(anchor='w')
            ttk.Entry(new_fields_frame, textvariable=price_var).pack(fill=tk.X)
            ttk.Label(new_fields_frame, text="Cost Price:").pack(anchor='w')
            ttk.Entry(new_fields_frame, textvariable=cost_price_var).pack(fill=tk.X)
            ttk.Label(new_fields_frame, text="Quantity:").pack(anchor='w')
            ttk.Entry(new_fields_frame, textvariable=quantity_var).pack(fill=tk.X)

            items.append({
                "prod_var": prod_var,
                "is_new_var": is_new_var,
                "name_var": name_var,
                "desc_var": desc_var,
                "price_var": price_var,
                "quantity_var": quantity_var,
                "category_var": category_var,
                "cost_price_var": cost_price_var
            })

        ttk.Label(scroll_frame, text="Products (Select or Add New):").pack(anchor='w', padx=20, pady=(10, 2))
        for _ in range(1):
            add_item_row()

        ttk.Button(scroll_frame, text="Add Another Product", command=add_item_row).pack(pady=5)

        def save_purchase():
            supplier_name = supplier_var.get()
            supplier_id = supplier_dict.get(supplier_name)
            if not supplier_id:
                messagebox.showerror("Input Error", "Please select a supplier.")
                return

            purchase_items = []
            total_amount = 0.0
            total_cost = 0.0
            for item in items:
                if item["is_new_var"].get():
                    # Validate all new product fields
                    name = item["name_var"].get().strip()
                    desc = item["desc_var"].get().strip()
                    category = item["category_var"].get().strip()
                    try:
                        price = float(item["price_var"].get())
                        cost_price = float(item["cost_price_var"].get())
                        quantity = int(item["quantity_var"].get())
                    except ValueError:
                        messagebox.showerror("Input Error", "Invalid price, cost price, or quantity for new product.")
                        return
                    if not name or price < 0 or cost_price < 0 or quantity <= 0:
                        messagebox.showerror("Input Error", "All product fields are required and must be valid.")
                        return
                    # Insert new product
                    try:
                        self.cursor.execute(
                            "INSERT INTO products (name, description, price, quantity, supplier_id, category, cost_price) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (name, desc, price, quantity, supplier_id, category, cost_price)
                        )
                        self.db.commit()
                        product_id = self.cursor.lastrowid
                        product_dict[name] = product_id
                        product_names.append(name)
                    except Exception as e:
                        self.db.rollback()
                        messagebox.showerror("Database Error", f"Failed to add product: {e}")
                        return
                else:
                    prod_name = item["prod_var"].get()
                    product_id = product_dict.get(prod_name)
                    if not product_id:
                        messagebox.showerror("Input Error", "Invalid product selected.")
                        return
                    try:
                        quantity = int(item["quantity_var"].get())
                        cost_price = float(item["cost_price_var"].get())
                        price = None  # Not used for existing product
                    except ValueError:
                        messagebox.showerror("Input Error", "Invalid quantity or cost price for existing product.")
                        return
                    if quantity <= 0 or cost_price < 0:
                        messagebox.showerror("Input Error", "Quantity and cost price must be valid.")
                        return

                # For both new and existing products
                purchase_items.append((product_id, quantity, cost_price))
                total_amount += quantity * (price if price is not None else cost_price)
                total_cost += quantity * cost_price

            if not purchase_items:
                messagebox.showerror("Input Error", "Add at least one product.")
                return

            try:
                self.db.start_transaction()
                self.cursor.execute(
                    "INSERT INTO purchases (supplier_id, date, total_amount, total_cost) VALUES (%s, NOW(), %s, %s)",
                    (supplier_id, total_amount, total_cost)
                )
                purchase_id = self.cursor.lastrowid

                for product_id, qty, cost_price in purchase_items:
                    self.cursor.execute(
                        "INSERT INTO purchase_items (purchase_id, product_id, quantity, cost_price) VALUES (%s, %s, %s, %s)",
                        (purchase_id, product_id, qty, cost_price)
                    )
                    self.cursor.execute(
                        "UPDATE products SET quantity = quantity + %s, cost_price = %s WHERE product_id = %s",
                        (qty, cost_price, product_id)
                    )

                self.db.commit()
                self.load_purchases()
                form.destroy()
                messagebox.showinfo("Success", "Purchase recorded and stock updated.")
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Database Error", f"Failed to record purchase: {e}")

        ttk.Button(scroll_frame, text="Save Purchase", command=save_purchase).pack(pady=15)
        ttk.Button(scroll_frame, text="Cancel", command=form.destroy).pack()

    def load_purchases(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.cursor.execute("""
            SELECT p.purchase_id, s.name AS supplier, p.date, p.total_amount, p.total_cost
            FROM purchases p
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            ORDER BY p.date DESC
        """)
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['purchase_id'], row['supplier'], row['date'], row['total_amount'], row['total_cost']))

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