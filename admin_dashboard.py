import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from gui_framework import BasePage
import mysql.connector
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import openai

# Set your OpenAI API key here
OPENAI_API_KEY = "sk-..."  # Replace with your actual key

class AdminDashboard(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.db_connection = None
        self.cursor = None
        self.setup_db()
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

        # Header
        header = ttk.Label(self.content, text="🧑‍💼 Admin Command Center", font=("Segoe UI", 22, "bold"), foreground="#4a90e2")
        header.pack(pady=10)

        # Metrics Cards Frame
        cards_frame = ttk.Frame(self.content)
        cards_frame.pack(fill=tk.X, padx=10, pady=5)
        self.metric_cards = []
        card_titles = [
            ("💰 Revenue (30d)", "#27ae60"),
            ("📦 Inventory Value", "#2980b9"),
            ("⚠️ Low Stock", "#e67e22"),
            ("👥 Customers", "#8e44ad"),
            ("🏆 Top Product", "#f39c12"),
            ("⭐ Top Customer", "#16a085"),
            ("💹 Profit (30d)", "#e74c3c"),
            ("🎁 Discounts (30d)", "#9b59b6")
        ]
        for i, (title, color) in enumerate(card_titles):
            frame = tk.Frame(cards_frame, bg=color, bd=0, relief=tk.RIDGE)
            frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6, ipadx=8, ipady=8)
            lbl = tk.Label(frame, text=title, font=("Segoe UI", 12, "bold"), bg=color, fg="white")
            lbl.pack(anchor="w", padx=8, pady=(4,0))
            val = tk.Label(frame, text="-", font=("Segoe UI", 16, "bold"), bg=color, fg="white")
            val.pack(anchor="w", padx=8, pady=(0,4))
            self.metric_cards.append(val)

        # Charts Frame
        charts_frame = ttk.Frame(self.content)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        charts_frame.columnconfigure((0,1), weight=1)
        charts_frame.rowconfigure((0,1), weight=1)

        # Top 5 Products Bar Chart
        top_products_frame = ttk.LabelFrame(charts_frame, text="Top 5 Products (30d)", padding=8)
        top_products_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.plot_top_products(top_products_frame)

        # Quick Actions
        right_frame = ttk.Frame(charts_frame)
        right_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=8, pady=8)
        right_frame.columnconfigure(0, weight=1)

        # Quick Actions
        qa_frame = ttk.LabelFrame(right_frame, text="Quick Actions", padding=8)
        qa_frame.pack(fill=tk.X, pady=(0,8))

        def open_inventory_add_product():
            inventory_page = self.controller.pages.get("Inventory")
            if inventory_page is None:
                messagebox.showerror("Error", "Inventory page is not loaded or available.")
                return
            add_product_func = getattr(inventory_page, "add_product", None)
            if callable(add_product_func):
                add_product_func()
            else:
                messagebox.showerror("Error", "The Inventory page does not support adding products.")

        ttk.Button(qa_frame, text="Add Product", command=open_inventory_add_product).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="Add Purchase", command=lambda: self.controller.show_page("PurchaseManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="View Reports", command=lambda: self.controller.show_page("Reports")).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="Low Stock", command=self.show_low_stock).pack(fill=tk.X, pady=2)

        # AI Suggestion Panel (no chat, just auto suggestion)
        ai_suggestion_frame = ttk.LabelFrame(right_frame, text="AI Business Suggestion (auto-renews every 30 hours)", padding=8)
        ai_suggestion_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        self.ai_suggestion_text = tk.Text(ai_suggestion_frame, height=8, font=("Segoe UI", 10), state=tk.DISABLED, wrap=tk.WORD)
        self.ai_suggestion_text.pack(fill=tk.BOTH, expand=True, pady=2)

        # Refresh Button
        ttk.Button(self.content, text="🔄 Refresh Dashboard", command=self.update_stats).pack(pady=8)

        self.update_stats()
        self.schedule_ai_suggestion()

    def schedule_ai_suggestion(self):
        # For demo/testing, use 1 minute (60000 ms). For production, use 30*60*60*1000 ms (30 hours).
        self.generate_ai_suggestion()
        self.content.after(30 * 60 * 60 * 1000, self.schedule_ai_suggestion)  # 30 hours

    def generate_ai_suggestion(self):
        # Gather summary stats
        try:
            stats = []
            # Revenue
            self.cursor.execute("SELECT SUM(total_amount) as revenue FROM sales WHERE sale_date >= NOW() - INTERVAL 30 DAY")
            revenue = self.cursor.fetchone()['revenue'] or 0
            stats.append(f"Revenue (30d): ₹{revenue:,.2f}")
            # Inventory Value
            self.cursor.execute("SELECT SUM(quantity * price) as value FROM products")
            inventory = self.cursor.fetchone()['value'] or 0
            stats.append(f"Inventory Value: ₹{inventory:,.2f}")
            # Low Stock
            self.cursor.execute("SELECT COUNT(*) as low FROM products WHERE quantity < 10")
            low_stock = self.cursor.fetchone()['low']
            stats.append(f"Low Stock Items: {low_stock}")
            # Customers
            self.cursor.execute("SELECT COUNT(*) as customers FROM customers")
            customers = self.cursor.fetchone()['customers']
            stats.append(f"Customers: {customers}")
            # Top Product
            self.cursor.execute("""
                SELECT p.name, SUM(si.quantity) as sold
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                JOIN sales s ON si.sale_id = s.sale_id
                WHERE s.sale_date >= NOW() - INTERVAL 30 DAY
                GROUP BY si.product_id
                ORDER BY sold DESC
                LIMIT 1
            """)
            row = self.cursor.fetchone()
            stats.append(f"Top Product: {row['name']} ({row['sold']})" if row else "Top Product: -")
            # Top Customer
            self.cursor.execute("""
                SELECT c.name, SUM(s.total_amount) as spent
                FROM sales s
                JOIN customers c ON s.customer_id = c.customer_id
                WHERE s.sale_date >= NOW() - INTERVAL 30 DAY
                GROUP BY s.customer_id
                ORDER BY spent DESC
                LIMIT 1
            """)
            row = self.cursor.fetchone()
            stats.append(f"Top Customer: {row['name']} (₹{row['spent']:,.0f})" if row else "Top Customer: -")
            # Profit
            self.cursor.execute("SELECT SUM(total_profit) as profit FROM sales WHERE sale_date >= NOW() - INTERVAL 30 DAY")
            profit = self.cursor.fetchone()['profit'] or 0
            stats.append(f"Profit (30d): ₹{profit:,.2f}")
            # Discounts
            self.cursor.execute("SELECT SUM(total_discount) as discount FROM sales WHERE sale_date >= NOW() - INTERVAL 30 DAY")
            discount = self.cursor.fetchone()['discount'] or 0
            stats.append(f"Discounts (30d): ₹{discount:,.2f}")
            summary = "\n".join(stats)
        except Exception as e:
            summary = f"Error gathering stats: {e}"

        # Call OpenAI for suggestion
        self.ai_suggestion_text.config(state=tk.NORMAL)
        self.ai_suggestion_text.delete(1.0, tk.END)
        self.ai_suggestion_text.insert(tk.END, "AI is analyzing your business data...\n")
        self.ai_suggestion_text.config(state=tk.DISABLED)
        self.content.update()
        try:
            openai.api_key = OPENAI_API_KEY
            response = openai.resources.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst for a retail store. Based on the following stats, give a concise, actionable suggestion to improve business performance. Be specific and practical."},
                    {"role": "user", "content": summary}
                ],
                max_tokens=200,
                temperature=0.7
            )
            suggestion = response.choices[0].message.content.strip()
        except Exception as e:
            suggestion = f"Error getting AI suggestion: {e}"
        self.ai_suggestion_text.config(state=tk.NORMAL)
        self.ai_suggestion_text.delete(1.0, tk.END)
        self.ai_suggestion_text.insert(tk.END, suggestion)
        self.ai_suggestion_text.config(state=tk.DISABLED)

    def plot_sales_trend(self, parent):
        try:
            if not self.cursor:
                self.setup_db()
                if not self.cursor:
                    return
            self.cursor.execute("""
                SELECT DATE(sale_date) as date, SUM(total_amount) as revenue 
                FROM sales 
                WHERE sale_date >= NOW() - INTERVAL 30 DAY
                GROUP BY DATE(sale_date)
                ORDER BY date ASC
            """)
            data = self.cursor.fetchall()
            dates = [row['date'].strftime('%b %d') if isinstance(row['date'], datetime) else str(row['date']) for row in data]
            revenues = [row['revenue'] for row in data]
            fig, ax = plt.subplots(figsize=(4, 2.2))
            ax.plot(dates, revenues, marker='o', linestyle='-', color='#4a90e2')
            ax.set_title('Sales Trend')
            ax.set_ylabel('Revenue (₹)')
            ax.grid(True)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Chart error: {e}")

    def plot_sales_by_category(self, parent):
        try:
            if not self.cursor:
                self.setup_db()
                if not self.cursor:
                    return
            self.cursor.execute("""
                SELECT p.category, SUM(si.quantity * si.price) as total
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                JOIN sales s ON si.sale_id = s.sale_id
                WHERE s.sale_date >= NOW() - INTERVAL 30 DAY
                GROUP BY p.category
            """)
            data = self.cursor.fetchall()
            categories = [row['category'] for row in data]
            totals = [row['total'] for row in data]
            fig, ax = plt.subplots(figsize=(4, 2.2))
            if categories:
                ax.pie(totals, labels=categories, autopct='%1.1f%%', startangle=140)
                ax.set_title("Sales by Category")
            else:
                ax.text(0.5, 0.5, "No Data", ha='center', va='center')
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Pie chart error: {e}")

    def plot_top_products(self, parent):
        try:
            if not self.cursor:
                self.setup_db()
                if not self.cursor:
                    return
            self.cursor.execute("""
                SELECT p.name, SUM(si.quantity) as sold
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                JOIN sales s ON si.sale_id = s.sale_id
                WHERE s.sale_date >= NOW() - INTERVAL 30 DAY
                GROUP BY si.product_id
                ORDER BY sold DESC
                LIMIT 5
            """)
            data = self.cursor.fetchall()
            names = [row['name'] for row in data]
            sold = [row['sold'] for row in data]
            fig, ax = plt.subplots(figsize=(4, 2.2))
            ax.bar(names, sold, color='#e67e22')
            ax.set_title("Top 5 Products")
            ax.set_ylabel("Units Sold")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Bar chart error: {e}")

    def show_low_stock(self):
        if not self.cursor:
            self.setup_db()
            if not self.cursor:
                return
        self.cursor.execute("SELECT name, quantity FROM products WHERE quantity < 10 ORDER BY quantity ASC")
        data = self.cursor.fetchall()
        msg = "\n".join([f"{row['name']}: {row['quantity']}" for row in data]) or "No low stock items."
        messagebox.showinfo("Low Stock Items", msg)

    def ask_ai(self):
        prompt = self.ai_entry.get().strip()
        if not prompt:
            return
        self.ai_chat_log.config(state=tk.NORMAL)
        self.ai_chat_log.insert(tk.END, f"You: {prompt}\n")
        self.ai_chat_log.config(state=tk.DISABLED)
        self.ai_entry.delete(0, tk.END)
        self.content.after(100, lambda: self._get_ai_response(prompt))

    def _get_ai_response(self, prompt):
        self.ai_chat_log.config(state=tk.NORMAL)
        self.ai_chat_log.insert(tk.END, "AI: Thinking...\n")
        self.ai_chat_log.see(tk.END)
        self.ai_chat_log.config(state=tk.DISABLED)
        self.content.update()
        try:
            openai.api_key = OPENAI_API_KEY
            response = openai.resources.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are an expert assistant for a store admin dashboard. Give concise, actionable answers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Error: {e}"
        self.ai_chat_log.config(state=tk.NORMAL)
        self.ai_chat_log.delete("end-2l", "end-1l")  # Remove "AI: Thinking..."
        self.ai_chat_log.insert(tk.END, f"AI: {answer}\n")
        self.ai_chat_log.see(tk.END)
        self.ai_chat_log.config(state=tk.DISABLED)

    def update_stats(self):
        try:
            if not self.cursor:
                self.setup_db()
                if not self.cursor:
                    for card in self.metric_cards:
                        card.config(text="Error")
                    return

            # Revenue (30d)
            self.cursor.execute("SELECT SUM(total_amount) as revenue FROM sales WHERE sale_date >= NOW() - INTERVAL 30 DAY")
            revenue = self.cursor.fetchone()['revenue'] or 0
            self.metric_cards[0].config(text=f"₹{revenue:,.2f}")

            # Inventory Value
            self.cursor.execute("SELECT SUM(quantity * price) as value FROM products")
            inventory = self.cursor.fetchone()['value'] or 0
            self.metric_cards[1].config(text=f"₹{inventory:,.2f}")

            # Low Stock
            self.cursor.execute("SELECT COUNT(*) as low FROM products WHERE quantity < 10")
            low_stock = self.cursor.fetchone()['low']
            self.metric_cards[2].config(text=f"{low_stock}")

            # Customers
            self.cursor.execute("SELECT COUNT(*) as customers FROM customers")
            customers = self.cursor.fetchone()['customers']
            self.metric_cards[3].config(text=f"{customers}")

            # Top Product
            self.cursor.execute("""
                SELECT p.name, SUM(si.quantity) as sold
                FROM sale_items si
                JOIN products p ON si.product_id = p.product_id
                JOIN sales s ON si.sale_id = s.sale_id
                WHERE s.sale_date >= NOW() - INTERVAL 30 DAY
                GROUP BY si.product_id
                ORDER BY sold DESC
                LIMIT 1
            """)
            row = self.cursor.fetchone()
            self.metric_cards[4].config(text=f"{row['name']} ({row['sold']})" if row else "-")

            # Top Customer
            self.cursor.execute("""
                SELECT c.name, SUM(s.total_amount) as spent
                FROM sales s
                JOIN customers c ON s.customer_id = c.customer_id
                WHERE s.sale_date >= NOW() - INTERVAL 30 DAY
                GROUP BY s.customer_id
                ORDER BY spent DESC
                LIMIT 1
            """)
            row = self.cursor.fetchone()
            self.metric_cards[5].config(text=f"{row['name']} (₹{row['spent']:,.0f})" if row else "-")

            # Profit (30d)
            self.cursor.execute("SELECT SUM(total_profit) as profit FROM sales WHERE sale_date >= NOW() - INTERVAL 30 DAY")
            profit = self.cursor.fetchone()['profit'] or 0
            self.metric_cards[6].config(text=f"₹{profit:,.2f}")

            # Discounts (30d)
            self.cursor.execute("SELECT SUM(total_discount) as discount FROM sales WHERE sale_date >= NOW() - INTERVAL 30 DAY")
            discount = self.cursor.fetchone()['discount'] or 0
            self.metric_cards[7].config(text=f"₹{discount:,.2f}")

        except Exception as e:
            print(f"Error updating metrics: {e}")
            for card in self.metric_cards:
                card.config(text="Error")

    def __del__(self):
        if self.db_connection and self.db_connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.db_connection.close()