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
        self.create_inventory_ui()
        self.load_inventory()

    def create_inventory_ui(self):
        header = ttk.Label(self.content, text="Inventory Management", font=('Helvetica', 16))
        header.pack(pady=10)

        search_frame = ttk.Frame(self.content)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", lambda e: self.load_inventory())

        ttk.Button(search_frame, text="Export CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=5)

        columns = ("ID", "Name", "Category", "Quantity", "Unit Price")
        self.tree = ttk.Treeview(self.content, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120 if col != "Name" else 180)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=5)
        if self.controller.current_user['role'] == 'admin':
            ttk.Button(btn_frame, text="Manual Stock Adjustment", command=self.manual_adjust_stock).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self.load_inventory).pack(side=tk.LEFT, padx=2)

    def load_inventory(self):
        search = self.search_var.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = "SELECT product_id, name, category, quantity, price FROM products"
        params = ()
        if search:
            query += " WHERE name LIKE %s OR category LIKE %s"
            like = f"%{search}%"
            params = (like, like)
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['product_id'], row['name'], row['category'], row['quantity'], row['price']))

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
                self.load_inventory()
                form.destroy()
                messagebox.showinfo("Success", "Stock adjusted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to adjust stock: {e}")

        ttk.Button(form, text="Save", command=save_adjustment).pack(pady=10)
        ttk.Button(form, text="Cancel", command=form.destroy).pack()

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
            messagebox.showinfo("Exported", "Inventory exported successfully.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def check_stock_alerts(self):
        self.cursor.execute("SELECT name, quantity FROM products WHERE quantity < 10")
        low_stock = self.cursor.fetchall()
        if low_stock:
            alert = "\n".join([f"{p['name']}: {p['quantity']} left" for p in low_stock])
            messagebox.showwarning("Low Stock Alert", alert)