import os
import tkinter as tk
from tkinter import messagebox, filedialog

FOLDERS = ['1-RAW', '2-PROC', '3-EXPORT']

def directoryStructure(ROOT, ref, name, methods):
    topDir = os.path.join(ROOT, f'{ref}_{name.upper()}')
    os.makedirs(topDir, exist_ok=True)

    docFolder = os.path.join(topDir, f'EXTRA_DOCUMENTATION_{ref}')
    os.makedirs(docFolder, exist_ok=True)

    for meth in methods:
        subDir = os.path.join(topDir, f'{meth.upper()}_{ref}')
        for fold in FOLDERS:
            foldDir = os.path.join(subDir, f'{fold}_{meth.upper()}_{ref}')
            os.makedirs(foldDir, exist_ok=True)

def browse_root():
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        root_entry.delete(0, tk.END)
        root_entry.insert(0, selected_dir)

def create_folders():
    ROOT = root_entry.get()
    try:
        YEAR = int(year_entry.get())
        NR = int(nr_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "YEAR and NR must be numbers.")
        return

    short_name = shortname_entry.get().replace(' ', '_')
    ref_nr = f'AL{YEAR}-{str(NR).zfill(3)}'
    meths = [m.strip() for m in meths_entry.get().split(';') if m.strip()]

    if not (ROOT and short_name and meths):
        messagebox.showerror("Input Error", "Please fill in all fields correctly.")
        return

    try:
        directoryStructure(ROOT, ref_nr, short_name, meths)
        messagebox.showinfo("Success", "Folders created successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# --- GUI Setup ---
app = tk.Tk()
app.title("ArtLab UU Folder Structure Creator")
app.geometry("800x400")  # <-- Set size
app.resizable(False, False)  # <-- Fixed size window

# Center frame
center_frame = tk.Frame(app)
center_frame.place(relx=0.5, rely=0.5, anchor='center')

# ROOT
tk.Label(center_frame, text="ROOT Path:").grid(row=0, column=0, sticky='e', pady=5)
root_entry = tk.Entry(center_frame, width=40)
root_entry.grid(row=0, column=1, pady=5)
browse_button = tk.Button(center_frame, text="Browse", command=browse_root)
browse_button.grid(row=0, column=2, padx=5)
root_entry.insert(0, r"C:\artlab-research")

# YEAR
tk.Label(center_frame, text="YEAR:").grid(row=1, column=0, sticky='e', pady=5)
year_entry = tk.Entry(center_frame, width=40)
year_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky='w')
year_entry.insert(0, "2025")

# NR
tk.Label(center_frame, text="NR:").grid(row=2, column=0, sticky='e', pady=5)
nr_entry = tk.Entry(center_frame, width=40)
nr_entry.grid(row=2, column=1, columnspan=2, pady=5, sticky='w')
nr_entry.insert(0, "1")

# Short name
tk.Label(center_frame, text="Short Name:").grid(row=3, column=0, sticky='e', pady=5)
shortname_entry = tk.Entry(center_frame, width=40)
shortname_entry.grid(row=3, column=1, columnspan=2, pady=5, sticky='w')

# Methods
tk.Label(center_frame, text="Methods (semicolon-separated):").grid(row=4, column=0, sticky='e', pady=5)
meths_entry = tk.Entry(center_frame, width=40)
meths_entry.grid(row=4, column=1, columnspan=2, pady=5, sticky='w')

# Create button
create_button = tk.Button(center_frame, text="Create Folders", width=20, command=create_folders)
create_button.grid(row=5, columnspan=3, pady=20)

app.mainloop()
