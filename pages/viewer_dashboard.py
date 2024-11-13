import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from database.db_connection import get_db_connection
from datetime import datetime

class ViewerDashboard:
    def __init__(self, username):
        self.username = username
        self.root = tk.Tk()
        self.root.title("Vehicle Monitoring Dashboard")
        self.root.geometry("1400x800")

        # Initialize styles
        self.setup_styles()

        # Configure the grid layout for equal-sized quadrants
        self.root.grid_rowconfigure(0, weight=1, uniform="quadrant")
        self.root.grid_rowconfigure(1, weight=1, uniform="quadrant")
        self.root.grid_columnconfigure(0, weight=1, uniform="quadrant")
        self.root.grid_columnconfigure(1, weight=1, uniform="quadrant")

        # Setup quadrants
        self.setup_quadrants()
        self.root.mainloop()

    def setup_quadrants(self):
        # Quadrant 1: Driver Photo Display
        self.photo_frame = ttk.Frame(self.root, style="Main.TFrame")
        self.photo_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.setup_driver_photo_display()

        # Quadrant 2: Fullscreen Driver Details Display
        self.details_frame = ttk.Frame(self.root, style="Main.TFrame")
        self.details_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.setup_driver_details_display()

        # Quadrant 3: Logo Display with Header
        self.logo_frame = ttk.Frame(self.root, style="Main.TFrame")
        self.logo_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.setup_logo_display_with_header()

        # Quadrant 4: Registered Vehicles List and Timed In Log
        self.vehicles_frame = ttk.Frame(self.root, style="Main.TFrame")
        self.vehicles_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.setup_vehicles_tab()

    def setup_driver_photo_display(self):
        ttk.Label(self.photo_frame, text="Driver Photo", style="Header.TLabel").pack(pady=5)
        self.photo_label = ttk.Label(self.photo_frame)
        self.photo_label.pack(pady=10)

        self.plate_entry = ttk.Entry(self.photo_frame, font=("Helvetica", 12))
        self.plate_entry.pack(pady=5)

        verify_button = ttk.Button(self.photo_frame, text="Display Photo",
                                   command=self.display_driver_info, style="Nav.TButton")
        verify_button.pack(pady=10)

    def setup_logo_display_with_header(self):
        ttk.Label(self.logo_frame, text="CSU Vehicle Monitoring System", style="Title.TLabel").pack(pady=(0, 10))
        try:
            logo_image = Image.open("images/lcsu2-02.jpeg")
            logo_image = logo_image.resize((200, 200), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(self.logo_frame, image=logo_photo, style="Header.TLabel")
            logo_label.image = logo_photo
            logo_label.pack()
        except Exception:
            ttk.Label(self.logo_frame, text="Logo Missing", style="Header.TLabel").pack(pady=10)

    def setup_driver_details_display(self):
        # Setting up driver details to take full quadrant space
        self.details_frame.grid_rowconfigure(0, weight=1)  # Row expands to fill available vertical space
        self.details_frame.grid_columnconfigure(0, weight=1)  # Column expands to fill available horizontal space

        # Label for the section
        ttk.Label(self.details_frame, text="Driver Details", style="Header.TLabel").grid(row=0, column=0, pady=5)

        # Fullscreen text widget for driver details
        self.details_text = tk.Text(self.details_frame, wrap='word', font=("Helvetica", 12))
        self.details_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def setup_vehicles_tab(self):
        # Notebook for Timed In and Registered Vehicles tabs
        self.notebook = ttk.Notebook(self.vehicles_frame)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Timed In Tab (now the first tab)
        self.timed_in_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.timed_in_tab, text="Timed In")
        self.setup_timed_in_log()

        # Registered Vehicles Tab (now the second tab)
        self.registered_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.registered_tab, text="Registered Vehicles")
        self.setup_vehicles_table()


    def setup_vehicles_table(self):
        ttk.Label(self.registered_tab, text="Registered Vehicles", style="Header.TLabel").pack(pady=5)
        tree_frame = ttk.Frame(self.registered_tab)
        tree_frame.pack(fill='both', expand=True)

        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        columns = ("Plate ID", "Plate Number", "Model", "Proprietor",
                   "Driver Code", "First Name", "Last Name", "Driver Type", "Registered At",
                   "CR Expiry Date", "OR Expiry Date", "Driver License No")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                 yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=100, width=120)

        self.tree.pack(fill='both', expand=True)
        self.load_vehicle_data()

    def setup_timed_in_log(self):
        ttk.Label(self.timed_in_tab, text="Timed In Log", style="Header.TLabel").pack(pady=5)
        log_frame = ttk.Frame(self.timed_in_tab)
        log_frame.pack(fill='both', expand=True)

        scrollbar_y = ttk.Scrollbar(log_frame, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(log_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        log_columns = ("Plate Number", "Driver License No", "First Name", "Last Name", "Check-in Time")
        self.timed_in_tree = ttk.Treeview(log_frame, columns=log_columns, show='headings',
                                          yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        for col in log_columns:
            self.timed_in_tree.heading(col, text=col)
            self.timed_in_tree.column(col, minwidth=100, width=120)

        self.timed_in_tree.pack(fill='both', expand=True)

    def load_vehicle_data(self):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT plate_id, plate_number, model, proprietor,
                           driver_code, first_name, last_name, driver_type, registered_at,
                           cr_expiry_date, or_expiry_date, driver_license_no
                    FROM vehicles;
                """)
                records = cursor.fetchall()
            for record in records:
                self.tree.insert('', 'end', values=record)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load vehicle data: {str(e)}")

    def display_driver_info(self):
        plate_number = self.plate_entry.get()
        if not plate_number:
            messagebox.showwarning("Input Required", "Please enter a plate number.")
            return

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM vehicles WHERE plate_number = %s", (plate_number,))
                result = cursor.fetchone()

            if result:
                self.update_photo(result[9])
                details = (f"Name: {result[6]} {result[7]}\n"
                           f"Driver Type: {result[8]}\n"
                           f"Model: {result[2]}\n"
                           f"Proprietor: {result[4]}\n"
                           f"CR Expiry: {result[10]}\n"
                           f"OR Expiry: {result[11]}\n"
                           f"License No.: {result[12]}")
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, details)
                
                # Log check-in in Timed In tab
                check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.timed_in_tree.insert('', 'end', values=(
                    result[2], result[12], result[6], result[7], check_in_time
                ))
            else:
                messagebox.showinfo("Not Found", "Vehicle not found in the database.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch driver info: {str(e)}")

    def update_photo(self, photo_path):
        try:
            image = Image.open(photo_path)
            image = image.resize((150, 150), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.photo_label.configure(image=photo)
            self.photo_label.image = photo
        except Exception:
            self.photo_label.configure(text="Photo Unavailable")

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Main.TFrame", background="#F0F2F5")
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), background="#F0F2F5", foreground="green")
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), background="#F0F2F5")
        style.configure("Nav.TButton", font=("Helvetica", 12), padding=5)

