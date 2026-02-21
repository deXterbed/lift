#!/usr/bin/env python3
"""
Lift — auto-copy on text selection (macOS).

Uses a listen-only CGEventTap so mouse events are only observed, not intercepted.
When you release the mouse after dragging to select text, Cmd+C is simulated.
Left click and Cmd+C continue to work normally.

Requires: Input Monitoring permission (System Settings > Privacy & Security > Input Monitoring).
"""

import math
import time

from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventGetLocation,
    CGEventMaskBit,
    CGEventPost,
    CGEventSetFlags,
    CGEventTapCreate,
    CGEventTapEnable,
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

    tap = CGEventTapCreate(
        kCGSessionEventTap,
        kCGHeadInsertEventTap,
        kCGEventTapOptionListenOnly,
        event_mask,
        event_callback,
        None,
    )

    if tap is None:
        print(
            "Failed to create event tap. Grant Input Monitoring permission:\n"
            "  System Settings > Privacy & Security > Input Monitoring\n"
            "  Add the app you run this from (e.g. Cursor or Terminal) and restart it."
        )
        return 1

    run_loop_source = CFMachPortCreateRunLoopSource(None, tap, 0)
    CFRunLoopAddSource(CFRunLoopGetCurrent(), run_loop_source, kCFRunLoopCommonModes)
    CGEventTapEnable(tap, True)

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
