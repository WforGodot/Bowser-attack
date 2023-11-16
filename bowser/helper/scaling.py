import ctypes


def adjust_for_scaling(values, scaling_factor=1.25):
    """Adjust a tuple of values based on the display scaling factor."""
    return tuple(int(value * scaling_factor) for value in values)


def get_scaling_factor():
    user32 = ctypes.windll.user32

    # Get the handle to the desktop window
    hwnd = user32.GetDesktopWindow()

    # Get the DPI for the desktop window
    dpi = user32.GetDpiForWindow(hwnd)

    # The standard DPI in Windows is 96, so the scaling factor would be dpi / 96
    scaling_factor = dpi / 96
    return scaling_factor


def hex_to_rgb(hex_color):
    """Convert hexadecimal color to RGB."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def apply_tolerance(color, tolerance):
    """Apply tolerance to each element of the color."""
    return [[max(c - tolerance, 0), min(c + tolerance, 255)] for c in color]