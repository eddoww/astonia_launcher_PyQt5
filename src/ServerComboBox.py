import json
import os

from PyQt5.QtWidgets import (
    QComboBox
)


class ServerComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        if parent:
            self.servers_file = parent.servers_file  # Use the settings file from the parent
        else:
            self.servers_file = "settings/servers.json"  # Fallback path
        self.load_servers()

    def load_servers(self):
        if not os.path.isfile(self.servers_file):
            # Create a new servers file with default values
            default_servers = [
                {"name": "Ugaris Server", "address": "login.ugaris.com"},
                # {"name": "Localhost (127.0.0.1)", "address": "127.0.0.1"}
            ]
            with open(self.servers_file, 'w') as f:
                json.dump({'servers': default_servers}, f)
            for server in default_servers:
                self.addItem(server['name'], server['address'])
        else:
            # Load servers from the file
            with open(self.servers_file, 'r') as f:
                data = json.load(f)
                servers = data.get('servers', [])
                for server in servers:
                    self.addItem(server['name'], server['address'])

    def save_servers(self):
        servers = []
        for i in range(self.count()):
            name = self.itemText(i)
            address = self.itemData(i)
            servers.append({'name': name, 'address': address})

        with open(self.servers_file, 'w') as f:
            json.dump({'servers': servers}, f)

    def add_server(self, name, address):
        self.addItem(name, address)
        self.setCurrentIndex(self.count() - 1)
        self.save_servers()

    def delete_server(self, index):
        self.removeItem(index)
        self.save_servers()
