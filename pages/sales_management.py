# Add these imports at the top of the file
from fpdf import FPDF
import tempfile
import os

import tkinter as tk
from tkinter import ttk, messagebox
from gui_framework import BasePage
import mysql.connector
from datetime import datetime

class SalesManagement(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.cart_items = []
        self.total_var = tk.StringVar(value="0.00")
        self.discount_var = tk.StringVar(value="0.00")
        self.net_pay_var = tk.StringVar(value="0.00")
        
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Aniruddh@217",
                database="inventory_db"
            )
            self.cursor = self.db.cursor(dictionary=True)
            self.create_sales_ui()
            self.load_products()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            self.db = None

    def create_sales_ui(self):
        # Create a canvas and a frame for scrolling
        canvas = tk.Canvas(self.content)
        scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
    
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
    
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
    
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
        # Add your UI elements to scrollable_frame
        header = ttk.Label(scrollable_frame, text="Sales Management", font=('Helvetica', 16))
        header.pack(pady=10)
    
        # Product Search Section
        search_frame = ttk.Frame(scrollable_frame)  # Changed from self.content to scrollable_frame
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(search_frame, text="Product Name:").pack(side=tk.LEFT)
        product_search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=product_search_var).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=lambda: self.search_product(product_search_var.get())).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Show All", command=self.load_products).pack(side=tk.LEFT, padx=5)
    
        # Product List with selection capability
        columns = ("ID", "Name", "Price", "Quantity")
        self.tree = ttk.Treeview(scrollable_frame, columns=columns, show='headings', height=12, selectmode='browse')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add selection button
        select_button = ttk.Button(scrollable_frame, text="Add to Cart", command=self.add_to_cart)
        select_button.pack(pady=5)
    
        # Add a scrollbar to the product list
        scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=self.tree.yview)  # Changed from self.content to scrollable_frame
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
        # Cart Section with quantity controls
        cart_frame = ttk.LabelFrame(scrollable_frame, text="My Cart", padding=10)
        cart_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Cart Treeview with quantity adjustment buttons
        self.cart_tree = ttk.Treeview(cart_frame, columns=("Product", "Qty", "Price", "Total"), show='headings', height=5)
        for col in ("Product", "Qty", "Price", "Total"):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, anchor=tk.CENTER, width=100)
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Quantity adjustment buttons
        button_frame = ttk.Frame(cart_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="+", command=self.increase_quantity).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="-", command=self.decrease_quantity).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove", command=self.remove_from_cart).pack(side=tk.LEFT, padx=5)

        # Billing Section with validation
        billing_frame = ttk.LabelFrame(scrollable_frame, text="Customer Billing Area", padding=10)
        billing_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Customer details
        self.customer_name_var = tk.StringVar()
        self.contact_no_var = tk.StringVar()
        
        ttk.Label(billing_frame, text="Customer Name:").pack(anchor='w')
        ttk.Entry(billing_frame, textvariable=self.customer_name_var).pack(fill=tk.X, padx=5)
        
        ttk.Label(billing_frame, text="Contact No.:").pack(anchor='w')
        ttk.Entry(billing_frame, textvariable=self.contact_no_var).pack(fill=tk.X, padx=5)
        
        # Totals
        self.total_var = tk.StringVar(value="0.00")
        self.discount_var = tk.StringVar(value="0.00")
        self.net_pay_var = tk.StringVar(value="0.00")
        
        ttk.Label(billing_frame, text="Total Amount:").pack(anchor='w')
        ttk.Entry(billing_frame, textvariable=self.total_var, state='readonly').pack(fill=tk.X, padx=5)
        
        ttk.Label(billing_frame, text="Discount (%):").pack(anchor='w')
        ttk.Entry(billing_frame, textvariable=self.discount_var).pack(fill=tk.X, padx=5)
        
        ttk.Label(billing_frame, text="Net Pay:").pack(anchor='w')
        ttk.Entry(billing_frame, textvariable=self.net_pay_var, state='readonly').pack(fill=tk.X, padx=5)
        
        # Final buttons
        ttk.Button(billing_frame, text="Generate Bill", command=self.process_bill).pack(side=tk.LEFT, padx=5)
        ttk.Button(billing_frame, text="Clear All", command=self.clear_cart).pack(side=tk.LEFT, padx=5)

    def increase_quantity(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item from cart")
            return
            
        item = self.cart_tree.item(selected[0])
        values = item['values']
        product_id = next((x[0] for x in self.cart_items if x[1] == values[0]), None)
        
        # Check stock availability
        self.cursor.execute("SELECT quantity FROM products WHERE product_id = %s", (product_id,))
        result = self.cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Product not found in database")
            return
            
        stock = result['quantity']
        
        if int(values[1]) >= stock:  # Convert quantity to int for comparison
            messagebox.showwarning("Stock Limit", "Cannot add more than available stock")
            return
            
        # Update quantity and calculate new total as float
        new_qty = int(values[1]) + 1
        unit_price = float(values[2])
        new_total = new_qty * unit_price
        
        # Update treeview with properly formatted values
        self.cart_tree.item(selected[0], values=(
            values[0], 
            str(new_qty), 
            f"{unit_price:.2f}", 
            f"{new_total:.2f}"
        ))
        
        # Update cart_items list with numeric values
        for i, cart_item in enumerate(self.cart_items):
            if cart_item[0] == product_id:
                self.cart_items[i] = (product_id, cart_item[1], new_qty, unit_price, new_total)
                break
                
        self.update_totals()

    def update_totals(self):
        # Calculate total from cart items (already stored as numbers)
        total = sum(item[4] for item in self.cart_items)  # item[4] is already float
        
        # Update UI with formatted strings
        self.total_var.set(f"{total:.2f}")
        
        # Calculate discount and net pay
        try:
            discount = float(self.discount_var.get())
        except ValueError:
            discount = 0.0
        
        net_pay = total - (total * discount / 100)
        self.net_pay_var.set(f"{net_pay:.2f}")

    def decrease_quantity(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item from cart")
            return
            
        item = self.cart_tree.item(selected[0])
        values = item['values']
        
        if values[1] <= 1:
            self.remove_from_cart()
            return
            
        product_id = next((x[0] for x in self.cart_items if x[1] == values[0]), None)
        new_qty = values[1] - 1
        new_total = new_qty * values[2]
        
        self.cart_tree.item(selected[0], values=(values[0], new_qty, values[2], new_total))
        
        # Update cart_items list
        for i, cart_item in enumerate(self.cart_items):
            if cart_item[0] == product_id:
                self.cart_items[i] = (product_id, cart_item[1], new_qty, cart_item[3], new_total)
                break
                
        self.update_totals()

    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item from cart")
            return
            
        item = self.cart_tree.item(selected[0])
        product_name = item['values'][0]
        
        # Remove from cart_items list
        self.cart_items = [x for x in self.cart_items if x[1] != product_name]
        
        # Remove from treeview
        self.cart_tree.delete(selected[0])
        self.update_totals()

    def update_totals(self):
        total = 0.0
        for item in self.cart_items:
            # Ensure we're working with numeric values
            if isinstance(item[4], str):
                # Clean string by removing duplicate decimal points
                clean_value = item[4].replace('.', '', item[4].count('.')-1)
                total += float(clean_value)
            else:
                total += float(item[4])
        
        self.total_var.set(f"{total:.2f}")
        
        try:
            discount = float(self.discount_var.get())
        except ValueError:
            discount = 0.0
        
        net_pay = total - (total * discount / 100)
        self.net_pay_var.set(f"{net_pay:.2f}")

    def process_bill(self):
        if not self.cart_items:
            messagebox.showwarning("Empty Cart", "Please add items to cart before billing")
            return
            
        customer_name = self.customer_name_var.get().strip()
        if not customer_name:
            messagebox.showwarning("Missing Info", "Please enter customer name")
            return
            
        try:
            # Start transaction
            if self.db.in_transaction:
                self.db.rollback()
            self.db.start_transaction()
            
            # Create/update customer record
            self.cursor.execute(
                "INSERT INTO customers (name) VALUES (%s) ON DUPLICATE KEY UPDATE name=VALUES(name)",
                (customer_name,)
            )
            customer_id = self.cursor.lastrowid
            
            # Calculate totals
            total_amount = sum(item[4] for item in self.cart_items)  # item[4] is total price
            discount = float(self.discount_var.get()) if self.discount_var.get() else 0.0
            net_amount = total_amount - (total_amount * discount / 100)
            
            # Create sale record
            self.cursor.execute(
                "INSERT INTO sales (customer_id, user_id, total_amount, sale_date, discount, net_amount) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (customer_id, self.controller.current_user['user_id'], 
                 total_amount, datetime.now(), discount, net_amount)
            )
            sale_id = self.cursor.lastrowid
            
            # Add sale items
            for item in self.cart_items:
                product_id, name, qty, unit_price, total_price = item
                self.cursor.execute(
                    "INSERT INTO sale_items (sale_id, product_id, quantity, price) "  # Changed from sales_item to sale_item
                    "VALUES (%s, %s, %s, %s)",
                    (sale_id, product_id, qty, unit_price)
                )
                
                # Update product stock
                self.cursor.execute(
                    "UPDATE products SET quantity = quantity - %s WHERE product_id = %s",
                    (qty, product_id)
                )
                
            self.db.commit()
            
            # Generate and show bill
            self.generate_and_show_bill(sale_id, customer_name, total_amount, discount, net_amount)
            
            messagebox.showinfo("Success", f"Bill #{sale_id} generated successfully!")
            self.clear_cart()
            
        except Exception as e:
            if self.db.in_transaction:
                self.db.rollback()
            messagebox.showerror("Error", f"Failed to process bill: {str(e)}")

    def load_products(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.cursor.execute("""
            SELECT product_id, name, price, quantity
            FROM products
            ORDER BY name ASC
        """)
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['product_id'], row['name'], row['price'], row['quantity']))

    def search_product(self, product_name):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.cursor.execute("""
            SELECT product_id, name, price, quantity
            FROM products
            WHERE name LIKE %s
            ORDER BY name ASC
        """, ('%' + product_name + '%',))
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['product_id'], row['name'], row['price'], row['quantity']))

    def add_to_cart(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a product first")
            return
        
        product_id, name, price, quantity = self.tree.item(selected_item[0], 'values')
        
        # Convert string values to proper types
        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Invalid product data")
            return
        
        # Check if product already in cart
        for item in self.cart_items:
            if item[0] == product_id:
                messagebox.showinfo("Info", f"{name} is already in your cart")
                return
        
        # Check stock availability
        if quantity <= 0:
            messagebox.showerror("Stock Error", f"Product {name} is out of stock")
            return
        
        # Add to cart
        # Ensure numeric values are stored in cart_items
        self.cart_items.append((
            product_id, 
            name, 
            1,  # quantity as int
            float(price),  # unit price as float
            float(price)   # total as float
        ))
        self.cart_tree.insert('', 'end', values=(
            name, 
            "1", 
            f"{float(price):.2f}", 
            f"{float(price):.2f}"
        ))
        self.update_totals()

    def update_totals(self):
        # Calculate total from cart items
        total = 0.0
        for item in self.cart_items:
            total += float(item[4])  # item[4] is the total price for each item
        
        self.total_var.set(f"{total:.2f}")
        
        # Calculate discount and net pay
        try:
            discount = float(self.discount_var.get())
        except ValueError:
            discount = 0.0
        
        net_pay = total - (total * discount / 100)
        self.net_pay_var.set(f"{net_pay:.2f}")

    def clear_cart(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        self.cart_items.clear()
        self.total_var.set("0.00")  # Changed from total_var to self.total_var
        self.discount_var.set("0.00")  # Changed from discount_var to self.discount_var
        self.net_pay_var.set("0.00")  # Changed from net_pay_var to self.net_pay_var

    def generate_and_show_bill(self, bill_id, customer_name, total, discount, net_amount):
        # Create a new window for bill display
        bill_window = tk.Toplevel(self.master)
        bill_window.title(f"Bill #{bill_id}")
        bill_window.geometry("600x800")
        
        # Bill header
        ttk.Label(bill_window, text="STORE INVOICE", font=('Helvetica', 16, 'bold')).pack(pady=10)
        ttk.Label(bill_window, text=f"Bill #: {bill_id}").pack()
        ttk.Label(bill_window, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}").pack()
        ttk.Label(bill_window, text=f"Customer: {customer_name}").pack(pady=10)
        
        # Items table
        columns = ("Product", "Qty", "Price", "Total")
        tree = ttk.Treeview(bill_window, columns=columns, show='headings', height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Add items to the bill
        for item in self.cart_items:
            tree.insert('', 'end', values=(item[1], item[2], f"{item[3]:.2f}", f"{item[4]:.2f}"))
        
        # Summary section
        summary_frame = ttk.Frame(bill_window)
        summary_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(summary_frame, text="Subtotal:").grid(row=0, column=0, sticky=tk.E)
        ttk.Label(summary_frame, text=f"{total:.2f}").grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(summary_frame, text=f"Discount ({discount}%):").grid(row=1, column=0, sticky=tk.E)
        ttk.Label(summary_frame, text=f"{(total * discount / 100):.2f}").grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(summary_frame, text="Total:", font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky=tk.E)
        ttk.Label(summary_frame, text=f"{net_amount:.2f}", font=('Helvetica', 10, 'bold')).grid(row=2, column=1, sticky=tk.W)
        
        # Action buttons
        btn_frame = ttk.Frame(bill_window)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Download PDF", 
                  command=lambda: self.generate_pdf(bill_id, customer_name, total, discount, net_amount)).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(btn_frame, text="Send via SMS", 
                  command=lambda: self.send_sms(bill_id, customer_name, net_amount)).pack(side=tk.LEFT, padx=10)

    def generate_pdf(self, bill_id, customer_name, total, discount, net_amount):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Bill header
        pdf.cell(200, 10, txt="STORE INVOICE", ln=1, align='C')
        pdf.cell(200, 10, txt=f"Bill #: {bill_id}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"Customer: {customer_name}", ln=1, align='L')
        
        # Items table header
        pdf.cell(60, 10, txt="Product", border=1)
        pdf.cell(30, 10, txt="Qty", border=1)
        pdf.cell(40, 10, txt="Price", border=1)
        pdf.cell(40, 10, txt="Total", border=1, ln=1)
        
        # Items
        for item in self.cart_items:
            pdf.cell(60, 10, txt=item[1], border=1)
            pdf.cell(30, 10, txt=str(item[2]), border=1)
            pdf.cell(40, 10, txt=f"{item[3]:.2f}", border=1)
            pdf.cell(40, 10, txt=f"{item[4]:.2f}", border=1, ln=1)
        
        # Summary
        pdf.cell(130, 10, txt="Subtotal:", border=1)
        pdf.cell(40, 10, txt=f"{total:.2f}", border=1, ln=1)
        
        pdf.cell(130, 10, txt=f"Discount ({discount}%):", border=1)
        pdf.cell(40, 10, txt=f"{(total * discount / 100):.2f}", border=1, ln=1)
        
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(130, 10, txt="Total:", border=1)
        pdf.cell(40, 10, txt=f"{net_amount:.2f}", border=1, ln=1)
        
        # Save PDF to temp file and open
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"bill_{bill_id}.pdf")
        pdf.output(pdf_path)
        
        os.startfile(pdf_path)

    def send_sms(self, bill_id, customer_name, net_amount):
        # This is a placeholder - you'll need to integrate with an SMS gateway API
        contact_no = self.contact_no_var.get().strip()
        
        if not contact_no:
            messagebox.showwarning("Warning", "Contact number is required to send SMS")
            return
            
        try:
            # In a real implementation, you would call your SMS API here
            # For example: sms_api.send(contact_no, f"Bill #{bill_id} for {customer_name}: Total Rs.{net_amount:.2f}")
            
            messagebox.showinfo("SMS Sent", 
                              f"SMS would be sent to {contact_no}\n"
                              f"Message: Bill #{bill_id} for {customer_name}: Total Rs.{net_amount:.2f}")
        except Exception as e:
            messagebox.showerror("SMS Error", f"Failed to send SMS: {str(e)}")