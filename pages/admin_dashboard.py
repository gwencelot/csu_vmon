import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from database.db_connection import get_db_connection
from pages.manage_user import ManageUser
from pages.vehicle_display import VehicleDisplay

class AdminDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Admin Dashboard")
        self.root.configure(bg="#F5F5F5")
        self.root.geometry("1400x800")

        # Load and set background image
        try:
            bg_image = Image.open("images/csu-1-e1643418396913.jpeg")  # Adjust path as needed
            bg_image = bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(self.root, image=self.bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Could not load background image: {e}")

        # Set custom styles
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), foreground="#333333")
        style.configure("TFrame", background="#FFFFFF")
        style.configure("TLabel", font=("Helvetica", 12), foreground="#333333", background="#FFFFFF")
        style.configure("TEntry", font=("Helvetica", 12))
        style.configure("TCombobox", font=("Helvetica", 12))
        style.configure("Logout.TButton", font=("Helvetica", 12, "bold"), foreground="black")

        # Main container frame
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True)

        # Header frame with logo and logout button
        self.header_frame = ttk.Frame(self.main_container)
        self.header_frame.pack(fill='x', pady=10)

        # Logo label
        self.logo_label = ttk.Label(self.header_frame)
        self.logo_label.pack(side='left', padx=10)
        try:
            logo_image = Image.open("images/lcsu2-02.jpeg")
            logo_image = logo_image.resize((50, 50), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            self.logo_label.configure(image=logo_photo)
            self.logo_label.image = logo_photo
        except Exception as e:
            self.logo_label.configure(text="Logo")

        # Header text
        self.header_label = ttk.Label(
            self.header_frame,
            text="CSU Vehicle Monitoring System",
            font=("Helvetica", 16, "bold"),
            foreground="green"
        )
        self.header_label.pack(side='left', padx=10)

        # Logout button
        self.logout_button = ttk.Button(
            self.header_frame,
            text="Logout",
            command=self.logout,
            style="Logout.TButton"
        )
        self.logout_button.pack(side='right', padx=10)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Initialize vehicle_display and other required variables
        self.vehicle_display = None
        self.current_photo = None

        # Create the tabs
        self.create_registration_tab()
        self.create_manage_users_tab()
        self.create_vehicles_tab()

        self.root.mainloop()

    def create_registration_tab(self):
        self.registration_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.registration_frame, text='Registration')

        # Vehicle information container
        vehicle_info_frame = ttk.Frame(self.registration_frame, style="TFrame")
        vehicle_info_frame.pack(expand=True, padx=10, pady=10, anchor='center')

        # Vehicle details section
        self.create_vehicle_widgets(vehicle_info_frame)

        # Button container
        button_frame = ttk.Frame(vehicle_info_frame)
        button_frame.grid(row=13, column=0, columnspan=2, pady=15, sticky="ew")

        # Register and upload photo buttons
        ttk.Button(button_frame, text="Register Vehicle", command=self.register_vehicle,
                   style="TButton").pack(side='left', padx=5)
        ttk.Button(button_frame, text="Upload Photo", command=self.upload_image,
                   style="TButton").pack(side='left', padx=5)

    def create_vehicle_widgets(self, frame):
        # Updated labels list without 'Certificate' and with renamed 'cr_expiry_date'
        labels = ["Plate ID", "Plate Number", "Model", "Proprietor",
                  "Driver Code", "First Name", "Last Name", "Driver Type", "Driver Photo",
                  "CR Expiry Date", "OR Expiry Date", "Driver License No"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(frame, text=label, style="TLabel").grid(row=i, column=0, padx=5, pady=5, sticky='e')
            if label == "Driver Type":
                self.driver_type_var = tk.StringVar()
                driver_types = ["Employee Parking", "Board of Regent", "Agencies", "CSU VIP's",
                                "Drop-off", "Graduate", "Undergraduate", "Concessionaire"]
                dropdown = ttk.Combobox(frame, textvariable=self.driver_type_var, values=driver_types,
                                        width=28)
                dropdown.grid(row=i, column=1, padx=5, pady=5, sticky='w')
                self.entries['driver_type'] = dropdown
            elif label in ["CR Expiry Date", "OR Expiry Date"]:
                date_entry = ttk.Entry(frame, width=30)
                date_entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
                self.entries[label.lower().replace(" ", "_")] = date_entry
            else:
                entry = ttk.Entry(frame, width=30)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
                self.entries[label.lower().replace(" ", "_")] = entry

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if file_path:
            self.entries['driver_photo'].delete(0, tk.END)
            self.entries['driver_photo'].insert(0, file_path)

    def register_vehicle(self):
        data = {key: entry.get() for key, entry in self.entries.items()}
        data['driver_type'] = self.driver_type_var.get()

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO vehicles (plate_id, plate_number, model, proprietor,
                driver_code, first_name, last_name, driver_type, driver_photo, 
                cr_expiry_date, or_expiry_date, driver_license_no)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['plate_id'], data['plate_number'], data['model'],
                  data['proprietor'], data['driver_code'], data['first_name'],
                  data['last_name'], data['driver_type'], data['driver_photo'],
                  data['cr_expiry_date'], data['or_expiry_date'], data['driver_license_no']))
            conn.commit()
            messagebox.showinfo("Success", "Vehicle registered successfully!")
            for entry in self.entries.values():
                if hasattr(entry, 'delete'):
                    entry.delete(0, tk.END)
            self.driver_type_var.set('')
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def create_vehicles_tab(self):
        self.vehicle_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.vehicle_frame, text='Vehicles')
        self.vehicle_display = VehicleDisplay(self.vehicle_frame, self)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        tab = event.widget.tab('current')['text']
        if tab == 'Vehicles':
            self.vehicle_display.display_vehicles()

    def create_manage_users_tab(self):
        self.manage_users_frame = ManageUser(self.notebook)
        self.notebook.add(self.manage_users_frame, text='Manage Users')

    def update_vehicle(self, record):
        # Remove certificate and use 'cr_expiry_date'
        for key in self.entries:
            self.entries[key].delete(0, tk.END)
        self.entries['plate_id'].insert(0, record[1])
        self.entries['plate_number'].insert(0, record[2])
        self.entries['model'].insert(0, record[3])
        self.entries['proprietor'].insert(0, record[4])
        self.entries['driver_code'].insert(0, record[5])
        self.entries['first_name'].insert(0, record[6])
        self.entries['last_name'].insert(0, record[7])
        self.driver_type_var.set(record[8])
        self.entries['driver_photo'].insert(0, record[9])
        self.entries['cr_expiry_date'].insert(0, record[10])
        self.entries['or_expiry_date'].insert(0, record[11])
        self.entries['driver_license_no'].insert(0, record[12])

        self.notebook.select(self.registration_frame)
        ttk.Button(self.registration_frame, text="Save Changes",
                  command=lambda: self.save_updates(record[0])).grid(row=14, column=0,
                                                                   columnspan=2, padx=10, pady=10)

    def save_updates(self, vehicle_id):
        data = {key: entry.get() for key, entry in self.entries.items()}
        data['driver_type'] = self.driver_type_var.get()

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE vehicles
                SET plate_id=%s, plate_number=%s, model=%s, proprietor=%s,
                    driver_code=%s, first_name=%s, last_name=%s, driver_type=%s, driver_photo=%s,
                    cr_expiry_date=%s, or_expiry_date=%s, driver_license_no=%s
                WHERE vehicle_id=%s
            """, (data['plate_id'], data['plate_number'], data['model'],
                  data['proprietor'], data['driver_code'], data['first_name'],
                  data['last_name'], data['driver_type'], data['driver_photo'],
                  data['cr_expiry_date'], data['or_expiry_date'], data['driver_license_no'], vehicle_id))
            conn.commit()
            messagebox.showinfo("Success", "Vehicle details updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()
