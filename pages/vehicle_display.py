import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from database.db_connection import get_db_connection
import os

class UpdateVehicleModal:
    def __init__(self, parent, vehicle_data):
        self.top = tk.Toplevel(parent)
        self.top.title("Update Vehicle")
        self.top.geometry("500x700")
        self.vehicle_data = vehicle_data

        # Make the modal window modal
        self.top.grab_set()
        self.center_window()
        
        # Variable to hold the new photo path
        self.new_photo_path = None

        # Create form widgets for all vehicle details
        self.create_widgets()

    def center_window(self):
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.top, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas with scrollbar for a larger number of fields
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form fields for vehicle details including renamed and new fields
        fields = [
            ("Plate ID:", self.vehicle_data[1]),
            ("Plate Number:", self.vehicle_data[2]),
            ("Model:", self.vehicle_data[3]),
            ("Proprietor:", self.vehicle_data[4]),
            ("Driver Code:", self.vehicle_data[5]),
            ("First Name:", self.vehicle_data[6]),
            ("Last Name:", self.vehicle_data[7]),
            ("Driver Type:", self.vehicle_data[8]),
            ("CR Expiry Date:", self.vehicle_data[10]),
            ("OR Expiry Date:", self.vehicle_data[11]),
            ("Driver License No:", self.vehicle_data[12])
        ]

        self.entries = {}
        for i, (label_text, value) in enumerate(fields):
            label = ttk.Label(scrollable_frame, text=label_text)
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            if label_text == "Driver Type:":
                entry = ttk.Combobox(scrollable_frame, values=["professional", "non-professional"])
                entry.set(value if value else "professional")
            else:
                entry = ttk.Entry(scrollable_frame, width=40)
                entry.insert(0, value if value else "")

            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.entries[label_text] = entry

        # Upload photo button
        ttk.Label(scrollable_frame, text="Driver Photo:").grid(row=len(fields), column=0, padx=5, pady=5, sticky="e")
        self.photo_button = ttk.Button(scrollable_frame, text="Upload Photo", command=self.upload_photo)
        self.photo_button.grid(row=len(fields), column=1, padx=5, pady=5, sticky="w")

        # Buttons frame for save and cancel
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT, padx=5)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def upload_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select Driver Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.new_photo_path = file_path
            messagebox.showinfo("Photo Selected", "Photo has been selected successfully.")

    def save_changes(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            update_query = """
            UPDATE vehicles
            SET plate_id = %s, plate_number = %s, model = %s,
                proprietor = %s, driver_code = %s,
                first_name = %s, last_name = %s, driver_type = %s, driver_photo = %s,
                cr_expiry_date = %s, or_expiry_date = %s, driver_license_no = %s
            WHERE vehicle_id = %s
            """

            driver_photo_path = self.new_photo_path if self.new_photo_path else self.vehicle_data[9]

            values = (
                self.entries["Plate ID:"].get(),
                self.entries["Plate Number:"].get(),
                self.entries["Model:"].get(),
                self.entries["Proprietor:"].get(),
                self.entries["Driver Code:"].get(),
                self.entries["First Name:"].get(),
                self.entries["Last Name:"].get(),
                self.entries["Driver Type:"].get(),
                driver_photo_path,
                self.entries["CR Expiry Date:"].get(),
                self.entries["OR Expiry Date:"].get(),
                self.entries["Driver License No:"].get(),
                self.vehicle_data[0]  # vehicle_id
            )

            cursor.execute(update_query, values)
            conn.commit()
            messagebox.showinfo("Success", "Vehicle information updated successfully!")
            self.top.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update vehicle information: {str(e)}")
        finally:
            cursor.close()
            conn.close()

class VehicleDisplay:
    def __init__(self, vehicle_frame, parent):
        self.vehicle_frame = vehicle_frame
        self.parent = parent
        self.current_record = None
        self.current_photo = None
        self.selected_row = None
        self.selected_record = None
        self.scrollable_frame = None
        self.image_box = None

        # Define a style for the application
        style = ttk.Style()
        style.configure("TFrame", background="#F0F0F0")
        style.configure("TLabel", font=("Helvetica", 10), background="#F0F0F0")
        style.configure("TButton", font=("Helvetica", 10), padding=5)

    def display_vehicles(self):
        # Clear existing content in vehicle_frame
        for widget in self.vehicle_frame.winfo_children():
            widget.destroy()

        # Create main container frame
        self.main_container = ttk.Frame(self.vehicle_frame, style="TFrame")
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Create left frame for vehicle list
        self.left_frame = ttk.Frame(self.main_container, style="TFrame")
        self.left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Create right frame for photo and details
        self.right_frame = ttk.Frame(self.main_container, style="TFrame")
        self.right_frame.pack(side='right', fill='y', padx=10, pady=10)

        # Create and configure image box in right frame
        self.image_box = ttk.Label(self.right_frame, text="Driver Photo", anchor='center', style="TLabel")
        self.image_box.pack(pady=10)

        # Create scrollable frame for vehicle list
        canvas = tk.Canvas(self.left_frame, bg="#FFFFFF")
        v_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.left_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.scrollable_frame = scrollable_frame  # Store reference to scrollable_frame

        # Create headers
        labels = ["Vehicle ID", "Plate ID", "Plate Number", "Model", "Proprietor", 
                  "CR Expiry Date", "OR Expiry Date", "License No.", "Actions"]
        for i, label in enumerate(labels):
            ttk.Label(scrollable_frame, text=label, font=('Helvetica', 10, 'bold'), style="TLabel").grid(row=0,
                                                                                                          column=i,
                                                                                                          padx=5,
                                                                                                          pady=5)

        # Fetch and display vehicle records
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM vehicles")
            records = cursor.fetchall()

            for i, record in enumerate(records, start=1):
                essential_info = [str(record[0]), record[1], record[2], record[3], record[4],
                                  record[10], record[11], record[12]]
                row_labels = []
                for j, value in enumerate(essential_info):
                    label = ttk.Label(scrollable_frame, text=value, style="TLabel")
                    label.grid(row=i, column=j, padx=5, pady=2)
                    row_labels.append(label)
                    label.bind("<Button-1>", lambda e, r=record, rl=row_labels: self.select_row(r, rl))

                    if self.selected_record and record[0] == self.selected_record[0]:
                        label.config(background="lightblue")
                        self.selected_row = row_labels
                        self.show_details(record)

                action_frame = ttk.Frame(scrollable_frame, style="TFrame")
                action_frame.grid(row=i, column=len(essential_info), padx=5, pady=2)

                ttk.Button(action_frame, text="Update",
                           command=lambda r=record: self.show_update_modal(r),
                           style="TButton").pack(side='left', padx=2)
                ttk.Button(action_frame, text="Delete",
                           command=lambda r=record[0]: self.delete_vehicle(r), style="TButton").pack(side='left',
                                                                                                     padx=2)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch vehicle records: {str(e)}")
        finally:
            cursor.close()
            conn.close()

        # Pack scrollbars and canvas
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

    def select_row(self, record, row_labels):
        if self.selected_row:
            for label in self.selected_row:
                label.config(background="#F0F0F0")

        for label in row_labels:
            label.config(background="lightblue")

        self.selected_row = row_labels
        self.selected_record = record
        self.show_details(record)

    def show_details(self, record):
        self.current_record = record
        if len(record) > 9 and record[9]:  # Update column index for photo path if necessary
            self.update_image(record[9])

    def update_image(self, driver_photo_path):
        try:
            if driver_photo_path and isinstance(driver_photo_path, str):
                image = Image.open(driver_photo_path)
                image = image.resize((200, 200), Image.LANCZOS)
                self.current_photo = ImageTk.PhotoImage(image)
                self.image_box.config(image=self.current_photo)
            else:
                self.image_box.config(text="No Image Available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.image_box.config(image='')

    def show_update_modal(self, record):
        update_modal = UpdateVehicleModal(self.vehicle_frame, record)
        self.vehicle_frame.wait_window(update_modal.top)
        self.display_vehicles()

    def delete_vehicle(self, vehicle_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this vehicle?"):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
                conn.commit()
                messagebox.showinfo("Success", "Vehicle deleted successfully!")
                self.display_vehicles()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete vehicle: {str(e)}")
            finally:
                cursor.close()
                conn.close()
