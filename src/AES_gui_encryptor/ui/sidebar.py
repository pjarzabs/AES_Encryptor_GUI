from __future__ import annotations

import customtkinter as ctk

from .styles import TEXT_MUTED, outline_button, section_label


class Sidebar(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        *,
        status_variable: ctk.StringVar,
        on_encrypt,
        on_decrypt,
        on_swap,
        on_appearance_change,
    ) -> None:
        super().__init__(parent, corner_radius=16)

        self.status_variable = status_variable
        self.on_encrypt = on_encrypt
        self.on_decrypt = on_decrypt
        self.on_swap = on_swap
        self.on_appearance_change = on_appearance_change

        self._build()

    def _build(self) -> None:
        self.grid_rowconfigure(200, weight=1)

        section_label(
            self,
            "AES-256\nSzyfrowanie plików",
            row=0,
            font=ctk.CTkFont(size=22, weight="bold"),
            pady=(18, 6),
        )

        section_label(
            self,
            "PBKDF2 + AES-GCM\nBIN / Base64\nMetadane w pliku",
            row=1,
            text_color=TEXT_MUTED,
            pady=(0, 12),
        )

        section_label(self, "Wygląd", row=2, text_color=TEXT_MUTED, pady=(8, 4))

        self.appearance = ctk.CTkOptionMenu(
            self,
            values=["Ciemny", "Jasny", "Systemowy"],
            command=self.on_appearance_change,
            width=160,
        )
        self.appearance.set("Ciemny")
        self.appearance.grid(row=3, column=0, padx=16, pady=(0, 16), sticky="w")

        self.btn_encrypt = ctk.CTkButton(
            self,
            text="Szyfruj",
            height=42,
            command=self.on_encrypt,
        )
        self.btn_encrypt.grid(row=4, column=0, padx=16, pady=(6, 10), sticky="ew")

        self.btn_decrypt = outline_button(
            self,
            text="Odszyfruj",
            height=42,
            command=self.on_decrypt,
        )
        self.btn_decrypt.grid(row=5, column=0, padx=16, pady=(0, 10), sticky="ew")

        self.btn_swap = outline_button(
            self,
            text="Zamień wej./wyj.",
            height=38,
            command=self.on_swap,
        )
        self.btn_swap.grid(row=6, column=0, padx=16, pady=(0, 14), sticky="ew")

        self.progress = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress.grid(row=7, column=0, padx=16, pady=(6, 10), sticky="ew")
        self.progress.grid_remove()

        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_variable,
            wraplength=220,
            justify="left",
        )
        self.status_label.grid(row=201, column=0, padx=16, pady=(10, 18), sticky="sw")

    def show_progress(self) -> None:
        self.progress.grid()
        self.progress.start()

    def hide_progress(self) -> None:
        self.progress.stop()
        self.progress.grid_remove()

    def disabled_widgets(self) -> list:
        # celowo nie wylaczono decrypt i swapa, mozna w nie kliklac.
        # ale jesli aplikacja jest w stanie "running" to prezenter igonruje wszysktie kliknięcia.
        return [
            self.btn_encrypt,
            self.appearance,
        ]