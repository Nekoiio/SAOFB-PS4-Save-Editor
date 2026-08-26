from dataclasses import dataclass
import struct
import json


with open("Data/accessories.json", "r") as f: K_ACCESSORIES: dict = json.load(f)
with open("Data/weapons.json", "r") as f: K_WEAPONS: dict = json.load(f)
with open("Data/chips.json", "r") as f: K_CHIPS: dict = json.load(f)

INT_CHIPS: list[str] = ["VIT", "AGI", "DEX", "LUC", "STR", "INT", "Medals Acquired"]

WEAPON_CHIPC_OFF:    int = 0x23
WEAPON_CUSC_OFF:     int = 0x1c

ACCESSORY_CHIPC_OFF: int = 0x2B
ACCESSORY_CUSC_OFF:  int = 0x00



class Chip:
    chipID:     str
    chipName:   str
    chipVal:    float
    offset:   int
    valid:    bool      = True


    def __init__(self, data: bytes, offset: int, AorW: str):   
        if data[0] == 0 or data[0] > 0x41:
            self.valid = False 
            return
        
        self.chipID        = f"{data[0]:02X}"                    #* First byte is the chipID interpreted as Hex
        self.offset        = offset
        try:
            self.chipName      = K_CHIPS[AorW][self.chipID]
        except KeyError:
            print(f"[X] Couldn't resolve chip: {self.chipID}")
            self.chipName = "COULD NOT RESOLVE"
        self.chipVal       = struct.unpack("<f", data[1:5])[0]   #* the last 4 are either an int or flot depending on the chi type


    def set_value(self, data: bytearray, value: float) -> None:

        self.chipVal = value

        struct.pack_into(
            "<f",
            data,
            self.offset + 1,
            value
        )

    def set_id(self, data: bytearray, chip_id: str, AorW: str) -> None:
        """Overwrite this chip's ID byte in the save data and re-resolve
        chipName from the catalog, the same way __init__ does.

        `chip_id` is the same 2-char hex string used as a key in
        chips.json (e.g. "3F"), matching what's stored in `self.chipID`.
        `AorW` is "Weapon" or "Accessory" (i.e. `equipment.type`), used to
        pick the right sub-dict out of K_CHIPS.
        """
        new_id: int = int(chip_id, 16)

        if new_id == 0 or new_id > 0x41:
            raise ValueError(f"Chip id {chip_id!r} is out of the valid range.")

        data[self.offset] = new_id
        self.chipID = f"{new_id:02X}"

        try:
            self.chipName = K_CHIPS[AorW][self.chipID]
        except KeyError:
            print(f"[X] Couldn't resolve chip: {self.chipID}")
            self.chipName = "COULD NOT RESOLVE"

    def __str__(self) -> str:
        return f"{self.chipName}: {(self.chipVal * 100) if self.chipVal < 1 else self.chipVal}"


    
                            
class Equipment:            # Combines Accessory and Weapn, differentiation will be done separately
    name:       str
    name_len:   int
    type:       str
    chipCount:  int
    chips:      list[Chip]
    valid:      bool      = True         #used to check integrity when returning on error
    size:       int

    def __init__(self, data: bytes, offset: int):

        self.chips      = []

        #!  ------------    Handling Name and Type   ---------------
        self.name_len:       int = int.from_bytes(data[offset:offset+4], byteorder="little")
        offset += 4
        try:
            self.name  = (data[offset:offset + self.name_len - 1]).decode("ascii")
        except UnicodeDecodeError:
            print(f"Unicode error reading at offset {offset}")
            self.valid = False
            return

        offset = self._set_type(offset)

        if offset < 0:
            self.valid = False
            return
        

        #! ------------    Handling Chips   ---------------
        self.chipCount: int = int.from_bytes(data[offset:offset+4], byteorder="little")
        offset += 4
        chip_block_len: int = self.chipCount * 5
        chip_block: bytes = data[offset:offset + chip_block_len]
        offset += 4

        offset = self._read_chips(chip_block,chip_block_len, offset)
        if offset < 0:
            self.valid = False
            return
        
        self.size = self._get_size()
        #! -------------    Handling Customs   ---------------


    def _get_size(self) -> int:
        return (len(self.chips) * 5) + 71 + self.name_len + 4 

    def _set_type(self, offset: int) -> int:
        pass

    def _read_chips(self, cb: bytes, cbl: int, offset: int) -> None:

        for i in range(0, cbl, 5):
            chip: Chip = Chip(cb[i:i+5], offset+i, self.type)
            if not chip.valid: return -1
            self.chips.append(chip)

        return offset+cbl

    def _read_customs(self, data: bytes, offset: int): 
        ...

    def __str__(self) -> str:
        chips = "\n".join(str(chip) for chip in self.chips)

        return (
            f"{self.name}'s "
            f"Chips:\n{chips}"
        )

    
class Accessory(Equipment):
    
    def _set_type(self, offset) -> int:
        try:
            self.type = "Accessory"
            offset += self.name_len + ACCESSORY_CHIPC_OFF
            self.name = K_ACCESSORIES[self.name]
        except KeyError:
            self.valid = False
            return -1
        
        return offset
    
    def __str__(self) -> str:
        chips = "\n".join(str(chip) for chip in self.chips)

        return (
            f"{self.name}'s "
            f"Chips:\n{chips}"
        )


class Weapon(Equipment):

    def _set_type(self, offset):
        try:
            self.type = "Weapon"
            offset += self.name_len + WEAPON_CHIPC_OFF
            self.name = K_WEAPONS[self.name]
        except KeyError:
            self.valid = False
            return -1
        
        return offset
    
    def __str__(self) -> str:
        chips = "\n".join(str(chip) for chip in self.chips)

        return (
            f"{self.name}'s "
            f"Chips:\n{chips}"
        )





"""
 #* Last 4 bytes of accessory/Weapon are always How many customization fields are appended
 #* Customization format: 5 byte ID and 2 chunks of (x(4 bytes))(Name with length x)
 
 all follow same pattern:
 Custom_Chunk_Length = 5 + 4 + customization_name_len + 4 + customization_2_name_len <-( This is repeated * the last 4 bytes in the structure it was found)

 Weapon:    4 + name_len + 71 + (chips * 5) + (Custom_Chunk_Length)
 Accessory: 4 + name_len + 71 + (chips * 5) + (Custom_Chunk_Length)
 Costume:   4 + name_len + 71 + (Custom_Chunk_Length)
 Material:  4 + name_len + 71
 Bullet:    4 + name_len + 71


Accessory With Fabric Color Attached:
0D 00 00 00 41 43 43 30 32 38 5F 30 30
33 5F 43 00 01 00 00 00 0E 00 00 00 03
2F 00 00 00 0A 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 04 00 00 00 04 00 00 00 05
00 00 00 42 06 00 00 00 42 30 00 00 80
3E 27 0A D7 A3 3E 

(01 00 00 00)
09 00 00 00 00 
11 00 00 00 46 61 62 72 69 63 5F 43 6F 6C 6F 72 5F 30 35 30 00 
05 00 00 00 4E 6F 6E 65 00 

Accessory with Metal Color:
0D 00 00 00 41 43 43 30 33 31 5F 30 30
37 5F 43 00 01 00 00 00 0E 00 00 00 03
30 00 00 00 0A 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 04 00 00 00
04 00 00 00 01 00 00 20 42 05 00 00 08 42 06 00 00 08 42 2F CD CC CC 3D 

(01 00 00 00) 
09 00 00 00 00
10 00 00 00 4D 65 74 61 6C 5F 43 6F 6C 6F 72 5F 30 35 30 00 
05 00 00 00 4E 6F 6E 65 00

Accessory with no customization:
0D 00 00 00 41 43 43 30 32 37 5F 30 30
38 5F 43 00 01 00 00 00 0E 00 00 00 03
31 00 00 00 0A 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 04 00 00 00 
04 00 00 00 01 00 00 20 42 05 00 00 08 42 06 00 00 08 42 2F CD CC CC 3D 

(00 00 00 00)

Accessory with Both available but none set:
0D 00 00 00 41 43 43 30 30 31 5F 30 30
35 5F 43 00 01 00 00 00 0E 00 00 00 03
33 00 00 00 0A 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 04 00 00 00
04 00 00 00 30 AE 47 61 3E 28 CC CC BC 3F 04 00 00 F0 41 05 00 00 F0 41 

(02 00 00 00)
09 00 00 00 00
10 00 00 00 4D 65 74 61 6C 5F 43 6F 6C 6F 72 5F 30 35 30 00 05 00 00 00 4E 6F 6E 65 00

09 01 00 00 00
11 00 00 00 46 61 62 72 69 63 5F 43 6F 6C 6F 72 5F 30 35 30 00 05 00 00 00 4E 6F 6E 65 00
"""
