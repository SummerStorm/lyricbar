#!/usr/bin/env python

# configure dbus and mainloo
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import Gtk
from mpris2.utils import get_players_uri
from mpris2.player import Player

DBusGMainLoop(set_as_default=True)
mloop = gobject.MainLoop()

# you can use get_players_uri to get current running players uri
uris = get_players_uri()
if not uris:
    raise Exception('No MPRIS2 players available, please start some player with mpris2.')
if len(uris) != 1:
    raise Exception('Found ' + len(uris) + ' players!')

uri = uris[0] 


# create you player
player = Player(dbus_interface_info={'dbus_uri': uri})

print(player.Metadata) 
# player.Next()

def handle_Seeked(self, Position):
    # return
    print('\nhandled' + str(Position))
    # print 'self handled', self.last_fn_return, type(self.last_fn_return)

def handle_PropertiesChanged(self, *args, **kw):
    if kw:
        raise Exception('kw not empty!!!')
    global counter
    print('\ncounter' + str(counter))
    counter += 1
    print(args[1]) 

counter = 0

player.Seeked = handle_Seeked

player.PropertiesChanged = handle_PropertiesChanged

mloop.run()
