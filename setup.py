"""
py2app setup for Lift — standalone macOS .app bundle.
Build: uv run python setup.py py2app
Output: dist/Lift.app (zip this for distribution).
"""
from setuptools import setup

APP = ["lift.py"]
OPTIONS = {
    "py2app": {
        "plist": {
            "CFBundleName": "Lift",
            "CFBundleDisplayName": "Lift",
            "CFBundleIdentifier": "app.lift",
            "CFBundleVersion": "0.1.0",
            "CFBundleShortVersionString": "0.1.0",
            "LSUIElement": True,  # Background app: no Dock icon, no menu bar app menu
            "NSHumanReadableCopyright": "Lift — auto-copy on text selection.",
        },
        "packages": ["Quartz", "Foundation", "CoreFoundation", "objc"],
    }
}

setup(
    app=APP,
    options=OPTIONS,
)
