import win32gui
import win32process
import win32api
import psutil  # This module simplifies process handling

def get_chrome_windows():
    """Get a list of window handles and titles for all Chrome windows."""
    chrome_windows = []

    def enum_window_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            length = win32gui.GetWindowTextLength(hwnd)
            title = win32gui.GetWindowText(hwnd)
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            if length > 0:
                try:
                    process = psutil.Process(process_id)
                    executable_path = process.exe()
                    if 'chrome' in executable_path.lower():
                        chrome_windows.append((hwnd, title))
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
                except Exception as e:
                    print("Error getting window info:", e)

    win32gui.EnumWindows(enum_window_callback, None)
    return chrome_windows

def get_highest_chrome_window_title():
    """Get the title of the highest Chrome window on the Z-order."""
    chrome_windows = get_chrome_windows()
    if chrome_windows:
        # Assuming the first window in the list is the highest in the Z-order
        return chrome_windows[0][1]
    return None

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
    active_window_title = get_highest_chrome_window_title()
    #print(active_window_title)
    
    if active_window_title:
        if driver.title != active_window_title.replace(" - Google Chrome", ""):
        # Check each window that Selenium has a handle for
            for handle in driver.window_handles[::-1]:
                # Switch to each window
                driver.switch_to.window(handle)
                # Compare the titles after stripping the possible trailing - Google Chrome
                if driver.title == active_window_title.replace(" - Google Chrome", ""):
                    print('switched to tab with title "' + driver.title + '"')
                    # If the title matches, then this is the tab we want to switch to
                    break
            else:
                # If no tabs match, raise an exception or handle as needed
                raise Exception("Active tab not found among Selenium's known tabs")
    else:
        raise Exception("Active window title not found")