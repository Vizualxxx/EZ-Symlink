import os
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog, messagebox

def create_symbolic_links(source_dir, target_dir):
    if not os.path.exists(source_dir) or not os.path.exists(target_dir):
        return "Error: Source or target directory does not exist."

    messages = []

    for root, _, files in os.walk(source_dir):
        for item in files:
            source_path = os.path.join(root, item)
            relative_path = os.path.relpath(source_path, source_dir)
            target_path = os.path.join(target_dir, relative_path)

            if os.path.exists(target_path):
                messages.append(f"Warning: {item} already exists in the target directory. Skipping.")
            else:
                try:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    os.symlink(source_path, target_path)
                    messages.append(f"Created symbolic link: {target_path}")
                except OSError as e:
                    messages.append(f"Error creating symbolic link for {item}: {e}")
                except Exception as e:
                    messages.append(f"Unexpected error occurred for {item}: {e}")

    return "\n".join(messages)

def browse_button(entry):
    selected_directory = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, selected_directory)

def create_label_and_entry(root, text):
    label = ttk.Label(root, text=text)
    label.grid(sticky=tk.W, padx=5, pady=2)  # Align the label to the left
    entry = ttk.Entry(root)
    entry.grid(row=root.grid_size()[1] - 1, column=1, sticky=tk.W, padx=5, pady=2)  # Align the entry to the left
    return entry

def create_links():
    source_dir = entry_source.get()
    target_dir = entry_target.get()
    result = create_symbolic_links(source_dir, target_dir)
    messagebox.showinfo("Result", result)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Symbolic Link Creator")
    style = ttk.Style(root)
    style.theme_use('clam')

    entry_source = create_label_and_entry(root, "Source Directory:")
    entry_target = create_label_and_entry(root, "Target Directory:")

    # "Browse" buttons aligned to the right of the respective entry fields
    ttk.Button(root, text="Browse", command=lambda: browse_button(entry_source)).grid(row=0, column=2, padx=5, pady=2)
    ttk.Button(root, text="Browse", command=lambda: browse_button(entry_target)).grid(row=1, column=2, padx=5, pady=2)

    # "Create Links" button
    ttk.Button(root, text="Create Links", command=create_links).grid(row=root.grid_size()[1], columnspan=3, pady=10)

    # Set the initial size of the main window to 500x200 pixels
    root.geometry("500x200")

    root.mainloop()
