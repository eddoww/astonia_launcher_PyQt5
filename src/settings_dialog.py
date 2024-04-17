import json
import os

from PyQt5.QtWidgets import (
    QDialog,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Variables
        self.widgets = None

        if parent:
            self.settings_file = parent.settings_file  # Use the settings file from the parent
        else:
            self.settings_file = "settings/settings.json"  # Fallback path

        # Create widgets for all settings
        self.resolution_combo = QComboBox()
        self.populate_resolutions()
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
        self.enable_inventory_optimization = QCheckBox()
        self.enable_animation_optimization = QCheckBox()
        self.enable_gamma_increase = QCheckBox()  # For gamma increase
        self.enable_gamma_increase_more = QCheckBox()  # For more gamma increase
        self.enable_minimap_management = QCheckBox()  # For minimap management
        self.enable_minimap = QCheckBox()  # To enable/disable minimap
        self.enable_sliding_top_bar_sensitivity = QCheckBox()  # Less reactive slider top
        self.enable_appdata_usage = QCheckBox()  # To use %appdata% for storing application files
        self.enable_lighting_effects_reduction = QCheckBox()  # Disable some lightning effects for better performance
        self.executable_name = QLineEdit()
        self.sdl_frames = QSpinBox()
        self.sdl_cache_size = QSpinBox()
        self.sdl_multi = QSpinBox()

        # Set up limitations on fields
        self.sdl_frames.setRange(24, 60)  # Assuming upper limit for frames
        self.sdl_cache_size.setRange(8000, 16000)
        self.sdl_multi.setRange(4, 10)  # Assuming a realistic upper limit

        # Create layout for settings
        self.widget_layout = QGridLayout()
        self.setup_widgets()

        # Connect the fullscreen checkbox to the toggle function
        self.enable_fullscreen.toggled.connect(self.handle_checkbox_toggle)
        self.enable_true_full_screen.toggled.connect(self.handle_checkbox_toggle)

        # Buttons
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.widget_layout.addWidget(self.save_button, 26, 0)
        self.widget_layout.addWidget(self.cancel_button, 26, 1)

        # Signals
        self.save_button.clicked.connect(self.save_settings_to_file)
        self.cancel_button.clicked.connect(self.cancel)

        self.setLayout(self.widget_layout)

        if not self.load_settings_from_file():
            self.initialize_default_settings()

    def setup_widgets(self):
        self.widgets = [
            (self.enable_true_full_screen, "Fullscreen:", 0, False),
            (self.enable_fullscreen, "Windowed Fullscreen:", 1, True),
            (self.resolution_combo, "Resolution (Windowed mode only):", 2, "1600x1200"),
            (self.enable_sound, "Sound:", 3, True),
            (self.enable_dark_gui, "Dark GUI:", 4, False),
            (self.enable_context, "Context Menu Enabled:", 5, True),
            (self.enable_keybindings, "Enable Keybindings:", 6, True),
            (self.enable_smaller_bottom_window, "Smaller Bottom GUI:", 7, False),
            (self.enable_smaller_top_window, "Top GUI Slides Away:", 8, False),
            (self.enable_big_health_bar, "Big Health/Mana Bars:", 9, True),
            (self.enable_large_font, "Large Font:", 10, False),
            (self.enable_legacy_mouse_wheel, "Legacy Mouse Wheel Logic:", 12, False),
            (self.enable_inventory_optimization, "Faster Inventory", 13, True),
            (self.enable_animation_optimization, "Reduced animation buffer:", 14, False),
            (self.enable_gamma_increase, "Increase Gamma:", 15, False),
            (self.enable_gamma_increase_more, "More Gamma Increase:", 16, False),
            (self.enable_minimap_management, "Manage Minimaps:", 17, True),
            (self.enable_minimap, "Enable Minimap:", 18, True),
            (self.enable_sliding_top_bar_sensitivity, "Makes the sliding top bar less sensitive:", 19, False),
            (self.enable_lighting_effects_reduction, "Reduces lighting effects for more performance:", 20, False),
            (self.enable_appdata_usage, "Write to %appdata%:", 21, False),
            (self.executable_name, "Executable Name:", 22, "bin/moac.exe"),
            (self.sdl_frames, "SDL Frames:", 23, 24),
            (self.sdl_cache_size, "SDL Cache Size:", 24, 8000),
            (self.sdl_multi, "SDL Multi-threading:", 25, 3),
        ]
        self.add_widgets_to_layout()

    def handle_checkbox_toggle(self):
        # Mutual exclusivity
        sender = self.sender()
        if sender == self.enable_fullscreen and self.enable_fullscreen.isChecked():
            self.enable_true_full_screen.setChecked(False)
        elif sender == self.enable_true_full_screen and self.enable_true_full_screen.isChecked():
            self.enable_fullscreen.setChecked(False)

        # Visibility of resolution settings
        self.resolution_combo.setVisible(
            not (self.enable_fullscreen.isChecked() or self.enable_true_full_screen.isChecked()))

    def add_widgets_to_layout(self):
        for widget, label, row, default in self.widgets:
            self.widget_layout.addWidget(QLabel(label), row, 0)
            self.widget_layout.addWidget(widget, row, 1)
            if isinstance(widget, QCheckBox):
                widget.setChecked(default)
            elif isinstance(widget, QComboBox):
                index = widget.findText(default)
                if index >= 0:
                    widget.setCurrentIndex(index)
            elif isinstance(widget, QLineEdit):
                widget.setText(default if isinstance(widget, QLineEdit) else default)
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(default))

    def cancel(self):
        self.close()

    def populate_resolutions(self):
        # Common screen resolutions to populate the combo box
        resolutions = ["800x600", "1600x1200", "2400x1800", "3200x2400"]
        for res in resolutions:
            self.resolution_combo.addItem(res)

    def toggle_resolution_visibility(self, checked):
        """Hide or show the resolution combo box based on the fullscreen checkbox."""
        self.resolution_combo.setVisible(not checked)

    def save_settings_to_file(self):
        settings_dict = {name: getattr(self, name).isChecked() if isinstance(getattr(self, name), QCheckBox)
        else getattr(self, name).value() if isinstance(getattr(self, name), QSpinBox)
        else getattr(self, name).currentText() if isinstance(getattr(self, name), QComboBox)
        else getattr(self, name).text()
                         for name in dir(self) if
                         isinstance(getattr(self, name), (QCheckBox, QSpinBox, QComboBox, QLineEdit))}
        try:
            with open(self.settings_file, "w") as f:
                json.dump(settings_dict, f, indent=4)
            print("Settings saved successfully.")
        except Exception as e:
            print(f"Failed to save settings: {e}")
        else:
            self.close()

    def load_settings_from_file(self):
        try:
            with open(self.settings_file, "r") as f:
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
                    elif isinstance(widget, QComboBox):
                        index = widget.findText(value)
                        if index >= 0:
                            widget.setCurrentIndex(index)
        except FileNotFoundError:
            print("Settings file not found, loading defaults.")
            return False
        except json.JSONDecodeError:
            print("Error decoding settings, check file format.")
        return True

    def initialize_default_settings(self):
        if not os.path.exists(self.settings_file):
            self.save_settings_to_file()
