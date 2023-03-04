import os
import sys

from bitarray import bitarray
import requests
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QProgressBar, QMessageBox, QVBoxLayout, \
    QLineEdit, QComboBox, QCheckBox, QDialog, QTableWidget, QTableWidgetItem, QAbstractItemView
from bitfields import Bits

from settings_dialog import SettingsDialog


class UpdateApp(QWidget):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        # URLs and file paths
        self.repo_owner = "DanielBrockhaus"
        self.repo_name = "astonia_client"
        self.release_api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        self.latest_version_file = "version.txt"
        self.settings_file = "settings.txt"
        self.release_api_url_body = requests.get(self.release_api_url).json()

        # initialize the dialogs
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.load_settings_from_file()

        self.add_character_dialog = QDialog(self)

        self.initUI()
        self.initSignals()
        self.restore_inputs()

        self.check_updates()

    def initUI(self):
        # UI setup
        self.setWindowTitle("Astonia Launcher")

        self.label = QLabel("Latest Release Notes : ")

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.hide()

        # Load user input values
        self.restore_inputs()

        # self.username_input_label = QLabel("Username")
        # self.username_input = QLineEdit(self)
        # self.username_input.setText(self.inputs.get("username", ""))
        # self.username_input.setLabelText("Username")

        # self.password_input_label = QLabel("Password")
        # self.password_input = QLineEdit(self)
        # self.password_input.setText(self.inputs.get("password", ""))
        # self.password_input.setEchoMode(QLineEdit.Password)
        # self.password_input.setLabelText("Password")

        # self.server_input_label = QLabel("Server")
        # self.server_input = QComboBox(self)
        # self.server_input.addItem("Localhost (127.0.0.1)", "127.0.0.1")
        # self.server_input.addItem("Local Network (192.168.1.110)", "192.168.1.110")
        # self.server_input.addItem("Ugaris Server", "login.ugaris.com")
        # self.server_input.setCurrentIndex(int(self.inputs.get("server", 0)))
        # self.server_input.addItem("Localhost", "127.0.0.1")
        # self.server_input.addItem("Localhost", "127.0.0.1")
        # self.server_input.addItem("Localhost", "127.0.0.1")

        self.PlayButton = QPushButton(self)
        self.PlayButton.setText("Launch App")
        self.PlayButton.setEnabled(False)

        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setChecked(True)

        self.SettingsButton = QPushButton(self)
        self.SettingsButton.setText("Settings")

        self.addCharacterButton = QPushButton(self)
        self.addCharacterButton.setText("Add Character")

        # Table
        self.CharacterTable = QTableWidget()
        self.CharacterTable.setColumnCount(3)
        self.CharacterTable.setHorizontalHeaderLabels(['Server', 'Name', 'Password'])
        self.CharacterTable.setEditTriggers(QTableWidget.NoEditTriggers)
        self.CharacterTable.setSortingEnabled(True)
        self.CharacterTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.populate_character_table()
        self.CharacterTable.selectRow(0)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.SettingsButton)
        self.layout.addWidget(self.addCharacterButton)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.CharacterTable)
        # self.layout.addWidget(self.username_input_label)
        # self.layout.addWidget(self.username_input)
        # self.layout.addWidget(self.password_input_label)
        # self.layout.addWidget(self.password_input)
        # self.layout.addWidget(self.server_input_label)
        # self.layout.addWidget(self.server_input)
        self.layout.addWidget(self.remember_checkbox)
        self.layout.addWidget(self.PlayButton)
        self.setLayout(self.layout)

        # Show the UI
        self.show()

    def populate_character_table(self):
        try:
            with open('characters.json', 'r') as f:
                characters = json.load(f)
        except FileNotFoundError:
            characters = []
        # Clear table and populate it with logins
        self.CharacterTable.setRowCount(0)
        for character in characters:
            if isinstance(character,
                          dict) and 'server' in character and 'username' in character and 'password' in character:
                row = self.CharacterTable.rowCount()
                self.CharacterTable.insertRow(row)
                self.CharacterTable.setItem(row, 0, QTableWidgetItem(character['server']))
                self.CharacterTable.setItem(row, 1, QTableWidgetItem(character['username']))
                self.CharacterTable.setItem(row, 2, QTableWidgetItem(character['password']))
                self.CharacterTable.setColumnHidden(2, True)

    def initSignals(self):
        # self.username_input.textChanged.connect(self.usernameChanged)
        # self.password_input.textChanged.connect(self.passwordChanged)
        # self.server_input.currentIndexChanged.connect(self.serverChanged)
        self.PlayButton.clicked.connect(self.launch_app)
        self.SettingsButton.clicked.connect(self.open_settings_dialog)
        self.addCharacterButton.clicked.connect(self.open_add_character_dialog)

    def open_settings_dialog(self):
        self.settings_dialog.show()
        self.settings_dialog.exec_()

    def open_add_character_dialog(self):
        self.add_character_dialog.setWindowTitle("Add Character")

        # Create input fields for character data
        character_input_label = QLabel("Character")
        character_input = QLineEdit(self.add_character_dialog)

        password_input_label = QLabel("Password")
        password_input = QLineEdit(self.add_character_dialog)
        password_input.setEchoMode(QLineEdit.Password)

        server_input_label = QLabel("Server")
        server_input = QComboBox(self)
        server_input.addItem("Localhost (127.0.0.1)", "127.0.0.1")
        server_input.addItem("Local Network (192.168.1.110)", "192.168.1.110")
        server_input.addItem("Ugaris Server", "login.ugaris.com")
        server_input.setCurrentIndex(int(self.inputs.get("server", 0)))

        # Create a layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(server_input_label)
        layout.addWidget(server_input)
        layout.addWidget(character_input_label)
        layout.addWidget(character_input)
        layout.addWidget(password_input_label)
        layout.addWidget(password_input)

        # Create a button to save the data
        save_button = QPushButton("Save", self.add_character_dialog)
        layout.addWidget(save_button)

        # Connect the save button to a function to save the data
        save_button.clicked.connect(
            lambda: self.save_character(server_input.currentData(), character_input.text(), password_input.text()))

        self.add_character_dialog.setLayout(layout)
        self.add_character_dialog.exec_()

    def save_character(self, server, character, password):
        # Load the current settings from the JSON file
        if os.path.isfile("characters.json"):
            with open("characters.json", "r") as f:
                settings = json.load(f)
        else:
            settings = []

        # Add the new server and character data to the settings
        character_data = {"server": server, "username": character, "password": password}
        settings.append(character_data)

        # Save the updated settings to the JSON file
        with open("characters.json", "w") as f:
            json.dump(settings, f)

        # Close the dialog
        self.add_character_dialog.close()
        self.populate_character_table()
        self.CharacterTable.selectRow(0)

    def save_settings(self, server, character, password):
        # Load the current settings from the JSON file
        if os.path.isfile("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
        else:
            settings = {"servers": [], "characters": []}

        # Add the new server and character data to the settings
        server_data = {"name": server}
        character_data = {"username": character, "password": password}
        settings["servers"].append(server_data)
        settings["characters"].append(character_data)

        # Save the updated settings to the JSON file
        with open("settings.json", "w") as f:
            json.dump(settings, f)

        # Close the dialog
        self.settings_dialog.close()

    def restore_inputs(self):
        self.inputs = {}
        if os.path.isfile("inputs.txt"):
            with open("inputs.txt", "r") as f:
                for line in f:
                    key, value = line.strip().split(":")
                    self.inputs[key] = value

    def save_inputs(self):
        with open("inputs.txt", "w") as f:
            for key, value in self.inputs.items():
                f.write(f"{key}:{value}\n")

    def serverChanged(self, index):
        self.inputs["server"] = index
        if self.remember_checkbox.isChecked():
            self.save_inputs()

    def usernameChanged(self, text):
        self.inputs["username"] = text
        if self.remember_checkbox.isChecked():
            self.save_inputs()

    def passwordChanged(self, text):
        self.inputs["password"] = text
        if self.remember_checkbox.isChecked():
            self.save_inputs()

    def check_updates(self):
        # Parse the response for the latest version
        latest_version = self.release_api_url_body["tag_name"]

        # Check if version.txt exists
        if not os.path.isfile(self.latest_version_file):
            self.label.setText("Downloading latest release...")
            self.update_app(latest_version)
            return

        # Check if update is available
        with open(self.latest_version_file, "r") as f:
            current_version = f.read().strip()

        if current_version != latest_version:
            # Get release notes
            release_notes = self.release_api_url_body["body"]

            # Display update message
            message = f"A new version ({latest_version}) of the app is available:\n\n{release_notes}"
            response = QMessageBox.question(self, "Update Available", message, QMessageBox.Yes | QMessageBox.No)

            if response == QMessageBox.Yes:
                self.label.setText("Downloading update...")
                self.update_app(latest_version)
        else:
            self.label.setText("No updates available.")
            self.PlayButton.setEnabled(True)

    def update_app(self, latest_version):
        # Download the latest release from GitHub
        asset_url = self.release_api_url_body["assets"][0]["browser_download_url"]
        release_file = self.release_api_url_body["assets"][0]["name"]
        try:
            with requests.get(asset_url, stream=True) as r:
                r.raise_for_status()
                self.progress_bar.show()
                with open(release_file, 'wb') as f:
                    total_length = int(r.headers.get("content-length"))
                    dl = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)
                        dl += len(chunk)
                        progress = int(100 * dl / total_length)
                        print(progress)
                        self.progress_bar.setValue(progress)
                        QApplication.processEvents()

        except requests.exceptions.RequestException as e:
            self.label.setText(f"Error: {e}")
            return

        # Extract the release files to the current directory
        import zipfile
        with zipfile.ZipFile(release_file, "r") as zip_ref:
            zip_ref.extractall(".")

        # Update the version file
        with open(self.latest_version_file, "w") as f:
            f.write(latest_version)

        # Clean up
        os.remove(release_file)
        self.label.setText(f"Updated to version {latest_version}")
        self.PlayButton.setEnabled(True)

    def create_options_arg(self):

        option_mapping = {
            'enable_dark_gui': 0,
            'enable_context': 1,
            'enable_actionbar': 2,
            'enable_smaller_bottom_window': 3,
            'enable_smaller_top_window': 4,
            'enable_big_health_bar': 5,
            'enable_sound': 6,
            'enable_large_font': 7,
            'enable_true_full_screen': 8,
            'enable_legacy_mouse_wheel': 9
        }

        options = bitarray(len(option_mapping))
        options.setall(False)
        if self.settings_dialog:
            for checkbox_name, option_value in option_mapping.items():
                checkbox = getattr(self.settings_dialog, checkbox_name)
                if checkbox.isChecked():
                    options[option_value] = True
        return int.from_bytes(options.tobytes(), byteorder='little')

    def launch_app(self):

        server = self.CharacterTable.item(self.CharacterTable.currentRow(), 0).text()
        username = self.CharacterTable.item(self.CharacterTable.currentRow(), 1).text()
        password = self.CharacterTable.item(self.CharacterTable.currentRow(), 2).text()
        width = self.settings_dialog.desired_width.text()
        height = self.settings_dialog.desired_height.text()
        sdl_cache = self.settings_dialog.sdl_cache_size.text()
        sdl_multi = self.settings_dialog.sdl_multi.text()
        sdl_frames = self.settings_dialog.sdl_frames.text()

        options_arg = self.create_options_arg()
        app_path = None
        app_args = None
        if sys.platform == "linux" or sys.platform == "linux2":
            # linux
            app_path = "wine"
            app_args = ["bin/moac.exe", f"-u {username}", f"-p {password}",
                        f"-d {server}", f"-w {width}",
                        f"-h {height}", f"-o {options_arg}", f"-c {sdl_cache}", f"-k {sdl_frames}", f"-m {sdl_multi}"]

        elif sys.platform == "darwin":
            # OS X
            app_path = "wine"
            app_args = ["bin/moac.exe", f"-u {username}", f"-p {password}",
                        f"-d {server}", f"-w {width}",
                        f"-h {height}", f"-o {options_arg}", f"-c {sdl_cache}", f"-k {sdl_frames}", f"-m {sdl_multi}"]

        elif sys.platform == "win32":
            # Windows...
            app_path = "bin/moac.exe"
            app_args = [f"-u {username}", f"-p {password}",
                        f"-d {server}", f"-w {width}",
                        f"-h {height}", f"-o {options_arg}", f"-c {sdl_cache}", f"-k {sdl_frames}", f"-m {sdl_multi}"]

        # Launch the app
        try:
            print(app_path + " " + str(app_args))
            os.execvp(app_path, [app_path] + app_args)
        except OSError as e:
            self.label.setText(f"Error: {e}")

    def close(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    update_app = UpdateApp()
    update_app.show()
    sys.exit(app.exec_())
