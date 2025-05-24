import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.scrolledtext as scrolledtext
import sys

# Tree components (same as original)
PREFIX_MIDDLE = "├── "
PREFIX_LAST = "└── "
PREFIX_PARENT_MIDDLE = "│   "
PREFIX_PARENT_LAST = "    "

class DirectoryTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Directory Tree Generator")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)  # Handle window close button
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # Variables
        self.directory_path = tk.StringVar()
        self.show_hidden = tk.BooleanVar(value=False)
        self.dirs_only = tk.BooleanVar(value=False)
        self.depth_limit = tk.IntVar(value=0)  # 0 means no limit
        self.generation_running = False
        self.should_cancel = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Top frame for directory selection
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=0, column=0, sticky="ew")
        
        # Directory selection
        ttk.Label(top_frame, text="Directory:").grid(row=0, column=0, sticky="w")
        ttk.Entry(top_frame, textvariable=self.directory_path, width=50).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(top_frame, text="Browse...", command=self.browse_directory).grid(row=0, column=2, padx=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.root, text="Options", padding="10")
        options_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Checkboxes
        ttk.Checkbutton(options_frame, text="Show hidden files", variable=self.show_hidden).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(options_frame, text="Directories only", variable=self.dirs_only).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        # Depth limit
        ttk.Label(options_frame, text="Max depth (0=unlimited):").grid(row=0, column=1, sticky="e", padx=5)
        ttk.Spinbox(options_frame, from_=0, to=20, width=5, textvariable=self.depth_limit).grid(row=0, column=2, sticky="w", padx=5)
        
        # Generate button
        ttk.Button(options_frame, text="Generate Tree", command=self.generate_tree).grid(row=0, column=3, padx=10)
        
        # Tree display
        self.tree_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=('Courier', 10))
        self.tree_text.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        # Bottom buttons
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=3, column=0, sticky="ew")
        
        ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save to File", command=self.save_to_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.confirm_exit).pack(side=tk.RIGHT, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_path.set(directory)
            
    def generate_tree(self):
        if self.generation_running:
            return
            
        directory = self.directory_path.get()
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("Error", "Please select a valid directory")
            return
            
        self.tree_text.delete(1.0, tk.END)
        self.tree_text.insert(tk.END, f"Generating tree for: {directory}\n")
        self.tree_text.insert(tk.END, "-" * 50 + "\n")
        
        # Reset flags
        self.generation_running = True
        self.should_cancel = False
        
        # Disable controls during generation
        self._set_controls_state(tk.DISABLED)
        
        # Start generation in a separate thread to keep UI responsive
        import threading
        threading.Thread(target=self._generate_tree_thread, args=(directory,), daemon=True).start()
    
    def _generate_tree_thread(self, directory):
        """Run the tree generation in a separate thread"""
        try:
            dir_count, file_count = self._generate_tree(
                directory,
                level=0,
                limit_depth=self.depth_limit.get() if self.depth_limit.get() > 0 else None,
                show_hidden=self.show_hidden.get(),
                dir_only=self.dirs_only.get()
            )
            
            if not self.should_cancel:
                self.root.after(0, self._update_summary, dir_count, file_count)
                
        except Exception as e:
            if not self.should_cancel:
                self.root.after(0, self.tree_text.insert, tk.END, f"\nError: {str(e)}\n")
        finally:
            self.root.after(0, self._generation_complete)
    
    def _update_summary(self, dir_count, file_count):
        """Update the UI with the generation summary"""
        self.tree_text.insert(tk.END, "-" * 50 + "\n")
        summary = []
        if not self.dirs_only.get():
            summary.append(f"{dir_count} director{'y' if dir_count == 1 else 'ies'}")
            summary.append(f"{file_count} file{'s' if file_count != 1 else ''}")
        else:
            summary.append(f"{dir_count} director{'y' if dir_count == 1 else 'ies'}")
        
        self.tree_text.insert(tk.END, ", ".join(summary) + "\n")
    
    def _generation_complete(self):
        """Clean up after tree generation completes"""
        self.generation_running = False
        self._set_controls_state(tk.NORMAL)
    
    def _set_controls_state(self, state):
        """Enable/disable controls during generation"""
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Button, ttk.Checkbutton, ttk.Spinbox)) and widget.winfo_name() != "!button4":  # Don't disable Exit button
                widget.state(["!disabled"] if state == tk.NORMAL else ["disabled"])
            elif isinstance(widget, ttk.Entry):
                widget.state(["!readonly"] if state == tk.NORMAL else ["readonly"])
    
    def _generate_tree(self, directory, prefix="", level=0, limit_depth=None, show_hidden=False, dir_only=False, ignore_list=None):
        """Modified version of the original generate_tree function for use with GUI"""
        if ignore_list is None:
            ignore_list = []

        if level == 0:  # Root call
            self.root.after(0, self.tree_text.insert, tk.END, os.path.basename(os.path.abspath(directory)) + "\n")
            level = 1  # Start actual depth counting
        
        if limit_depth is not None and level > limit_depth:
            return 0, 0  # dir_count, file_count

        try:
            # Get all items, then filter
            all_items = os.listdir(directory)
            items = []
            for item_name in all_items:
                if self.should_cancel:  # Check if we should stop
                    return 0, 0
                    
                if not show_hidden and item_name.startswith('.'):
                    continue
                if item_name in ignore_list:
                    continue
                items.append(item_name)
            items.sort()  # Sort for consistent output
        except PermissionError:
            self.root.after(0, self.tree_text.insert, tk.END, f"{prefix}{PREFIX_MIDDLE}[Error: Permission Denied for {os.path.basename(directory)}]\n")
            return 0, 0
        except FileNotFoundError:
            self.root.after(0, self.tree_text.insert, tk.END, f"{prefix}{PREFIX_MIDDLE}[Error: Directory Not Found: {os.path.basename(directory)}]\n")
            return 0, 0

        dir_count = 0
        file_count = 0
        pointers = [PREFIX_MIDDLE] * (len(items) - 1) + [PREFIX_LAST]

        for pointer, item_name in zip(pointers, items):
            if self.should_cancel:  # Check if we should stop
                return dir_count, file_count
                
            path = os.path.join(directory, item_name)
            is_dir = os.path.isdir(path)

            if dir_only and not is_dir:
                continue  # Skip files if only directories are requested

            self.root.after(0, self.tree_text.insert, tk.END, f"{prefix}{pointer}{item_name}\n")
            self.root.after(0, self.tree_text.see, tk.END)  # Auto-scroll to the end
            self.root.update()  # Allow GUI to process events

            if is_dir:
                dir_count += 1
                # Determine the new prefix for children
                extension = PREFIX_PARENT_MIDDLE if pointer == PREFIX_MIDDLE else PREFIX_PARENT_LAST
                # Recursively call for subdirectories
                sub_d_count, sub_f_count = self._generate_tree(
                    path,
                    prefix + extension,
                    level + 1,
                    limit_depth,
                    show_hidden,
                    dir_only,
                    ignore_list
                )
                dir_count += sub_d_count
                file_count += sub_f_count
            else:
                file_count += 1
                
            # Small delay to keep UI responsive
            if level % 3 == 0:  # Only update every few levels
                self.root.update()
                
        return dir_count, file_count
    
    def copy_to_clipboard(self):
        text = self.tree_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "No tree to copy")
            return
            
        # Split into lines and remove header and footer
        lines = text.split('\n')
        # Find the start of the tree (after the line of dashes)
        try:
            start_idx = next(i for i, line in enumerate(lines) if line.startswith('----')) + 1
            # Find the end of the tree (before the summary line)
            end_idx = next((i for i, line in enumerate(lines) if i > start_idx and line.startswith('----')), len(lines) - 1)
            # Get just the tree portion
            tree_lines = lines[start_idx:end_idx]
            # Remove any empty lines at the beginning or end
            while tree_lines and not tree_lines[0].strip():
                tree_lines.pop(0)
            while tree_lines and not tree_lines[-1].strip():
                tree_lines.pop()
            # Join back with newlines
            clean_text = '\n'.join(tree_lines)
        except StopIteration:
            clean_text = text  # Fallback to original text if parsing fails
            
        self.root.clipboard_clear()
        self.root.clipboard_append(clean_text)
        messagebox.showinfo("Success", "Tree copied to clipboard!")
    
    def save_to_file(self):
        text = self.tree_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "No tree to save")
            return
            
        # Clean the text to remove header and footer (same as in copy_to_clipboard)
        lines = text.split('\n')
        try:
            start_idx = next(i for i, line in enumerate(lines) if line.startswith('----')) + 1
            end_idx = next((i for i, line in enumerate(lines) if i > start_idx and line.startswith('----')), len(lines) - 1)
            tree_lines = lines[start_idx:end_idx]
            while tree_lines and not tree_lines[0].strip():
                tree_lines.pop(0)
            while tree_lines and not tree_lines[-1].strip():
                tree_lines.pop()
            clean_text = '\n'.join(tree_lines)
        except StopIteration:
            clean_text = text  # Fallback to original text if parsing fails
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Tree As"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(clean_text)
                messagebox.showinfo("Success", f"Tree saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def confirm_exit(self):
        """Show confirmation dialog before exiting"""
        if not self.generation_running:
            self.root.quit()
            return
            
        # Only show confirmation if generation is running
        if messagebox.askyesno("Generation in Progress", 
                             "A directory tree is currently being generated.\n"
                             "Do you want to cancel generation and exit?"):
            self.should_cancel = True
            # Schedule the exit for after generation is cancelled
            self.root.after(100, self._check_generation_and_exit)
    
    def _check_generation_and_exit(self):
        """Check if generation has stopped and exit if it has"""
        if self.generation_running:
            # Check again in 100ms
            self.root.after(100, self._check_generation_and_exit)
        else:
            self.root.quit()
            
    def clear_output(self):
        self.tree_text.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = DirectoryTreeApp(root)
    
    # Set application icon (if you have one)
    # try:
    #     root.iconbitmap('icon.ico')  # Place icon.ico in the same directory
    # except:
    #     pass  # Icon not found, use default
    
    # Center the window
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
