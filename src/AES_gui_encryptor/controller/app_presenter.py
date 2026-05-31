from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from ..core.errors import (
    InvalidFormatError,
    UnsupportedVersionError,
    WrongPasswordOrCorruptedFileError,
)
from ..core.service import decrypt_file, encrypt_file, normalize_extension
from ..ui.background import run_in_background
from ..utils.password import generate_password


class AppPresenter:
    def __init__(self, view) -> None:
        self.view = view

    # Główne rzeczy i operacje:
    def encrypt(self) -> None:
        if self.view.is_busy:
            return

        try:
            input_path, output_path, password = self._validate_common()
            output_ext = normalize_extension(self.view.output_ext.get())
            self.view.output_ext.set(output_ext)
        except Exception as exc:
            messagebox.showerror("Błąd", str(exc))
            return

        def work() -> str:
            return encrypt_file(
                input_path=input_path,
                output_path=output_path,
                password=password,
                as_base64=self.view.as_base64.get(),
                output_ext=output_ext,
            )

        self._start_crypto_task(
            status="Trwa szyfrowanie...",
            work=work,
            success_message="Szyfrowanie zakończone.",
            success_status_prefix="Zaszyfrowano",
        )

    def decrypt(self) -> None:
        if self.view.is_busy:
            return

        try:
            input_path, output_path, password = self._validate_common()
        except Exception as exc:
            messagebox.showerror("Błąd", str(exc))
            return

        def work() -> str:
            return decrypt_file(input_path, output_path, password)

        self._start_crypto_task(
            status="Trwa odszyfrowywanie...",
            work=work,
            success_message="Odszyfrowywanie zakończone.",
            success_status_prefix="Odszyfrowano",
        )

    def _start_crypto_task(
        self,
        *,
        status: str,
        work,
        success_message: str,
        success_status_prefix: str,
    ) -> None:
        def on_success(final_path: str) -> None:
            self.view.output_path.set(final_path)
            self.view.set_busy(
                False,
                f"{success_status_prefix}: {Path(final_path).name}"
            )
            messagebox.showinfo("Sukces!", success_message)

        def on_error(exc: Exception) -> None:
            self.view.set_busy(False, "Wystąpił błąd...")
            self._show_error(exc)

        self.view.set_busy(True, status)
        run_in_background(self.view, work, on_success, on_error)

    # dialogi wyswieltane uzytkownikowui zwiazane z plikami
    def browse_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Wybierz plik wejściowy"
        )

        if not path:
            return

        self.view.input_path.set(path)
        self._suggest_output_path()

    def browse_output(self) -> None:
        ext = normalize_extension(self.view.output_ext.get())
        self.view.output_ext.set(ext)

        path = filedialog.asksaveasfilename(
            title="Wybierz plik wyjściowy",
            defaultextension=ext,
            filetypes=[
                ("Pliki zaszyfrowane", f"*{ext}"),
                ("Wszystkie pliki", "*.*"),
            ],
        )

        if path:
            self.view.output_path.set(path)

    def _suggest_output_path(self) -> None:
        input_path = self.view.input_path.get().strip()

        if not input_path:
            return

        ext = normalize_extension(self.view.output_ext.get())
        self.view.output_ext.set(ext)

        if not self.view.output_path.get().strip():
            self.view.output_path.set(input_path + ext)

    # rzeczy zwiazane z hasłem
    def toggle_password_visibility(self) -> None:
        self.view.password_card.set_password_visible(
            self.view.show_password.get()
        )

    def generate_password(self) -> None:
        self.view.password.set(generate_password(20))
        self.view.status.set(
            "Wygenerowano hasło (zapisz je w bezpiecznym miejscu)."
        )

    def copy_password(self) -> None:
        password = self.view.password.get()

        if not password:
            messagebox.showwarning(
                "Ostrzeżenie",
                "Hasło jest puste."
            )
            return

        self.view.clipboard_clear()
        self.view.clipboard_append(password)

        self.view.status.set(
            "Skopiowano hasło do schowka."
        )

    # Pomniejsze czynności interfejsu graficznego
    def swap_paths(self) -> None:
        input_path = self.view.input_path.get()
        output_path = self.view.output_path.get()

        self.view.input_path.set(output_path)
        self.view.output_path.set(input_path)

        self.view.status.set(
            "Zamieniono ścieżki wejściową i wyjściową."
        )

    def change_appearance(self, mode: str) -> None:
        mapping = {
            "Ciemny": "Dark",
            "Jasny": "Light",
            "Systemowy": "System",
        }

        ctk.set_appearance_mode(mapping[mode])

    # Walidacja danych / bledy
    def _validate_common(self) -> tuple[str, str, str]:
        input_path = self.view.input_path.get().strip()
        output_path = self.view.output_path.get().strip()
        password = self.view.password.get()

        if not input_path:
            raise ValueError(
                "Ścieżka pliku wejściowego jest pusta."
            )

        if not Path(input_path).exists():
            raise ValueError(
                "Plik wejściowy nie istnieje."
            )

        if not output_path:
            raise ValueError(
                "Ścieżka pliku wyjściowego jest pusta."
            )

        if not password:
            raise ValueError(
                "Hasło jest puste."
            )

        return input_path, output_path, password

    def _show_error(self, exc: Exception) -> None:
        if isinstance(exc, WrongPasswordOrCorruptedFileError):
            messagebox.showerror(
                "Błąd",
                "Nieprawidłowe hasło lub plik został uszkodzony albo zmodyfikowany."
            )

        elif isinstance(
            exc,
            (
                InvalidFormatError,
                UnsupportedVersionError,
            ),
        ):
            messagebox.showerror(
                "Błąd",
                f"Nieprawidłowy lub nieobsługiwany format pliku: {exc}"
            )

        else:
            messagebox.showerror(
                "Błąd",
                str(exc)
            )
