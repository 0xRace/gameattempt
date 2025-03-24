import json
import os

class GameConfig:
    def __init__(self):
        self.default_settings = {
            'window': {
                'width': 1200,
                'height': 800,
                'title': 'Tower Defense Game',
                'fps': 60
            },
            'game': {
                'starting_health': 100,
                'starting_balance': 100,
                'tower_cost': 50,
                'object_speed': 2,
                'object_spawn_rate': 2000  # milliseconds
            },
            'ui': {
                'health_bar_width_percentage': 0.3,
                'health_bar_height_percentage': 0.05,
                'button_min_width': 200,
                'button_height': 50,
                'slider_height': 20,
                'dialog_width_percentage': 0.4,
                'dialog_height_percentage': 0.3
            }
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                saved_settings = json.load(f)
                return self.merge_settings(self.default_settings, saved_settings)
        return self.default_settings.copy()

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f, indent=4)

    def merge_settings(self, default, saved):
        merged = default.copy()
        for key, value in saved.items():
            if key in merged:
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key] = self.merge_settings(merged[key], value)
                else:
                    merged[key] = value
        return merged

    def get(self, category, key):
        return self.settings[category][key]

    def set(self, category, key, value):
        self.settings[category][key] = value
        self.save_settings()

    # Properties for easy access to common settings
    @property
    def window_width(self):
        return self.get('window', 'width')

    @property
    def window_height(self):
        return self.get('window', 'height')

    @property
    def window_title(self):
        return self.get('window', 'title')

    @property
    def fps(self):
        return self.get('window', 'fps')

    @property
    def starting_health(self):
        return self.get('game', 'starting_health')

    @property
    def starting_balance(self):
        return self.get('game', 'starting_balance')

    @property
    def tower_cost(self):
        return self.get('game', 'tower_cost')

    @property
    def object_speed(self):
        return self.get('game', 'object_speed')

    @property
    def object_spawn_rate(self):
        return self.get('game', 'object_spawn_rate')

    @property
    def health_bar_width_percentage(self):
        return self.get('ui', 'health_bar_width_percentage')

    @property
    def health_bar_height_percentage(self):
        return self.get('ui', 'health_bar_height_percentage')

    @property
    def button_min_width(self):
        return self.get('ui', 'button_min_width')

    @property
    def button_height(self):
        return self.get('ui', 'button_height')

    @property
    def slider_height(self):
        return self.get('ui', 'slider_height')

    @property
    def dialog_width_percentage(self):
        return self.get('ui', 'dialog_width_percentage')

    @property
    def dialog_height_percentage(self):
        return self.get('ui', 'dialog_height_percentage') 