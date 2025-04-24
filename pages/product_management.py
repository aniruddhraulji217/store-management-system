import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui_framework import BasePage
import mysql.connector
import csv

class ProductManagement(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.create_product_ui()
        self.load_products()

    def create_product_ui(self):
        # Header and search
        header_frame = ttk.Frame(self.content)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame, text="Product Management", font=('Helvetica', 16)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Search:").pack(side=tk.LEFT, padx=(30, 2))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(header_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", lambda e: self.load_products())

        # Treeview for products
        columns = ("ID", "Name", "Description", "Price", "Quantity", "Supplier")
        self.tree = ttk.Treeview(self.content, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120 if col != "Description" else 200)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add", width=10, command=self.add_product).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Edit", width=10, command=self.edit_product).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", width=10, command=self.delete_product).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Export CSV", width=12, command=self.export_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh", width=10, command=self.load_products).pack(side=tk.LEFT, padx=2)

    def load_products(self):
        search = self.search_var.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = """
            SELECT p.product_id, p.name, p.description, p.price, p.quantity, s.name AS supplier
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        """
        params = ()
        if search:
            query += " WHERE p.name LIKE %s OR p.description LIKE %s OR s.name LIKE %s"
            like = f"%{search}%"
            params = (like, like, like)
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['product_id'], row['name'], row['description'], row['price'], row['quantity'], row['supplier']))

    def add_product(self):
        self.open_product_form("Add Product")

    def edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to edit.")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_product_form("Edit Product", values)

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product to delete.")
            return
        product_id = self.tree.item(selected[0], 'values')[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM products WHERE product_id=%s", (product_id,))
                self.db.commit()
                self.load_products()
                messagebox.showinfo("Deleted", "Product deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {e}")

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(("ID", "Name", "Description", "Price", "Quantity", "Supplier"))
                for row_id in self.tree.get_children():
                    writer.writerow(self.tree.item(row_id)['values'])
            messagebox.showinfo("Exported", f"Products exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def open_product_form(self, title, product=None):
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry("350x500")
        form.resizable(False, False)

        name_var = tk.StringVar(value=product[1] if product else "")
        desc_var = tk.StringVar(value=product[2] if product else "")
        price_var = tk.StringVar(value=product[3] if product else "")
        # Remove quantity from here; handled via purchase
        # quantity_var = tk.StringVar(value=product[4] if product else "")

        self.cursor.execute("SELECT supplier_id, name FROM suppliers")
        suppliers = self.cursor.fetchall()
        supplier_dict = {s['name']: s['supplier_id'] for s in suppliers}
        supplier_names = list(supplier_dict.keys())

        supplier_var = tk.StringVar(value=product[5] if product else (supplier_names[0] if supplier_names else ""))

        ttk.Label(form, text="Name:").pack(anchor='w', padx=20, pady=(20, 2))
        name_entry = ttk.Entry(form, textvariable=name_var)
        name_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Description:").pack(anchor='w', padx=20, pady=(10, 2))
        desc_entry = ttk.Entry(form, textvariable=desc_var)
        desc_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Unit Price:").pack(anchor='w', padx=20, pady=(10, 2))
        price_entry = ttk.Entry(form, textvariable=price_var)
        price_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Supplier:").pack(anchor='w', padx=20, pady=(10, 2))
        supplier_combo = ttk.Combobox(form, textvariable=supplier_var, values=supplier_names, state='readonly')
        supplier_combo.pack(fill=tk.X, padx=20)

        # Prompt for initial stock only when adding a new product
        if not product:
            ttk.Label(form, text="Initial Quantity:").pack(anchor='w', padx=20, pady=(10, 2))
            initial_qty_var = tk.StringVar(value="0")
            initial_qty_entry = ttk.Entry(form, textvariable=initial_qty_var)
            initial_qty_entry.pack(fill=tk.X, padx=20)

        def save():
            name = name_var.get().strip()
            desc = desc_var.get().strip()
            price = price_var.get().strip()
            supplier_name = supplier_var.get()
            supplier_id = supplier_dict.get(supplier_name)

            if not all([name, price, supplier_id]):
                messagebox.showerror("Input Error", "Please fill all required fields.")
                return

            try:
                price_float = float(price)
            except ValueError:
                messagebox.showerror("Input Error", "Price must be a number.")
                return

            try:
                if product:
                    self.cursor.execute("""
                        UPDATE products SET name=%s, description=%s, price=%s, supplier_id=%s
                        WHERE product_id=%s
                    """, (name, desc, price_float, supplier_id, product[0]))
                else:
                    # Insert product
                    self.cursor.execute("""
                        INSERT INTO products (name, description, price, supplier_id)
                        VALUES (%s, %s, %s, %s)
                    """, (name, desc, price_float, supplier_id))
                    product_id = self.cursor.lastrowid

                    # Prompt for initial purchase if quantity > 0
                    initial_qty = int(initial_qty_var.get())
                    if initial_qty > 0:
                        # Create a purchase record
                        self.cursor.execute(
                            "INSERT INTO purchases (supplier_id, date, total_amount) VALUES (%s, NOW(), %s)",
                            (supplier_id, price_float * initial_qty)
                        )
                        purchase_id = self.cursor.lastrowid
                        self.cursor.execute(
                            "INSERT INTO purchase_items (purchase_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                            (purchase_id, product_id, initial_qty, price_float)
                        )
                        # Update inventory stock
                        self.cursor.execute(
                            "UPDATE products SET quantity = quantity + %s WHERE product_id = %s",
                            (initial_qty, product_id)
                        )
                self.db.commit()
                self.load_products()
                form.destroy()
                messagebox.showinfo("Success", "Product saved successfully.")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save product: {e}")

        btn_frame = ttk.Frame(form)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Save", command=save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=form.destroy).pack(side=tk.LEFT, padx=10)

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
                self.load_products()
                form.destroy()
                messagebox.showinfo("Success", "Stock adjusted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to adjust stock: {e}")

        ttk.Button(form, text="Save", command=save_adjustment).pack(pady=10)
        ttk.Button(form, text="Cancel", command=form.destroy).pack()

