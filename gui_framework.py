import tkinter as tk
from tkinter import ttk, messagebox

# Modern, balanced color palette
BG_COLOR = '#f7f9fb'
SIDEBAR_BG = '#f0f3f7'
SIDEBAR_FG = '#2c3e50'
PRIMARY = '#4a90e2'
ACCENT = '#e67e22'
CONTENT_BG = '#ffffff'
CARD_BG = '#ffffff'
SHADOW_BG = '#e3e7ee'

class BasePage(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=BG_COLOR)
        self.pack(fill=tk.BOTH, expand=True)
        self.controller = controller
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._init_styles()
        self.active_menu_btn = None

        # Subtle shadow/card effect for main area
        self.shadow = tk.Frame(self, bg=SHADOW_BG, bd=0, highlightthickness=0)
        self.shadow.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.98)
        self.card = tk.Frame(self, bg=CARD_BG, bd=0, highlightthickness=0)
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.96, relheight=0.96)
        self.lift(self.card)

        self._create_navbar()
        self._create_sidebar()
        self._create_content_frame()
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.shadow.place_configure(relwidth=0.98, relheight=0.98)
        self.card.place_configure(relwidth=0.96, relheight=0.96)

    def _init_styles(self):
        # Navbar
        self.style.configure('Navbar.TFrame', background=PRIMARY, relief='flat')
        self.style.configure('Navbar.TLabel', background=PRIMARY, foreground='white', font=('Segoe UI', 15, 'bold'))
        self.style.configure('Navbar.TButton', background=PRIMARY, foreground='white', font=('Segoe UI', 11, 'bold'), relief='flat')
        # Sidebar
        self.style.configure('Sidebar.TFrame', background=SIDEBAR_BG)
        self.style.configure('Sidebar.TButton', background=SIDEBAR_BG, foreground=SIDEBAR_FG, font=('Segoe UI', 12), relief='flat', borderwidth=0, padding=8)
        self.style.map('Sidebar.TButton',
            background=[('active', PRIMARY), ('!active', SIDEBAR_BG)],
            foreground=[('active', '#fff'), ('!active', SIDEBAR_FG)]
        )
        # Content
        self.style.configure('Content.TFrame', background=CONTENT_BG)
        # Buttons
        self.style.configure('Accent.TButton', background=ACCENT, foreground='white', font=('Segoe UI', 12, 'bold'), relief='flat')
        self.style.map('Accent.TButton', background=[('active', PRIMARY)])
        # Role badge and avatar styles
        self.style.configure('RoleBadge.Admin.TLabel', background='#e74c3c', foreground='white', font=('Segoe UI', 9, 'bold'), padding=4)
        self.style.configure('RoleBadge.Staff.TLabel', background='#27ae60', foreground='white', font=('Segoe UI', 9, 'bold'), padding=4)
        self.style.configure('ActiveMenu.TButton', background=PRIMARY, foreground='#f1c40f', font=('Segoe UI', 12, 'bold'), relief='flat')

    def _create_navbar(self):
        nav = ttk.Frame(self.card, style='Navbar.TFrame')
        nav.pack(side=tk.TOP, fill=tk.X, padx=0, pady=(0, 2))
        ttk.Button(nav, text='← Back', style='Navbar.TButton', command=self._on_back).pack(side=tk.LEFT, padx=16, pady=8)
        ttk.Label(nav, text='Store Management System', style='Navbar.TLabel').pack(side=tk.LEFT, padx=24, pady=8)
        user = getattr(self.controller, 'current_user', {})
        uname = user.get('username', '')
        role = user.get('role', '')
        fullname = user.get('full_name', uname)
        initials = ''.join([x[0].upper() for x in fullname.split()]) if fullname else 'U'
        avatar = tk.Canvas(nav, width=36, height=36, bg=PRIMARY, highlightthickness=0, bd=0)
        avatar.create_oval(3, 3, 33, 33, fill='#fff', outline=PRIMARY)
        avatar.create_text(18, 18, text=initials, fill=PRIMARY, font=('Segoe UI', 14, 'bold'))
        avatar.pack(side=tk.RIGHT, padx=(0, 10), pady=4)
        badge_style = 'RoleBadge.Admin.TLabel' if role == 'admin' else 'RoleBadge.Staff.TLabel'
        ttk.Label(nav, text=role.capitalize(), style=badge_style).pack(side=tk.RIGHT, padx=(0, 10), pady=8)
        self.user_label = ttk.Label(nav, text=f"{fullname} ({uname})", style='Navbar.TLabel')
        self.user_label.pack(side=tk.RIGHT, padx=(0, 10), pady=8)
        ttk.Button(nav, text='Logout', style='Navbar.TButton', command=self._on_logout).pack(side=tk.RIGHT, padx=(0, 10), pady=8)

    def _on_back(self):
        if hasattr(self.controller, 'history') and len(self.controller.history) > 1:
            self.controller.history.pop()
            self.controller.show_page(self.controller.history[-1], add_to_history=False)

    def _on_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            self.controller.show_login()

    def _create_sidebar(self):
        sb = ttk.Frame(self.card, style='Sidebar.TFrame', width=220)
        sb.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0), pady=(0, 0))
        ttk.Label(sb, text='Menu', background=SIDEBAR_BG, foreground=SIDEBAR_FG, font=('Segoe UI', 14, 'bold')).pack(pady=(32, 18))
        user = getattr(self.controller, 'current_user', {})
        role = user.get('role', 'staff')
        # Menu definitions with icons (unicode)
        if role == 'admin':
            menu_items = [
                ('🏠 Dashboard', 'Dashboard'),
                # ('📦 Products', 'ProductManagement'),  # Removed Product Management
                ('📦 Inventory', 'Inventory'),  # <-- Ensure Inventory is here for admin
                ('👥 Users Management', 'UserManagement'),
                ('🚚 Suppliers', 'SupplierManagement'),
                ('🛒 Purchases', 'PurchaseManagement'),
                ('📊 Reports', 'Reports'),  # <-- Change 'ReportsPage' to 'Reports'
                ('👤 Customers', 'CustomerManagement'),  # <-- Admin can now see CustomerManagement
                ('⚙️ Settings', 'SettingsPage')
            ]
        else:
            menu_items = [
                ('🏠 Dashboard', 'Dashboard'),
                ('📦 Inventory', 'Inventory'),
                ('💰 Sales', 'SalesManagement'),
                ('👤 Customers', 'CustomerManagement') # <-- Only staff sees this now
              
            ]
        self.menu_buttons = []
        for label, page in menu_items:
            btn = ttk.Button(sb, text=label, style='Sidebar.TButton', command=lambda p=page, b=label: self._on_menu_click(p, b))
            btn.pack(fill=tk.X, pady=4, padx=18, ipady=8)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(style='ActiveMenu.TButton'))
            btn.bind("<Leave>", lambda e, b=btn, l=label: self._set_active_menu(l if self.active_menu_btn and self.active_menu_btn.cget('text') == l else None))
            self.menu_buttons.append((btn, label))
        self._set_active_menu(menu_items[0][0])

    def _set_active_menu(self, label):
        for btn, lbl in self.menu_buttons:
            if lbl == label:
                btn.configure(style='ActiveMenu.TButton')
                self.active_menu_btn = btn
            else:
                btn.configure(style='Sidebar.TButton')

    def _on_menu_click(self, page, label):
        self._set_active_menu(label)
        self.controller.show_page(page)

    def _create_content_frame(self):
        self.content = ttk.Frame(self.card, style='Content.TFrame')
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=18, pady=18)

    # Convenience for child pages
    def update_user_info(self, username, role):
        """Update user information in the navbar"""
        if hasattr(self, 'user_label'):
            self.user_label.config(text=f"{username} ({role})")
        if hasattr(self, 'avatar'):
            initials = ''.join([x[0].upper() for x in username.split()]) if username else 'U'
            self.avatar.delete("all")
            self.avatar.create_oval(3, 3, 33, 33, fill='#fff', outline=PRIMARY)
            self.avatar.create_text(18, 18, text=initials, fill=PRIMARY, font=('Segoe UI', 14, 'bold'))

def create_dashboard_pages():
    from .admin_dashboard import AdminDashboard
    from .user_dashboard import UserDashboard
    return {'AdminDashboard': AdminDashboard, 'UserDashboard': UserDashboard}
