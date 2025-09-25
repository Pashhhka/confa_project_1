import tkinter as tk
from tkinter import scrolledtext, font


class VFSEmulator:
    def __init__(self, root):
        self.root = root
        self.title = "VFS"
        self.root.title(f"{self.title}")
        self.custom_font = font.Font(family="Courier New", size=10)
        self.create_widgets()
        self.print_welcome()
        self.prompt()
        self.command_entry.bind("<Return>", self.execute_command)

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
            text="user@vfs$ ",
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

    def print_welcome(self):
        welcome_msg = "Welcome to VFS Emulator\nType 'exit' to quit.\n"
        self.print_output(welcome_msg)

    def prompt(self):
        self.prompt_label.config(text="user@vfs$ ")

    def print_output(self, text):
        self.output_area.config(state="normal")
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state="disabled")

    def parse_command(self, command_line):
        parts = command_line.strip().split()
        if not parts:
            return "", []
        return parts[0], parts[1:]

    def execute_command(self, event=None):
        command_line = self.command_entry.get().strip()

        if not command_line:
            self.command_entry.delete(0, tk.END)
            return

        self.print_output(f"user@vfs$ {command_line}\n")

        command, args = self.parse_command(command_line)

        if command == "exit":
            self.cmd_exit(args)
        elif command == "ls":
            self.cmd_ls(args)
        elif command == "cd":
            self.cmd_cd(args)
        elif command:
            self.print_output(f"vfs: {command}: command not found\n")

        self.command_entry.delete(0, tk.END)

    def cmd_exit(self, args):
        if args:
            self.print_output(f"exit: arguments: {args}\n")
        self.print_output("Exiting...\n")
        self.root.after(100, self.root.destroy)

    def cmd_ls(self, args):
        if args:
            self.print_output(f"ls: arguments: {args}\n")
        else:
            self.print_output("ls: no arguments\n")

    def cmd_cd(self, args):
        if args:
            self.print_output(f"cd: arguments: {args}\n")
        else:
            self.print_output("cd: no arguments\n")


def main():
    root = tk.Tk()
    root.geometry("800x600")
    root.configure(bg="black")
    emulator = VFSEmulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()