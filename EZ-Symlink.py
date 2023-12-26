import os
import sys
import ctypes
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from concurrent.futures import ThreadPoolExecutor
from tkfilebrowser import askopendirnames

# Function to check if the script is running with administrator privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Function to run the script as an administrator
def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(['"' + arg + '"' for arg in sys.argv]), None, 1)

# Function to create symbolic links
def create_symbolic_links(source_paths, target_dir, progress_callback):
    if not os.path.exists(target_dir):
        logging.error("Error: Target directory does not exist.")
        return

    total_files = len(source_paths)
    completed_files = 0

    for source_path in source_paths:
        if os.path.isdir(source_path):
            for root, _, files in os.walk(source_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, start=source_path)
                    target_path = os.path.join(target_dir, relative_path)
                    link_file(full_path, target_path)
                    completed_files += 1
                    progress_callback(completed_files / total_files)
        else:
            relative_path = os.path.basename(source_path)
            target_path = os.path.join(target_dir, relative_path)
            link_file(source_path, target_path)
            completed_files += 1
            progress_callback(completed_files / total_files)

def link_file(source_path, target_path):
    if os.path.exists(target_path):
        logging.warning(f"Warning: {target_path} already exists. Skipping.")
    else:
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            os.symlink(source_path, target_path)
            logging.info(f"Created symbolic link: {target_path}")
        except OSError as e:
            logging.error(f"Error creating symbolic link: {e}")

def browse_button(entry):
    selected_paths = askopendirnames(title="Select Files and/or Directories")
    entry.delete(0, tk.END)
    entry.insert(0, '; '.join(selected_paths))

def create_links():
    source_paths = entry_source.get().split('; ')
    target_dir = entry_target.get()
    create_button.config(state=tk.DISABLED)
    progress_bar['value'] = 0

    def link_creation_thread():
        create_symbolic_links(source_paths, target_dir, update_progress)
        messagebox.showinfo("Result", "Symbolic links creation completed!")
        create_button.config(state=tk.NORMAL)

    threading.Thread(target=link_creation_thread).start()

def update_progress(progress):
    progress_bar['value'] = progress * 100
    root.update_idletasks()

def create_label_and_entry(root, text):
    label = ttk.Label(root, text=text)
    label.grid(sticky=tk.W, padx=5, pady=2)
    entry = ttk.Entry(root)
    entry.grid(row=root.grid_size()[1] - 1, column=1, sticky=tk.W, padx=5, pady=2)
    return entry

if __name__ == "__main__":
    if is_admin():
        # Create the main application window
        root = tk.Tk()
        root.title("Symbolic Link Creator")
        style = ttk.Style(root)
        style.theme_use('clam')

        entry_source = create_label_and_entry(root, "Source Paths:")
        entry_target = create_label_and_entry(root, "Target Directory:")

        ttk.Button(root, text="Browse", command=lambda: browse_button(entry_source)).grid(row=0, column=2, padx=5, pady=2)
        ttk.Button(root, text="Browse", command=lambda: browse_button(entry_target)).grid(row=1, column=2, padx=5, pady=2)

        create_button = ttk.Button(root, text="Create Links", command=create_links)
        create_button.grid(row=2, columnspan=3, pady=10)

        progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate')
        progress_bar.grid(row=3, columnspan=3, pady=5)

        root.geometry("350x150")
        root.mainloop()
    else:
        # If not admin, rerun the script with admin rights
        run_as_admin()
