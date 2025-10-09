import tkinter as tk
from tkinter import scrolledtext, font
import argparse
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import csv
import hashlib
import base64


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            indent(child, level + 1)
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
        self.current_path = ["/"]
        self.title = os.path.splitext(os.path.basename(vfs_path))[0]
        self.username = "user"
        self.hostname = "vfs"
        self.root.title(self.title)
        self.custom_font = font.Font(family="Courier New", size=10)

        try:
            with open(self.vfs_path, "rb") as f:
                self.vfs_raw = f.read()
            self.vfs_sha256 = hashlib.sha256(self.vfs_raw).hexdigest()
            self.vfs_tree = self._load_vfs_from_csv(self.vfs_raw.decode('utf-8'))
        except FileNotFoundError:
            print(f"Error: VFS file not found: {self.vfs_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: Invalid VFS format: {e}")
            sys.exit(1)

        self.create_widgets()
        self.print_welcome()
        self.load_startup_script()
        self.prompt()
        self.command_entry.bind("<Return>", self.execute_command)

    def _load_vfs_from_csv(self, csv_text):
        tree = {"": {"type": "dir", "children": {}}}
        reader = csv.DictReader(csv_text.splitlines())
        for row in reader:
            path = row["path"]
            parts = [p for p in path.split("/") if p]
            current = tree[""]["children"]
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {"type": "dir", "children": {}}
                elif current[part]["type"] != "dir":
                    pass
                current = current[part]["children"]
            last = parts[-1] if parts else ""
            if not parts:
                continue
            if last not in current:
                if row["type"] == "dir":
                    current[last] = {"type": "dir", "children": {}}
                else:
                    content = base64.b64decode(row["content"]) if row["content"] else b""
                    current[last] = {"type": "file", "content": content}
        return tree

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
