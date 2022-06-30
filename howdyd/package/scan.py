#! /usr/bin/python3
from gi.repository import GLib, Gio
from pydbus.error import register_error, map_error, map_by_default, error_registration
import subprocess
import cv2
import re
import howdyd
import configparser

OBJECT_PATH_PREFIX = "/nl/boltgolt/Howdy/Scans"

class HowdyScan(object):
    """
        <node>
            <interface name="nl.boltgolt.Howdy.Scan">
                <property type="s" name="Name" access="read"/>
                <property type="d" name="Id" access="read"/>
            </interface>
        </node>
    """

    def __init__(self, scan_data):
        self.scan_data = scan_data

        self.bus_object_path = f"{OBJECT_PATH_PREFIX}/{self.scan_data['id']}"

    @property
    def Name(self):
        return self.scan_data['label']

    @property
    def Id(self):
        return self.scan_data['id']
