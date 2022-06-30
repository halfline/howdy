#! /usr/bin/python3
import os
import pwd

from gi.repository import GLib, Gio

from pydbus import SystemBus
from pydbus.error import register_error, map_error, map_by_default, error_registration

bus = SystemBus()

class HowdyCaller(object):
    def __init__(self, bus_name):
        self.bus_name = bus_name

        proxy = bus.get("org.freedesktop.DBus")
        self.uid = proxy.GetConnectionUnixUser(bus_name)
        self.username = pwd.getpwuid(self.uid).pw_name

    def get_management_policy_for_username(self, username):
        if self.username == username:
            return "nl.boltgolt.Howdy.manage-own-snapshots"

        return "nl.boltgolt.Howdy.manage-any-snapshots"
