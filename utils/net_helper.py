# IP file - connections, requests, responses, etc.

from __future__ import annotations

import os
from datetime import datetime as date
from typing import Tuple

import requests


def attachment_extract(
    url: str,
    name: str,
    ext: str,
    *,
    timeout: Tuple[float, float] = (5.0, 60.0),
    max_size_bytes: int = 50 * 1024 * 1024,
) -> str:
    """Download an attachment by URL to data/<ext>/<name>/... and return the local path.

    Important: this function MUST NOT hang forever. We always use timeouts and validate response.
    """

    try:
        response = requests.get(url, stream=True, timeout=timeout)
    except requests.RequestException as e:
        raise RuntimeError(f"Не удалось скачать файл (ошибка сети): {e}")

    # VK may return 302/403/404 etc. Treat as error and tell user.
    if response.status_code != 200:
        raise RuntimeError(
            f"Не удалось скачать файл: HTTP {response.status_code}. "
            "Попробуйте отправить документ заново (не пересылкой)."
        )

    base_dir = os.path.join('data', ext, name)
    os.makedirs(base_dir, exist_ok=True)

    filename = ("_".join(str(date.now())[:-7].replace(":", "-").split())) + "." + ext
    path = os.path.join(base_dir, filename)

    total = 0
    try:
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=256 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_size_bytes:
                    raise RuntimeError(
                        f"Файл слишком большой (>{max_size_bytes // (1024 * 1024)}MB). "
                        "Сожмите документ или отправьте меньший файл."
                    )
                f.write(chunk)
    finally:
        try:
            response.close()
        except Exception:
            pass

    if total == 0:
        raise RuntimeError("Скачанный файл пустой. Попробуйте отправить документ заново.")

    return path
