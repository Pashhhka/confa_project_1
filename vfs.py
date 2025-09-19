import tkinter as tk
from tkinter import scrolledtext, font


class VFSEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("VFS - Virtual File System")
        self.custom_font = font.Font(family="Courier New", size=10)
        self.current_dir = "/home/user"
        self.create_widgets()
        self.print_welcome()
        self.prompt()
        self.setup_bindings()

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.output_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=self.custom_font,
            bg="black",
            fg="white",
            insertbackground="white",
            state="disabled"
        )
        self.output_area.pack(fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(main_frame, bg="black")
        input_frame.pack(fill=tk.X, pady=(2, 0))

        self.prompt_label = tk.Label(
            input_frame,
            text=f"user@{self.current_dir}$ ",
            font=self.custom_font,
            bg="black",
            fg="green",
            anchor="w"
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.command_entry = tk.Entry(
            input_frame,
            font=self.custom_font,
            bg="black",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        self.command_entry.focus()

    def setup_bindings(self):
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.bind("<Up>", self.command_history_up)
        self.command_entry.bind("<Down>", self.command_history_down)
        self.command_history = []
        self.history_index = -1

    def print_welcome(self):
        welcome_msg = """Welcome to VFS (Virtual File System) Emulator
Type 'help' for available commands, 'exit' to quit.
"""
        self.print_output(welcome_msg)

    def prompt(self):
        self.prompt_label.config(text=f"user@{self.current_dir}$ ")

    def print_output(self, text):
        self.output_area.config(state="normal")
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state="disabled")

    def parse_command(self, command_line):
        tokens = []
        current_token = ""
        in_quotes = False
        quote_char = None

        for char in command_line:
            if char in ['"', "'"]:
                if in_quotes and char == quote_char:
                    in_quotes = False
                    quote_char = None
                elif not in_quotes:
                    in_quotes = True
                    quote_char = char
                else:
                    current_token += char
            elif char == ' ' and not in_quotes:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char

        if current_token:
            tokens.append(current_token)

        return tokens[0] if tokens else "", tokens[1:] if len(tokens) > 1 else []

    def execute_command(self, event=None):
        command_line = self.command_entry.get().strip()

        if not command_line:
            self.command_entry.delete(0, tk.END)
            return

        self.command_history.append(command_line)
        self.history_index = len(self.command_history)

        self.print_output(f"user@{self.current_dir}$ {command_line}\n")

        command, args = self.parse_command(command_line)

        try:
            if command == "exit":
                self.cmd_exit(args)
            elif command == "ls":
                self.cmd_ls(args)
            elif command == "cd":
                self.cmd_cd(args)
            elif command == "help":
                self.cmd_help(args)
            elif command == "":
                pass
            else:
                self.print_output(f"vfs: {command}: command not found\n")
        except Exception as e:
            self.print_output(f"Error: {str(e)}\n")

        self.command_entry.delete(0, tk.END)
        self.prompt()

    def command_history_up(self, event):
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        return "break"

    def command_history_down(self, event):
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = len(self.command_history)
            self.command_entry.delete(0, tk.END)
        return "break"

    def cmd_exit(self, args):
        self.print_output("Exiting VFS emulator...\n")
        self.root.after(100, self.root.destroy)

    def cmd_ls(self, args):
        if args:
            dir_path = " ".join(args)
            self.print_output(f"ls: listing directory '{dir_path}'\n")
        else:
            self.print_output(f"ls: listing directory '{self.current_dir}'\n")

        self.print_output("file1.txt  file2.txt  directory1/  directory2/\n")

    def cmd_cd(self, args):
        if not args:
            self.current_dir = "/home/user"
            self.print_output(f"Changed directory to {self.current_dir}\n")
        else:
            new_dir = " ".join(args)
            if new_dir == "..":
                if self.current_dir != "/":
                    parts = self.current_dir.rstrip('/').split('/')
                    self.current_dir = '/'.join(parts[:-1]) or '/'
            elif new_dir.startswith('/'):
                self.current_dir = new_dir
            else:
                self.current_dir = f"{self.current_dir.rstrip('/')}/{new_dir}"

            self.print_output(f"Changed directory to {self.current_dir}\n")

    def cmd_help(self, args):
        help_text = """Available commands:
  ls [directory]    - List directory contents
  cd [directory]    - Change directory
  exit              - Exit the emulator
  help              - Show this help message

These are currently stub commands that demonstrate basic functionality.
"""
        self.print_output(help_text)


def main():
    root = tk.Tk()
    root.geometry("800x600")
    root.configure(bg="black")

    try:
        root.iconbitmap("vfs.ico")
    except:
        pass

    emulator = VFSEmulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()