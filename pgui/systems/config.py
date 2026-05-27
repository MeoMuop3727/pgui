"""Utility module for loading and managing application configuration files."""

PATH_CONFIG_SCREEN = "pgui/config/_screen.json"

import json

class config:
    def __init__(self, path: str = PATH_CONFIG_SCREEN):
        self.__path = path

        try:
            with open(self.__path, "r") as file:
                self.__data: dict = json.load(file)
        except FileNotFoundError:
            self.__data: dict = []
    
    def load(self) -> dict:
        return self.__data
    
    def set(self, key: str, value: any):
        self.__data[key] = value
    
    def pop(self, key: str) -> any:
        return self.__data.pop(key)

    def intro_doc(self, name):
        print(f"{self.__data["window"]["intro-doc"]}. {name}")
    
    def update(self):
        with open(self.__path, "w") as file:
            json.dump(self.__data, file, indent="\t", ensure_ascii=False)
