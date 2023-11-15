import os
import win32gui
import win32con
import win32process
import subprocess
import time
import keyboard
from PIL import ImageGrab
from example_agent import Agent
from helper.scaling import adjust_for_scaling, get_scaling_factor
import logging
from pathlib import Path
import pyautogui

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Controller:
    def __init__(self, agent_class, agent_params={}, controller_params={}):
        self.mode = 'paused'
        self.hwnd = None
        self.chrome_windows = []  # List to hold Chrome window handles
        self.screenshots = []  # List to hold screenshots
        self.agent = agent_class(agent_params)  # Initialize the Agent
        self.controller_params = controller_params
        self.scaling_factor = get_scaling_factor()

    def open_chrome(self):
        chrome_path = self.controller_params.get('chrome_path', "C:/Program Files/Google/Chrome/Application/chrome.exe") # Adjust as necessary
        try:
            proc = subprocess.Popen([chrome_path])
            logging.info("Chrome opened with PID: %s", proc.pid)
            # ...
        except FileNotFoundError:
            logging.error("Chrome executable not found at path: %s", chrome_path)
            # Handle the error, maybe exit the script
        time.sleep(5)  # Wait for the window to open

        def enum_window_callback(hwnd, lParam): 
            """Check if the given window belongs to the Chrome process started."""
            try:
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == lParam:
                    self.hwnd = hwnd
                    return False
            except Exception as e:
                logging.error(f"EnumWindows encountered an error: {e}")
            return True

        try:
            win32gui.EnumWindows(enum_window_callback, proc.pid)
        except Exception as e:
            logging.error(f"Failed to enumerate windows: {e}")

        if self.hwnd is None:
            logging.error("Failed to find Chrome window handle.")

    def update_chrome_windows(self):
        """Update the list of Chrome window handles and sort by opening time."""
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd) and 'Chrome' in win32gui.GetClassName(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                # Get the process start time and use it to sort the windows
                try:
                    creation_time = win32process.GetProcessTimes(pid).CreationTime
                    self.chrome_windows.append((hwnd, creation_time))
                except Exception:
                    pass
            return True

        self.chrome_windows.clear()
        win32gui.EnumWindows(enum_windows_callback, None)
        # Sort windows by creation time, oldest first
        self.chrome_windows.sort(key=lambda x: x[1])

    def bring_to_foreground_and_resize(self):
        """Bring the window with the current handle to the foreground and resize it.
           If the current handle is no longer valid, use the oldest Chrome window.
        """
        def is_valid_window(hwnd):
            """Check if the window handle is valid and the window is visible."""
            return win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)

        # Try to use the current handle
        if is_valid_window(self.hwnd):
            try:
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.hwnd)
                # Resize to 1024x1024 and move to the top left corner
                win32gui.MoveWindow(self.hwnd, 0, 0, 1024, 1024, True)
            except Exception as e:
                logging.error(f"Failed to bring the window to the foreground: {e}")
                self.hwnd = None  # Invalidate the handle so it finds a new one

        # If the current handle is invalid, find the oldest Chrome window
        if not is_valid_window(self.hwnd):
            self.update_chrome_windows()  # Refresh the Chrome windows list
            if self.chrome_windows:
                self.hwnd = self.chrome_windows[0][0]  # Use the oldest window
                win32gui.SetForegroundWindow(self.hwnd)
                # Resize to 1024x1024 and move to the top left corner
                win32gui.MoveWindow(self.hwnd, 0, 0, 1024, 1024, True)
            else:
                logging.error("No Chrome windows found.")

    def perform_actions(self, actions):
        """Perform actions returned by agent.step(), including mouse moves, clicks, and keyboard input."""
        (x, y), click, keyboard_input = actions
        if (x, y) is not None:
            # Convert screen position based on scaling factor
            screen_x, screen_y = adjust_for_scaling((x, y), self.scaling_factor)
            # Get the current window position
            rect = win32gui.GetWindowRect(self.hwnd)
            # Offset the mouse position by the window's top left corner, taking scaling into account
            absolute_x = rect[0] + screen_x
            absolute_y = rect[1] + screen_y
            # Move the mouse to the specified coordinates
            pyautogui.moveTo(absolute_x, absolute_y)

            # Perform the click if specified
            if click == "left":
                pyautogui.click(button='left')
            elif click == "right":
                pyautogui.click(button='right')

        # Type the keyboard input if provided
        if keyboard_input:
            keyboard.write(keyboard_input)

    def screenshot(self):
        """Take a screenshot of the window with the given handle."""
        if self.hwnd is not None:
            self.bring_to_foreground_and_resize()
            # Verify the window is in the foreground
            if win32gui.GetForegroundWindow() == self.hwnd:
                rect = win32gui.GetWindowRect(self.hwnd)
                # Adjust the coordinates for scaling
                rect = adjust_for_scaling(rect, self.scaling_factor)
                image = ImageGrab.grab(rect)

                self.screenshots.append(image)
                
                # When 10 screenshots have been taken
                if len(self.screenshots) == 10:
                    # Call the agent's step function
                    actions = self.agent.step(self.screenshots)
                    
                    # Perform the actions returned by the agent
                    self.perform_actions(actions)
                    
                    # Save the 10th screenshot
                    screenshot_folder = Path('screenshots')
                    screenshot_folder.mkdir(exist_ok=True)
                    screenshot_path = screenshot_folder / f'screenshot_{int(time.time())}.png'
                    self.screenshots[-1].save(screenshot_path)
                    logging.info("Saved %s", screenshot_path)
                    
                    # Clear the screenshots list
                    self.screenshots.clear()
                        
            else:
                logging.error("Window is not in the foreground.")
                self.mode = 'paused'

    def on_press(self, event):
        if event.name == 'f10':
            self.mode = 'recording'
            self.ss_count = 0  # Reset screenshot counter
        elif event.name == 'f11':
            self.mode = 'inference'
            self.ss_count = 0  # Reset screenshot counter
        elif event.name == 'f12':
            self.mode = 'paused'
        elif event.name == 'f9':
            self.stop()

    def start(self):
        keyboard.on_press(self.on_press)
        self.open_chrome()

        try:
            while True:
                if self.mode != 'paused':
                    self.screenshot()
                time.sleep(0.1)  # Rest for a bit to not overload the system
        except KeyboardInterrupt:
            print("Exiting the program.")
            keyboard.unhook_all()

    def stop(self):
        """Stop the program."""
        logging.info("Stopping the program.")
        # Perform any cleanup if necessary
        # ...

        # This will break the main loop and exit the program
        raise SystemExit


# Create a Controller instance and start it
def main():
    agent_params = {}  # Add actual agent parameters here
    controller_params = {}  # Add actual controller parameters here
    controller = Controller(Agent, agent_params, controller_params)
    try:
        controller.start()
    except SystemExit:
        logging.info("Program terminated.")
    except Exception as e:
        logging.exception("An unexpected error occurred: %s", e)


if __name__ == "__main__":
    main()
