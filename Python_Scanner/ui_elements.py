import cv2
import numpy as np
import pyautogui
from typing import Any, Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class UIElement:
    """Represents a UI element with its relative position and size"""

    name: str
    template_path: str  # path to the template image (using 1440p as base)
    relative_x: Optional[float] = None  # x position as percentage of screen width
    relative_y: Optional[float] = None  # y position as percentage of screen height
    relative_width: Optional[float] = None  # width as percentage of screen width
    relative_height: Optional[float] = None  # height as percentage of screen height
    confidence: float = 0.6  # optional: minimum confidence threshold


class UIElementMatcher:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self._template_cache = {}

    def _get_absolute_region(
        self, element: UIElement
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Convert relative coordinates to absolute screen coordinates
        Returns None if any positioning information is missing
        """
        # Check if all positioning elements are provided
        if None in (
            element.relative_x,
            element.relative_y,
            element.relative_width,
            element.relative_height,
        ):
            return None

        return (
            int(element.relative_x * self.screen_width),
            int(element.relative_y * self.screen_height),
            int(element.relative_width * self.screen_width),
            int(element.relative_height * self.screen_height),
        )

    def _load_and_resize_template(self, element: UIElement) -> np.ndarray:
        """
        Load template image and resize it proportionally based on current resolution
        Base templates are assumed to be created at 1440p resolution
        """
        BASE_RESOLUTION_HEIGHT = 1440  # Base resolution for templates

        if element.template_path not in self._template_cache:
            template = cv2.imread(element.template_path)
            if template is None:
                error_msg = f"Could not load template image: {element.template_path}"
                raise ValueError(error_msg)

            # Calculate scale factor based on current screen height vs base resolution
            scale_factor = self.screen_height / BASE_RESOLUTION_HEIGHT

            # Get original template dimensions
            original_height, original_width = template.shape[:2]

            # Calculate new dimensions
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            # Resize template based on scale factor
            template_resized = cv2.resize(
                template, (new_width, new_height), interpolation=cv2.INTER_AREA
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
            # Get the region to search in (or None to search the entire screen)
            region = self._get_absolute_region(element)

            # Take screenshot of the region or entire screen
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()

            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Get the properly scaled template
            template = self._load_and_resize_template(element)

            # Perform template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= element.confidence:
                # If using a region, adjust coordinates to global screen position
                if region:
                    x = region[0] + max_loc[0]
                    y = region[1] + max_loc[1]
                else:
                    x = max_loc[0]
                    y = max_loc[1]
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


class ExistingScreenshotMatcher(UIElementMatcher):
    """
    A specialized UIElementMatcher that works with an existing screenshot
    instead of taking new screenshots

    Usage:
        Used in get_character_equipment_status() to determine what disks are available to scan off of one image of the whole disk wheel region
    """

    def __init__(self, screenshot: Any, screen_width: int, screen_height: int):
        """
        Initialize with an existing screenshot

        Args:
            screenshot: The screenshot image (PIL.Image or numpy array)
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        super().__init__(screen_width, screen_height)
        # Convert screenshot to cv2 format if it's not already
        if hasattr(screenshot, "convert"):  # Check if it's a PIL Image
            self.screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        else:  # Assume it's already a numpy array
            self.screenshot_cv = screenshot

    def locate_element_in_screenshot(
        self, element: UIElement
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Locate an element in the existing screenshot

        Args:
            element(UIElement): The UI element to find

        Returns:
            Tuple of (left, top, width, height) if found, None otherwise
        """
        try:
            # Get the properly scaled template
            template = self._load_and_resize_template(element)

            # Perform template matching on the existing screenshot
            result = cv2.matchTemplate(
                self.screenshot_cv, template, cv2.TM_CCOEFF_NORMED
            )
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= element.confidence:
                x, y = max_loc
                return (x, y, template.shape[1], template.shape[0])

            return None

        except Exception as e:
            error_msg = f"Error locating element {element.name} in screenshot: {e}"
            raise Exception(error_msg) from e

    def locate_all_elements_in_screenshot(
        self, element: UIElement, threshold: Optional[float] = None
    ) -> List[Tuple[int, int, int, int]]:
        """
        Locate all occurrences of an element in the existing screenshot

        Args:
            element: The UI element to find
            threshold: Optional confidence threshold, defaults to element.confidence

        Returns:
            List of tuples (left, top, width, height) for all matches
        """
        try:
            # Use either provided threshold or element's confidence
            if threshold is None:
                threshold = element.confidence

            # Get the properly scaled template
            template = self._load_and_resize_template(element)

            # Perform template matching on the existing screenshot
            result = cv2.matchTemplate(
                self.screenshot_cv, template, cv2.TM_CCOEFF_NORMED
            )

            # Find all locations where match exceeds threshold
            locations = np.where(result >= threshold)

            # Combine the results into a list of (x, y, width, height) tuples
            matches = []
            template_w, template_h = template.shape[1], template.shape[0]

            for pt in zip(*locations[::-1]):  # Reverse to get (x, y) instead of (y, x)
                matches.append((pt[0], pt[1], template_w, template_h))

            return matches

        except Exception as e:
            error_msg = f"Error locating all elements {element.name} in screenshot: {e}"
            raise Exception(error_msg) from e


UI_ELEMENTS = {
    "equipment_button": UIElement(
        name="equipment_button",
        relative_x=0.565,
        relative_y=0.8725,
        relative_width=0.125,
        relative_height=0.075,
        template_path="./Target_Images/zzz-equipment-button.png",  # this one doesn't have a suffix for 1440p
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
    "wengine_remove_button": UIElement(
        name="wengine_remove_button",
        relative_x=0.7,
        relative_y=0.91,
        relative_width=0.15,
        relative_height=0.075,
        template_path="./Target_Images/zzz-character-equipment-wengine-remove-button-1440p.png",
    ),
    "no_disk_drive_icon": UIElement(
        name="no_disk_drive_icon",
        template_path="./Target_Images/zzz-no-disk-drive-icon.png",  # this one doesn't have a suffix for 1440p
        confidence=0.8,
    ),
    "no_disk_drive_scrollbar": UIElement(
        name="no_disk_drive_scrollbar",
        template_path="./Target_Images/zzz-no-disk-drive-scrollbar.png",  # this one doesn't have a suffix for 1440p
        confidence=0.9,
    ),
    "inventory_end_scrollbar": UIElement(
        name="inventory_end_scrollbar",
        template_path="./Target_Images/zzz-inventory-end-scrollbar-1440p.png",
        confidence=0.9,
    ),
    "no_inventory_item_icon": UIElement(
        name="no_inventory_item_icon",
        template_path="./Target_Images/zzz-no-inventory-item-icon-1440p.png",
        confidence=0.9,
    ),
}
