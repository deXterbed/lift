#!/usr/bin/env python3
"""
Apply py2app fix for Python 3.12 (zlib has no __file__).
Run once after: uv sync --extra dev
Then: ./build_app.sh
"""
import sys
from pathlib import Path

try:
    import py2app
except ImportError:
    print("py2app not installed. Run: uv sync --extra dev", file=sys.stderr)
    sys.exit(1)

build_app_path = Path(py2app.__file__).parent / "build_app.py"

with open(build_app_path) as f:
    content = f.read()

old = """        self.copy_file(arcname, arcdir)
        if sys.version_info[0] != 2:
            import zlib

            self.copy_file(zlib.__file__, os.path.dirname(arcdir))"""

new = """        self.copy_file(arcname, arcdir)
        if sys.version_info[0] != 2:
            import zlib

            # Python 3.12+: zlib is builtin and has no __file__
            zlib_file = getattr(zlib, "__file__", None)
            if zlib_file is not None:
                self.copy_file(zlib_file, os.path.dirname(arcdir))"""

if new in content:
    print("Patch already applied.")
    sys.exit(0)
if old not in content:
    print("Could not find target block in py2app build_app.py (version mismatch?).", file=sys.stderr)
    sys.exit(1)

content = content.replace(old, new)
with open(build_app_path, "w") as f:
    f.write(content)
print("Patched py2app for Python 3.12 (zlib). You can run ./build_app.sh now.")
