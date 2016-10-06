#!/usr/bin/env python3

from gi.repository import Gtk, GLib, Gdk
from gi.repository import AppIndicator3 as appindicator
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import pympris
from threading import Timer, Thread
from os.path import join, exists
from Settings import Settings
from LrcParser import LrcParser
import subprocess
import time

class LyricBar:
    def __init__(self):
        self.counter = 0 
        self.currentLine = None
        self.lyricsPath = Settings().getSettings()['lyrics path']

        dbus_loop = DBusGMainLoop()
        self.bus = dbus.SessionBus(mainloop=dbus_loop)
        
        self.menu = Gtk.Menu()
        self.indie = appindicator.Indicator.new(
            "lyric-bar", "/home/user/bin/1x1.png", appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indie.set_status(appindicator.IndicatorStatus.ACTIVE)
        # create a menu
        self.populate_menu(self.menu)
        
        self.currentFile = ""
        self.pendingTimers = list()
        self.lines = list()
        self.paused = False
        self.mediaplayer = None
        self.playerSetup()

    def playerSetup(self):
        if self.isValidPlayersRunning():
            self.setupMediaPlayer()
            self.displayLine("Waiting for song change.")
        else:
            self.displayLine("No music players active.")
            GLib.timeout_add(500, self.handlerCheckPlayer)
            
    def getLyricsFile(self, artist, title):
        result = join(self.lyricsPath, artist, artist + ' - ' + title + '.lrc')
        for illegal in ["*", "?", ":"]:
            result = result.replace(illegal, "_")
        return result
 
    # =============================== MPRIS2 Part ===============================      
    def handlerCheckPlayer(self):
        if self.isValidPlayersRunning():
            self.setupMediaPlayer()
            self.displayLine("Waiting for song change.")
            return False  # deregister the handler
        else:
            return True  # keep checking
       
    def isValidPlayersRunning(self): 
        return not not pympris.available_players()

    def setupMediaPlayer(self): 
        mediaplayer = pympris.MediaPlayer(list(pympris.available_players())[0], self.bus)
        mediaplayer.player.register_properties_handler(self.handle_properties_changes)
        mediaplayer.playlists.register_properties_handler(self.handle_properties_changes)
        mediaplayer.player.register_signal_handler('Seeked', self.seeked)
        self.mediaplayer = mediaplayer
        self.disconnect.show()

    def handle_properties_changes(self, changed_props, invalidated_props):
        print("===== changed props")
        print(changed_props)
        print("===== invalidated props")
        print(invalidated_props)
        print("===== current line: {}".format(self.currentLine))
        if 'PlaybackStatus' in changed_props:
            # TODO: add saving lines upon pausing and resuming 
            if changed_props['PlaybackStatus'] == 'Paused':
                print("pause signal")
                self.clearAllPendingTimers()
                temp = self.currentLine
                self.displayLine("Paused")
                self.currentLine = temp
                self.paused = True
                return
            elif changed_props['PlaybackStatus'] == 'Playing':
                print("playing signal")
                if self.currentLine:
                    self.displayLine(self.currentLine)
                elif self.paused:
                    self.displayLine("Resumed")
                self.paused = False
        if not 'Metadata' in changed_props:
            return
        metadata = changed_props['Metadata']
        if not 'xesam:artist' in metadata or not 'xesam:title' in metadata:
            self.displayLine("This song is missing its artist or title metadata")
            return
        self.paused = False
        artist = metadata['xesam:artist'][0]
        title = metadata['xesam:title']
        newFile = self.getLyricsFile(artist, title)
        if not self.currentFile or self.currentFile != newFile:
            self.openItem.set_label("Open lyrics file")
            self.openItem.show()
            self.currentFile = newFile
            self.lyricThread = LyricThread(self)
            self.lyricThread.start()
        
    def seeked(self, seekTime):
        print("seeking to " + str(seekTime))
        if not self.paused and seekTime > 0:
            if self.currentLine:
                self.displayLine(self.currentLine)
            self.seekThread = SeekThread(self, seekTime)
            self.seekThread.start()
      
    # =============================== GUI Part ===============================      
    def populate_menu(self, m):
        self.clipboardItem = Gtk.MenuItem("Copy current line to clipboard")
        self.clipboardItem.connect("activate", self.copyToClipboard)
        self.clipboardItem.show()
        m.append(self.clipboardItem)
        self.openItem = Gtk.MenuItem("")
        self.openItem.connect("activate", self.openLyricsFile)
        m.append(self.openItem)
        runItem = Gtk.MenuItem("Run Lyric Converter")
        runItem.connect("activate", self.runConverter)
        runItem.show()
        m.append(runItem)
        self.disconnect = Gtk.MenuItem("Redetect player")
        self.disconnect.connect("activate", self.redetectPlayer)
        m.append(self.disconnect)
        runItem = Gtk.MenuItem("Run Lyric Converter")
        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.quit)
        quit_item.show()
        m.append(quit_item)
        self.indie.set_menu(m)
        
    def redetectPlayer(self, dummy):
        self.disconnect.hide()
        self.playerSetup()
        
    def quit(self, dummy):
        if hasattr(self, 'lyricThread'):
            self.clearAllPendingTimers()
        Gtk.main_quit()

    def copyToClipboard(self, dummy):
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(self.currentLine, -1)

    def openLyricsFile(self, dummy):
        RunThread(['gedit', self.currentFile]).start()

    ConverterCommand = ['scala', "-cp", "~/workspace/lyric-matcher/target/scala-2.11/classes", "matcher.LyricConverter"]
    def runConverter(self, dummy):
        RunThread(self.ConverterCommand).start()
        
    def displayLine(self, line):
        self.counter += 1
        line = line.strip()
        if not line:
            line = " " # enforce a mininum length of at least one
        print("{} trying to display ==>{}<==".format(time.strftime("%Y-%m-%d %H:%M:%S"), line))
        self.currentLine = line
        self.indie.set_label(line, "A"*55)

    def clearAllPendingTimers(self):
        for timer in self.pendingTimers:
            timer.cancel()
        self.pendingTimers.clear()

    def main(self):
        Gtk.main()

# Work in Progress
class DeadmanSwitchThread(Thread):
    def __init__(self, lyricbar, time):
        Thread.__init__(self)
        self.lyricbar = lyricbar
        
    def run(self):
        pass
 
class SeekThread(Thread):
    def __init__(self, lyricbar, time):
        Thread.__init__(self)
        self.lyricbar = lyricbar
        self.time = time
        
    def run(self):
        self.lyricbar.displayLine(" ")
        self.lyricbar.clearAllPendingTimers()
        timeInSeconds = self.time / 1000000.0
        lines = filter(lambda line: line[0] >= timeInSeconds, self.lyricbar.lines)
        for line in lines:
            time = line[0] - timeInSeconds
            timer = Timer(time, self.lyricbar.displayLine, [line[1]])
            self.lyricbar.pendingTimers.append(timer)
        for timer in self.lyricbar.pendingTimers:
            timer.start()

class LyricThread(Thread):
    def __init__(self, lyricbar):
        Thread.__init__(self)
        self.lyricbar = lyricbar
        
    def run(self):
        self.lyricbar.clearAllPendingTimers()
        if not exists(self.lyricbar.currentFile):
            self.lyricbar.displayLine(self.lyricbar.currentFile + " not found!")
        else:
            self.lyricbar.displayLine(" ")
            self.lyricbar.lines.clear()
            self.lyricbar.lines = LrcParser.load(self.lyricbar.currentFile)
            for line in self.lyricbar.lines:
                # Schedule future display
                time = line[0]
                timer = Timer(time, self.lyricbar.displayLine, [line[1]])
                self.lyricbar.pendingTimers.append(timer)
            for timer in self.lyricbar.pendingTimers:
                timer.start()
    
class RunThread(Thread):
    def __init__(self, command):
        Thread.__init__(self)
        self.command = command
        
    def run(self):
        subprocess.call(self.command)
        
if __name__ == "__main__":
    lyricbar = LyricBar()
    lyricbar.main()
