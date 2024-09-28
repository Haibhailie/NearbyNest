import customtkinter as ctk
from tkinter import scrolledtext  # Import scrolled text for console log
from tkinter import ttk
import os
import csv
import json
import subprocess
import threading
import pandas as pd

# Set the theme to 'dark' mode to match CustomTkinter
ctk.set_appearance_mode("dark")  # Modes: system, light, dark
ctk.set_default_color_theme("dark-blue")  # Theme color

# Function to load initial data from config.json and addresses.csv
def load_data():
    try:
        # Load API keys and amenities from config.json
        with open('config.json') as f:
            config_data = json.load(f)
        
        google_api_key.set(config_data.get('google_maps_api_key', ''))
        ipinfo_key.set(config_data.get('ipinfo_io_api_key', ''))
        amenities_list = config_data.get('amenities', '')
        amenities_entry.insert(0, amenities_list)
    except json.JSONDecodeError:
        console_log.insert(ctk.END, "Error: config.json is either empty or has invalid JSON formatting.\n")
    except FileNotFoundError:
        console_log.insert(ctk.END, "Error: config.json file not found. Please create the file with appropriate values.\n")

    # Load addresses from addresses.csv
    try:
        addresses_df = pd.read_csv('addresses.csv')
        for idx, row in addresses_df.iterrows():
            addresses_table.insert('', 'end', values=(row['MLS'], row['Address']))
    except FileNotFoundError:
        console_log.insert(ctk.END, "Error: addresses.csv file not found.\n")

# Function to save API keys and amenities back to config.json
def save_config():
    with open('config.json', 'w') as f:
        config_data = {
            'google_maps_api_key': google_api_key.get(),
            'ipinfo_io_api_key': ipinfo_key.get(),
            'amenities': amenities_entry.get()
        }
        json.dump(config_data, f, indent=4)
    console_log.insert(ctk.END, "Config saved successfully.\n")

# Function to save new addresses to addresses.csv
def save_addresses():
    with open('addresses.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['MLS', 'Address'])  # Write headers
        for row in addresses_table.get_children():
            writer.writerow(addresses_table.item(row)['values'])
    console_log.insert(ctk.END, "Addresses saved successfully.\n")

# Function to add new address to the table
def add_address():
    mls = mls_entry.get()
    address = address_entry.get()
    if mls and address:
        addresses_table.insert('', 'end', values=(mls, address))
        mls_entry.delete(0, ctk.END)
        address_entry.delete(0, ctk.END)
        console_log.insert(ctk.END, f"Address added: {mls}, {address}\n")
    else:
        console_log.insert(ctk.END, "Input Error: Please provide both MLS and Address.\n")

# Function to delete selected address from the table
def delete_address():
    selected_item = addresses_table.selection()
    if selected_item:
        addresses_table.delete(selected_item)
        console_log.insert(ctk.END, "Address deleted.\n")
    else:
        console_log.insert(ctk.END, "Selection Error: Please select an address to delete.\n")

# Function to run NearbyNest.py script
def run_nearbynest():
    # Save config and addresses before running
    save_config()
    save_addresses()

    # Update status in console
    console_log.insert(ctk.END, "Config and addresses saved. Executing script...\n")
    
    # Start progress bar animation
    progress_bar.start()

    # Run the script in a separate thread to keep the UI responsive
    threading.Thread(target=execute_script).start()

# Function to run the NearbyNest.py script and capture the output
def execute_script():
    try:
        # Disable buffering for real-time output
        process = subprocess.Popen(
            ['python', 'NearbyNest.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Capture output in real-time
        for line in process.stdout:
            console_log.insert(ctk.END, line)
            console_log.see(ctk.END)  # Scroll to the end as new lines are added
            root.update_idletasks()  # Force update to ensure GUI stays responsive

        process.wait()  # Wait for the process to complete

        if process.returncode == 0:
            console_log.insert(ctk.END, "NearbyNest script executed successfully!\n")
        else:
            console_log.insert(ctk.END, f"Error: NearbyNest script returned an error (code {process.returncode}).\n")

    except Exception as e:
        console_log.insert(ctk.END, f"Error: {e}\n")

    # Stop progress bar animation
    progress_bar.stop()

# Set up the main CustomTkinter window
root = ctk.CTk()
root.title("NearbyNest Configuration")
root.geometry("800x850")

# Font styles (move them after initializing the root window)
title_font = ctk.CTkFont(size=28, weight="bold")
label_font = ctk.CTkFont(size=18)
entry_font = ctk.CTkFont(size=16)

# Configure grid to give equal weight to all columns for central alignment and rows to be responsive
for col in range(4):
    root.grid_columnconfigure(col, weight=1, minsize=100)  # Makes columns responsive to resizing
for row in range(14):
    root.grid_rowconfigure(row, weight=1, minsize=40)  # Makes rows responsive to resizing

# Title: "NearbyNest"
title_label = ctk.CTkLabel(root, text="NearbyNest", font=title_font)
title_label.grid(row=0, column=0, columnspan=4, padx=10, pady=20, sticky="ew")  # Centered across columns

# Set up the style for the Treeview to match the dark theme
style = ttk.Style()
style.theme_use("clam")  # Use 'clam' theme for more customization options
style.configure("Treeview", 
                background="#2b2b2b", 
                foreground="white", 
                rowheight=25, 
                fieldbackground="#2b2b2b")

style.configure("Treeview.Heading", 
                background="#1f1f1f", 
                foreground="white", 
                relief="flat")

style.map('Treeview', 
          background=[('selected', '#4d4d4d')], 
          foreground=[('selected', 'white')])

# API Key fields
google_api_key = ctk.StringVar()
ipinfo_key = ctk.StringVar()

google_api_label = ctk.CTkLabel(root, text="Google Maps API Key", font=label_font)  # Removed colon
google_api_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
google_api_entry = ctk.CTkEntry(root, textvariable=google_api_key, font=entry_font, width=240)
google_api_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=3, sticky="ew")  # Center align by spanning columns

ipinfo_key_label = ctk.CTkLabel(root, text="Open IP API Key", font=label_font)  # Removed colon
ipinfo_key_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
ipinfo_key_entry = ctk.CTkEntry(root, textvariable=ipinfo_key, font=entry_font, width=240)
ipinfo_key_entry.grid(row=2, column=1, padx=10, pady=10, columnspan=3, sticky="ew")  # Center align by spanning columns

# Addresses table
addresses_label = ctk.CTkLabel(root, text="MLS & Address", font=label_font)  # Removed colon
addresses_label.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=4)  # Center-align

# Define the table (Treeview)
addresses_table = ttk.Treeview(root, columns=('MLS', 'Address'), show='headings', height=8)
addresses_table.heading('MLS', text='MLS')
addresses_table.heading('Address', text='Address')
addresses_table.grid(row=4, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

# Add Address form
mls_entry_label = ctk.CTkLabel(root, text="MLS", font=label_font)  # Removed colon
mls_entry_label.grid(row=5, column=0, padx=10, pady=5, sticky="e")
mls_entry = ctk.CTkEntry(root, font=entry_font, width=200)
mls_entry.grid(row=5, column=1, padx=10, pady=5, columnspan=3, sticky="ew")  # Center align by spanning columns

address_entry_label = ctk.CTkLabel(root, text="Address", font=label_font)  # Removed colon
address_entry_label.grid(row=6, column=0, padx=10, pady=5, sticky="e")
address_entry = ctk.CTkEntry(root, font=entry_font, width=240)
address_entry.grid(row=6, column=1, padx=10, pady=5, columnspan=3, sticky="ew")  # Center align by spanning columns

add_address_button = ctk.CTkButton(root, text="Add Address", command=add_address)
add_address_button.grid(row=7, column=1, padx=10, pady=5, sticky="ew", columnspan=1)  # Center align

delete_address_button = ctk.CTkButton(root, text="Delete Address", command=delete_address)
delete_address_button.grid(row=7, column=2, padx=10, pady=5, sticky="ew", columnspan=1)  # Center align

# Amenities field
amenities_label = ctk.CTkLabel(root, text="Amenities (comma-separated)", font=label_font)  # Removed colon
amenities_label.grid(row=8, column=0, padx=10, pady=10, sticky="ew", columnspan=4)  # Center-align

amenities_entry = ctk.CTkEntry(root, font=entry_font, width=450)
amenities_entry.grid(row=9, column=0, columnspan=4, padx=10, pady=10, sticky="ew")  # Center-align

# Save buttons
save_config_button = ctk.CTkButton(root, text="Save Config", command=save_config)
save_config_button.grid(row=10, column=1, padx=10, pady=20, sticky="ew", columnspan=1)  # Center-align

save_addresses_button = ctk.CTkButton(root, text="Save Addresses", command=save_addresses)
save_addresses_button.grid(row=10, column=2, padx=10, pady=20, sticky="ew", columnspan=1)  # Center-align

# Add Search button to run NearbyNest.py
search_button = ctk.CTkButton(root, text="Search", command=run_nearbynest)
search_button.grid(row=11, column=1, columnspan=2, pady=20, sticky="ew")  # Center align the button

# Console log for displaying real-time output
console_label = ctk.CTkLabel(root, text="Console Log", font=label_font)  # Removed colon
console_label.grid(row=12, column=0, padx=10, pady=10, sticky="ew", columnspan=4)  # Center-align

console_log = scrolledtext.ScrolledText(root, height=8, bg="#2b2b2b", fg="white", wrap="word", state="normal", font=entry_font)
console_log.grid(row=13, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

# Progress bar to indicate the script is running
progress_bar = ctk.CTkProgressBar(root, mode="indeterminate")
progress_bar.grid(row=14, column=0, columnspan=4, padx=10, pady=20, sticky="ew")

# Load the data on start
load_data()

# Automatically adjust window size to fit content
root.update()  # Update geometry calculations
root.geometry(f'{root.winfo_reqwidth()}x{root.winfo_reqheight()}')  # Set window size to fit content

# Start the Tkinter event loop
root.mainloop()
