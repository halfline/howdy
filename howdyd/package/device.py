#! /usr/bin/python3
from gi.repository import GLib, Gio
from pydbus.error import register_error, map_error, map_by_default, error_registration
import subprocess
import cv2
import os
import re
import howdyd
import configparser
from howdyd.error import DeviceWontOpenException

OBJECT_PATH_PREFIX = "/nl/boltgolt/Howdy/Devices"

class HowdyDevice(object):
    """
        <node>
            <interface name="nl.boltgolt.Howdy.Device">
                <property name="DevicePath" type="ay" access="read"/>
                <property name="DeviceName" type="s" access="read"/>
                <property name="IsInfrared" type="b" access="read"/>
                <property name="IsDefault" type="b" access="read"/>
                <method name="SetDefault"/>
            </interface>
        </node>
    """

    def __init__(self, device_path):
        self.device_path = device_path
        self.device_name = device_path

        # FIXME: Use gudev for this
        udevadm = subprocess.check_output([f"udevadm info -r --query=all -n {device_path}"], shell=True).decode("utf-8")

        for line in udevadm.split("\n"):
            re_name = re.search('product.*=(.*)$', line, re.IGNORECASE)
            if re_name:
                self.device_name = re_name.group(1).replace("_", " ")

        capture = cv2.VideoCapture(device_path)
        is_open, frame = capture.read()

        if not is_open:
            raise DeviceWontOpenException()

        # FIXME: There are better ways to find out if it's gray/IR
        self.is_infrared = self.is_gray(frame)

        if self.is_infrared:
            self.device_name += " (Infrared)"
        else:
            self.device_name += " (Color)"

        def escape_path_component(match_object):
            return f"__{ord(match_object.group(0))}__"

        bus_base_name = re.sub(r'[^A-Za-z0-9]',
                               escape_path_component,
                               self.device_path)

        self.bus_object_path = f"{OBJECT_PATH_PREFIX}/{bus_base_name}"
    def is_gray(self, frame):
        for row in frame:
            for pixel in row:
                if not pixel[0] == pixel[1] == pixel[2]:
                    return False
                return True

    def SetDefault(self):
        """Sets the video device to use for scans"""
        config_path = os.path.join("/etc/howdy", "config.ini")
        config = configparser.ConfigParser()
        config.read(config_path)
        try:
            config.add_section("video")
        except:
            pass

        try:
            config.set("video", "device_path", self.device_path)
        except:
            pass

        with open(config_path, 'w') as config_file:
            config.write(config_file)

    @property
    def DevicePath(self):
        """The video device path"""
        return bytes(self.device_path, encoding='utf-8', errors='ignore')

    @property
    def DeviceName(self):
        """A human readable device name"""
        return self.device_name

    @property
    def IsInfrared(self):
        """A human readable device name"""
        return self.is_infrared

    @property
    def IsDefault(self):
        config_path = os.path.join("/etc/howdy", "config.ini")
        config = configparser.ConfigParser()
        config.read(config_path)
        default_device = config.get("video", "device_path")

        return default_device == self.device_path
