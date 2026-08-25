from Crypto.Cipher import AES


class SAOC:
    _key: bytearray = bytes.fromhex(
        "41 33 66 7A 67 39 38 75 30 63 50 4F 34 64 67 72"
        "6E 6A 45 30 6F 37 38 69 65 34 33 67 37 35 77 32"
        "67 72 65 64 43 56 6E 47 67 72 45 52 73 69 67 36"
        "35 6A 68 37 6C 6F 67 65 74 6F 33 73 47 52 6A 6F"
    )
    _AESKEY = _key[:32]
    _CRYPT = AES.new(_AESKEY, AES.MODE_ECB)
    SAVE_LOC_FILE: str =""

    def decryptSave(self, inputFile: str, outputFile: str) -> bool:
        with open(self.SAVE_LOC_FILE + inputFile, 'rb') as f:
            data: bytearray = f.read()

        out: bytearray = bytearray()

        for i in range(0, len(data), 16):
            block: bytearray = data[i:i+16]
            if (len(block) < 16):
                out += block
                break

            out += self._CRYPT.decrypt(block)

        with open(self.SAVE_LOC_FILE + outputFile, "wb") as f2:
            f2.write(out)

        return True

    def encryptSave(self, inputFile: str, outputFile: str) -> bool:
        with open(self.SAVE_LOC_FILE + inputFile, "rb") as f:
            data: bytearray = f.read()

        out: bytearray = bytearray()
        for j in range(0, len(data), 16):
            block: bytearray = block[j:j+16]
            if (len(block) < 16):
                out += block
                break
            out += self._CRYPT.encrypt(block)

        with open(self.SAVE_LOC_FILE + outputFile, "wb")as f2:
            f2.write(out)

        return True