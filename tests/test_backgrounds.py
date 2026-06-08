from __future__ import annotations

import base64

from designer.backgrounds import css_url_value, resolve_background_image_src
from designer.models import Design
from designer.serialization import design_from_dict, design_to_dict


_ONE_PIXEL_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WlH0V8AAAAASUVORK5CYII="
)


def test_resolve_background_image_src_keeps_https_url() -> None:
    value = "https://example.com/background.png"
    assert resolve_background_image_src(value) == value


def test_resolve_background_image_src_local_file_becomes_data_uri(tmp_path) -> None:
    image_path = tmp_path / "bg.png"
    image_path.write_bytes(base64.b64decode(_ONE_PIXEL_PNG))

    resolved = resolve_background_image_src(str(image_path))
    assert resolved.startswith("data:image/png;base64,")


def test_resolve_background_image_src_file_uri_becomes_data_uri(tmp_path) -> None:
    image_path = tmp_path / "bg.png"
    image_path.write_bytes(base64.b64decode(_ONE_PIXEL_PNG))

    resolved = resolve_background_image_src(image_path.as_uri())
    assert resolved.startswith("data:image/png;base64,")


def test_css_url_value_normalizes_missing_windows_path() -> None:
    value = r'C:\Users\O\"Neil\Pictures\background.jpg'
    assert css_url_value(value) == 'C:/Users/O/\\"Neil/Pictures/background.jpg'


def test_design_background_image_round_trip_preserves_raw_path() -> None:
    design = Design(name="Test", background_image=r"C:\Users\OLEGRAZ\Pictures\background.jpg")

    restored = design_from_dict(design_to_dict(design))
    assert restored.background_image == design.background_image



