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
