import mysql.connector
from tkinter import messagebox

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                auth_plugin='mysql_native_password'
            )
            return True
        except mysql.connector.Error as err:
            error_msg = f"MySQL Connection Error: {err}\n\n"
            error_msg += "TROUBLESHOOTING STEPS:\n"
            error_msg += "1. Open Command Prompt AS ADMINISTRATOR\n"
            error_msg += "2. Run: net start mysql80\n"
            error_msg += "3. If service doesn't exist, check exact name with:\n"
            error_msg += "   sc query | find \"mysql\"\n"
            error_msg += "4. Verify MySQL is installed at: C:\\Program Files\\MySQL"
            messagebox.showerror("Database Connection Failed", error_msg)
            return False

    def verify_user(self, username, password):
        if not self.connect():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT user_id, username, role, full_name 
                FROM users 
                WHERE username=%s AND password=%s
            """, (username, password))
            user = cursor.fetchone()
            return user
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Query Error: {err}")
            return None
        finally:
            if self.connection:
                self.connection.close()

    def is_admin(self, user):
        return user and user.get('role') == 'admin'