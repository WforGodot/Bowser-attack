import win32gui

def get_window_class(hwnd, _):
    """Function to print the handle and class name of each window."""
    class_name = win32gui.GetClassName(hwnd)
    window_text = win32gui.GetWindowText(hwnd)
    print(f"Handle: {hwnd}, Class: {class_name}, Text: {window_text}")

def main():
    print("Getting class names for all open windows...\n")
    win32gui.EnumWindows(get_window_class, None)

if __name__ == "__main__":
    main()
