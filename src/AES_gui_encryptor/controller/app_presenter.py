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


class AppController:
    """
    Controller layer.

    This class contains application behavior:
    - validation,
    - encryption/decryption actions,
    - file dialogs,
    - password actions,
    - error handling.

    The App class stays mostly responsible for building and updating the UI.
    """

    def __init__(self, view) -> None:
        self.view = view

    # ---------- Main actions ----------
    def encrypt(self) -> None:
        if self.view.is_busy:
            return

        try:
            input_path, output_path, password = self._validate_common()
            output_ext = normalize_extension(self.view.output_ext.get())
            self.view.output_ext.set(output_ext)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
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
            status="Encrypting...",
            work=work,
            success_message="Encryption finished.",
            success_status_prefix="Done. Encrypted",
        )

    def decrypt(self) -> None:
        if self.view.is_busy:
            return

        try:
            input_path, output_path, password = self._validate_common()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        def work() -> str:
            return decrypt_file(input_path, output_path, password)

        self._start_crypto_task(
            status="Decrypting...",
            work=work,
            success_message="Decryption finished.",
            success_status_prefix="Done. Decrypted",
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
            self.view.set_busy(False, f"{success_status_prefix} -> {Path(final_path).name}")
            messagebox.showinfo("Success", success_message)

        def on_error(exc: Exception) -> None:
            self.view.set_busy(False, "Error.")
            self._show_error(exc)

        self.view.set_busy(True, status)
        run_in_background(self.view, work, on_success, on_error)

    # ---------- File dialogs ----------
    def browse_input(self) -> None:
        path = filedialog.askopenfilename(title="Select input file")

        if not path:
            return

        self.view.input_path.set(path)
        self._suggest_output_path()

    def browse_output(self) -> None:
        ext = normalize_extension(self.view.output_ext.get())
        self.view.output_ext.set(ext)

        path = filedialog.asksaveasfilename(
            title="Select output file",
            defaultextension=ext,
            filetypes=[("Encrypted files", f"*{ext}"), ("All files", "*.*")],
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

    # ---------- Password actions ----------
    def toggle_password_visibility(self) -> None:
        self.view.password_card.set_password_visible(self.view.show_password.get())

    def generate_password(self) -> None:
        self.view.password.set(generate_password(20))
        self.view.status.set("Generated password (save it!).")

    def copy_password(self) -> None:
        password = self.view.password.get()

        if not password:
            messagebox.showwarning("Warning", "Password is empty.")
            return

        self.view.clipboard_clear()
        self.view.clipboard_append(password)
        self.view.status.set("Password copied to clipboard.")

    # ---------- Small UI actions ----------
    def swap_paths(self) -> None:
        input_path = self.view.input_path.get()
        output_path = self.view.output_path.get()

        self.view.input_path.set(output_path)
        self.view.output_path.set(input_path)
        self.view.status.set("Swapped input/output paths.")

    def change_appearance(self, mode: str) -> None:
        ctk.set_appearance_mode(mode)

    # ---------- Validation / errors ----------
    def _validate_common(self) -> tuple[str, str, str]:
        input_path = self.view.input_path.get().strip()
        output_path = self.view.output_path.get().strip()
        password = self.view.password.get()

        if not input_path:
            raise ValueError("Input path is empty.")

        if not Path(input_path).exists():
            raise ValueError("Input file does not exist.")

        if not output_path:
            raise ValueError("Output path is empty.")

        if not password:
            raise ValueError("Password is empty.")

        return input_path, output_path, password

    def _show_error(self, exc: Exception) -> None:
        if isinstance(exc, WrongPasswordOrCorruptedFileError):
            messagebox.showerror(
                "Error",
                "Wrong password OR file corrupted/modified (GCM tag mismatch).",
            )
        elif isinstance(exc, (InvalidFormatError, UnsupportedVersionError)):
            messagebox.showerror("Error", f"Invalid/unsupported file format: {exc}")
        else:
            messagebox.showerror("Error", str(exc))