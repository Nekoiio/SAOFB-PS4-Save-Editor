import hashlib
import hmac
import tkinter as tk
from tkinter import filedialog

HMAC_KEY = b"1FB00CC8D8D94CD0A94C847C2F04A921"

# Absolute offset of the checksum's length-prefix field (the "14 00 00 00" marker),
# i.e. the byte position where the HMAC-covered data ends.
# Confirmed via HMAC(key, data[:ABSOLUTE_OFFSET]) matching the stored digest.
ABSOLUTE_OFFSET = 0x1B35A3
#0x1B93DF



def patch_save(data, offset=ABSOLUTE_OFFSET):
    """Recompute and rewrite the checksum that lives right after `offset`.

    Assumes the on-disk layout at `offset` is:
        [int32 length = 20][20-byte HMAC-SHA1 digest]
    and that the digest covers data[:offset].
    """
    if offset + 24 > len(data):
        print(f"[!] Offset {offset:#x} + 24 exceeds file size ({len(data)} bytes); aborting.")
        return data

    cleaned_data = data[:offset]
    computed = hmac.new(HMAC_KEY, cleaned_data, hashlib.sha1).digest()

    stored = bytes(data[offset + 4:offset + 24])
    print(f"Offset:   {offset:#x}")
    print(f"Stored:   {stored.hex().upper()}")
    print(f"Computed: {computed.hex().upper()}")
    print(f"Already valid: {stored == computed}")

    final_data = cleaned_data + bytearray.fromhex('14000000') + bytearray(computed)

    # preserve any trailing bytes after the 24-byte checksum block, if the
    # file is longer than offset+24 (e.g. other checksums/data further on)
    remainder = data[offset + 24:]
    if remainder:
        final_data += remainder

    return final_data


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Save Fixer")

    def run_fix():
        path = filedialog.askopenfilename(title="Select save file")
        if not path:
            return
        with open(path, 'rb') as f:
            data = bytearray(f.read())

        fixed = patch_save(data)

        with open(path, 'wb') as f:
            f.write(fixed)

        print("[+] Save fixed successfully")

    fix_button = tk.Button(root, text="Fix Save", command=run_fix)
    fix_button.pack(padx=20, pady=20)
    root.mainloop()