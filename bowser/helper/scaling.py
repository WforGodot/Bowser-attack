import ctypes


def adjust_for_scaling(values, scaling_factor=1.25):
    """Adjust a tuple of values based on the display scaling factor."""
    return tuple(int(value * scaling_factor) for value in values)

def calculate_dimensions(x, y, w, z):
    width = w - x
    height = z - y
    return (width, height)

def get_scaling_factor():
    user32 = ctypes.windll.user32

    # Get the handle to the desktop window
    hwnd = user32.GetDesktopWindow()

    # Get the DPI for the desktop window
    dpi = user32.GetDpiForWindow(hwnd)

    # The standard DPI in Windows is 96, so the scaling factor would be dpi / 96
    scaling_factor = dpi / 96
    return scaling_factor

def get_intersection(box1, box2, scaling_factor=1.25):
    x1, y1, x2, y2 = box1
    x3, y3, x4, y4 = box2

    # Find overlap in the x-axis
    overlap_x1 = max(x1, x3)
    overlap_x2 = min(x2, x4)

    # Find overlap in the y-axis
    overlap_y1 = max(y1, y3)
    overlap_y2 = min(y2, y4)

    # Check if there is an overlap
    if overlap_x1 < overlap_x2 and overlap_y1 < overlap_y2:
        # Adjust coordinates to be relative to box1's top left corner
        unscaled = (overlap_x1 - x1, overlap_y1 - y1, overlap_x2 - x1, overlap_y2 - y1)
        return tuple(int(value / scaling_factor) for value in unscaled)
    else:
        # No overlap
        return None


def hex_to_rgb(hex_color):
    """Convert hexadecimal color to RGB."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def apply_tolerance(color, tolerance):
    """Apply tolerance to each element of the color."""
    return [[max(c - tolerance, 0), min(c + tolerance, 255)] for c in color]