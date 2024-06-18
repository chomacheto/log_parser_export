import customtkinter as ctk
import subprocess
import os
import re
from keywords import KEYWORDS_LIST
import json
import tkinter as tk

# Set the appearance mode and color theme for the customtkinter library
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

def save_faults_to_file(faults, file_path='commands_output/faults.json'):
    with open(file_path, 'w') as f:
        json.dump(faults, f)

def load_faults_from_file(file_path='commands_output/faults.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return []

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip or not self.text:
            return
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        label = tk.Label(self.tooltip, text=self.text, justify='left', background='white', relief='solid', borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

def check_server_status():
    server_status = []
    server_details = {}

    with open('commands_output/show server status detail.txt', 'r') as f:
        log_file_lines = f.readlines()

    index = 0
    while index < len(log_file_lines):
        if re.match('Server \\d+/\\d+', log_file_lines[index]):
            server_info = log_file_lines[index].strip()
            slot_status_line = log_file_lines[index + 1]
            overall_status_line = log_file_lines[index + 7]

            if 'Slot Status: Equipped' in slot_status_line:
                if 'Overall Status: Ok' in overall_status_line:
                    status = "OK"
                elif 'Overall Status: Unassociated' in overall_status_line:
                    status = "UNASSOCIATED"
                elif 'Overall Status: Discovery' in overall_status_line:
                    status = "DISCOVERY"
                else:
                    status = "ERROR"
            elif 'Slot Status: Empty' in slot_status_line:
                status = "EMPTY"
            else:
                status = "ERROR"

            server_status.append((server_info, status))
            server_details[server_info] = log_file_lines[index:index+8]

            index += 8
        else:
            index += 1

    return server_status, server_details

def parse_faults():
    faults = []
    fault_file_path = 'commands_output/show fault detail.txt'

    if not os.path.exists(fault_file_path):
        print(f"File {fault_file_path} does not exist.")
        return faults

    with open(fault_file_path, 'r') as f:
        content = f.read()
        fault_blocks = content.split("Severity: ")[1:]

        for block in fault_blocks:
            lines = block.strip().split("\n")
            if len(lines) < 6:
                print(f"Skipping malformed block: {block.strip()}")
                continue

            try:
                fault = {
                    "Severity": lines[0].strip(),
                    "Code": lines[1].split(":")[1].strip(),
                    "Last Transition Time": lines[2].split(":")[1].strip(),
                    "Description": lines[5].split(":")[1].strip(),
                    "Details": block.strip()
                }
                faults.append(fault)
            except IndexError as e:
                print(f"Error parsing block: {block.strip()}")
                print(f"Exception: {e}")
                continue

    save_faults_to_file(faults)
    print(f"Parsed {len(faults)} faults.")
    return faults

def segment_data():
    log_file_path = 'sam_techsupportinfo'
    output_dir = 'commands_output'

    with open(log_file_path, 'r') as f:
        log_file_lines = f.readlines()

    os.makedirs(output_dir, exist_ok=True)

    server_pattern = re.compile(r'(Server \d+/\d+):')
    chassis_pattern = re.compile(r'(Chassis \d+):')
    command_pattern = re.compile(r'`')

    current_data = []
    current_name = None
    current_command = None

    for line in log_file_lines:
        server_match = server_pattern.match(line)
        chassis_match = chassis_pattern.match(line)
        command_match = command_pattern.match(line)

        if command_match:
            current_command = line.strip()

        if server_match or chassis_match:
            if current_name and current_data:
                write_data_to_file(current_name, current_data, output_dir)

            current_name = server_match.group(1) if server_match else chassis_match.group(1)
            current_data = [current_command + '\n', line]
        elif command_match:
            if current_name and current_data:
                write_data_to_file(current_name, current_data, output_dir)
                current_name = None
                current_data = []
        else:
            if current_name:
                current_data.append(line)

    if current_name and current_data:
        write_data_to_file(current_name, current_data, output_dir)

def write_data_to_file(name, data, output_dir):
    file_safe_name = name.replace('/', '_').replace(':', '')
    file_path = os.path.join(output_dir, f'{file_safe_name}.txt')
    
    with open(file_path, 'a') as file:
        file.write(''.join(data) + '\n')

def reorder_keywords(KEYWORDS_LIST, file_path):
    reordered_keywords = []
    with open(file_path, 'r') as f:
        for line in f:
            for keyword in KEYWORDS_LIST:
                if keyword in line:
                    reordered_keywords.append(keyword)
                    break
    return reordered_keywords

def process_log_file():
    log_file_path = 'sam_techsupportinfo'
    commands_output_dir = 'commands_output'

    os.makedirs(commands_output_dir, exist_ok=True)

    with open(log_file_path, 'r') as f:
        log_file_lines = f.readlines()

    reordered_keywords = reorder_keywords(KEYWORDS_LIST, log_file_path)

    index_of_current_keyword = 0
    number_of_files = 0
    for index, line in enumerate(log_file_lines):
        if index_of_current_keyword >= len(reordered_keywords):
            print('All keywords processed')
            break

        current_keyword = reordered_keywords[index_of_current_keyword]

        if re.match(current_keyword, line):
            number_of_files += 1
            while re.search('`', log_file_lines[index + 1]) is None:
                current_keyword_without_backticks = current_keyword.strip('`')
                with open(f'commands_output/{current_keyword_without_backticks}.txt', 'a') as output_file:
                    output_file.write(log_file_lines[index])
                    index += 1
            else:
                with open(f'commands_output/{current_keyword_without_backticks}.txt', 'a') as output_file:
                    output_file.write(log_file_lines[index])
            print(current_keyword)
            index_of_current_keyword += 1

    print(number_of_files)
    segment_data()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Server Grid")
        self.geometry("1000x600")

        self.side_menu = ctk.CTkScrollableFrame(self, width=200)
        self.side_menu.pack(side="left", fill="y")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.button_search_entry = ctk.CTkEntry(self.side_menu, placeholder_text="Search buttons")
        self.button_search_entry.pack(pady=10, padx=10, fill="x")
        self.button_search_entry.bind("<KeyRelease>", self.search_buttons)

        self.text_search_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Search text")
        self.text_search_entry.pack(pady=10, padx=10, fill="x")
        self.text_search_entry.bind("<KeyRelease>", self.search_text)

        self.search_nav_frame = ctk.CTkFrame(self.main_frame)
        self.search_nav_frame.pack(fill="x", padx=5, pady=5)

        self.last_search_term = ""
        self.search_matches = []
        self.current_match_index = -1

        self.notification_label = ctk.CTkLabel(self, text="", fg_color="black", text_color="white")
        self.notification_label.place(relx=1, rely=1, anchor="se")

        self.prev_button = ctk.CTkButton(self.search_nav_frame, text="Previous", command=self.prev_match)
        self.prev_button.pack(side="left", padx=5)
        self.next_button = ctk.CTkButton(self.search_nav_frame, text="Next", command=self.next_match)
        self.next_button.pack(side="left", padx=5)

        self.buttons = {
            'Run Log Parser': self.run_parser,
            'Show Server Status Detail': self.check_status,
            'Show Faults': self.show_faults,
        }

        self.button_widgets = []

        self.create_buttons()

        self.textbox = ctk.CTkTextbox(self.main_frame, wrap='none')
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.textbox.configure(state="disabled")

        self.status_detail_frame = ctk.CTkFrame(self.main_frame)
        self.status_detail_frame.pack(fill="both", expand=True)

        self.fault_detail_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.fault_detail_frame.pack(fill="both", expand=True)

        self.show_main_frame()

        self.server_details = {}

        self.faults = load_faults_from_file()

        self.show_faults()

    def create_buttons(self):
        for _, button in self.button_widgets:
            button.pack_forget()
            button.destroy()
        self.button_widgets = []

        commands_output_exists = os.path.exists("commands_output")

        for button_text, action in self.buttons.items():
            button = ctk.CTkButton(self.side_menu, text=button_text, command=action)
            button.pack(pady=10, padx=10, fill="x")
            self.button_widgets.append((button_text, button))

            if button_text == "Run Log Parser":
                button.configure(state="normal" if not commands_output_exists else "disabled")

        if commands_output_exists:
            created_buttons = set()
            for file_name in os.listdir("commands_output"):
                if file_name.endswith(".txt"):
                    command_name = os.path.splitext(file_name)[0]

                    if not command_name.startswith("Server ") and command_name not in created_buttons:
                        button = ctk.CTkButton(
                            self.side_menu,
                            text=command_name,
                            command=lambda file=file_name: self.display_command_output(file)
                        )
                        button.pack(pady=10, padx=10, fill="x")
                        self.button_widgets.append((command_name, button))
                        created_buttons.add(command_name)

                    elif command_name.startswith("Server ") and command_name not in created_buttons:
                        original_server_name = command_name.replace('_', '/')
                        button = ctk.CTkButton(
                            self.side_menu,
                            text=original_server_name,
                            command=lambda file=file_name: self.display_server_output(file)
                        )
                        button.pack(pady=10, padx=10, fill="x")
                        self.button_widgets.append((original_server_name, button))
                        created_buttons.add(original_server_name)

    def search_buttons(self, event):
        search_term = self.button_search_entry.get().lower()
        for text, button in self.button_widgets:
            if search_term in text.lower():
                button.pack(pady=10, padx=10, fill="x")
            else:
                button.pack_forget()

    def search_text(self, event):
        if event.keysym != "Return":
            return

        search_term = self.text_search_entry.get().lower()
        content = self.textbox.get("1.0", "end-1c").lower()
        self.textbox.tag_remove("highlight", "1.0", "end")
        self.search_matches = []
        self.current_match_index = -1

        if search_term:
            start_idx = "1.0"
            while True:
                start_idx = self.textbox.search(search_term, start_idx, nocase=1, stopindex="end")
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(search_term)}c"
                self.textbox.tag_add("highlight", start_idx, end_idx)
                self.search_matches.append((start_idx, end_idx))
                start_idx = end_idx
            self.textbox.tag_config("highlight", background="#000000")

            num_matches = len(self.search_matches)
            self.notification_label.configure(text=f"{num_matches} matches found")

            if self.search_matches:
                self.current_match_index = 0
                self.textbox.see(self.search_matches[self.current_match_index][0])

        self.notification_label.place(relx=1, rely=1, anchor="se")

    def next_match(self):
        if self.search_matches:
            self.current_match_index = (self.current_match_index + 1) % len(self.search_matches)
            self.textbox.see(self.search_matches[self.current_match_index][0])
            self.textbox.tag_remove("current_match", "1.0", "end")
            start, end = self.search_matches[self.current_match_index]
            self.textbox.tag_add("current_match", start, end)
            self.textbox.tag_config("current_match", background="orange")

    def prev_match(self):
        if self.search_matches:
            self.current_match_index = (self.current_match_index - 1) % len(self.search_matches)
            self.textbox.see(self.search_matches[self.current_match_index][0])
            self.textbox.tag_remove("current_match", "1.0", "end")
            start, end = self.search_matches[self.current_match_index]
            self.textbox.tag_add("current_match", start, end)
            self.textbox.tag_config("current_match", background="orange")

    def show_main_frame(self):
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.status_detail_frame.pack_forget()
        self.fault_detail_frame.pack_forget()
        self.clear_search_entry()

    def show_status_detail_frame(self):
        self.textbox.pack_forget()
        self.status_detail_frame.pack(fill="both", expand=True)
        self.fault_detail_frame.pack_forget()
        self.clear_search_entry()

    def show_fault_detail_frame(self):
        self.textbox.pack_forget()
        self.status_detail_frame.pack_forget()
        self.fault_detail_frame.pack(fill="both", expand=True)
        self.clear_search_entry()

    def refresh_main_frame(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def clear_search_entry(self):
        self.text_search_entry.delete(0, "end")
        self.last_search_term = ""

    def run_parser(self):
        for widget in self.side_menu.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget('text') == 'Run Log Parser':
                widget.configure(state='disabled')

        process_log_file()
        self.faults = parse_faults()
        self.display_message("Log parser ran successfully.")
        self.create_buttons()
        self.show_faults()

    def check_status(self):
        server_status, self.server_details = check_server_status()
        self.show_status_detail_frame()

        for widget in self.status_detail_frame.winfo_children():
            widget.destroy()

        row = 0
        col = 0
        if server_status is not None:
            for server_info, status in server_status:
                label_text = f"{server_info}: {status}"
                label = ctk.CTkLabel(self.status_detail_frame, text=label_text)
                label.grid(row=row, column=col, padx=5, pady=5)

                sanitized_server_info = server_info.replace('/', '_').replace(':', '') + ".txt"
                label.bind("<Button-1>", lambda e, srv=sanitized_server_info: self.display_server_output(srv))

                if status == "OK":
                    label.configure(text_color="green")
                elif status == "UNASSOCIATED":
                    label.configure(text_color="orange")
                elif status == "EMPTY":
                    label.configure(text_color="gray")
                elif status == "DISCOVERY":
                    label.configure(text_color="yellow")
                else:
                    label.configure(text_color="red")

                row += 1
                if row == 8:
                    row = 0
                    col += 1

    def show_faults(self):
        self.show_fault_detail_frame()

        for widget in self.fault_detail_frame.winfo_children():
            widget.destroy()

        row = 0
        for fault in self.faults:
            label_text = f"{fault['Severity']}: {fault['Code']} - {fault['Last Transition Time']}"
            label = ctk.CTkLabel(self.fault_detail_frame, text=label_text, justify='left')
            label.grid(row=row, column=0)

            if fault['Severity'] == "Cleared":
                label.configure(text_color="green")
            elif fault['Severity'] == "Info":
                label.configure(text_color="lightblue")
            elif fault['Severity'] == "Minor":
                label.configure(text_color="yellow")
            elif fault['Severity'] == "Warning":
                label.configure(text_color="orange")
            elif fault['Severity'] == "Major":
                label.configure(text_color="orangered")
            elif fault['Severity'] == "Critical":
                label.configure(text_color="red")

            label.bind("<Button-1>", lambda e, fault=fault: self.display_fault_details(fault))
            Tooltip(label, fault["Details"])

            row += 1

    def display_fault_details(self, fault):
        details_window = ctk.CTkToplevel(self)
        details_window.title(f"Fault Details: {fault['Code']}")
        details_window.attributes('-topmost', 'true')  # Ensure the window stays on top
        details_window.geometry("900x400")
        details_textbox = ctk.CTkTextbox(details_window, wrap='none')
        details_textbox.pack(expand=True, fill='both')
        details_textbox.insert('1.0', fault["Details"])
        details_textbox.configure(state="disabled")

    def display_server_output(self, server):
        self.refresh_main_frame()

        directory = "commands_output"
        server_file_path = directory + "/" + server

        if os.path.exists(server_file_path):
            with open(server_file_path, 'r') as file:
                content = file.read()
            self.display_message(content)
        else:
            self.display_message("No details available for this server.")

    def show_server_details(self, server):
        self.refresh_main_frame()
        file_safe_server_name = server.replace('/', '_')
        server_file = f"{file_safe_server_name}.txt"
        server_file_path = os.path.join("commands_output", server_file)

        if os.path.exists(server_file_path):
            with open(server_file_path, 'r') as file:
                details = file.read()
            self.display_message(details)
        else:
            self.display_message("No details available for this server.")

    def clear_labels(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")

    def display_message(self, message):
        self.refresh_main_frame()
        self.textbox.configure(state="normal")
        self.textbox.insert("end", message)
        self.textbox.configure(state="disabled")
        self.after(200, lambda: self.textbox.see("end"))

    def display_command_output(self, file_name):
        with open(os.path.join("commands_output", file_name), "r") as file:
            content = file.read()

        self.show_main_frame()
        self.clear_labels()
        self.textbox.configure(state="normal")
        self.textbox.insert("end", content)
        self.textbox.configure(state="disabled")

    def display_server_output(self, file_name):
        with open(os.path.join("commands_output", file_name), "r") as file:
            content = file.read()

        self.show_main_frame()
        self.clear_labels()
        self.textbox.configure(state="normal")
        self.textbox.insert("end", content)
        self.textbox.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()
