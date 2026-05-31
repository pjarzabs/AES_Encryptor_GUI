from __future__ import annotations

import threading


def run_in_background(root, work, on_success, on_error) -> None:
    def runner() -> None:
        try:
            result = work()

            root.after(
                0,
                lambda result=result: on_success(result)
            )

        except Exception as exc:
            root.after(
                0,
                lambda exc=exc: on_error(exc)
            )

    threading.Thread(
        target=runner,
        daemon=True,
    ).start()