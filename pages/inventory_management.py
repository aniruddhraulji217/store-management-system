import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui_framework import BasePage
import mysql.connector
import csv

class InventoryManagement(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.audit_log = []  # Simple in-memory audit log for demo
        self.low_stock_only = tk.BooleanVar(value=False)
        self.create_inventory_ui()
        self.load_inventory()

    def create_inventory_ui(self):
        header = ttk.Label(self.content, text="Inventory Management", font=('Segoe UI', 16, 'bold'))
        header.pack(pady=10)

        # Top controls
        top_frame = ttk.Frame(self.content)
        top_frame.pack(fill=tk.X, pady=5)

        ttk.Label(top_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", lambda e: self.load_inventory())

        ttk.Checkbutton(top_frame, text="Show Low Stock Only", variable=self.low_stock_only, command=self.load_inventory).pack(side=tk.LEFT, padx=10)

        ttk.Button(top_frame, text="Export CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=5)
        if self.controller.current_user['role'] == 'admin':
            ttk.Button(top_frame, text="Import CSV", command=self.import_csv).pack(side=tk.RIGHT, padx=5)
            ttk.Button(top_frame, text="Add Product", command=self.add_product).pack(side=tk.RIGHT, padx=5)

        # Inventory Table
        columns = ("ID", "Name", "Category", "Quantity", "Unit Price", "Cost Price", "Total Cost", "Total Price", "Supplier")
        self.tree = ttk.Treeview(self.content, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120 if col not in ("Name", "Total Cost", "Total Price") else 180)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tree.bind("<Double-1>", self.on_row_double_click)

        # Bottom controls
        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=5)
        if self.controller.current_user['role'] == 'admin':
            ttk.Button(btn_frame, text="Edit Product", command=self.edit_product).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_frame, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_frame, text="Manual Stock Adjustment", command=self.manual_adjust_stock).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_frame, text="View Audit Log", command=self.show_audit_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self.load_inventory).pack(side=tk.LEFT, padx=2)

        # Inventory summary
        self.summary_label = ttk.Label(self.content, text="", font=('Segoe UI', 11, 'italic'), foreground="#4a90e2")
        self.summary_label.pack(pady=(5, 0))

    def load_inventory(self):
        search = self.search_var.get().strip()
        low_stock = self.low_stock_only.get()
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = """
            SELECT p.product_id, p.name, p.category, p.quantity, p.price, p.cost_price, s.name as supplier
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        """
        params = ()
        where = []
        if search:
            where.append("(p.name LIKE %s OR p.category LIKE %s OR s.name LIKE %s)")
            like = f"%{search}%"
            params += (like, like, like)
        if low_stock:
            where.append("p.quantity < 10")
        if where:
            query += " WHERE " + " AND ".join(where)
        self.cursor.execute(query, params)
        total_value = 0
        total_items = 0
        for row in self.cursor.fetchall():
            value = row['quantity'] * row['price']
            total_cost = row['quantity'] * (row['cost_price'] if row['cost_price'] else 0)
            total_price = row['quantity'] * row['price']
            total_value += value
            total_items += row['quantity']
            self.tree.insert('', 'end', values=(
                row['product_id'], row['name'], row['category'], row['quantity'],
                row['price'], row['cost_price'], total_cost, total_price, row['supplier'] or ""))
        self.summary_label.config(text=f"Total Items: {total_items}    Inventory Value: ₹{total_value:,.2f}")

    def on_row_double_click(self, event):
        if self.controller.current_user['role'] == 'admin':
            self.edit_product()
        else:
            self.view_product_details()

    def add_product(self):
        form = tk.Toplevel(self)
        form.title("Add Product")
        form.geometry("400x500")
        # Fetch suppliers for dropdown
        self.cursor.execute("SELECT supplier_id, name FROM suppliers")
        suppliers = self.cursor.fetchall()
        supplier_dict = {s['name']: s['supplier_id'] for s in suppliers}
        supplier_names = list(supplier_dict.keys())
        # Fields
        fields = [
            ("Name", tk.StringVar()),
            ("Category", tk.StringVar()),
            ("Quantity", tk.StringVar()),
            ("Unit Price", tk.StringVar()),
            ("Cost Price", tk.StringVar()),
            ("Supplier", tk.StringVar(value=supplier_names[0] if supplier_names else "")),
            ("Description", tk.StringVar())
        ]
        for label, var in fields:
            ttk.Label(form, text=label).pack(pady=5)
            if label == "Supplier":
                ttk.Combobox(form, textvariable=var, values=supplier_names, state='readonly').pack(fill=tk.X, padx=10)
            else:
                ttk.Entry(form, textvariable=var).pack(fill=tk.X, padx=10)
        def save():
            name = fields[0][1].get().strip()
            category = fields[1][1].get().strip()
            try:
                quantity = int(fields[2][1].get())
                price = float(fields[3][1].get())
                cost_price = float(fields[4][1].get())
            except ValueError:
                messagebox.showerror("Input Error", "Quantity, Unit Price, and Cost Price must be valid numbers.")
                return
            supplier_name = fields[5][1].get()
            supplier_id = supplier_dict.get(supplier_name)
            description = fields[6][1].get().strip()
            if not (name and category and supplier_id and description):
                messagebox.showerror("Input Error", "All fields are required.")
                return
            if quantity < 0 or price < 0 or cost_price < 0:
                messagebox.showerror("Input Error", "Quantity and prices must be non-negative.")
                return
            try:
                self.cursor.execute(
                    "INSERT INTO products (name, category, quantity, price, cost_price, supplier_id, description) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, category, quantity, price, cost_price, supplier_id, description)
                )
                self.db.commit()
                self.audit_log.append(f"Added product: {name}")
                self.load_inventory()
                form.destroy()
                messagebox.showinfo("Success", "Product added.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add product: {e}")
        ttk.Button(form, text="Save", command=save).pack(pady=10)
        ttk.Button(form, text="Cancel", command=form.destroy).pack()

    def edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to edit.")
            return
        values = self.tree.item(selected[0], 'values')
        form = tk.Toplevel(self)
        form.title("Edit Product")
        form.geometry("400x500")
        # Fetch suppliers for dropdown
        self.cursor.execute("SELECT supplier_id, name FROM suppliers")
        suppliers = self.cursor.fetchall()
        supplier_dict = {s['name']: s['supplier_id'] for s in suppliers}
        supplier_names = list(supplier_dict.keys())
        # Fetch current description from DB
        self.cursor.execute("SELECT description FROM products WHERE product_id=%s", (values[0],))
        desc_row = self.cursor.fetchone()
        current_description = desc_row['description'] if desc_row else ""
        # Fields
        fields = [
            ("Name", tk.StringVar(value=values[1])),
            ("Category", tk.StringVar(value=values[2])),
            ("Quantity", tk.StringVar(value=values[3])),
            ("Unit Price", tk.StringVar(value=values[4])),
            ("Cost Price", tk.StringVar(value=values[5])),
            ("Supplier", tk.StringVar(value=values[8] if values[8] in supplier_names else (supplier_names[0] if supplier_names else ""))),
            ("Description", tk.StringVar(value=current_description))
        ]
        for label, var in fields:
            ttk.Label(form, text=label).pack(pady=5)
            if label == "Supplier":
                ttk.Combobox(form, textvariable=var, values=supplier_names, state='readonly').pack(fill=tk.X, padx=10)
            else:
                ttk.Entry(form, textvariable=var).pack(fill=tk.X, padx=10)
        def save():
            name = fields[0][1].get().strip()
            category = fields[1][1].get().strip()
            try:
                quantity = int(fields[2][1].get())
                price = float(fields[3][1].get())
                cost_price = float(fields[4][1].get())
            except ValueError:
                messagebox.showerror("Input Error", "Quantity, Unit Price, and Cost Price must be valid numbers.")
                return
            supplier_name = fields[5][1].get()
            supplier_id = supplier_dict.get(supplier_name)
            description = fields[6][1].get().strip()
            if not (name and category and supplier_id and description):
                messagebox.showerror("Input Error", "All fields are required.")
                return
            if quantity < 0 or price < 0 or cost_price < 0:
                messagebox.showerror("Input Error", "Quantity and prices must be non-negative.")
                return
            try:
                self.cursor.execute(
                    "UPDATE products SET name=%s, category=%s, quantity=%s, price=%s, cost_price=%s, supplier_id=%s, description=%s WHERE product_id=%s",
                    (name, category, quantity, price, cost_price, supplier_id, description, values[0])
                )
                self.db.commit()
                self.audit_log.append(f"Edited product: {name}")
                self.load_inventory()
                form.destroy()
                messagebox.showinfo("Success", "Product updated.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update product: {e}")
        ttk.Button(form, text="Save", command=save).pack(pady=10)
        ttk.Button(form, text="Cancel", command=form.destroy).pack()

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to delete.")
            return
        values = self.tree.item(selected[0], 'values')
        if messagebox.askyesno("Confirm Delete", f"Delete product '{values[1]}'?"):
            try:
                self.cursor.execute("DELETE FROM products WHERE product_id=%s", (values[0],))
                self.db.commit()
                self.audit_log.append(f"Deleted product: {values[1]}")
                self.load_inventory()
                messagebox.showinfo("Deleted", "Product deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {e}")

    def manual_adjust_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to adjust stock.")
            return
        product_id = self.tree.item(selected[0], 'values')[0]
        form = tk.Toplevel(self)
        form.title("Adjust Stock")
        form.geometry("300x200")
        qty_var = tk.StringVar()

        ttk.Label(form, text="Adjustment Amount (+/-):").pack(pady=10)
        ttk.Entry(form, textvariable=qty_var).pack(pady=5)

        def save_adjustment():
            try:
                adj = int(qty_var.get())
                self.cursor.execute(
                    "UPDATE products SET quantity = quantity + %s WHERE product_id = %s",
                    (adj, product_id)
                )
                self.db.commit()
                self.audit_log.append(f"Adjusted stock for product_id {product_id} by {adj}")
                self.load_inventory()
                form.destroy()
                messagebox.showinfo("Success", "Stock adjusted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to adjust stock: {e}")

        ttk.Button(form, text="Save", command=save_adjustment).pack(pady=10)
        ttk.Button(form, text="Cancel", command=form.destroy).pack()

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            with open(file_path, newline='', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.cursor.execute(
                        "INSERT INTO products (name, category, quantity, price) VALUES (%s, %s, %s, %s)",
                        (row["Name"], row["Category"], int(row["Quantity"]), float(row["Unit Price"]))
                    )
                self.db.commit()
            self.audit_log.append(f"Imported products from {file_path}")
            self.load_inventory()
            messagebox.showinfo("Imported", "Products imported successfully.")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {e}")

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            self.cursor.execute("SELECT product_id, name, category, quantity, price FROM products")
            rows = self.cursor.fetchall()
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Category", "Quantity", "Unit Price"])
                for row in rows:
                    writer.writerow([row['product_id'], row['name'], row['category'], row['quantity'], row['price']])
            self.audit_log.append(f"Exported inventory to {file_path}")
            messagebox.showinfo("Exported", "Inventory exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def show_audit_log(self):
        log_win = tk.Toplevel(self)
        log_win.title("Audit Log")
        log_win.geometry("400x400")
        text = tk.Text(log_win, wrap="word", bg="#f7f9fb", fg="#2c3e50", font=("Segoe UI", 10))
        text.pack(fill="both", expand=True)
        text.insert("end", "\n".join(self.audit_log) if self.audit_log else "No actions yet.")
        text.config(state="disabled")

    def view_product_details(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a product to view details.")
            return
        values = self.tree.item(selected[0], 'values')
        detail_win = tk.Toplevel(self)
        detail_win.title("Product Details")
        detail_win.geometry("350x300")
        fields = ["ID", "Name", "Category", "Quantity", "Unit Price", "Cost Price", "Total Cost", "Total Price", "Supplier"]
        for i, f in enumerate(fields):
            ttk.Label(detail_win, text=f"{f}:", font=('Segoe UI', 11, 'bold')).pack(anchor="w", padx=16, pady=(10 if i==0 else 2, 2))
            ttk.Label(detail_win, text=values[i], font=('Segoe UI', 11)).pack(anchor="w", padx=32)

    def check_stock_alerts(self):
        self.cursor.execute("SELECT name, quantity FROM products WHERE quantity < 10")
        low_stock = self.cursor.fetchall()
        if low_stock:
            alert = "\n".join([f"{p['name']}: {p['quantity']} left" for p in low_stock])
            messagebox.showwarning("Low Stock Alert", alert)