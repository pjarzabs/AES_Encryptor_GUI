class CryptoAppError(Exception):
    """Base app error."""


class InvalidFormatError(CryptoAppError):
    """File does not match expected presenter format."""


class UnsupportedVersionError(CryptoAppError):
    """Presenter version not supported."""


class WrongPasswordOrCorruptedFileError(CryptoAppError):
    """Password is wrong OR file was modified/corrupted."""