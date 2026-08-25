import hashlib
import hmac
from Classes.Objects import *

HMAC_KEY = b"1FB00CC8D8D94CD0A94C847C2F04A921"
LENGTH_MARKER = bytes.fromhex('14000000')  # int32 length=20, little-endian

START_MARKER: bytes = b"Gamepad_RightY"
START_MARKER_LENGTH: int = 0x0F

def locate_itembox_start(data):
    ...

def locate_checksum(data: bytearray, key=HMAC_KEY) -> int:
    """Scan the file once and find the checksum whose message is data[:offset].

    Returns the absolute offset of the length-prefix field (the '14 00 00 00'
    marker) for the first candidate that actually verifies against `key`.
    Raises ValueError if nothing verifies.
    """
    h = hmac.new(key, b'', hashlib.sha1)
    pos:         int = 0
    search_from: int = 0

    while True:
        candidate: int = data.find(LENGTH_MARKER, search_from)
        if candidate == -1:
            break
        if candidate + 24 > len(data):
            break
        h.update(data[pos:candidate])
        pos = candidate
        stored = data[candidate + 4:candidate + 24]
        if h.copy().digest() == stored:
            return candidate
        search_from = candidate + 1
    raise ValueError("No checksum in this file verifies against the given key.")


def update_checksum(data: bytearray, offset: int, key=HMAC_KEY) -> bytes:
    """Recompute the HMAC over data[:offset] and rewrite the 20 bytes after
    the length marker at `offset` in place. Returns the same bytearray.
    """
    if not isinstance(data, bytearray):
        raise TypeError("data must be a bytearray so it can be edited in place")
    computed = hmac.new(key, bytes(data[:offset]), hashlib.sha1).digest()
    data[offset + 4:offset + 24] = computed
    return data


class SaveFile:
    """Keeps the checksum offset around between load and save so ewe can
    edit `self.data` freely in between without re-locating anything.
    """
    weapons:        list[Equipment]    = []
    accessories:    list[Equipment]    = []

    def __init__(self, path, key=HMAC_KEY):
        self.path = path
        self.key = key
        with open(path, 'rb') as f:
            self.data = bytearray(f.read())
        self.checksum_offset = locate_checksum(self.data, key)
        print(f"[+] Loaded '{path}', checksum offset = {self.checksum_offset:#x}")

    def save(self, path=None):
        """Recompute the checksum at the stored offset and write the file."""
        update_checksum(self.data, self.checksum_offset, self.key)
        out_path = path or self.path
        with open(out_path, 'wb') as f:
            f.write(self.data)
        print(f"[+] Saved '{out_path}' with updated checksum")
