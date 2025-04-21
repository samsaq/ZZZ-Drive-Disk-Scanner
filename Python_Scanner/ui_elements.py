import cv2
import numpy as np
import pyautogui
from typing import Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class UIElement:
    """Represents a UI element with its relative position and size"""

    name: str
    relative_x: float  # x position as percentage of screen width
    relative_y: float  # y position as percentage of screen height
    relative_width: float  # width as percentage of screen width
    relative_height: float  # height as percentage of screen height
    template_path: str  # path to the template image (using 1440p as base)
    confidence: float = 0.8  # minimum confidence threshold


class UIElementMatcher:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._template_cache = {}

    def _get_absolute_region(self, element: UIElement) -> Tuple[int, int, int, int]:
        """Convert relative coordinates to absolute screen coordinates"""
        return (
            int(element.relative_x * self.screen_width),
            int(element.relative_y * self.screen_height),
            int(element.relative_width * self.screen_width),
            int(element.relative_height * self.screen_height),
        )

    def _load_and_resize_template(self, element: UIElement) -> np.ndarray:
        """
        Load template image and resize it to match the current screen resolution
        Raises exceptions with detailed error message if something goes wrong
        """
        if element.template_path not in self._template_cache:
            template = cv2.imread(element.template_path)
            if template is None:
                error_msg = f"Could not load template image: {element.template_path}"
                raise ValueError(error_msg)

            # Get the target region size
            region = self._get_absolute_region(element)
            target_size = (region[2], region[3])

            # Resize template to match the target region size
            template_resized = cv2.resize(
                template, target_size, interpolation=cv2.INTER_AREA
            )
            self._template_cache[element.template_path] = template_resized

        return self._template_cache[element.template_path]

    def locate_element(self, element: UIElement) -> Optional[Tuple[int, int, int, int]]:
        """
        Locate a UI element on screen using template matching
        Returns tuple of (left, top, width, height) if found, None otherwise
        Raises exceptions with detailed error message if something goes wrong
        """
        try:
            # Get the region to search in
            region = self._get_absolute_region(element)

            # Take screenshot of the region
            screenshot = pyautogui.screenshot(region=region)
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Get and resize the template
            template = self._load_and_resize_template(element)

            # Perform template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= element.confidence:
                x = region[0] + max_loc[0]
                y = region[1] + max_loc[1]
                return (x, y, template.shape[1], template.shape[0])

            return None

        except Exception as e:
            error_msg = f"Error locating element {element.name}: {e}"
            raise Exception(error_msg) from e

    def click_element(self, element: UIElement) -> bool:
        """
        Click on a UI element if found
        Returns True if clicked successfully, False if element not found
        Raises exceptions with detailed error message if something goes wrong
        """
        location = self.locate_element(element)
        if location:
            center_x = location[0] + location[2] // 2
            center_y = location[1] + location[3] // 2
            pyautogui.moveTo(center_x, center_y)
            pyautogui.click()
            return True
        return False


# Example UI elements definition
UI_ELEMENTS = {
    "equipment_button": UIElement(
        name="equipment_button",
        relative_x=0.87,
        relative_y=0.925,
        relative_width=0.1,
        relative_height=0.05,
        template_path="./Target_Images/zzz-equipment-button-1440p.png",
    ),
    "character_not_owned": UIElement(
        name="character_not_owned",
        relative_x=0.25,
        relative_y=0.4,
        relative_width=0.5,
        relative_height=0.2,
        template_path="./Target_Images/zzz-character-not-owned-1440p.png",
        confidence=0.9,
    ),
}
