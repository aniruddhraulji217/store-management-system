import tkinter as tk
from tkinter import ttk, messagebox
from gui_framework import BasePage

class AdminDashboard(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.controller = controller
        self.create_dashboard_ui()

    def create_dashboard_ui(self):
        # Main layout: sidebar and right frame
        main_frame = ttk.Frame(self.content)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar (optional, can be removed if not needed)
        sidebar = ttk.Frame(main_frame, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)
        ttk.Label(sidebar, text="Admin Menu", font=('Segoe UI', 12, 'bold')).pack(pady=(10, 20))
        ttk.Button(sidebar, text="Dashboard", command=lambda: self.controller.show_page("AdminDashboard")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Inventory", command=lambda: self.controller.show_page("Inventory")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Users", command=lambda: self.controller.show_page("UserManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Suppliers", command=lambda: self.controller.show_page("SupplierManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Purchases", command=lambda: self.controller.show_page("PurchaseManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Reports", command=lambda: self.controller.show_page("Reports")).pack(fill=tk.X, pady=2)
        ttk.Button(sidebar, text="Settings", command=lambda: self.controller.show_page("SettingsPage")).pack(fill=tk.X, pady=2)

        # Right frame for dashboard content
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Dashboard header
        ttk.Label(right_frame, text="Admin Dashboard", font=('Helvetica', 18, 'bold')).pack(anchor='w', pady=(0, 10))

        # Quick Actions
        qa_frame = ttk.LabelFrame(right_frame, text="Quick Actions", padding=8)
        qa_frame.pack(fill=tk.X, pady=(0,8))
        def open_inventory_add_product():
            inventory_page = self.controller.pages.get("Inventory")
            if inventory_page and hasattr(inventory_page, "add_product"):
                inventory_page.add_product()
            else:
                messagebox.showerror("Error", "Inventory page is not available. Please ensure the Inventory page is loaded.")
        ttk.Button(qa_frame, text="Add Product", command=open_inventory_add_product).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="Add Purchase", command=lambda: self.controller.show_page("PurchaseManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="View Reports", command=lambda: self.controller.show_page("Reports")).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="Low Stock", command=self.show_low_stock).pack(fill=tk.X, pady=2)

        # Example dashboard stats (customize as needed)
        stats_frame = ttk.LabelFrame(right_frame, text="Statistics", padding=8)
        stats_frame.pack(fill=tk.X, pady=(10,8))
        ttk.Label(stats_frame, text="Total Products:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="...").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="Total Users:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="...").grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="Total Sales:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(stats_frame, text="...").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

    def show_low_stock(self):
        # Example implementation for low stock alert
        messagebox.showinfo("Low Stock", "This would show a list of products with low stock.")

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

        # Removed Sales Trend and Sales by Category charts

        # Top 5 Products Bar Chart
        top_products_frame = ttk.LabelFrame(charts_frame, text="Top 5 Products (30d)", padding=8)
        top_products_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.plot_top_products(top_products_frame)

        # Quick Actions & AI Assistant
        right_frame = ttk.Frame(charts_frame)
        right_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=8, pady=8)
        right_frame.columnconfigure(0, weight=1)

        # Quick Actions
        qa_frame = ttk.LabelFrame(right_frame, text="Quick Actions", padding=8)
        qa_frame.pack(fill=tk.X, pady=(0,8))
        ttk.Button(qa_frame, text="Add Product", command=lambda: self.controller.show_page("ProductManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="Add Purchase", command=lambda: self.controller.show_page("PurchaseManagement")).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="View Reports", command=lambda: self.controller.show_page("Reports")).pack(fill=tk.X, pady=2)
        ttk.Button(qa_frame, text="Low Stock", command=self.show_low_stock).pack(fill=tk.X, pady=2)

        # AI Assistant Panel
        ai_frame = ttk.LabelFrame(right_frame, text="AI Assistant (GPT-4.1)", padding=8)
        ai_frame.pack(fill=tk.BOTH, expand=True)
        self.ai_chat_log = scrolledtext.ScrolledText(ai_frame, height=8, font=("Segoe UI", 10), state=tk.DISABLED, wrap=tk.WORD)
        self.ai_chat_log.pack(fill=tk.BOTH, expand=True, pady=2)
        ai_entry_frame = ttk.Frame(ai_frame)
        ai_entry_frame.pack(fill=tk.X)
        self.ai_entry = ttk.Entry(ai_entry_frame)
        self.ai_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,4))
        ttk.Button(ai_entry_frame, text="Ask", command=self.ask_ai).pack(side=tk.RIGHT)

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