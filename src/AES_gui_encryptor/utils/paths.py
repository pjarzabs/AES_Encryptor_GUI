import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Dostaje PEŁŃĄ sciężke do zasobów.
    Działa w  PyInstallerze, jak chcemy w pliku .exe calosc.
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # type: ignore
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)