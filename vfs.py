import tkinter as tk
from tkinter import scrolledtext, font
import argparse
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import sys


def indent(elem, level=0):
    """Добавляет отступы для красивого форматирования XML"""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class VFSEmulator:
    def __init__(self, root, vfs_path, log_file, startup_script):
        self.root = root
        self.vfs_path = vfs_path
        self.log_file = log_file
        self.startup_script = startup_script
        self.current_directory = vfs_path
        self.title = "VFS"
        self.root.title(f"{self.title}")
        self.custom_font = font.Font(family="Courier New", size=10)
        self.create_widgets()
        self.print_welcome()
        self.log_startup_parameters()
        self.load_startup_script()
        self.prompt()
        self.command_entry.bind("<Return>", self.execute_command)

    def log_startup_parameters(self):
        print("Debug: VFS Path:", self.vfs_path)
        print("Debug: Log File:", self.log_file)
        print("Debug: Startup Script:", self.startup_script)

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

    def load_startup_script(self):
        if self.startup_script and os.path.exists(self.startup_script):
            try:
                with open(self.startup_script, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.print_output(f"user@vfs$ {line}\n")
                        command, args = self.parse_command(line)
                        self.log_command(command, args)  # Логируем команду из скрипта
                        success = self.execute_parsed_command(command, args)
                        if not success:
                            self.print_output("Script execution stopped due to error.\n")
                            return
            except Exception as e:
                self.print_output(f"Error executing startup script: {e}\n")
        elif self.startup_script:
            self.print_output(f"Error: startup script not found: {self.startup_script}\n")

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

    def log_command(self, command, args):
        root_elem = ET.Element("log")
        event_elem = ET.SubElement(root_elem, "event")
        ET.SubElement(event_elem, "timestamp").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ET.SubElement(event_elem, "command").text = command
        ET.SubElement(event_elem, "arguments").text = " ".join(args) if args else ""

        if os.path.exists(self.log_file):
            try:
                existing_tree = ET.parse(self.log_file)
                existing_root = existing_tree.getroot()
                existing_root.append(event_elem)

                # Применяем форматирование
                indent(existing_root)
                tree = ET.ElementTree(existing_root)
            except ET.ParseError:
                # Если файл лога пустой или поврежден, создаем новый
                indent(root_elem)
                tree = ET.ElementTree(root_elem)
        else:
            # Создаем новый файл с красивым форматированием
            indent(root_elem)
            tree = ET.ElementTree(root_elem)

        tree.write(self.log_file, encoding="utf-8", xml_declaration=True)

    def execute_command(self, event=None):
        command_line = self.command_entry.get().strip()

        if not command_line:
            self.command_entry.delete(0, tk.END)
            return

        self.print_output(f"user@vfs$ {command_line}\n")

        command, args = self.parse_command(command_line)
        self.log_command(command, args)

        success = self.execute_parsed_command(command, args)
        if not success:
            self.print_output("Script execution stopped due to error.\n")

        self.command_entry.delete(0, tk.END)

    def execute_parsed_command(self, command, args):
        if command == "exit":
            self.cmd_exit(args)
            return True
        elif command == "ls":
            self.cmd_ls(args)
            return True
        elif command == "cd":
            self.cmd_cd(args)
            return True
        elif command:
            self.print_output(f"vfs: {command}: command not found\n")
            return False
        return True

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
    parser = argparse.ArgumentParser(description="VFS Emulator")
    parser.add_argument("--vfs-path", required=True, help="Path to VFS")
    parser.add_argument("--log-file", required=True, help="Path to log file")
    parser.add_argument("--startup-script", help="Path to startup script")

    args = parser.parse_args()

    root = tk.Tk()
    root.geometry("800x600")
    root.configure(bg="black")
    emulator = VFSEmulator(root, args.vfs_path, args.log_file, args.startup_script)
    root.mainloop()


if __name__ == "__main__":
    main()