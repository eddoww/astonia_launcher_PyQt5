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
        self.enable_sound = QCheckBox()
        self.enable_dark_gui = QCheckBox()
        self.enable_context = QCheckBox()
        self.enable_actionbar = QCheckBox()
        self.enable_smaller_bottom_window = QCheckBox()
        self.enable_smaller_top_window = QCheckBox()
        self.enable_big_health_bar = QCheckBox()
        self.enable_large_font = QCheckBox()
        self.enable_true_full_screen = QCheckBox()
        self.enable_legacy_mouse_wheel = QCheckBox()
        self.executable_name = QLineEdit()
        self.sdl_frames = QSpinBox()
        self.sdl_cache_size = QSpinBox()
        self.sdl_multi = QSpinBox()

        # Set up limitations on fields
        self.desired_width.setMinimum(800)
        self.desired_width.setMaximum(5000)
        self.desired_height.setMinimum(600)
        self.desired_height.setMaximum(5000)
        self.sdl_frames.setMinimum(24)
        self.sdl_cache_size.setMinimum(8000)
        self.sdl_cache_size.setMaximum(16000)
        self.sdl_multi.setMinimum(4)

        # Create layout for settings
        layout = QGridLayout()
        layout.addWidget(QLabel("Width:"), 0, 0)
        layout.addWidget(self.desired_width, 0, 1)
        layout.addWidget(QLabel("Height:"), 1, 0)
        layout.addWidget(self.desired_height, 1, 1)
        layout.addWidget(QLabel("Fullscreen:"), 2, 0)
        layout.addWidget(self.enable_fullscreen, 2, 1)
        layout.addWidget(QLabel("Sound:"), 3, 0)
        layout.addWidget(self.enable_sound, 3, 1)
        layout.addWidget(QLabel("Dark GUI:"), 4, 0)
        layout.addWidget(self.enable_dark_gui, 4, 1)
        layout.addWidget(QLabel("Context:"), 5, 0)
        layout.addWidget(self.enable_context, 5, 1)
        layout.addWidget(QLabel("Action bar and keybindings:"), 6, 0)
        layout.addWidget(self.enable_actionbar, 6, 1)
        layout.addWidget(QLabel("Smaller bottom window:"), 7, 0)
        layout.addWidget(self.enable_smaller_bottom_window, 7, 1)
        layout.addWidget(QLabel("Smaller top window:"), 8, 0)
        layout.addWidget(self.enable_smaller_top_window, 8, 1)
        layout.addWidget(QLabel("Big health bar:"), 9, 0)
        layout.addWidget(self.enable_big_health_bar, 9, 1)
        layout.addWidget(QLabel("Large font:"), 10, 0)
        layout.addWidget(self.enable_large_font, 10, 1)
        layout.addWidget(QLabel("True Fullscreen:"), 11, 0)
        layout.addWidget(self.enable_true_full_screen, 11, 1)
        layout.addWidget(QLabel("Legacy Mousewheel"), 12, 0)
        layout.addWidget(self.enable_legacy_mouse_wheel, 12, 1)

        layout.addWidget(QLabel("Executable name:"), 13, 0)
        layout.addWidget(self.executable_name, 13, 1)
        layout.addWidget(QLabel("SDL frames:"), 14, 0)
        layout.addWidget(self.sdl_frames, 14, 1)
        layout.addWidget(QLabel("SDL cache"), 15, 0)
        layout.addWidget(self.sdl_cache_size, 15, 1)
        layout.addWidget(QLabel("SDL multi"), 16, 0)
        layout.addWidget(self.sdl_multi, 16, 1)
        # Buttons
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        layout.addWidget(self.save_button, 17, 0)
        layout.addWidget(self.cancel_button, 17, 1)

        # Signals
        self.save_button.clicked.connect(self.save_settings_to_file)
        self.cancel_button.clicked.connect(self.cancel)

        self.setLayout(layout)

    def cancel(self):
        self.close()

    def save_settings_to_file(self):
        # List of field names
        field_names = [
            "desired_width",
            "desired_height",
            "enable_fullscreen",
            "enable_sound",
            "enable_dark_gui",
            "enable_context",
            "enable_actionbar",
            "enable_smaller_bottom_window",
            "enable_smaller_top_window",
            "enable_big_health_bar",
            "enable_large_font",
            "enable_true_full_screen",
            "enable_legacy_mouse_wheel",
            "executable_name",
            "sdl_frames",
            "sdl_cache_size",
            "sdl_multi",
        ]

        # Create an empty dictionary to hold the settings
        settings_dict = {}

        # Loop through the field names and add them to the settings_dict
        for field_name in field_names:
            field_widget = getattr(self, field_name)
            if isinstance(field_widget, QCheckBox):
                settings_dict[field_name] = field_widget.isChecked()
            elif isinstance(field_widget, QLineEdit):
                field_value = field_widget.text()
                if field_value.isdigit():
                    settings_dict[field_name] = int(field_value)
                else:
                    settings_dict[field_name] = field_value
            elif isinstance(field_widget, QSpinBox):
                settings_dict[field_name] = field_widget.value()

        with open("settings/settings.json", "w") as f:
            json.dump(settings_dict, f)
            self.close()

    def load_settings_from_file(self):
        default_settings_dict = {
            "desired_width": 1600,
            "desired_height": 1200,
            "enable_fullscreen": False,
            "enable_sound": True,
            "enable_dark_gui": False,
            "enable_context": True,
            "enable_actionbar": True,
            "enable_smaller_bottom_window": True,
            "enable_smaller_top_window": True,
            "enable_big_health_bar": True,
            "enable_large_font": False,
            "enable_true_full_screen": False,
            "enable_legacy_mouse_wheel": False,
            "executable_name": "bin/moac.exe",
            "sdl_frames": 24,
            "sdl_cache_size": 8000,
            "sdl_multi": 4,
        }
        try:
            with open("settings/settings.json", "r") as f:
                settings_dict = json.load(f)
        except FileNotFoundError:
            # Return default settings if file not found
            settings_dict = default_settings_dict

        # Update widget values based on settings_dict
        for key, value in settings_dict.items():
            if hasattr(self, key):
                widget = getattr(self, key)
                if isinstance(widget, QCheckBox):
                    widget.setChecked(value)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(value)
                elif isinstance(widget, QLineEdit):
                    widget.setText(value)
            else:
                print(f"Warning: widget {key} not found")
