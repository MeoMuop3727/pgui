"""

"""

import json

# Return the config of screen
def load_config_screen() -> dict:
    with open("packages/config/_screen.json") as file:
        config_screen = json.load(file)
        
    return config_screen

# Return the config of logger
def load_config_logger() -> dict:
    with open("packages/config/_log.json") as file:
        config_logger = json.load(file)
    
    return config_logger

# Set the config of screen
def set_config_screen(key: str, new_value: any) -> None:
    pass

# Set the config of logger
def set_config_logger(key: str, new_value: any) -> None:
    pass

