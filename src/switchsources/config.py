import json


class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = None
        self.load_config()

    def load_config(self):
        if not self.config:
            with open(self.config_path, 'r') as config_file:
                self.config = json.load(config_file)

    def get_config(self, key=None):
        if not self.config:
            self.load_config()
        if not key:
            return self.config
        return self.config.get(key)

    def set_config(self, key, value):
        if not self.config:
            self.load_config()
        self.config[key] = value

    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)