import tkinter as tk
from tkinter import ttk
from gui_framework import BasePage
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AdminDashboard(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.db_connection = None
        self.cursor = None
        self.setup_db()  # Initialize database connection
        self.create_content()

    def setup_db(self):
        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Aniruddh@217",
                database="inventory_db"
            )
            self.cursor = self.db_connection.cursor(dictionary=True)
        except Exception as e:
            print(f"Database connection error: {e}")
            self.db_connection = None
            self.cursor = None

    def create_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        # Header Frame
        header = ttk.Label(self.content, text="AI-Powered Admin Command Center", font=("Helvetica", 20, "bold"))
        header.pack(pady=20)

        # Grid Layout Frame
        grid_frame = ttk.Frame(self.content)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        grid_frame.columnconfigure((0, 1), weight=1)

        # Business Pulse Section
        pulse = ttk.LabelFrame(grid_frame, text="Business Pulse", padding=15)
        pulse.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.metrics = {
            "revenue": ttk.Label(pulse, text="30-Day Revenue: ₹-"),
            "inventory": ttk.Label(pulse, text="Inventory Value: ₹-"),
            "low_stock": ttk.Label(pulse, text="Low Stock Items: -"),
            "customers": ttk.Label(pulse, text="New Customers: -")
        }
        for label in self.metrics.values():
            label.pack(anchor="w", pady=5)

        # Predictive Analytics Panel (placeholder)
        prediction_frame = ttk.LabelFrame(grid_frame, text="Predictive Analytics (Coming Soon)", padding=15)
        prediction_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ttk.Label(prediction_frame, text="AI will provide restock predictions, sales trends, etc.").pack()

        # Chart Frame
        chart_frame = ttk.LabelFrame(self.content, text="Interactive Reports", padding=15)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.plot_sales_trend(chart_frame)

        # Refresh + Export buttons
        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Refresh", command=self.update_stats).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Export Report (Future)").pack(side=tk.LEFT)

        self.update_stats()

    def plot_sales_trend(self, parent):
        try:
            if not self.cursor:
                self.setup_db()
                if not self.cursor:
                    return

            self.cursor.execute("""
                SELECT DATE(sale_date) as date, SUM(total_amount) as revenue 
                FROM sales 
                WHERE sale_date >= NOW() - INTERVAL 7 DAY
                GROUP BY DATE(sale_date)
                ORDER BY date ASC
            """)
            data = self.cursor.fetchall()
            dates = [row['date'].strftime('%b %d') for row in data]
            revenues = [row['revenue'] for row in data]

            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(dates, revenues, marker='o', linestyle='-', color='royalblue')
            ax.set_title('7-Day Sales Trend')
            ax.set_ylabel('Revenue (₹)')
            ax.grid(True)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Chart error: {e}")

    def update_stats(self):
        try:
            if not self.cursor:
                self.setup_db()
                if not self.cursor:
                    for key in self.metrics:
                        self.metrics[key].config(text=f"{key.replace('_',' ').title()}: Error")
                    return

            self.cursor.execute("SELECT SUM(total_amount) as revenue FROM sales WHERE sale_date >= NOW() - INTERVAL 30 DAY")
            revenue = self.cursor.fetchone()['revenue'] or 0
            self.metrics['revenue'].config(text=f"30-Day Revenue: ₹{revenue:,.2f}")

            self.cursor.execute("SELECT SUM(quantity * price) as value FROM products")
            inventory = self.cursor.fetchone()['value'] or 0
            self.metrics['inventory'].config(text=f"Inventory Value: ₹{inventory:,.2f}")

            self.cursor.execute("SELECT COUNT(*) as low FROM products WHERE quantity < 10")
            low_stock = self.cursor.fetchone()['low']
            self.metrics['low_stock'].config(text=f"Low Stock Items: {low_stock}")

            # Modified to remove customer date filtering since there's no created_at column
            self.cursor.execute("SELECT COUNT(*) as customers FROM customers")
            customers = self.cursor.fetchone()['customers']
            self.metrics['customers'].config(text=f"Total Customers: {customers}")

        except Exception as e:
            print(f"Error updating metrics: {e}")
            for key in self.metrics:
                self.metrics[key].config(text=f"{key.replace('_',' ').title()}: Error")

    def __del__(self):
        if self.db_connection and self.db_connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.db_connection.close()
