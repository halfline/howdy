#! /usr/bin/python3
from gi.repository import GLib
from pydbus import SystemBus

import sys

import howdyd
from howdyd.manager import HowdyManager

def run():
    loop = GLib.MainLoop()
    with SystemBus() as bus:
        with bus.publish("nl.boltgolt.Howdy", ("Manager", HowdyManager())):
            loop.run()
