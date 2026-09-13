"""Starter-format compatibility bridge for ``backend/models.py``.

The project uses a package layout under ``backend/models/``. This file allows
``import models`` to continue working in environments that expect the single
starter-file path to exist.
"""

from pathlib import Path

# Make this module package-like so relative imports in models/__init__.py work.
_MODELS_DIR = Path(__file__).with_name("models")
__path__ = [str(_MODELS_DIR)]
__package__ = "models"

# Execute the real models package initializer in this module namespace.
_init_code = (_MODELS_DIR / "__init__.py").read_text(encoding="utf-8")
exec(compile(_init_code, str(_MODELS_DIR / "__init__.py"), "exec"), globals(), globals())
