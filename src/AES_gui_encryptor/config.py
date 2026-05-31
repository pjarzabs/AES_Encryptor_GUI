FORMAT_MAGIC = b"AGF1"  # AES plik GUI, w wersji 1
FORMAT_VERSION = 1

# KDF / parametry kryptograficzne
PBKDF2_ITERATIONS = 300_000
SALT_LEN = 16
NONCE_LEN = 12  # tyle najlepiej podobno dla GCM
KEY_LEN = 32    # tak jest w szyfrowaniu AES-256, dlugość klucza 32

# IDs (a tak na przyszłość, może się przyda xd)
KDF_ID_PBKDF2_SHA256 = 1
CIPHER_ID_AES_256_GCM = 1