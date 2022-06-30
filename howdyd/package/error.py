#! /usr/bin/python3
from gi.repository import GLib, Gio
from pydbus.error import register_error, map_error, map_by_default, error_registration

HOWDY_ERROR = Gio.DBusError.quark()

@register_error("nl.boltgolt.Howdy.Error.NoDeviceFound", HOWDY_ERROR, 0)
class NoDeviceFoundException(Exception):
    pass

@register_error("nl.boltgolt.Howdy.Error.DeviceWontOpen", HOWDY_ERROR, 0)
class DeviceWontOpenException(Exception):
    pass

@register_error("nl.boltgolt.Howdy.Error.NoScanFound", HOWDY_ERROR, 0)
class NoScanFoundException(Exception):
    pass

@register_error("nl.boltgolt.Howdy.Error.ScanFailed", HOWDY_ERROR, 0)
class ScanFailedException(Exception):
    pass

@register_error("nl.boltgolt.Howdy.Error.AccessDenied", HOWDY_ERROR, 0)
class AccessDenied(Exception):
    pass
