#!/usr/bin/env python3
"""
Lift — auto-copy on text selection (macOS).

Uses a listen-only CGEventTap so mouse events are only observed, not intercepted.
When you release the mouse after dragging to select text, Cmd+C is simulated.
Left click and Cmd+C continue to work normally.

Requires: Input Monitoring permission (System Settings > Privacy & Security > Input Monitoring).
"""

import math
import os
import subprocess
import sys
import time

from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventGetLocation,
    CGEventMaskBit,
    CGEventPost,
    CGEventSetFlags,
    CGEventTapCreate,
    CGEventTapEnable,
    CGPreflightListenEventAccess,
    CGRequestListenEventAccess,
    CFRunLoopAddSource,
    CFRunLoopGetCurrent,
    CFRunLoopRunInMode,
    CFMachPortCreateRunLoopSource,
    kCGHIDEventTap,
    kCFRunLoopDefaultMode,
    kCFRunLoopRunTimedOut,
    kCGEventFlagMaskCommand,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGEventTapOptionListenOnly,
    kCGSessionEventTap,
    kCGHeadInsertEventTap,
    kCFRunLoopCommonModes,
)

# Minimum mouse movement (points) to treat as a selection drag rather than a click
DRAG_THRESHOLD_PX = 5
# Seconds to wait before another selection triggers copy (preserves clipboard for paste/replace)
COPY_SUPPRESS_SEC = 5.0
# Virtual key code for 'C'
VK_ANSI_C = 8

# State
mouse_down_pos = None
last_copy_time = 0.0


def _app_bundle_path():
    """Path to the .app bundle if we're running as an app; else None."""
    exe = os.path.abspath(sys.executable)
    if ".app/Contents/MacOS" in exe:
        return exe.split(".app/Contents/MacOS")[0] + ".app"
    return None


def _add_to_login_items():
    """Add this app to Login Items (open at login) if running as Lift.app."""
    bundle = _app_bundle_path()
    if not bundle or not os.path.isdir(bundle):
        return
    # Get current login item paths
    try:
        out = subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get the path of every login item',
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode != 0:
            return
        paths = [p.strip() for p in (out.stdout or "").split(",")]
        if bundle in paths:
            return
        # Add to login items (hidden so it doesn't show in Dock)
        esc = bundle.replace("\\", "\\\\").replace('"', '\\"')
        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "System Events" to make login item at end with properties {{path:"{esc}", hidden:true}}',
            ],
            capture_output=True,
            timeout=5,
        )
    except Exception:
        pass


def post_cmd_c():
    """Post Cmd+C to the system (copy)."""
    key_down = CGEventCreateKeyboardEvent(None, VK_ANSI_C, True)
    CGEventSetFlags(key_down, kCGEventFlagMaskCommand)
    key_up = CGEventCreateKeyboardEvent(None, VK_ANSI_C, False)
    CGEventSetFlags(key_up, kCGEventFlagMaskCommand)
    CGEventPost(kCGHIDEventTap, key_down)
    CGEventPost(kCGHIDEventTap, key_up)


def event_callback(proxy, event_type, event, refcon):
    global mouse_down_pos, last_copy_time

    if event is None:
        return event

    if event_type == kCGEventLeftMouseDown:
        loc = CGEventGetLocation(event)
        mouse_down_pos = (loc.x, loc.y)
        return event

    if event_type == kCGEventLeftMouseUp:
        if mouse_down_pos is None:
            return event

        loc = CGEventGetLocation(event)
        dx = loc.x - mouse_down_pos[0]
        dy = loc.y - mouse_down_pos[1]
        dist = math.sqrt(dx * dx + dy * dy)
        mouse_down_pos = None

        now = time.time()
        if dist >= DRAG_THRESHOLD_PX and (now - last_copy_time) >= COPY_SUPPRESS_SEC:
            last_copy_time = now
            post_cmd_c()
            print("Copied!")

        return event

    return event


def main():
    event_mask = CGEventMaskBit(kCGEventLeftMouseDown) | CGEventMaskBit(kCGEventLeftMouseUp)

    # Only prompt when we actually lack permission. If permission is granted, tap creation
    # can still fail briefly (e.g. at login); retry before showing any dialog.
    has_listen_access = CGPreflightListenEventAccess()
    if not has_listen_access:
        CGRequestListenEventAccess()
        time.sleep(1.5)
        has_listen_access = CGPreflightListenEventAccess()

    tap = None
    for attempt in range(3):
        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            kCGEventTapOptionListenOnly,
            event_mask,
            event_callback,
            None,
        )
        if tap is not None:
            break
        if has_listen_access:
            time.sleep(1.0)
        else:
            break

    if tap is None:
        if has_listen_access:
            msg = (
                "Lift couldn’t start the event tap. Try logging out and back in, or restart Lift."
            )
        else:
            msg = (
                "Lift needs Input Monitoring to work. "
                "Open System Settings → Privacy & Security → Input Monitoring, add Lift, then open Lift again."
            )
        print(msg)
        if _app_bundle_path():
            try:
                esc = msg.replace("\\", "\\\\").replace('"', '\\"')
                subprocess.run(
                    ["/usr/bin/osascript", "-e", f'display dialog "{esc}" with title "Lift" buttons {{"OK"}} default button 1 with icon stop'],
                    timeout=10,
                )
            except Exception:
                pass
        return 0

    run_loop_source = CFMachPortCreateRunLoopSource(None, tap, 0)
    CFRunLoopAddSource(CFRunLoopGetCurrent(), run_loop_source, kCFRunLoopCommonModes)
    CGEventTapEnable(tap, True)

    _add_to_login_items()

    print("Lift is running. Drag to select text, then release to copy. Press Ctrl+C to quit.")
    try:
        while True:
            result = CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.5, False)
            if result != kCFRunLoopRunTimedOut:
                break
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    exit(main())
