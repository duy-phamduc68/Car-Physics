# ─────────────────────────────────────────────────────────────────────────────
# controls.py — Xbox controller (XInput) and pygame joystick input handling
# ─────────────────────────────────────────────────────────────────────────────

import sys

try:
    import ctypes
    XINPUT_AVAILABLE = True
except ImportError:
    XINPUT_AVAILABLE = False

# Module-level handle set by load_xinput()
_xinput_dll = None

# We can remove XINPUT_BUTTON_B since we are mapping brakes to LT now


def load_xinput():
    """Try to load an XInput DLL. Returns True on success."""
    global _xinput_dll
    if not XINPUT_AVAILABLE or sys.platform != "win32":
        return False
    for name in ("xinput1_4", "xinput1_3", "xinput9_1_0"):
        try:
            _xinput_dll = ctypes.windll.LoadLibrary(name)
            return True
        except OSError:
            continue
    return False


# ctypes structs are only usable when ctypes imported successfully
if XINPUT_AVAILABLE:
    class XINPUT_GAMEPAD(ctypes.Structure):
        _fields_ = [
            ("wButtons",      ctypes.c_ushort),
            ("bLeftTrigger",  ctypes.c_ubyte),
            ("bRightTrigger", ctypes.c_ubyte),
            ("sThumbLX",      ctypes.c_short),
            ("sThumbLY",      ctypes.c_short),
            ("sThumbRX",      ctypes.c_short),
            ("sThumbRY",      ctypes.c_short),
        ]

    class XINPUT_STATE(ctypes.Structure):
        _fields_ = [
            ("dwPacketNumber", ctypes.c_ulong),
            ("Gamepad",        XINPUT_GAMEPAD),
        ]
else:
    class XINPUT_GAMEPAD:   # noqa: F811  (stub when ctypes unavailable)
        pass

    class XINPUT_STATE:     # noqa: F811
        pass


def get_xinput_state(pad=0):
    """
    Poll XInput pad `pad`.

    Returns (right_trigger_0_to_1, left_trigger_binary) or None if unavailable.
    """
    if _xinput_dll is None:
        return None
    state = XINPUT_STATE()
    ret   = _xinput_dll.XInputGetState(pad, ctypes.byref(state))
    if ret != 0:
        return None
        
    rt = state.Gamepad.bRightTrigger / 255.0
    
    # Evaluate LT as binary: True if pressed past a small deadzone (10/255)
    lt_binary = bool(state.Gamepad.bLeftTrigger > 10) 
    
    return rt, lt_binary