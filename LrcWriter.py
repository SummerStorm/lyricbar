#!/usr/bin/env python3
from pytag import AudioReader
import glob
# import os.path
from os import walk, makedirs
from os.path import dirname, join, exists
from _datetime import timedelta

from Settings import exit_with_message, Settings

class LrcWriter:
    def __init__(self):
        self.settingsDict = Settings().getSettings()
    
    def run(self):
        basePath = self.settingsDict['music path']
        for artistFolder in next(walk(basePath))[1]:
            artistFolder = join(basePath, artistFolder)
            for file in glob.glob(join(artistFolder, "*.mp3")):
                self.process(file)

    def process(self, file):
        print("\nProcessing " + file)
        pair = FilePair(file, self.settingsDict['music path'], self.settingsDict['lyrics path'])
        pair.writeDummy()
        # pair.write()
        

class FilePair:
    def __init__(self, mp3, mp3Base, lrcBase):
        self.mp3 = mp3
        self.tags = AudioReader(mp3).get_tags()
        self.artist = self.tags['artist'].strip()
        if self.artist[-1] == "\0":
            self.artist = self.artist[:-1]
        self.title = self.tags['title'].strip()
        if self.title[-1] == "\0":
            self.title = self.title[:-1]
        self.validate(mp3Base)
        self.lrc = join(lrcBase, self.artist, self.artist + ' - ' + self.title + '.lrc')

    def validate(self, mp3Base):
        mp3Alt = join(mp3Base, self.artist, self.artist + ' - ' + self.title + '.mp3')
        if self.mp3 != mp3Alt:
            exit_with_message("\nMP3 file path does not match its ID3 tags:\n" + 
                              "mp3 file path: " + self.mp3 + 
                              "\nProper path: " + mp3Alt + "\n\n")
    
    def write(self):
        self.checkDirectory()
        if exists(self.lrc):
            return  # If the lrc file already exists, do nothing 
            
        return
    
    def checkDirectory(self):
        directory = dirname(self.lrc)
        if not exists(directory):
            makedirs(directory)
            
    def writeDummy(self):
        self.checkDirectory()
        if exists(self.lrc):
            return  # If the lrc file already exists, do nothing 
        
        oneSecond = timedelta(seconds=1) 
        time = timedelta(seconds=0) 
        
        lyrics = open(self.lrc, 'w')
        for i in range(600):
            time += oneSecond
            lyrics.write(self.toLrcTime(time) + str(time.seconds) + " seconds into " + self.title + '\n')
        lyrics.close()
        
    def toLrcTime(self, time):
        return '[{:02}:{:02}.{:02}]'.format(time.seconds // 60, time.seconds % 60, time.microseconds // 10000)

def main():
    writer = LrcWriter()
    writer.run()

if __name__ == "__main__":
    main()