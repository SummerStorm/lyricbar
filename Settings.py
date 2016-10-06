#!/usr/bin/env python3
import yaml
from os.path import expanduser, join, exists

def exit_with_message(message):
    print(message)
    exit()

class Settings:
    SETTINGS_FILE = ".lyricbar.yaml"
    SETTING_PATHS = ['music path', 'lyrics path']

    def __init__(self):
        self.SETTINGS_FILE = join(expanduser("~"), self.SETTINGS_FILE)
        if not exists(self.SETTINGS_FILE):
            exit_with_message("\n\nError! " + self.SETTINGS_FILE + " not found! Exiting.")

        self.settingsDict = yaml.load(open(self.SETTINGS_FILE, 'r'))
        for pathName in self.SETTING_PATHS:
            if pathName not in self.settingsDict:
                exit_with_message("The required path \"" + pathName + "\" was not found in " + self.SETTINGS_FILE + "! Exiting.")
                
            path = self.settingsDict[pathName]
            if path[-1] != '/':
                path += '/'
    
    def getSettings(self):
        return self.settingsDict