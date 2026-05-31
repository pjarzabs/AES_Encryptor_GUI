from __future__ import annotations

import customtkinter as ctk

from .styles import INNER_RADIUS, TEXT_MUTED, card


class OutputCard:
    def __init__(
        self,
        parent,
        *,
        row: int,
        extension_variable: ctk.StringVar,
        base64_variable: ctk.BooleanVar,
    ) -> None:
        self.parent = parent
        self.row = row
        self.extension_variable = extension_variable
        self.base64_variable = base64_variable

        self._build()

    def _build(self) -> None:
        self.frame = card(self.parent, "Output Settings", self.row)

        row_frame = ctk.CTkFrame(self.frame, corner_radius=INNER_RADIUS)
        row_frame.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
        row_frame.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(row_frame, corner_radius=INNER_RADIUS)
        left.grid(row=0, column=0, padx=12, pady=12, sticky="ew")

        ctk.CTkLabel(left, text="Extension:", text_color=TEXT_MUTED).grid(
            row=0,
            column=0,
            padx=(12, 8),
            pady=12,
            sticky="w",
        )

        self.extension_entry = ctk.CTkEntry(
            left,
            textvariable=self.extension_variable,
            width=140,
        )
        self.extension_entry.grid(row=0, column=1, padx=(0, 12), pady=12, sticky="w")

        right = ctk.CTkFrame(row_frame, corner_radius=INNER_RADIUS)
        right.grid(row=0, column=1, padx=12, pady=12, sticky="e")

        self.base64_switch = ctk.CTkSwitch(
            right,
            text="Save as Base64 text",
            variable=self.base64_variable,
        )
        self.base64_switch.grid(row=0, column=0, padx=14, pady=12)

    def disabled_widgets(self) -> list:
        return [
            self.extension_entry,
            self.base64_switch,
        ]