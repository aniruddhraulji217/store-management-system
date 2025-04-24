import re
import tkinter as tk
from tkinter import ttk, messagebox
from gui_framework import BasePage
import mysql.connector
from tkcalendar import DateEntry

class UserManagement(BasePage):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        # Initialize DB connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Aniruddh@217",
            database="inventory_db"
        )
        self.cursor = self.db.cursor(dictionary=True)

        # Apply a modern theme
        style = ttk.Style()
        style.theme_use('clam')  # or 'vista', 'alt'
        style.configure('Header.TFrame', background='#eaf6fb')
        style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'), foreground='#fff', background='#2980b9')
        style.map('Accent.TButton', background=[('active', '#3498db')])
        style.configure('Custom.Treeview', font=('Helvetica', 10), rowheight=24, background='#f9f9f9', fieldbackground='#f9f9f9')
        style.configure('Treeview.Heading', font=('Helvetica', 11, 'bold'), background='#2980b9', foreground='#fff')

        self.create_user_ui()
        self.load_users()

    def create_user_ui(self):
        # Header with Search
        header = ttk.Frame(self.content, style='Header.TFrame', padding=(10, 5))
        header.grid(row=0, column=0, sticky='ew')
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="User Management", font=('Helvetica', 18, 'bold'), foreground='#2c3e50').grid(row=0, column=0, padx=(0,20))
        ttk.Label(header, text="Search:", font=('Helvetica', 10, 'bold')).grid(row=0, column=1, sticky='e')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(header, textvariable=self.search_var)
        search_entry.grid(row=0, column=2, sticky='ew', padx=(5,0))
        search_entry.bind('<KeyRelease>', lambda e: self.load_users())

        # Treeview with Scrollbars
        tree_frame = ttk.Frame(self.content)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        self.content.rowconfigure(1, weight=1)
        self.content.columnconfigure(0, weight=1)

        columns = ("ID", "Username", "Full Name", "Role", "Joined", "Education", "Salary", "Address", "Email", "Contact")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Custom.Treeview')
        for col in columns:
            width = 80 if col in ("ID","Role","Joined","Salary","Contact") else 150
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')
        vsb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Action Buttons
        btn_frame = ttk.Frame(self.content, padding=10)
        btn_frame.grid(row=2, column=0, sticky='ew')
        for i, (text, cmd) in enumerate([
            ("Add", self.add_user),
            ("Edit", self.edit_user),
            ("Delete", self.delete_user),
            ("Refresh", self.load_users)
        ]):
            ttk.Button(btn_frame, text=text, command=cmd, style='Accent.TButton').grid(row=0, column=i, padx=5)

    def load_users(self):
        search = self.search_var.get().strip()
        [self.tree.delete(i) for i in self.tree.get_children()]
        query = ("SELECT user_id, username, full_name, role, date_of_joining, education, salary, address, email, contact "
                 "FROM users" )
        params = ()
        if search:
            query += " WHERE username LIKE %s OR full_name LIKE %s OR role LIKE %s OR email LIKE %s"
            like = f"%{search}%"
            params = (like, like, like, like)
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            # Highlight low stock (if any role logic needed)
            self.tree.insert('', 'end', values=(
                row['user_id'], row['username'], row['full_name'], row['role'],
                row['date_of_joining'] or '', row['education'] or '',
                f"{row['salary']:.2f}" if row['salary'] else '', row['address'] or '',
                row['email'] or '', row['contact'] or ''
            ))

    def open_user_form(self, title, user=None):
        form = tk.Toplevel(self)
        form.title(title)
        form.geometry('500x650')
        form.resizable(False, False)
        form.configure(bg='#f7fbfc')

        # Form Variables
        vars = {
            'username': tk.StringVar(value=user[1] if user else ''),
            'fullname': tk.StringVar(value=user[2] if user else ''),
            'role': tk.StringVar(value=user[3] if user else 'staff'),
            'doj': tk.StringVar(value=user[4] if user and user[4] else ''),
            'education': tk.StringVar(value=user[5] if user else ''),
            'salary': tk.StringVar(value=user[6] if user else ''),
            'address': tk.StringVar(value=user[7] if user else ''),
            'email': tk.StringVar(value=user[8] if user else ''),
            'contact': tk.StringVar(value=user[9] if user else ''),
            'password': tk.StringVar(),
            'confirm': tk.StringVar()
        }

        # Field definitions: label, widget
        fields = [
            ('Username*', ttk.Entry, 'username'),
            ('Full Name*', ttk.Entry, 'fullname'),
            ('Role*', ttk.Combobox, 'role', {'values':['admin','staff'], 'state':'readonly'}),
            ('Date of Joining', DateEntry, 'doj', {'date_pattern':'yyyy-mm-dd'}),
            ('Education', ttk.Entry, 'education'),
            ('Salary', ttk.Entry, 'salary'),
            ('Address', ttk.Entry, 'address'),
            ('Email', ttk.Entry, 'email'),
            ('Contact', ttk.Entry, 'contact'),
            ('Password{}', ttk.Entry, 'password', {'show':'*'}),
            ('Confirm Password{}', ttk.Entry, 'confirm', {'show':'*'})
        ]
        # Layout fields
        for idx, field in enumerate(fields):
            label = field[0].format('*' if '*' in field[0] else '')
            ttk.Label(form, text=label, font=('Helvetica', 11, 'bold')).grid(row=idx, column=0, padx=30, pady=5, sticky='w')
            widget_cls = field[1]
            opts = field[3] if len(field) > 3 else {}
            wi = widget_cls(form, textvariable=vars[field[2]], font=('Helvetica',11), **opts)
            wi.grid(row=idx, column=1, padx=30, pady=5, sticky='ew')
        form.columnconfigure(1, weight=1)

        def validate_fields():
            # Required fields
            if not vars['username'].get().strip() or not vars['fullname'].get().strip() or not vars['role'].get():
                messagebox.showerror('Validation Error','Username, Full Name, and Role are required.')
                return False
            # Email format
            email = vars['email'].get().strip()
            if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messagebox.showerror('Validation Error','Enter a valid email address.')
                return False
            # Contact: must be exactly 10 digits
            contact = vars['contact'].get().strip()
            if contact and (not contact.isdigit() or len(contact) != 10):
                messagebox.showerror('Validation Error','Contact must be exactly 10 digits.')
                return False
            # Password match on new user or change
            pwd, conf = vars['password'].get(), vars['confirm'].get()
            if not user and not pwd:
                messagebox.showerror('Validation Error','Password is required for new users.')
                return False
            if pwd and pwd != conf:
                messagebox.showerror('Validation Error','Passwords do not match.')
                return False
            # Salary numeric
            sal = vars['salary'].get().strip()
            if sal:
                try: float(sal)
                except: messagebox.showerror('Validation Error','Salary must be a number.'); return False
            return True

        def save():
            if not validate_fields():
                return
            data = {k: vars[k].get().strip() for k in vars}
            try:
                if user:
                    # Update existing user
                    sql = ("UPDATE users SET username=%s, full_name=%s, role=%s, date_of_joining=%s, education=%s, "
                           "salary=%s, address=%s, email=%s, contact=%s" )
                    params = [data['username'], data['fullname'], data['role'], data['doj'] or None,
                              data['education'], float(data['salary']) if data['salary'] else None,
                              data['address'], data['email'], data['contact']]
                    if data['password']:
                        sql += ", password=%s"
                        params.append(data['password'])
                    sql += " WHERE user_id=%s"
                    params.append(user[0])
                else:
                    # Insert new user
                    sql = ("INSERT INTO users (username,password,role,full_name,date_of_joining,education,salary,address,email,contact) "
                           "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                    params = [data['username'], data['password'], data['role'], data['fullname'],
                              data['doj'] or None, data['education'], float(data['salary']) if data['salary'] else None,
                              data['address'], data['email'], data['contact']]
                self.cursor.execute(sql, tuple(params))
                self.db.commit()
                self.load_users()
                form.destroy()
                messagebox.showinfo('Success','User saved successfully.')
            except mysql.connector.IntegrityError:
                messagebox.showerror('Error','Username already exists.')
            except Exception as e:
                messagebox.showerror('Database Error',f'Failed to save user: {e}')

        # Buttons
        btn_fr = ttk.Frame(form, padding=10)
        btn_fr.grid(row=len(fields), column=0, columnspan=2)
        ttk.Button(btn_fr, text="Save", command=save, style='Accent.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(btn_fr, text="Cancel", command=form.destroy, style='Accent.TButton').grid(row=0, column=1, padx=5)

    def add_user(self):
        self.open_user_form("Add User")

    def edit_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('No Selection','Select a user to edit.')
            return
        vals = self.tree.item(sel[0], 'values')
        self.open_user_form("Edit User", vals)

    def delete_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('No Selection','Select a user to delete.')
            return
        uid = self.tree.item(sel[0], 'values')[0]
        if messagebox.askyesno('Confirm','Delete this user permanently?'):
            try:
                self.cursor.execute("DELETE FROM users WHERE user_id=%s", (uid,))
                self.db.commit()
                self.load_users()
                messagebox.showinfo('Deleted','User removed.')
            except Exception as e:
                messagebox.showerror('Error',f'Failed to delete user: {e}')
