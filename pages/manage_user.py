import tkinter as tk
from tkinter import ttk
from database.db_connection import get_db_connection

class ManageUser(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Set a custom style
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), foreground="#333333")
        style.configure("TEntry", font=("Helvetica", 12), foreground="#333333", background="#FFFFFF")
        style.configure("TButton", font=("Helvetica", 12), foreground="#333333", background="#FFFFFF")
        style.configure("TFrame", background="#F5F5F5")

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(self, background="#F5F5F5")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configure the scrollbar
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.display_user_logins()

    def display_user_logins(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all login times for each 'viewer' user
        cursor.execute("""
            SELECT u.username, u.role, ll.login_time
            FROM users u
            JOIN login_log ll ON u.username = ll.username
            WHERE u.role = 'viewer' AND ll.success = TRUE
            ORDER BY ll.login_time DESC
        """)
        records = cursor.fetchall()
        
        labels = ["Username", "Role", "Login Time"]
        
        for i, label in enumerate(labels):
            ttk.Label(self.scrollable_frame, text=label, style="TLabel").grid(row=0, column=i, padx=10, pady=5)
        
        for i, record in enumerate(records, start=1):
            for j, value in enumerate(record):
                ttk.Label(self.scrollable_frame, text=value, style="TLabel").grid(row=i, column=j, padx=10, pady=5)

        cursor.close()
        conn.close()