import json

from PyQt5.QtWidgets import (
    QDialog,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QGridLayout,
    QLabel,
    QPushButton,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create widgets for all settings
        self.desired_width = QSpinBox()
        self.desired_height = QSpinBox()
        self.enable_fullscreen = QCheckBox()
        self.enable_true_full_screen = QCheckBox()
        self.enable_sound = QCheckBox()
        self.enable_dark_gui = QCheckBox()
        self.enable_context = QCheckBox()
        self.enable_keybindings = QCheckBox()  # For new keybindings
        self.enable_smaller_bottom_window = QCheckBox()
        self.enable_smaller_top_window = QCheckBox()
        self.enable_big_health_bar = QCheckBox()
        self.enable_large_font = QCheckBox()
        self.enable_legacy_mouse_wheel = QCheckBox()
        self.enable_gamma_increase = QCheckBox()  # For gamma increase
        self.enable_minimap_management = QCheckBox()  # For minimap management
        self.enable_minimap = QCheckBox()  # To enable/disable minimap
        self.enable_appdata_usage = QCheckBox()  # To use %appdata% for storing application files
        self.executable_name = QLineEdit()
        self.sdl_frames = QSpinBox()
        self.sdl_cache_size = QSpinBox()
        self.sdl_multi = QSpinBox()

        # Set up limitations on fields
        self.desired_width.setRange(800, 5000)
        self.desired_height.setRange(600, 5000)
        self.sdl_frames.setRange(24, 60)  # Assuming upper limit for frames
        self.sdl_cache_size.setRange(8000, 16000)
        self.sdl_multi.setRange(4, 10)  # Assuming a realistic upper limit

        # Create layout for settings
        layout = QGridLayout()
        self.add_widgets_to_layout(layout)

        # Buttons
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        layout.addWidget(self.save_button, 21, 0)
        layout.addWidget(self.cancel_button, 21, 1)

        # Signals
        self.save_button.clicked.connect(self.save_settings_to_file)
        self.cancel_button.clicked.connect(self.cancel)

        self.setLayout(layout)

    def add_widgets_to_layout(self, layout):
        widgets = [
            (self.desired_width, "Width:", 0),
            (self.desired_height, "Height:", 1),
            (self.enable_fullscreen, "Fullscreen:", 2),
            (self.enable_true_full_screen, "True Fullscreen Mode:", 3),
            (self.enable_sound, "Sound:", 4),
            (self.enable_dark_gui, "Dark GUI by Tegra:", 5),
            (self.enable_context, "Context Menu Enabled:", 6),
            (self.enable_keybindings, "New Keybindings:", 7),
            (self.enable_smaller_bottom_window, "Smaller Bottom GUI:", 8),
            (self.enable_smaller_top_window, "Top GUI Slides Away:", 9),
            (self.enable_big_health_bar, "Big Health/Mana Bars:", 10),
            (self.enable_large_font, "Large Font:", 11),
            (self.enable_legacy_mouse_wheel, "Legacy Mouse Wheel Logic:", 12),
            (self.enable_gamma_increase, "Increase Gamma:", 13),
            (self.enable_minimap_management, "Manage Minimaps:", 14),
            (self.enable_minimap, "Enable Minimap:", 15),
            (self.enable_appdata_usage, "Write to %appdata%:", 16),
            (self.executable_name, "Executable Name:", 17),
            (self.sdl_frames, "SDL Frames:", 18),
            (self.sdl_cache_size, "SDL Cache Size:", 19),
            (self.sdl_multi, "SDL Multi-threading:", 20),
        ]
        for widget, label, row in widgets:
            layout.addWidget(QLabel(label), row, 0)
            layout.addWidget(widget, row, 1)

    def cancel(self):
        self.close()

    def save_settings_to_file(self):
        settings_dict = {name: getattr(self, name).value() if isinstance(getattr(self, name), QSpinBox)
        else getattr(self, name).isChecked() if isinstance(getattr(self, name), QCheckBox)
        else getattr(self, name).text()
                         for name in self.__dict__ if not name.startswith('__') and not callable(getattr(self, name))}

        try:
            with open("settings/settings.json", "w") as f:
                json.dump(settings_dict, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")
        else:
            self.close()

    def load_settings_from_file(self):
        try:
            with open("settings/settings.json", "r") as f:
                settings_dict = json.load(f)
            for key, value in settings_dict.items():
                widget = getattr(self, key, None)
                if widget:
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(value)
                    elif isinstance(widget, QSpinBox):
                        widget.setValue(value)
                    elif isinstance(widget, QLineEdit):
                        widget.setText(value)
        except FileNotFoundError:
            print("Settings file not found, loading defaults.")
        except json.JSONDecodeError:
            print("Error decoding settings, check file format.")
