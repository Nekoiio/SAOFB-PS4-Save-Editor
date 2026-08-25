from Crypt.SAOC import SAOC 

SAOC.SAVE_LOC_FILE = "SAOFBS/"

def main():
    SAOC.decryptSave(SAOC, "SaveData.sav", "Decrypted.sav")


if __name__ == "__main__":
    main()