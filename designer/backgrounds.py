from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlparse


def _raw_background_value(value: object) -> str:
    return str(value or "").strip()


def _local_background_path(raw: str) -> Path:
    if raw.lower().startswith("file://"):
        parsed = urlparse(raw)
        path_text = unquote(parsed.path)
        if len(path_text) >= 3 and path_text[0] == "/" and path_text[2] == ":":
            path_text = path_text[1:]
        return Path(path_text).expanduser()
    return Path(raw).expanduser()


def is_local_background_image(value: object) -> bool:
    raw = _raw_background_value(value)
    if not raw:
        return False
    if raw.startswith("data:"):
        return False
    lower = raw.lower()
    return not lower.startswith(("http://", "https://"))


def resolve_background_image_src(value: object) -> str:
    raw = _raw_background_value(value)
    if not raw:
        return ""
    if raw.startswith("data:"):
        return raw

    lower = raw.lower()
    if lower.startswith(("http://", "https://")):
        return raw

    try:
        path = _local_background_path(raw)
        if path.is_file():
            mime_type, _ = mimetypes.guess_type(path.name)
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime_type or 'image/png'};base64,{encoded}"
    except OSError:
        pass

    return raw.replace("\\", "/")


def css_url_value(value: object) -> str:
    return resolve_background_image_src(value).replace('"', '\\"')


def background_style_html(selector: str, background_color: str = "", background_image: object = "") -> str:
    image_src = css_url_value(background_image)
    color_value = str(background_color or "").strip()
    if not color_value and not image_src:
        return ""
    css_parts = [f"{selector} {{ "]
    if color_value:
        css_parts.append(f"background-color: {color_value}; ")
    if image_src:
        css_parts.append(f'background-image: url("{image_src}"); ')
        css_parts.append("background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed; ")
    css_parts.append("}")
    return f"<style>{''.join(css_parts)}</style>"


