# Lift

**Lift** is a small macOS app that copies selected text to the clipboard when you release the mouse or trackpad after a selection. It uses a listen-only event tap, so normal left click and Cmd+C are unchanged.

- **Open source** — [License](LICENSE): MIT
- **macOS only** — Uses Quartz (PyObjC) for the event tap.

## How it works

Drag to select text anywhere, then release — the selection is copied. Single clicks do nothing. No Dock icon; runs in the background. First run: macOS will ask for **Input Monitoring** (System Settings → Privacy & Security → Input Monitoring). Grant it for the app you run from (e.g. Terminal or Cursor), or for **Lift** if you use the standalone .app.

When you open **Lift.app**, it adds itself to **Login Items** (Open at Login) once, so it will start automatically when you log in. You can turn this off in **System Settings → General → Login Items**.

**Why does it ask for Input Monitoring again when it’s already granted?** macOS ties the permission to the **exact binary** that runs. If you granted it for **Lift.app** and then run `uv run lift.py` (or from Cursor), the process is a different executable (e.g. Python or the uv runner), so macOS asks again. Similarly, granting for Terminal/Cursor doesn’t grant for **Lift.app**. Add and enable whichever binary you actually use in **System Settings → Privacy & Security → Input Monitoring**.

## Requirements

- macOS
- Python 3.8+ (for running from source)
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Install (from source)

```bash
git clone https://github.com/deXterbed/lift.git
cd lift
uv sync
```

## Run

```bash
uv run lift.py
```

- **Quit:** Press **Ctrl+C** in the terminal (or Activity Monitor → Lift → Quit when using the .app).

## Run at login (optional)

1. Create a Launch Agent (replace `PATH_TO_LIFT` with the path to this repo):

```bash
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/com.user.lift.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.user.lift</string>
  <key>ProgramArguments</key>
  <array>
    <string>PATH_TO_LIFT/.venv/bin/python</string>
    <string>PATH_TO_LIFT/lift.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
EOF
```

2. Edit the plist and replace `PATH_TO_LIFT` with your actual path (e.g. `/Users/you/repos/lift`).

3. Load and start:

```bash
launchctl load ~/Library/LaunchAgents/com.user.lift.plist
```

4. Grant **Input Monitoring** to the `python` binary (System Settings → Privacy & Security → Input Monitoring) if prompted.

## Distribution (standalone .app and zip)

1. Install dev dependencies and build (requires [py2app](https://py2app.readthedocs.io/); note: building with Python 3.12 may hit known py2app issues):

```bash
uv sync --extra dev
./build_app.sh
```

Or, if you don’t use the build script, temporarily move `pyproject.toml` aside and run:

```bash
.venv/bin/python setup.py py2app
```

2. The app is created at **`dist/Lift.app`**. Test it; macOS will ask for **Input Monitoring** for “Lift”.

3. Zip for distribution:

```bash
cd dist && zip -r Lift-macOS.zip Lift.app && cd ..
```

Share **`dist/Lift-macOS.zip`**. Users: unzip, move **Lift.app** to Applications (or keep in Downloads), open once and grant Input Monitoring when prompted.

## Uninstall (stop permission prompts)

If you removed Lift but macOS still asks for **Input Monitoring** or the app seems to start at login, clean up:

1. **Launch Agent (if you set it up)** — Stop the agent and remove the plist so it doesn’t run at login:
   ```bash
   launchctl bootout "gui/$(id -u)/com.user.lift"   # optional; may say "No such process" if not loaded
   rm ~/Library/LaunchAgents/com.user.lift.plist
   ```
   If `launchctl unload` or `bootout` fails, removing the plist is enough — it won’t load again after you log out and back in.

2. **Login Items** — Open **System Settings → General → Login Items** and remove **Lift** if it appears (it may point to a deleted app).

3. **Input Monitoring** — In **System Settings → Privacy & Security → Input Monitoring**, you can remove **Lift** or the **Python** entry so macOS stops prompting.

## Tuning

Edit `lift.py`:

- **`DRAG_THRESHOLD_PX`** — Minimum movement (points) to count as a selection (default: 5). Lower to 2–3 if trackpad selection doesn’t trigger.
- **`COPY_SUPPRESS_SEC`** — Seconds after a copy before another selection will copy again (default: 5). Keeps the clipboard intact when you highlight the target to replace.

## License

[MIT](LICENSE).

## Contributing

Contributions are welcome. Open an issue or a pull request on GitHub.
