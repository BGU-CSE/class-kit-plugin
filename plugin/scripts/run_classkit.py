"""Run classkit from the plugin's own src/, with no PYTHONPATH and no install of classkit itself.

`bin/classkit` runs this with the dependency venv's python. Putting src/ first on sys.path keeps
classkit's `__file__` inside the plugin, so `find_framework_root()` falls back to the plugin's own
schemas/ and methodologies/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from classkit.cli import main  # noqa: E402

raise SystemExit(main())
