import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk  # Import PIL for image handling
from database.db_connection import get_db_connection
from pages.admin_dashboard import AdminDashboard
from pages.viewer_dashboard import ViewerDashboard

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("350x250")  # Increased window size for better layout
        self.root.configure(bg="#F5F5F5")

        # Set a custom style
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), foreground="#333333")
        style.configure("TEntry", font=("Helvetica", 12), foreground="#333333", background="#FFFFFF")
        style.configure("TButton", font=("Helvetica", 12), foreground="#333333")
        style.configure("TFrame", background="#F5F5F5")

        # Frame for Login Form
        self.frame = ttk.Frame(self.root, padding="20 20 20 20", style="TFrame")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Load and display image
        self.load_image()

        # Title Label
        self.title_label = ttk.Label(self.frame, text="Login", font=("Helvetica", 16, "bold"), style="TLabel")
        self.title_label.grid(row=0, column=1, columnspan=2, pady=(0, 10))

        # Username and Password Labels
        ttk.Label(self.frame, text="Username:", style="TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(self.frame, text="Password:", style="TLabel").grid(row=2, column=0, sticky=tk.W, pady=5)

        # Entry fields for Username and Password
        self.username_entry = ttk.Entry(self.frame, width=25, style="TEntry")
        self.password_entry = ttk.Entry(self.frame, width=25, style="TEntry", show="*")

        self.username_entry.grid(row=1, column=1, pady=5)
        self.password_entry.grid(row=2, column=1, pady=5)

        # Placeholder text
        self.username_entry.insert(0, "Enter your username")
        self.password_entry.insert(0, "Enter your password")
        self.username_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.username_entry, "Enter your username"))
        self.password_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.password_entry, "Enter your password"))

        # Login Button
        self.login_button = ttk.Button(self.frame, text="Login", command=self.login, style="TButton")
        self.login_button.grid(row=3, column=1, columnspan=2, pady=10)

        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())

        # Centering the window
        self.center_window(350, 250)

    def load_image(self):
        """Loads and displays an image in the upper left corner."""
        try:
            image = Image.open("images\\oocsu_logo.png")  # Replace with your image path
            image = image.resize((70, 70), Image.LANCZOS)  # Resize image to fit
            photo = ImageTk.PhotoImage(image)
            image_label = ttk.Label(self.frame, image=photo, style="TLabel")
            image_label.image = photo  # Keep a reference to avoid garbage collection
            image_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        except Exception as e:
            print(f"Error loading image: {e}")

    def clear_placeholder(self, entry, placeholder):
        """Clears the placeholder text when the entry field is focused."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def center_window(self, width, height):
        """Centers the window on the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def log_login_attempt(self, cursor, username, success):
        """Log the login attempt to the login_log table."""
        cursor.execute(
            "INSERT INTO login_log (username, success) VALUES (%s, %s)",
            (username, success)
        )

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Check credentials
            cursor.execute(
                "SELECT role, password FROM users WHERE username=%s",
                (username,)
            )
            result = cursor.fetchone()

            if result and result[1] == password:
                role = result[0]
                # Log successful login
                self.log_login_attempt(cursor, username, True)
                conn.commit()

                # Close login window
                self.root.destroy()

                # Open appropriate dashboard
                if role == 'admin':
                    AdminDashboard()
                elif role == 'viewer':
                    ViewerDashboard(username)  # Pass username to ViewerDashboard
            else:
                # Log failed login attempt
                self.log_login_attempt(cursor, username, False)
                conn.commit()
                messagebox.showerror("Error", "Invalid credentials")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        finally:
            cursor.close()
            conn.close()

# Main function to run the application
def main():
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()