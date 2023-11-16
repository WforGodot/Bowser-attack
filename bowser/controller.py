import os
import win32gui
import win32con
import win32process
import subprocess
import time
import keyboard
from PIL import ImageGrab, Image
from example_agent import Agent
from helper.scaling import adjust_for_scaling, get_scaling_factor, hex_to_rgb, apply_tolerance
from helper.windows import get_active_window_title, find_chrome_tab_by_title, switch_to_active_tab
import logging
from pathlib import Path
import pyautogui
import numpy as np
import cv2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

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
        self.screenshot_folder = Path('screenshots')
        self.dimensions = (800, 800)
        self.driver = None  # Selenium driver
        self.max_inference = 20  # maximum number of steps per f10 press
        self.inference_count = 0  # counter for number of steps taken

    def open_chrome(self):
        chrome_options = ChromeOptions()
        # Add any specific options you need here, e.g., headless mode, specific profile

        chrome_service = ChromeService(executable_path="path/to/chromedriver")
        try:
            self.driver = webdriver.Chrome()
            logging.info("Chrome opened with WebDriver")
        except Exception as e:
            logging.error(f"Failed to open Chrome with WebDriver: {e}")
            # Handle the error, maybe exit the script
        time.sleep(5)  # Wait for the window to open

        # Since we're using WebDriver, the window handling is different
        self.hwnd = self.driver.current_window_handle

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
        """Bring the Selenium-driven Chrome window to the foreground and resize it."""

        if self.driver:
            try:
                self.driver.set_window_rect(0, 0, *self.dimensions)
                # self.driver.switch_to.window(self.hwnd)
            except Exception as e:
                logging.error(f"Failed to bring the window to the foreground: {e}")
        else:
            logging.error("No Chrome driver or window handle found.")

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
        self.bring_to_foreground_and_resize()
        # Verify the window is in the foreground
            # Adjust the coordinates for scaling
        rect = adjust_for_scaling(self.dimensions, self.scaling_factor)
        image = ImageGrab.grab((0, 0, *rect))
        image_resized = image.resize(self.dimensions) #, Image.ANTIALIAS)
        return image_resized


    def find_top_left_of_viewport(self):

        # Open the HTML file in the browser
        html_file_path = 'file://' + os.path.join(os.getcwd(), 'bowser/helper/green.html')
        self.driver.get(html_file_path)

        # Take a screenshot
        screenshot_path = 'screenshot.png'
        image = self.screenshot()
        image.save(screenshot_path)

        # Process the screenshot to find the green area
        image = cv2.imread(screenshot_path)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define the color range for green in HSV
        lower_green = np.array([45, 100, 100])  # Adjusted range
        upper_green = np.array([75, 255, 255])

        # Create a mask for green color
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Assuming the largest contour is the green area
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            return (x, y)
        else:
            return None

    def screenshot_and_dom(self):
        """Take a screenshot and get the current DOM, then send both to the agent."""
        # Ensure the window is in the foreground and at the correct size
        # Retrieve all window handles

        x = time.time()
        switch_to_active_tab(self.driver)

        # Switch to the current window handle (active tab)

        self.bring_to_foreground_and_resize()
        
        # Take a screenshot
        image = self.screenshot()
        
        # Get the current DOM
        dom = self.driver.page_source
        
        # Append the screenshot to the screenshots list
        self.screenshots.append((image, dom))
        
        # When 5 pairs of screenshots and DOMs have been taken
        if len(self.screenshots) == 1:
            # Call the agent's step function with both the screenshot and the DOM
            actions = self.agent.step(self.screenshots, mode = self.mode)
            
            # Perform the actions returned by the agent
            self.perform_actions(actions)
            
            # Save the last screenshot and DOM
            # self.save_screenshot(self.screenshots[-1][0])
            # self.save_dom(self.screenshots[-1][1])
            
            # Clear the screenshots list
            self.screenshots.clear()
        
        return (image, dom)

    def save_dom(self, dom):
        """Save the DOM to a file."""
        dom_folder = self.screenshot_folder / 'dom'
        dom_folder.mkdir(exist_ok=True)
        dom_path = dom_folder / f'dom_{int(time.time())}.html'
        with open(dom_path, 'w', encoding='utf-8') as file:
            file.write(dom)
        logging.info("Saved %s", dom_path)
    
    def save_screenshot(self, image):

        self.screenshot_folder.mkdir(exist_ok=True)
        screenshot_path = self.screenshot_folder / f'screenshot_{int(time.time())}.png'
        image.save(screenshot_path)
        logging.info("Saved %s", screenshot_path)
                        
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
        elif event.name == 'f8':
            image = self.screenshot_and_dom()
            self.save_screenshot(image[0])
            self.save_dom(image[1])

    def start(self):
        keyboard.on_press(self.on_press)
        self.open_chrome()
        self.bring_to_foreground_and_resize()
        self.viewport = self.find_top_left_of_viewport()
        print(self.viewport)

        try:
            while True:
                if self.mode == 'recording':
                    self.screenshot_and_dom()  # This is the updated line
                
                if self.mode == 'inference':
                    self.screenshot_and_dom()  # This is the updated line
                    self.inference_count += 1
                    if self.inference_count >= self.max_inference:
                        self.mode = 'paused'
                        self.inference_count = 0
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
