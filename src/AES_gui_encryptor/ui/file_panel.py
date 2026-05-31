from __future__ import annotations

import customtkinter as ctk

from .styles import INNER_RADIUS, card


class FileCard:
    def __init__(
        self,
        parent,
        *,
        row: int,
        input_variable: ctk.StringVar,
        output_variable: ctk.StringVar,
        on_browse_input,
        on_browse_output,
    ) -> None:
        self.parent = parent
        self.row = row
        self.input_variable = input_variable
        self.output_variable = output_variable
        self.on_browse_input = on_browse_input
        self.on_browse_output = on_browse_output

        self._build()

    def _build(self) -> None:
        self.frame = card(self.parent, "Files", self.row)

        self.input_entry, self.btn_browse_input = self._path_row(
            row=1,
            variable=self.input_variable,
            placeholder="Input file path...",
            button_text="Browse",
            command=self.on_browse_input,
        )

        self.output_entry, self.btn_browse_output = self._path_row(
            row=2,
            variable=self.output_variable,
            placeholder="Output file path...",
            button_text="Save As",
            command=self.on_browse_output,
            bottom_padding=16,
        )

    def _path_row(
        self,
        *,
        row: int,
        variable: ctk.StringVar,
        placeholder: str,
        button_text: str,
        command,
        bottom_padding: int = 10,
    ) -> tuple[ctk.CTkEntry, ctk.CTkButton]:
        row_frame = ctk.CTkFrame(self.frame, corner_radius=INNER_RADIUS)
        row_frame.grid(row=row, column=0, padx=16, pady=(0, bottom_padding), sticky="ew")
        row_frame.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            row_frame,
            textvariable=variable,
            placeholder_text=placeholder,
        )
        entry.grid(row=0, column=0, padx=12, pady=12, sticky="ew")

        button = ctk.CTkButton(
            row_frame,
            text=button_text,
            width=120,
            command=command,
        )
        button.grid(row=0, column=1, padx=(0, 12), pady=12)

        return entry, button

    def disabled_widgets(self) -> list:
        return [
            self.input_entry,
            self.output_entry,
            self.btn_browse_input,
            self.btn_browse_output,
        ]