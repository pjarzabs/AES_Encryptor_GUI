from __future__ import annotations

import platform
from pathlib import Path
import tkinter as tk

import customtkinter as ctk

from ..presenter.app_presenter import AppPresenter
from ..utils.paths import resource_path

from .file_panel import FilePanel
from .notes_panel import NotesPanel
from .output_panel import OutputPanel
from .password_panel import PasswordPanel
from .sidebar import Sidebar
from .styles import (
    APP_SIZE,
    APP_TITLE,
    TEXT_MUTED,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
    section_label,
)


def _enable_windows_dpi_awareness() -> None:
    if platform.system().lower() != "windows":
        return

    try:
        import ctypes  # type: ignore

        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            import ctypes  # type: ignore

            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


class App(ctk.CTk):
    def __init__(self) -> None:
        _enable_windows_dpi_awareness()

        super().__init__()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.geometry(APP_SIZE)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._init_state()
        self.presenter = AppPresenter(self)

        self._set_app_icon()
        self._build_ui()

    # stan
    def _init_state(self) -> None:
        self.input_path = ctk.StringVar(value="")
        self.output_path = ctk.StringVar(value="")
        self.password = ctk.StringVar(value="")
        self.output_ext = ctk.StringVar(value=".aes")
        self.as_base64 = ctk.BooleanVar(value=False)
        self.status = ctk.StringVar(value="Aplikacja gotowa.")
        self.show_password = ctk.BooleanVar(value=False)

        self._busy = False

    @property
    def is_busy(self) -> bool:
        return self._busy

    # fajowa ikonka
    def _set_app_icon(self) -> None:
        ico_path = resource_path("assets/app.ico")
        png_path = resource_path("assets/app.png")

        try:
            if Path(ico_path).exists() and platform.system().lower() == "windows":
                self.iconbitmap(ico_path)
                return
        except Exception:
            pass

        try:
            if Path(png_path).exists():
                photo = tk.PhotoImage(file=png_path)
                self.iconphoto(True, photo)
                self._icon_photo = photo
        except Exception:
            pass

    # rozkład graficzny elementów w interfejsie
    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()

    def _build_sidebar(self) -> None:
        self.sidebar = Sidebar(
            self,
            status_variable=self.status,
            on_encrypt=self.presenter.encrypt,
            on_decrypt=self.presenter.decrypt,
            on_swap=self.presenter.swap_paths,
            on_appearance_change=self.presenter.change_appearance,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=16, pady=16)

    def _build_content(self) -> None:
        self.content = ctk.CTkFrame(self, corner_radius=16)
        self.content.grid(row=0, column=1, sticky="nsew", padx=(0, 16), pady=16)
        self.content.grid_columnconfigure(0, weight=1)

        section_label(
            self.content,
            "Szyfrowanie i odszyfrowywanie plików",
            row=0,
            padx=20,
            pady=(18, 6),
            font=ctk.CTkFont(size=20, weight="bold"),
        )

        section_label(
            self.content,
            "AES-256-GCM + PBKDF2 (sól i iteracje). \nOdszyfrowywanie automatycznie wykrywa format: binarny lub Base64.",
            row=1,
            padx=20,
            pady=(0, 14),
            text_color=TEXT_MUTED,
        )

        self.file_card = FilePanel(
            self.content,
            row=2,
            input_variable=self.input_path,
            output_variable=self.output_path,
            on_browse_input=self.presenter.browse_input,
            on_browse_output=self.presenter.browse_output,
        )

        self.password_card = PasswordPanel(
            self.content,
            row=3,
            password_variable=self.password,
            show_password_variable=self.show_password,
            on_toggle_password=self.presenter.toggle_password_visibility,
            on_generate_password=self.presenter.generate_password,
            on_copy_password=self.presenter.copy_password,
        )

        self.output_card = OutputPanel(
            self.content,
            row=4,
            extension_variable=self.output_ext,
            base64_variable=self.as_base64,
        )

        self.notes_card = NotesPanel(self.content, row=5)

    # Stan zajęty (busy state)
    def set_busy(self, busy: bool, status: str | None = None) -> None:
        self._busy = busy

        if status is not None:
            self.status.set(status)

        state = "disabled" if busy else "normal"

        for widget in self._widgets_disabled_during_work():
            try:
                widget.configure(state=state)
            except Exception:
                pass

        if busy:
            self.sidebar.show_progress()
        else:
            self.sidebar.hide_progress()

        self.update_idletasks()

    def _widgets_disabled_during_work(self) -> list:
        return (
            self.sidebar.disabled_widgets()
            + self.file_card.disabled_widgets()
            + self.password_card.disabled_widgets()
            + self.output_card.disabled_widgets()
        )


def run_app() -> None:
    app = App()
    app.mainloop()