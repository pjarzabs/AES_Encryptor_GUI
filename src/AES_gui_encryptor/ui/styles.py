from __future__ import annotations

import customtkinter as ctk

APP_TITLE = "AES-256 File Encryptor"
APP_SIZE = "980x600"
WINDOW_MIN_WIDTH = 980
WINDOW_MIN_HEIGHT = 600

CARD_RADIUS = 14
INNER_RADIUS = 12

TEXT_MUTED = ("gray35", "gray75")
OUTLINE_TEXT = ("black", "white")
OUTLINE_TEXT_DISABLED = ("gray40", "gray60")


def outline_button(parent, **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        fg_color="transparent",
        border_width=1,
        text_color=OUTLINE_TEXT,
        text_color_disabled=OUTLINE_TEXT_DISABLED,
        **kwargs,
    )


def section_label(parent, text: str, *, row: int, padx=16, pady=6, **kwargs) -> None:
    ctk.CTkLabel(parent, text=text, justify="left", **kwargs).grid(
        row=row,
        column=0,
        padx=padx,
        pady=pady,
        sticky="w",
    )


def card(parent, title: str, row: int, *, bottom_padding: int = 14) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(parent, corner_radius=CARD_RADIUS)
    frame.grid(row=row, column=0, padx=20, pady=(0, bottom_padding), sticky="ew")
    frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        frame,
        text=title,
        font=ctk.CTkFont(size=16, weight="bold"),
    ).grid(row=0, column=0, padx=16, pady=(14, 10), sticky="w")

    return frame