#! /usr/bin/python3
from gi.repository import GLib, Gio
from pydbus.error import register_error, map_error, map_by_default, error_registration
import subprocess
import cv2
import os
import re
import howdyd
import configparser
import json
from howdyd.error import DeviceWontOpenException

class HowdyModel(object):
    def __init__(self, username):

        model_path = os.path.join("/var/lib/howdy", "models")
        self.model_file = os.path.join(model_path, f"{username}.dat")

        try:
            self.scans = json.load(open(self.model_file))
        except Exception as e:
            print(e)
            self.scans = {}
