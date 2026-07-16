import os
import yaml

class ConfigurationManager:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        self.configs = {}
        self.load_all()

    def load_all(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        for name in ["system", "models", "security", "hardware", "user"]:
            path = os.path.join(self.config_dir, f"{name}.yaml")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        self.configs[name] = yaml.safe_load(f) or {}
                    except Exception:
                        self.configs[name] = {}
            else:
                self.configs[name] = {}

    def get(self, section, key=None, default=None):
        section_data = self.configs.get(section, {})
        if key is None:
            return section_data
        return section_data.get(key, default)

    def set(self, section, key, value):
        if section not in self.configs:
            self.configs[section] = {}
        self.configs[section][key] = value
        path = os.path.join(self.config_dir, f"{section}.yaml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.configs[section], f)

_config_manager = ConfigurationManager()
def get_config(section, key=None, default=None):
    return _config_manager.get(section, key, default)
def set_config(section, key, value):
    _config_manager.set(section, key, value)
