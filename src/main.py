import json
import os
import sys

import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QProgressBar,
    QMessageBox,
    QVBoxLayout,
    QLineEdit,
    QCheckBox,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView, QInputDialog, QHBoxLayout,
)
from bitarray import bitarray

from ServerComboBox import ServerComboBox
from settings_dialog import SettingsDialog


class AstoniaLauncher(QWidget):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        # URLs and file paths
        self.repo_owner = "DanielBrockhaus"
        self.repo_name = "astonia_client"
        self.release_api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        self.latest_version_file = os.path.join(self.get_settings_file_path(), 'version.json')
        self.settings_file = os.path.join(self.get_settings_file_path(), 'settings.json')
        self.characters_file = os.path.join(self.get_settings_file_path(), 'characters.json')
        self.input_file = os.path.join(self.get_settings_file_path(), 'characters.json')
        self.release_api_url_body = requests.get(self.release_api_url).json()

        # Selected Character
        self.character = ""
        self.server = ""
        self.password = ""

        # Settings dialog
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.load_settings_from_file()
        # Add Character Dialog
        self.add_character_dialog = QDialog(self)

        self.init_ui()
        self.init_signals()
        self.restore_inputs()

        self.check_updates()

    def get_settings_file_path(self):
        if sys.platform.startswith('win'):
            # Windows path in APPDATA
            appdata_path = os.environ['APPDATA']
            settings_path = os.path.join(appdata_path, 'Ugaris', 'settings')
        else:
            # Linux and MacOS path in home directory
            home_path = os.path.expanduser('~')
            settings_path = os.path.join(home_path, '.Ugaris', 'settings')
        os.makedirs(settings_path, exist_ok=True)  # Ensure the directory exists
        return settings_path

    def init_ui(self):
        # UI setup
        self.setWindowTitle("Ugaris Launcher")
        self.label = QLabel("Latest Release Notes : ")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.hide()

        # Load user input values
        self.restore_inputs()

        self.PlayButton = QPushButton(self)
        self.PlayButton.setText("Launch Ugaris")
        self.PlayButton.setEnabled(False)

        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setChecked(True)

        self.SettingsButton = QPushButton(self)
        self.SettingsButton.setText("Settings")

        self.addCharacterButton = QPushButton(self)
        self.addCharacterButton.setText("Add Character")

        # Table
        self.CharacterTable = QTableWidget()
        self.CharacterTable.setColumnCount(4)
        self.CharacterTable.setHorizontalHeaderLabels(
            ["Server", "Name", "Password", "Delete"]
        )
        self.CharacterTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.CharacterTable.setSortingEnabled(True)
        self.CharacterTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.populate_character_table()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.SettingsButton)
        self.layout.addWidget(self.addCharacterButton)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.CharacterTable)
        self.layout.addWidget(self.remember_checkbox)
        self.layout.addWidget(self.PlayButton)
        self.setLayout(self.layout)

        # Show the UI
        self.show()

    def handle_character_selection_change(self):
        selected_rows = self.CharacterTable.selectionModel().selectedRows()
        if len(selected_rows) == 1:
            # Get the server and character names from the selected row
            row = selected_rows[0].row()
            server_item = self.CharacterTable.item(row, 0)
            character_item = self.CharacterTable.item(row, 1)
            password_item = self.CharacterTable.item(row, 2)
            if server_item and character_item and password_item:
                self.server = server_item.text()
                self.character = character_item.text()
                self.password = password_item.text()

    def populate_character_table(self):
        try:
            with open(self.characters_file, "r") as f:
                characters = json.load(f)
        except FileNotFoundError:
            characters = []
        # Clear table and populate it with logins
        self.CharacterTable.setRowCount(0)
        for character in characters:
            if (
                    isinstance(character, dict)
                    and "server" in character
                    and "username" in character
                    and "password" in character
            ):
                row = self.CharacterTable.rowCount()
                self.CharacterTable.insertRow(row)
                self.CharacterTable.setItem(
                    row, 0, QTableWidgetItem(character["server"])
                )
                self.CharacterTable.setItem(
                    row, 1, QTableWidgetItem(character["username"])
                )
                self.CharacterTable.setItem(
                    row, 2, QTableWidgetItem(character["password"])
                )
                self.CharacterTable.setColumnHidden(2, True)

                # Add a delete button with a red cross icon to the fourth column
                delete_button = QPushButton()
                delete_button.setIcon(QIcon("icons/red_cross.png"))
                delete_button.setToolTip("Delete character")
                delete_button.clicked.connect(self.handle_delete_button_click)
                self.CharacterTable.setCellWidget(row, 3, delete_button)

                self.CharacterTable.resizeColumnToContents(0)
                self.CharacterTable.resizeColumnToContents(1)
                self.CharacterTable.resizeColumnToContents(2)
                self.CharacterTable.resizeColumnToContents(3)

    def handle_delete_button_click(self):
        button = self.sender()
        row = self.CharacterTable.indexAt(button.pos()).row()
        server_item = self.CharacterTable.item(row, 0)
        character_item = self.CharacterTable.item(row, 1)
        if server_item and character_item:
            server = server_item.text()
            character = character_item.text()

            # Prompt the user to confirm the deletion
            message_box = QMessageBox()
            message_box.setText(
                f"Are you sure you want to delete {character} connected to {server}?"
            )
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.No)
            result = message_box.exec_()
            if result == QMessageBox.Yes:
                # Remove the character from the JSON file
                self.remove_character(server, character)
                # Refresh the table
                self.populate_character_table()

    def remove_character(self, server, character):
        # Load the current settings from the JSON file
        if os.path.isfile(self.characters_file):
            with open(self.characters_file, "r") as f:
                settings = json.load(f)
        else:
            settings = []

        # Remove the character data from the settings
        for character_data in settings:
            if (
                    character_data["server"] == server
                    and character_data["username"] == character
            ):
                settings.remove(character_data)
                break

        # Save the updated settings to the JSON file
        with open(self.characters_file, "w") as f:
            json.dump(settings, f)

    def init_signals(self):
        self.PlayButton.clicked.connect(self.launch_app)
        self.SettingsButton.clicked.connect(self.open_settings_dialog)
        self.addCharacterButton.clicked.connect(self.open_add_character_dialog)
        self.CharacterTable.itemSelectionChanged.connect(
            self.handle_character_selection_change
        )

    def open_settings_dialog(self):
        self.settings_dialog.show()
        self.settings_dialog.exec_()

    def open_add_character_dialog(self):
        self.add_character_dialog.setWindowTitle("Add Character")
        # Server Input
        self.server_input = ServerComboBox(self)
        # Create input fields for character data
        character_input_label = QLabel("Character")
        character_input = QLineEdit()

        password_input_label = QLabel("Password")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)

        server_input_label = QLabel("Server")
        # Create the QHBoxLayout for the buttons
        button_layout = QHBoxLayout()

        # Add the "Add" button to the QHBoxLayout
        # add_server_button = QPushButton("Add")
        # button_layout.addWidget(add_server_button)

        # Add the "Remove" button to the QHBoxLayout
        # remove_server_button = QPushButton("Remove")
        # button_layout.addWidget(remove_server_button)

        # Create a layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(server_input_label)
        layout.addWidget(self.server_input)
        layout.addLayout(button_layout)
        layout.addWidget(character_input_label)
        layout.addWidget(character_input)
        layout.addWidget(password_input_label)
        layout.addWidget(password_input)

        # Create the QHBoxLayout for the buttons
        button_layout = QHBoxLayout()

        # Add the "Add" button to the QHBoxLayout
        add_character_button = QPushButton("Add")
        button_layout.addWidget(add_character_button)

        # Add the "Remove" button to the QHBoxLayout
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Add server button clicked
        # add_server_button.clicked.connect(self.on_add_server)
        # remove_server_button.clicked.connect(self.on_delete_server)

        # Connect the save button to a function to save the data
        add_character_button.clicked.connect(
            lambda: self.save_character(
                self.server_input.currentData(),
                character_input.text(),
                password_input.text(),
            )
        )
        cancel_button.clicked.connect(self.on_add_character_dialog_close)

        self.add_character_dialog.setLayout(layout)
        self.add_character_dialog.exec_()

    def on_add_character_dialog_close(self):
        self.add_character_dialog.close()

    def on_delete_server(self):
        index = self.server_input.currentIndex()
        if index >= 0:
            self.server_input.delete_server(index)

    def on_add_server(self):
        name, ok = QInputDialog.getText(self, 'Add Server', 'Server Name:')
        if ok:
            address, ok = QInputDialog.getText(self, 'Add Server', 'Server Address:')
            if ok:
                self.server_input.add_server(name, address)

    def save_character(self, server, character, password):
        # Load the current settings from the JSON file
        if os.path.isfile(self.characters_file):
            with open(self.characters_file, "r") as f:
                settings = json.load(f)
        else:
            settings = []

        # Add the new server and character data to the settings
        character_data = {"server": server, "username": character, "password": password}
        settings.append(character_data)

        # Save the updated settings to the JSON file
        with open(self.characters_file, "w") as f:
            json.dump(settings, f)

        # Close the dialog
        self.add_character_dialog.close()
        self.populate_character_table()
        self.CharacterTable.selectRow(0)

    def save_settings(self, server, character, password):
        # Load the current settings from the JSON file
        if os.path.isfile(self.settings_file):
            with open(self.settings_file, "r") as f:
                settings = json.load(f)
        else:
            settings = {"servers": [], "characters": []}

        # Add the new server and character data to the settings
        server_data = {"name": server}
        character_data = {"username": character, "password": password}
        settings["servers"].append(server_data)
        settings["characters"].append(character_data)

        # Save the updated settings to the JSON file
        with open(self.settings_file, "w") as f:
            json.dump(settings, f)

        # Close the dialog
        self.settings_dialog.close()

    def restore_inputs(self):
        self.inputs = {}
        if os.path.isfile(self.input_file + "inputs.txt"):
            with open(self.input_file + "inputs.txt", "r") as f:
                for line in f:
                    key, value = line.strip().split(":")
                    self.inputs[key] = value

    def save_inputs(self):
        with open(self.input_file + "inputs.txt", "w") as f:
            for key, value in self.inputs.items():
                f.write(f"{key}:{value}\n")

    def server_changed(self, index):
        self.inputs["server"] = index
        if self.remember_checkbox.isChecked():
            self.save_inputs()

    def username_changed(self, text):
        self.inputs["username"] = text
        if self.remember_checkbox.isChecked():
            self.save_inputs()

    def password_changed(self, text):
        self.inputs["password"] = text
        if self.remember_checkbox.isChecked():
            self.save_inputs()

    def check_updates(self):
        # Download and parse the version from ugaris.com
        version_url = "https://ugaris.com/client/version.txt"
        try:
            response = requests.get(version_url)
            response.raise_for_status()
            latest_version = response.text.strip()
        except requests.exceptions.RequestException as e:
            self.label.setText(f"Error checking updates: {e}")
            return

        # Check if version.txt exists locally
        if not os.path.isfile(self.latest_version_file):
            self.label.setText("Downloading latest release...")
            self.update_app(latest_version)
            return

        # Check if an update is available
        with open(self.latest_version_file, "r") as f:
            current_version = f.read().strip()

        if current_version != latest_version:
            # Display update message
            message = f"A new version ({latest_version}) of the app is available. Do you want to update?"
            response = QMessageBox.question(
                self, "Update Available", message, QMessageBox.Yes | QMessageBox.No
            )

            if response == QMessageBox.Yes:
                self.label.setText("Downloading update...")
                self.update_app(latest_version)
        else:
            self.label.setText("No updates available.")
            self.PlayButton.setEnabled(True)

    def update_app(self, latest_version):
        # Construct the URL for the .zip file
        zip_url = f"https://ugaris.com/client/{latest_version}_client.zip"
        zip_file = f"{latest_version}_client.zip"
        try:
            with requests.get(zip_url, stream=True) as r:
                r.raise_for_status()
                self.progress_bar.show()
                with open(zip_file, "wb") as f:
                    total_length = int(r.headers.get("content-length"))
                    dl = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        dl += len(chunk)
                        progress = int(100 * dl / total_length)
                        self.progress_bar.setValue(progress)
                        QApplication.processEvents()

        except requests.exceptions.RequestException as e:
            self.label.setText(f"Error downloading update: {e}")
            return

        # Extract the release files to the current directory
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(".")

        # Update the version file
        with open(self.latest_version_file, "w") as f:
            f.write(latest_version)

        # Clean up
        os.remove(zip_file)
        self.label.setText(f"Updated to version {latest_version}")
        self.PlayButton.setEnabled(True)

    def create_options_arg(self):

        option_mapping = {
            "enable_dark_gui": 0,  # Bit 0: Dark GUI by Tegra
            "enable_context": 1,  # Bit 1: Context menu
            "enable_keybindings": 2,  # Bit 2: New keybindings
            "enable_smaller_bottom_window": 3,  # Bit 3: Smaller bottom GUI
            "enable_smaller_top_window": 4,  # Bit 4: Top GUI slides away
            "enable_big_health_bar": 5,  # Bit 5: Bigger health/mana bars
            "enable_sound": 6,  # Bit 6: Sound
            "enable_large_font": 7,  # Bit 7: Large font
            "enable_true_full_screen": 8,  # Bit 8: True full screen mode
            "enable_legacy_mouse_wheel": 9,  # Bit 9: Legacy mouse wheel logic
            "enable_inventory_optimization": 10,  # Bit 10: Out-of-order execution of inventory access
            "enable_animation_optimization": 11,  # Bit 11: Reduces animation buffer
            "enable_appdata_usage": 12,  # Bit 12: Writes application files to %appdata%
            "enable_minimap_management": 13,  # Bit 13: Loading and saving of minimaps
            "enable_gamma_increase": 14,  # Bit 14 and 15: Increase gamma
            "enable_sliding_top_bar_sensitivity": 16,  # Bit 16: Makes the sliding top bar less sensitive
            "enable_lighting_effects_reduction": 17,  # Bit 17: Reduces lighting effects for more performance
            "enable_minimap": 18  # Bit 18: Disables the minimap
        }

        options = bitarray(len(option_mapping) + 7)  # Adjusted size for the maximum bit index used + 1
        options.setall(False)
        if self.settings_dialog:
            for checkbox_name, option_value in option_mapping.items():
                checkbox = getattr(self.settings_dialog, checkbox_name)
                if checkbox.isChecked():
                    options[option_value] = True
        return int.from_bytes(options.tobytes(), byteorder="little")

    def launch_app(self):
        server = self.server.strip()
        username = self.character.strip()
        password = self.password.strip()
        executable_name = self.settings_dialog.executable_name.text().strip()
        sdl_cache = self.settings_dialog.sdl_cache_size.value()
        sdl_multi = self.settings_dialog.sdl_multi.value()
        sdl_frames = self.settings_dialog.sdl_frames.value()

        options_arg = self.create_options_arg()

        # Validate required fields
        app_args = {
            "Server": server,
            "Username": username,
            "Password": password,
            "Executable Name": executable_name,
            "SDL Cache Size": sdl_cache,
            "SDL Multi-threading": sdl_multi,
            "SDL Frames": sdl_frames
        }

        # Validate empty fields before proceeding
        for key, value in app_args.items():
            if isinstance(value, str) and not value:
                QMessageBox.warning(None, "Missing Information", f"{key} is required but is empty.")
                return  # Cancel execution if any field is empty

        # Construct command line arguments based on platform
        command_args = [
            f"-u {username}",
            f"-p {password}",
            f"-d {server}",
            f"-o {options_arg}",
            f"-c {sdl_cache}",
            f"-k {sdl_frames}",
            f"-m {sdl_multi}",
        ]

        if not (
                self.settings_dialog.enable_fullscreen.isChecked() or self.settings_dialog.enable_true_full_screen.isChecked()):
            resolution = self.settings_dialog.resolution_combo.currentText()
            width, height = resolution.split('x')
            command_args.extend([f"-w {width}", f"-h {height}"])

        if sys.platform in ["linux", "linux2", "darwin"]:
            # Assume Wine is needed to run Windows executable on Unix-like systems
            app_path = "wine"
            command_args.insert(0, executable_name)
        elif sys.platform == "win32":
            # Directly use the executable path on Windows
            app_path = executable_name

        # Launch the app
        try:
            full_command = [app_path] + command_args
            print("Command to execute:", ' '.join(full_command))  # Debug: print command to be executed
            os.execvp(app_path, full_command)  # Here, full_command[0] should match app_path
        except OSError as e:
            if self.label:
                self.label.setText(f"Error launching application: {e}")
            print(f"Error launching application: {e}")

    def close(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = AstoniaLauncher()
    launcher.show()
    sys.exit(app.exec_())
