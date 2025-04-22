import tkinter as tk
from tkinter import ttk, messagebox
from gui_framework import BasePage
import mysql.connector

class UserManagement(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.cursor = self.db.cursor(dictionary=True)
        self.create_user_ui()
        self.load_users()

    def create_user_ui(self):
        header_frame = ttk.Frame(self.content)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame, text="User Management", font=('Helvetica', 16)).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Search:").pack(side=tk.LEFT, padx=(30, 2))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(header_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", lambda e: self.load_users())

        columns = ("ID", "Username", "Full Name", "Role")
        self.tree = ttk.Treeview(self.content, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=120 if col != "Full Name" else 200)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(self.content)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add", width=10, command=self.add_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Edit", width=10, command=self.edit_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", width=10, command=self.delete_user).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh", width=10, command=self.load_users).pack(side=tk.LEFT, padx=2)

    def load_users(self):
        search = self.search_var.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        query = "SELECT user_id, username, full_name, role FROM users"
        params = ()
        if search:
            query += " WHERE username LIKE %s OR full_name LIKE %s OR role LIKE %s"
            like = f"%{search}%"
            params = (like, like, like)
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=(row['user_id'], row['username'], row['full_name'], row['role']))

    def add_user(self):
        self.open_user_form("Add User")

    def edit_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a user to edit.")
            return
        values = self.tree.item(selected[0], 'values')
        self.open_user_form("Edit User", values)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a user to delete.")
            return
        user_id = self.tree.item(selected[0], 'values')[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
                self.db.commit()
                self.load_users()
                messagebox.showinfo("Deleted", "User deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {e}")

    def open_user_form(self, title, user=None):
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry("350x350")
        form.resizable(False, False)

        username_var = tk.StringVar(value=user[1] if user else "")
        fullname_var = tk.StringVar(value=user[2] if user else "")
        role_var = tk.StringVar(value=user[3] if user else "staff")
        password_var = tk.StringVar()

        ttk.Label(form, text="Username:").pack(anchor='w', padx=20, pady=(20, 2))
        username_entry = ttk.Entry(form, textvariable=username_var)
        username_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Full Name:").pack(anchor='w', padx=20, pady=(10, 2))
        fullname_entry = ttk.Entry(form, textvariable=fullname_var)
        fullname_entry.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Role:").pack(anchor='w', padx=20, pady=(10, 2))
        role_combo = ttk.Combobox(form, textvariable=role_var, values=["admin", "staff"], state='readonly')
        role_combo.pack(fill=tk.X, padx=20)

        ttk.Label(form, text="Password:").pack(anchor='w', padx=20, pady=(10, 2))
        password_entry = ttk.Entry(form, textvariable=password_var, show="*")
        password_entry.pack(fill=tk.X, padx=20)

        def save():
            username = username_var.get().strip()
            fullname = fullname_var.get().strip()
            role = role_var.get()
            password = password_var.get().strip()

            if not all([username, fullname, role]):
                messagebox.showerror("Input Error", "Please fill all required fields.")
                return

            try:
                if user:
                    # Only update password if provided
                    if password:
                        self.cursor.execute("""
                            UPDATE users SET username=%s, full_name=%s, role=%s, password=%s WHERE user_id=%s
                        """, (username, fullname, role, password, user[0]))
                    else:
                        self.cursor.execute("""
                            UPDATE users SET username=%s, full_name=%s, role=%s WHERE user_id=%s
                        """, (username, fullname, role, user[0]))
                else:
                    if not password:
                        messagebox.showerror("Input Error", "Password is required for new users.")
                        return
                    self.cursor.execute("""
                        INSERT INTO users (username, password, role, full_name)
                        VALUES (%s, %s, %s, %s)
                    """, (username, password, role, fullname))
                self.db.commit()
                self.load_users()
                form.destroy()
                messagebox.showinfo("Success", "User saved successfully.")
            except mysql.connector.IntegrityError:
                messagebox.showerror("Error", "Username already exists.")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save user: {e}")

        btn_frame = ttk.Frame(form)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Save", command=save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=form.destroy).pack(side=tk.LEFT, padx=10)