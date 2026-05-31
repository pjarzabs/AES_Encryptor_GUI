from __future__ import annotations

import customtkinter as ctk

from .styles import INNER_RADIUS, card, outline_button


class PasswordPanel:
    def __init__(
        self,
        parent,
        *,
        row: int,
        password_variable: ctk.StringVar,
        show_password_variable: ctk.BooleanVar,
        on_toggle_password,
        on_generate_password,
        on_copy_password,
    ) -> None:
        self.parent = parent
        self.row = row
        self.password_variable = password_variable
        self.show_password_variable = show_password_variable
        self.on_toggle_password = on_toggle_password
        self.on_generate_password = on_generate_password
        self.on_copy_password = on_copy_password

        self._build()

    def _build(self) -> None:
        self.frame = card(self.parent, "Hasło", self.row)

        row_frame = ctk.CTkFrame(self.frame, corner_radius=INNER_RADIUS)
        row_frame.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")
        row_frame.grid_columnconfigure(0, weight=1)

        self.password_entry = ctk.CTkEntry(
            row_frame,
            textvariable=self.password_variable,
            placeholder_text="Podaj hasło...",
            show="•",
        )
        self.password_entry.grid(row=0, column=0, padx=12, pady=12, sticky="ew")

        self.chk_show = ctk.CTkCheckBox(
            row_frame,
            text="Wyświetl",
            variable=self.show_password_variable,
            command=self.on_toggle_password,
        )
        self.chk_show.grid(row=0, column=1, padx=(0, 8), pady=12)

        self.btn_generate = ctk.CTkButton(
            row_frame,
            text="Wygeneruj losowe",
            width=110,
            command=self.on_generate_password,
        )
        self.btn_generate.grid(row=0, column=2, padx=(0, 8), pady=12)

        self.btn_copy = outline_button(
            row_frame,
            text="Kopiuj",
            width=90,
            command=self.on_copy_password,
        )
        self.btn_copy.grid(row=0, column=3, padx=(0, 12), pady=12)

    def set_password_visible(self, visible: bool) -> None:
        self.password_entry.configure(show="" if visible else "•")

    def disabled_widgets(self) -> list:
        return [
            self.password_entry,
            self.chk_show,
            self.btn_generate,
            self.btn_copy,
        ]