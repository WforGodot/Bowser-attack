import win32gui

def get_active_window_title():
    """Get the title of the active window."""
    hwnd = win32gui.GetForegroundWindow()
    length = win32gui.GetWindowTextLength(hwnd)
    return win32gui.GetWindowText(hwnd)

def find_chrome_tab_by_title(title):
    """Find a Chrome tab that contains the specified title."""
    def window_enum_callback(hwnd, tabs):
        """A callback function that checks each window."""
        if 'Chrome' in win32gui.GetClassName(hwnd) and win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title in window_title:
                print(window_title)
                tabs.append(hwnd)

    tabs = []
    win32gui.EnumWindows(window_enum_callback, tabs)
    return tabs

def switch_to_active_tab(driver):
    """Switch to the active tab by matching the window title with the active window title."""
    # Get the title of the current active window using win32gui
    active_window_title = get_active_window_title()
    print(active_window_title)
    if driver.title != active_window_title.replace(" - Google Chrome", ""):
        # Check each window that Selenium has a handle for
        for handle in driver.window_handles[::-1]:
            # Switch to each window
            driver.switch_to.window(handle)
            # Compare the titles after stripping the possible trailing - Google Chrome
            if driver.title == active_window_title.replace(" - Google Chrome", ""):
                # If the title matches, then this is the tab we want to switch to
                break
        else:
            # If no tabs match, raise an exception or handle as needed
            raise Exception("Active tab not found among Selenium's known tabs")