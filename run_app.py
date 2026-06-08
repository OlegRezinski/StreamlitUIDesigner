from __future__ import annotations

import os
from pathlib import Path

from streamlit.web import bootstrap


def main() -> None:
    # app_path = str(Path(__file__).parent / "app.py")
    app_path = str(Path(__file__).parent / "UI_2.py")
    args = ["--server.runOnSave=true"]
    bootstrap.run(app_path, False, args, {})


if __name__ == "__main__":
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    main()
