from __future__ import annotations

import base64

from streamlit.testing.v1 import AppTest

from designer.models import Design


_ONE_PIXEL_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WlH0V8AAAAASUVORK5CYII="
)


def test_ui2_preview_uses_data_uri_for_local_background_image(tmp_path) -> None:
    image_path = tmp_path / "bg.png"
    image_path.write_bytes(base64.b64decode(_ONE_PIXEL_PNG))

    at = AppTest.from_file("UI_2.py")
    at.session_state["design"] = Design(name="Preview", background_image=str(image_path), widgets=[])
    at = at.run(timeout=20)

    assert any(
        ".st-key-ui1_preview_pane" in md.value and 'background-image: url("data:image/png;base64,' in md.value
        for md in at.markdown
    )

