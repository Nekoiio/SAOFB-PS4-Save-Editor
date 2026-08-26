import hashlib
import hmac
from Core.Classes.Objects import *

HMAC_KEY = b"1FB00CC8D8D94CD0A94C847C2F04A921"
LENGTH_MARKER = bytes.fromhex('14000000')  # int32 length=20, little-endian

START_MARKER: bytes = b"Gamepad_RightY"
START_MARKER_LENGTH: int = 0x0F

def locate_itembox_start(data: bytearray) -> int:
    start_offset: int =  data[:0x2000].find(START_MARKER)
    start_offset += (START_MARKER_LENGTH + 4) * 2
    return start_offset

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


def update_checksum(data: bytearray, offset: int, key=HMAC_KEY) -> bytes:       #TODO: CHECK AND VERIFY THAT THIS FUNCTON ACTUALLY WRITES THE CHECKSUM CORRECTLY
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
    data:            bytearray
    size:            int
    weapons:         list[Equipment]    = []
    accessories:     list[Equipment]    = []
    path:            str
    key:             bytes
    checksum_offset: int
    start_offset:    int

    def __init__(self, path: str, key=HMAC_KEY):
        self.path = path
        self.key = key
        with open(path, 'rb') as f:
            self.data = bytearray(f.read())
            self.bData = bytes(self.data)
            self.size = len(self.data)

        self.checksum_offset = locate_checksum(self.data, key)
        print(f"[+] Loaded '{path}':\nchecksum offset = {self.checksum_offset:#x}\nFile Size: {self.size}")

        self.start_offset = locate_itembox_start(self.data)
        print(f"[+] Found start offset @: {self.start_offset:#x}")

        print(f"[+] Parsing file: {self.path}...")
        self._start_read()

    def save(self, path=None):
        """Recompute the checksum at the stored offset and write the file."""
        self._create_backup(path or self.path)
        self._commit(path)
        print(f"[+] Saved '{path or self.path}' with updated checksum")


    def _commit(self, path=None) -> None:
        """Recompute the checksum over the current `self.data` and write it
        straight to disk. Only called from save() 
        """
        update_checksum(self.data, self.checksum_offset, self.key)
        out_path = path or self.path
        with open(out_path, 'wb') as f:
            f.write(self.data)

    def _start_read(self):
        current_offset: int = self.start_offset

        while current_offset < self.checksum_offset:
            current_offset = self._readNincrement(current_offset)

    def _readNincrement(self, current_offset: int):  #* Have to do -4 because the Equipment counts the length int in its size function.
        if self.bData[current_offset] == 0x41:
            newObj: Accessory = Accessory(self.bData, current_offset-4)
            if not newObj.valid:
                return current_offset + 1
            
            print(f"[+] Last made equipment at {current_offset}")
            self.accessories.append(newObj)
            return (current_offset - 4) + newObj.size
        
        elif self.bData[current_offset] == 0x57:
            newObj: Weapon = Weapon(self.bData, current_offset-4)
            if not newObj.valid:
                return current_offset + 1
            
            print(f"[+] Last made equipment at {current_offset}")
            self.weapons.append(newObj)
            return (current_offset - 4) + newObj.size
        return current_offset + 1

    def _get_equipment(self, equipment_type: str, equipment_index: int) -> Equipment:
        """Shared lookup used by both modify_chip and modify_chip_by_index."""
        if equipment_type == "Weapon":
            equipment_list = self.weapons
        elif equipment_type == "Accessory":
            equipment_list = self.accessories
        else:
            raise ValueError(f"Unknown equipment type: {equipment_type}")

        if not (0 <= equipment_index < len(equipment_list)):
            raise IndexError(
                f"Equipment index {equipment_index} out of range for "
                f"{equipment_type} (has {len(equipment_list)} items)"
            )

        return equipment_list[equipment_index]

    def modify_chip(self,
        equipment_type: str,
        equipment_index: int,
        chip_name: str,
        value: float
    ) -> None:
        """Find a chip by name on a piece of equipment and write its new
        value into `self.data`
        """

        equipment = self._get_equipment(equipment_type, equipment_index)

        for chip in equipment.chips:

            if chip.chipName == chip_name:
                chip.set_value(self.data, value)
                return

        raise ValueError(
            f"Chip '{chip_name}' not found on {equipment.name}"
        )

    def modify_chip_by_index(
        self,
        equipment_type: str,
        equipment_index: int,
        chip_index: int,
        chip_id: str | None = None,
        value: float | None = None,
    ) -> None:
        """Update a chip on a piece of equipment by its slot index, writing
        straight into `self.data`
        """
        equipment = self._get_equipment(equipment_type, equipment_index)

        if not (0 <= chip_index < len(equipment.chips)):
            raise IndexError(
                f"Chip index {chip_index} out of range for {equipment.name} "
                f"(has {len(equipment.chips)} chips)"
            )

        if chip_id is None and value is None:
            raise ValueError("Must provide chip_id and/or value to update.")

        chip = equipment.chips[chip_index]

        if chip_id is not None:
            chip.set_id(self.data, chip_id, equipment.type)

        if value is not None:
            chip.set_value(self.data, value)

    def _create_backup(self, path=None) -> None:
        real_path: str = path or self.path
        filename: str = real_path.split("\\")[-1]
        bakDir: str = '\\'.join(real_path.split("\\")[:-1]) + "\\" + filename + ".bak"
        with open(bakDir, "wb") as f:
            f.write(self.bData)
            print(f"[+] Writing backup to: {bakDir}")
    