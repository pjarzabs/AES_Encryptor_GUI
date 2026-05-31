from __future__ import annotations

import customtkinter as ctk

from .styles import TEXT_MUTED, card


class NotesPanel:
    def __init__(self, parent, *, row: int) -> None:
        self.parent = parent
        self.row = row

        self._build()

    def _build(self) -> None:
        self.frame = card(self.parent, "Warto wiedzieć:", self.row, bottom_padding=18)

        notes = (
            "• AES-GCM sprawdza integralność danych.\n"
            "• Sól, nonce i parametry PBKDF2 są zapisywane w pliku.\n"
            "• Program wczytuje cały plik do pamięci.\n"
            "• Po zaszyfrowaniu, jeśli chcesz szybko odszyfrować ten sam plik, kliknij 'Zamień wej./wyj.', a następnie 'Odszyfruj'."
        )

        ctk.CTkLabel(
            self.frame,
            text=notes,
            justify="left",
            text_color=TEXT_MUTED,
        ).grid(
            row=1,
            column=0,
            padx=16,
            pady=(0, 14),
            sticky="w",
        )