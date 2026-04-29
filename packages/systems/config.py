"""

"""

def load_config_screen() -> dict:
    try:
        import json

        with open("packages/.config/_screen.json") as file:
            config_data = json.load(file)
            
        return config_data
    except FileNotFoundError:
        pass
