#! /usr/bin/python3
import os
import subprocess
import shlex

from gi.repository import GLib, Gio

from pydbus import SystemBus
from pydbus.error import register_error, map_error, map_by_default, error_registration
import howdyd
from howdyd.error import NoDeviceFoundException, NoScanFoundException, ScanFailedException, AccessDenied
from howdyd.device import HowdyDevice
from howdyd.models import HowdyModel
from howdyd.scan import HowdyScan
from howdyd.caller import HowdyCaller

model_path = os.path.join("/var/lib/howdy", "models")
bus = SystemBus()

class HowdyManager(object):
    """
        <node>
            <interface name='nl.boltgolt.Howdy.Manager'>
                <method name='GetDevices'>
                    <arg type='ao' name='devices' direction='out'/>
                </method>
                <method name='GetPreferredDevice'>
                    <arg type='o' name='device' direction='out'/>
                </method>
                <method name='GetConfiguredDevice'>
                    <arg type='o' name='device' direction='out'/>
                </method>
                <method name="GetScans">
                  <arg type="s" name="username" direction="in"/>
                  <arg type="ao" name="scans" direction="out"/>
                </method>
                <method name="TakeScan">
                  <arg type="s" name="username" direction="in"/>
                  <arg type="s" name="name" direction="in"/>
                  <arg type="o" name="scan" direction="out"/>
                </method>
                <method name="DeleteScans">
                  <arg type="s" name="username" direction="in"/>
                </method>
            </interface>
        </node>
    """

    def __init__(self):
        self.devices = []
        self.scan_objects = {}
        self.model = {}
        self._callers = {}

    def get_devices(self):
        for device in self.devices:
            device._registration.unregister()

        self.devices = []
        self.preferred_device = None

        device_names = os.listdir("/dev/v4l/by-path")

        if not device_names:
            raise NoDeviceFoundException()

        for device_name in device_names:
            device_path = os.path.join("/dev/v4l/by-path", device_name)
            try:
                device = HowdyDevice(device_path)

                self.devices.append(device)

                if not self.preferred_device:
                    self.preferred_device = device
                elif not self.preferred_device.is_infrared:
                    self.preferred_device = device
            except Exception as e:
                print(e)

        for device in self.devices:
            device._registration = bus.register_object(device.bus_object_path, device, device.__doc__)

        return [device.bus_object_path for device in self.devices]

    def GetDevices(self):
        """Returns the video devices available for face scanning"""

        return self.get_devices()

    def get_preferred_device(self):
        if not self.preferred_device:
            self.get_devices()

        if not self.preferred_device:
            raise NoDeviceFoundException()

        return self.preferred_device

    def get_configured_device(self):
        if not self.devices:
            self.get_devices()

        try:
            [default_device] = list(filter(lambda device: device.IsDefault(), self.devices))
        except Exception as e:
            raise NoDeviceFoundException()

        return default_device

    def get_scans(self, username):
        if not username in self.model:
            self.model[username] = HowdyModel(username)

        if username in self.scan_objects:
            for scan_object in self.scan_objects[username]:
                scan_object._registration.unregister()

        self.scan_objects[username] = []

        if not self.model[username].scans:
            return []

        for scan in self.model[username].scans:
            scan_object = HowdyScan(scan)
            scan_object._registration = bus.register_object(scan_object.bus_object_path, scan_object, scan_object.__doc__)
            self.scan_objects[username].append(scan_object)

        return self.scan_objects[username]

    def take_scan(self, username, name):
        self.delete_scans(username)

        status, output = subprocess.getstatusoutput([f"howdy --user '{shlex.quote(username)}' add -y"])

        if status != 0:
            raise ScanFailedException(output)

        scans = self.get_scans(username)

        if not scans:
            raise ScanFailedException()

        return scans[0]

    def delete_scans(self, username):
        subprocess.call(["howdy", "--user", username, "clear", "-y"])

        if username in self.model:
            del self.model[username]

    def look_up_caller(self, dbus_context):
        def on_caller_vanished():
            if dbus_context.sender in self._callers:
                del self._callers[dbus_context.sender]._name_watch
                del self._callers[dbus_context.sender]

        if not dbus_context.sender in self._callers:
            self._callers[dbus_context.sender] = HowdyCaller(dbus_context.sender)
            self._callers[dbus_context.sender]._name_watch = bus.watch_name(dbus_context.sender, name_vanished=on_caller_vanished)

        return self._callers[dbus_context.sender]

    def check_management_policy_for_username(self, username, dbus_context):
        try:
            caller = self.look_up_caller(dbus_context)
        except Exception as e:
            print(e)
            raise AccessDenied()

        policy = caller.get_management_policy_for_username(username)
        if not dbus_context.is_authorized(policy, {}, interactive=True):
            raise AccessDenied()

    def GetPreferredDevice(self):
        """Returns the most appropriate video device for face scanning"""
        device = self.get_preferred_device()
        return device.bus_object_path

    def GetConfiguredDevice(self):
        """Returns the video device configured for face scanning"""
        device = self.get_configured_device()
        return device.bus_object_path

    def GetScans(self, username):
        """Returns the face scans available for face scanning"""
        scans = self.get_scans(username)
        return [scan_object.bus_object_path for scan_object in scans]

    def TakeScan(self, username, name, dbus_context):
        """Does a face scan"""
        self.check_management_policy_for_username(username, dbus_context)
        scan = self.take_scan(username, name)
        return scan.bus_object_path

    def DeleteScans(self, username, dbus_context):
        """Deletes face scans"""
        self.check_management_policy_for_username(username, dbus_context)
        self.delete_scans(username)
