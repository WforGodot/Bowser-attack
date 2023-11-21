import os
import win32gui
import win32con
import win32process
import subprocess
import time
import keyboard
from PIL import ImageGrab, Image
from example_agent import Agent
from helper.scaling import adjust_for_scaling, get_scaling_factor, calculate_dimensions, get_intersection
from helper.windows import switch_to_active_tab
from helper.dom import collect_element_info
from helper.dom_parser import build_tree, crop_dom_tree, print_dom_tree
from helper.tree_gui import TreeDisplayApp
from helper.visualize_elements import visualize_dom_tree
from helper.windows_area import get_window_area
import logging
from pathlib import Path
import pyautogui
import numpy as np
import cv2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import base64
import tkinter as tk

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
        self.screenshot_folder = Path('screenshots2')
        self.window_dimensions = (0, 0, 800, 800)
        self.driver = None  # Selenium driver
        self.max_inference = 20  # maximum number of steps per f10 press
        self.inference_count = 0  # counter for number of steps taken
        self.window_area = self.window_dimensions
        self.search_for_viewport = False
        self.viewport = (7, 131)

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
                self.driver.set_window_rect(*self.window_dimensions)
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
            
            # Offset the mouse position by the window's top left corner, taking scaling into account
            absolute_x = screen_x
            absolute_y = screen_y
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
        """Take a screenshot of the window with the given handle and window area."""
        switch_to_active_tab(self.driver)

        # Switch to the current window handle (active tab)

        self.bring_to_foreground_and_resize()
        # Verify the window is in the foreground
            # Adjust the coordinates for scaling
        rect = adjust_for_scaling(self.window_dimensions, self.scaling_factor)
        image = ImageGrab.grab(rect)
        image_resized_and_cropped = image.resize(calculate_dimensions(*self.window_dimensions)).crop(self.window_area)
        return image_resized_and_cropped
    
    def get_dom(self):

        dom = collect_element_info(self.driver)
        dom_tree = build_tree(dom)
        #dom_tree = crop_dom_tree(dom_tree, self.window_area, tolerance=10)
        return dom_tree, dom

   
    def save_canvas_screenshot(self):
        
        switch_to_active_tab(self.driver)
        self.bring_to_foreground_and_resize()
        # Find all iframe elements on the page
        # Initialize an empty list to hold all found canvas elements
        all_canvas_elements = []

        # Try to find iframes
        try:
            iframes = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe'))
            )
        except TimeoutException:
            logging.warning("No iframes found within the timeout period.")
            iframes = []

        # Process each iframe to find canvas elements
        for iframe in iframes:
            self.driver.switch_to.frame(iframe)
            canvas_elements = self.driver.find_elements(By.TAG_NAME, 'canvas')
            all_canvas_elements.extend(canvas_elements)  # Add the found canvas elements to the list
            self.driver.switch_to.parent_frame()  # Don't forget to switch back to the parent frame

        # If no canvas elements found in iframes, look in the main page
        
        canvas_elements = self.driver.find_elements(By.TAG_NAME, 'canvas')
        all_canvas_elements.extend(canvas_elements)

        # Process all collected canvas elements
        for index, canvas in enumerate(all_canvas_elements):
            # Get the canvas element as a PNG base64 string
            canvas_base64 = self.driver.execute_script(
                "return arguments[0].toDataURL('image/png').substring(21);", canvas
            )
            # Decode the base64 string and write the image data to a file
            canvas_png = base64.b64decode(canvas_base64)
            timestamp = int(time.time())
            canvas_filename = f'canvas_{timestamp}_{index}.png'
            canvas_path = Path(self.screenshot_folder) / canvas_filename
            with open(canvas_path, 'wb') as f:
                f.write(canvas_png)
            logging.info(f"Saved {canvas_path}")

        # Finally, ensure we switch back to the main content
        self.driver.switch_to.default_content()

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
            return (7, 131)
    


    def screenshot_and_dom(self, inference=False):
        """Take a screenshot and get the current DOM, then send both to the agent."""
        # Ensure the window is in the foreground and at the correct size
        # Retrieve all window handles

        x = time.time()

        
        # Take a screenshot
        image = self.screenshot()
        
        # Get the current DOM
        
        dom_tree, dom = self.get_dom()
        if not dom_tree:
            print('xxx')
        #print_dom_tree(dom_tree)
        
        # Append the screenshot to the screenshots list
        self.screenshots.append((image, dom_tree))

        #visualization = visualize_dom_tree(image.copy(), dom_tree, self.viewport)
        #visualization.show()
        
        # When x pairs of screenshots and DOMs have been taken
        if len(self.screenshots) == 1:
            # Call the agent's step function with both the screenshot and the DOM
            actions = self.agent.step(self.screenshots, mode=inference)
            
            # Perform the actions returned by the agent
            self.perform_actions(actions)
            
            # Save the last screenshot and DOM
            # self.save_screenshot(self.screenshots[-1][0])
            # self.save_dom(self.screenshots[-1][1])
            
            # Clear the screenshots list
            self.screenshots.clear()
        
        return (image, dom_tree, dom)

    def save_dom(self, dom):
        """Save the DOM to a file."""
        dom_folder = self.screenshot_folder / 'dom'
        dom_folder.mkdir(exist_ok=True)
        dom_path = dom_folder / f'dom_{int(time.time())}.html'
        with open(dom_path, 'w', encoding='utf-8') as json_file:
            json.dump(dom, json_file, indent=4)
        logging.info("Saved %s", dom_path)
    
    def save_screenshot(self, image):

        self.screenshot_folder.mkdir(exist_ok=True)
        screenshot_path = self.screenshot_folder / f'screenshot_{int(time.time())}.png'
        image.save(screenshot_path)
        logging.info("Saved %s", screenshot_path)
                        
    def on_press(self, event):
        """Handle key press events."""
        if keyboard.is_pressed('alt'):
            if event.name == 'f1':
                self.reset_window_area()    
            elif event.name == 'f9':
                self.update_window_area()
            elif event.name == 'f8':
                self.alt_f8()  # Save screenshot and DOM
            elif event.name == 'f10':
                self.alt_f10()
            elif event.name == 'f11':
                self.alt_f11()
            elif event.name == 'f12':
                self.alt_f12()

    def reset_window_area(self):
        self.window_area = self.window_dimensions
        self.update_ui()

    # Example function bindings
    def alt_f8(self):
        # Your code for F8 action
        image = self.screenshot_and_dom()
        self.save_screenshot(image[0])
        self.save_dom(image[2])
        #x = build_tree(image[1])
        #TreeDisplayApp(x)

    def update_window_area(self):
        # Your code for F9 action
        area = get_window_area()
        self.window_area = get_intersection(self.window_dimensions, area)
        self.update_ui()

    def alt_f10(self):
        # Your code for F10 action
        self.mode = 'recording'
        self.ss_count = 0  # Reset screenshot counter

    def alt_f11(self):
        self.mode = 'inference'
        self.ss_count = 0  # Reset screenshot counter

    def alt_f12(self):
        # Your code for F12 action
        self.mode = 'paused'
            
    def start(self):
        keyboard.on_press(self.on_press)
        self.open_chrome()
        self.bring_to_foreground_and_resize()
        if self.search_for_viewport:
            self.viewport = self.find_top_left_of_viewport()
        print(self.viewport)
        self.create_ui()

        try:
            while True:
                if self.mode == 'recording':
                    self.screenshot_and_dom()
                
                if self.mode == 'inference':
                    self.screenshot_and_dom(inference=True)
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
    
    def create_ui(self):
        self.ui_root = tk.Tk()
        self.ui_root.title("Glossary and Summary")
        self.ui_root.overrideredirect(True)
        self.ui_root.attributes('-topmost', True)  # Keeps the window always on top
        # Set a specific background color for transparency
        transparent_color = 'black'
        text_bg = 'black'  # Use the same color for the text widget background
        self.ui_root.config(bg=transparent_color)
        self.ui_root.attributes('-transparentcolor', transparent_color)
        window_width = 400
        window_height = 600
        screen_width = self.ui_root.winfo_screenwidth()
        screen_height = self.ui_root.winfo_screenheight()
        x_coordinate = screen_width - window_width
        y_coordinate = (screen_height - window_height) // 2
        self.ui_root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        self.glossary_text = tk.Text(self.ui_root, fg="red", bg=text_bg, insertbackground="black", wrap=tk.WORD, bd=0)
        self.glossary = "F8: Take a screenshot and display the DOM tree\n" \
                     "F9: Take a screenshot of the canvas elements\n" \
                        "F10: Start recording\n" \
                        "F11: Start inference\n" \
                        "F12: Pause\n"
        self.glossary_text.insert(tk.END, self.glossary)
        self.glossary_text.pack(expand=True, fill=tk.BOTH)
        self.ui_root.mainloop()
    
    def update_ui(self):
        """Update the UI with the latest screenshot and DOM."""
        if self.ui_root:
            self.glossary_text.delete('1.0', tk.END)
            self.glossary_text.insert(tk.END, self.glossary + 'Window area: ' + str(self.window_area))
            self.glossary_text.pack(expand=True, fill=tk.BOTH)


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
