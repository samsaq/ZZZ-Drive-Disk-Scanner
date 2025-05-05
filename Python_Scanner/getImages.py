import math
import os
import time
import sys
import PIL
import numpy as np
import pyautogui
import logging
import keyboard
from keyboard import press
from multiprocessing import Queue
from ui_elements import (
    ExistingScreenshotMatcher,
    UIElement,
    UIElementMatcher,
    UI_ELEMENTS,
)
from validMetadata import character_names
from typing import Optional


# screen resolutions supported enum
class ScreenResolution:
    RES_1440P = (2560, 1440)
    RES_1080P = (1920, 1080)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def setup_logging(log_file_path):
    logging.basicConfig(
        level=logging.DEBUG,
        filename=log_file_path,
        filemode="w",
        format="%(asctime)s - %(message)s",
    )


# Get the screen resolution
screenWidth, screenHeight = pyautogui.size()

# get the screen resolution enum
screenResolution = (
    ScreenResolution.RES_1440P if screenWidth == 2560 else ScreenResolution.RES_1080P
)


def switchToZZZ():
    """
    Switch to the Zenless Zone Zero game window
    """
    logging.info("Switching to ZenlessZoneZero")
    ZZZWindow = pyautogui.getWindowsWithTitle("ZenlessZoneZero")[0]
    if ZZZWindow.isActive == False:
        pyautogui.press(
            "altleft"
        )  # Somehow this is needed to switch to the window, Why though?
        ZZZWindow.activate()
    logging.info("Switched to ZenlessZoneZero")


def getToEquipmentScreen(
    queue: Queue, pageLoadTime, ui_matcher: Optional[UIElementMatcher] = None
):
    """
    Get to the equipment screen from the character screen

    Args:
        queue (Queue): Queue to send screenshots to for processing. Also used to signal the end of the image collection via error message
        pageLoadTime (float): The time to wait for the page to load
        ui_matcher (Optional[UIElementMatcher]): Optional UI element matcher to reuse. If None, a new one will be created.
    """
    logging.info("Getting to the equipment screen")

    # press c to get to the character screen
    press("c")
    logging.info("Pressed c for character screen")

    # wait for the character screen to load
    pyautogui.sleep(pageLoadTime)

    # Create or use the provided UI matcher
    if ui_matcher is None:
        ui_matcher = UIElementMatcher(screenWidth, screenHeight)

    # Use the pre-defined equipment button element
    equipment_button_element = UI_ELEMENTS["equipment_button"]

    # Try to locate and click the equipment button
    try:
        # Using the UI matcher to find and click the equipment button
        success = ui_matcher.click_element(equipment_button_element)

        if not success:
            logging.error("Equipment button not found")
            print("Equipment button not found")
            queue.put(
                "Error - failed to get to the equipment screen"
            )  # cause the process to end early
            sys.exit(1)

        logging.info("Successfully clicked equipment button")

    except Exception as e:
        logging.error(f"Error locating equipment button: {e}")
        logging.error(f"Current directory: {os.getcwd()}")
        queue.put(
            "Error - failed to get to the equipment screen"
        )  # cause the process to end early
        sys.exit(1)

    # wait for the equipment screen to load
    pyautogui.sleep(pageLoadTime)


def getXYOfCircleEdge(centerX, centerY, radius, angle):
    x = centerX + radius * math.cos(math.radians(angle))
    y = centerY + radius * math.sin(math.radians(angle))
    return x, y


def selectParition(diskNumber):
    diskradius = 0.25 * screenHeight
    diskCoreCenter = (0.75 * screenWidth, screenHeight / 2)

    # move the mouse to the center Y and the right side of the screen (75%)
    pyautogui.moveTo(diskCoreCenter)

    match diskNumber:
        case 1:
            # move the disk at 225 degrees (disk 1)
            x, y = getXYOfCircleEdge(
                diskCoreCenter[0], diskCoreCenter[1], diskradius, 225
            )
            pyautogui.moveTo(x, y)
        case 2:
            # move the disk at 180 degrees (disk 2)
            x, y = getXYOfCircleEdge(
                diskCoreCenter[0], diskCoreCenter[1], diskradius, 180
            )
            pyautogui.moveTo(x, y)
        case 3:
            # move the disk at 135 degrees (disk 3)
            x, y = getXYOfCircleEdge(
                diskCoreCenter[0], diskCoreCenter[1], diskradius, 135
            )
            pyautogui.moveTo(x, y)
        case 4:
            # move to the disk at 45 degrees (disk 4)
            x, y = getXYOfCircleEdge(
                diskCoreCenter[0], diskCoreCenter[1], diskradius, 45
            )
            pyautogui.moveTo(x, y)
        case 5:
            # move to the disk at 0 degrees (disk 5)
            x, y = getXYOfCircleEdge(
                diskCoreCenter[0], diskCoreCenter[1], diskradius, 0
            )
            pyautogui.moveTo(x, y)
        case 6:
            # move to the disk at 315 degrees (disk 6)
            x, y = getXYOfCircleEdge(
                diskCoreCenter[0], diskCoreCenter[1], diskradius, 315
            )
            pyautogui.moveTo(x, y)
    pyautogui.click()


def scanPartition(partitionNumber, queue: Queue, discScanTime):
    startPosition = (0.075 * screenWidth, 0.15 * screenHeight)  # start top left
    distanceBetwenColumns = 0.07 * screenWidth
    distanceBetwenRows = 0.158
    columnNumber = 4
    rowNumber = 5
    endOfDiskDrives = scanForEndOfDiskDrives(distanceBetwenRows)

    pyautogui.moveTo(startPosition)

    # loop through this row of disk drives
    # if the end of the disk drives is visible, we'll need to figure out which of the 4 columns is the last one
    # and only continue down the row until we reach the last column with a disk drive

    curRowStart = startPosition
    scanNumber = 1
    while True:  # Changed to infinite loop with explicit break
        scanNumber = scanRow(
            columnNumber,
            curRowStart,
            distanceBetwenColumns,
            partitionNumber,
            queue,
            discScanTime,
            scanNumber,
        )

        endOfDiskDrives = scanForEndOfDiskDrives(distanceBetwenRows)
        if endOfDiskDrives:
            break  # Exit after scanning the row where we found the end

        pyautogui.scroll(-1)

    # for loop for the remaining rows on the final page of disk drives
    for i in range(2, rowNumber + 1):
        curRowStart = (
            curRowStart[0],
            curRowStart[1] + distanceBetwenRows * screenHeight,
        )
        endOfDiskDrives = False
        scanNumber = scanRowUntilEndOfDiskDrives(
            columnNumber,
            i,
            curRowStart,
            distanceBetwenColumns,
            distanceBetwenRows,
            partitionNumber,
            queue,
            discScanTime,
            scanNumber,
        )


def scanRow(
    columns,
    rowStartPosition,
    distanceBetwenColumns,
    partitionNumber,
    queue: Queue,
    discScanTime,
    scanNumber=1,
):
    # pyautogui.click()
    for i in range(1, columns + 1):
        x = rowStartPosition[0] + (i - 1) * distanceBetwenColumns
        y = rowStartPosition[1]
        pyautogui.moveTo(x, y)
        pyautogui.click()
        scanNumber = scanDiskDrive(partitionNumber, queue, discScanTime, scanNumber)
    return scanNumber


# a version of scanRow that uses endOfDiskDrives to determine when to stop
# used on rows 2-5 on the final page of disk drives
def scanRowUntilEndOfDiskDrives(
    columns,
    rowNum,
    rowStartPosition,
    distanceBetwenColumns,
    distanceBetwenRows,
    partitionNumber,
    queue: Queue,
    discScanTime,
    scanNumber=1,
):
    # check the current row for the end of disk drives
    endOfDiskDrives = scanForEndOfDiskDrives(distanceBetwenRows, rowNum)
    # pyautogui.click()
    for i in range(1, columns + 1):
        x = rowStartPosition[0] + (i - 1) * distanceBetwenColumns
        y = rowStartPosition[1]
        # check if the x is past or at the end of the disk drives
        # if so, break the loop
        if endOfDiskDrives != False and x >= endOfDiskDrives[0]:
            break
        pyautogui.moveTo(x, y)
        pyautogui.click()
        scanNumber = scanDiskDrive(partitionNumber, queue, discScanTime, scanNumber)
    return scanNumber


def scanForEndOfDiskDrives(
    distanceBetwenRows, rowNumber=None, ui_matcher: Optional[UIElementMatcher] = None
):
    """
    Scan for the end of disk drives indicator

    Args:
        distanceBetwenRows: Distance between rows
        rowNumber: Row number to scan at (if None, scan entire screen)
        ui_matcher: Optional UI element matcher to reuse

    Returns:
        Location tuple if end of disk drives is found, False otherwise
    """
    # Create UI matcher if not provided
    if ui_matcher is None:
        ui_matcher = UIElementMatcher(screenWidth, screenHeight)

    # Get the UI elements from the predefined dictionary
    no_disk_icon_element = UI_ELEMENTS["no_disk_drive_icon"]
    no_disk_scrollbar_element = UI_ELEMENTS["no_disk_drive_scrollbar"]

    if rowNumber is None:
        # Create elements without region constraints for full screen search
        icon_element = UIElement(
            name=no_disk_icon_element.name,
            template_path=no_disk_icon_element.template_path,
            confidence=no_disk_icon_element.confidence,
        )

        scrollbar_element = UIElement(
            name=no_disk_scrollbar_element.name,
            template_path=no_disk_scrollbar_element.template_path,
            confidence=no_disk_scrollbar_element.confidence,
        )

        # Try to locate the icon
        try:
            endOfDiskDrivesIcon = ui_matcher.locate_element(icon_element)
            if endOfDiskDrivesIcon is None:
                endOfDiskDrivesIcon = False
        except:
            endOfDiskDrivesIcon = False

        # Try to locate the scrollbar
        try:
            endOfDiskDrivesScrollbar = ui_matcher.locate_element(scrollbar_element)
            if endOfDiskDrivesScrollbar is None:
                endOfDiskDrivesScrollbar = False
        except:
            endOfDiskDrivesScrollbar = False

        # Return false if both the icon and the scrollbar are not visible
        if endOfDiskDrivesIcon == False and endOfDiskDrivesScrollbar == False:
            return False
        # Else, return the one that is not false
        if endOfDiskDrivesIcon != False:
            return endOfDiskDrivesIcon
        return endOfDiskDrivesScrollbar

    # For specific row number search
    rowModifier = 0.1 + (distanceBetwenRows * (rowNumber - 1))

    # Create a region-constrained element for the specific row
    region_constrained_icon = UIElement(
        name=no_disk_icon_element.name,
        template_path=no_disk_icon_element.template_path,
        relative_x=0.04,
        relative_y=rowModifier,
        relative_width=0.275,
        relative_height=0.125,
        confidence=no_disk_icon_element.confidence,
    )

    # Check if the end of the disk drives is visible in the specific row
    try:
        endOfDiskDrives = ui_matcher.locate_element(region_constrained_icon)
        if endOfDiskDrives is None:
            endOfDiskDrives = False
    except:
        endOfDiskDrives = False

    return endOfDiskDrives


def testSnapshot(distanceBetwenRows, rowNumber):
    rowModifier = 0.1 + (distanceBetwenRows * (rowNumber - 1))
    screenshot = pyautogui.screenshot(
        region=(
            int(0.04 * screenWidth),  # left
            int(rowModifier * screenHeight),  # top
            int(0.275 * screenWidth),  # width
            int(0.125 * screenHeight),  # height
        )
    )
    screenshot.save("DiskDriveImages/test" + str(rowNumber) + ".png")


def scanDiskDrive(paritionNumber, queue: Queue, discScanTime, scanNumber=1):
    # get a screenshot of the disk drive after waiting for it to load, save it to a file
    pyautogui.sleep(discScanTime)
    screenshot = pyautogui.screenshot(
        region=(
            int(0.31 * screenWidth),  # left
            int(0.1 * screenHeight),  # top
            int(0.2 * screenWidth),  # width
            int(0.55 * screenHeight),  # height
        )
    )
    # save with partition number and scan number
    save_path = (
        "./scan_input/Partition"
        + str(paritionNumber)
        + "Scan"
        + str(scanNumber)
        + ".png"
    )
    screenshot.save(save_path)
    # put the image path in the queue
    queue.put(save_path)
    return scanNumber + 1


### WEngine specific functions ###


def switchToWEngineBackpack(pageLoadTime, pressTime=0.15):
    """
    Switch to the WEngine backpack view from open world traversal (no menu)

    Args:
        pageLoadTime (float): The time to wait for the page to load
        pressTime (float, optional): The time to hold the keypress. Defaults to 0.15.
    """
    logging.info("Opening the backpack")
    keyboard.press("b")
    pyautogui.sleep(pageLoadTime)
    logging.info("Arrived at WEngine backpack view")


def switchToWEngineBackpackFromDisks(pageLoadTime, pressTime=0.15):
    """
    Switch to the WEngine backpack view from the disk drive view (within character screen, with a partition selected)

    Args:
        pageLoadTime (float): The time to wait for the page to load
        pressTime (float, optional): The time to hold the keypress. Defaults to 0.15.
    """
    logging.info("Switching to the WEngine tab in the Backpack")

    logging.info("Exiting from the disk drive view")
    keyboard.press("esc")
    pyautogui.sleep(pageLoadTime)

    logging.info("Exiting parition view")
    keyboard.press("esc")
    pyautogui.sleep(pageLoadTime)

    logging.info("Exiting character screen")
    keyboard.press("esc")
    pyautogui.sleep(pageLoadTime)

    logging.info("Entering Backpack (default tab is WEngine)")
    keyboard.press("b")
    pyautogui.sleep(pageLoadTime)

    logging.info("Arrived at WEngine backpack view")


def getWEngine(queue: Queue = None, outputFile="TestImages/test.png"):
    """
    Screenshot the WEngine item and save it to a file

    Args:
        outputFile (str, optional): The path to save the screenshot to. Defaults to "TestImages/test.png". Will create the directory if it doesn't exist.
    """
    targetDir = os.path.dirname(outputFile)
    if targetDir and not os.path.exists(targetDir):
        os.makedirs(targetDir, exist_ok=True)
    screenshot = pyautogui.screenshot(
        region=(
            int(0.73 * screenWidth),  # left
            int(0.18 * screenHeight),  # top
            int(0.23 * screenWidth),  # width
            int(0.175 * screenHeight),  # height
        )
    )
    screenshot.save(outputFile)
    if queue:
        queue.put(outputFile)


# scan the WEngine tab in the backpack
def getWEngineTab(
    queue: Queue = None,
    scanTime: float = 0.25,
    save_folder: str = "scan_input",
    ui_matcher: Optional[UIElementMatcher] = None,
):
    """
    Scans the WEngine tab in the backpack, either sending screenshots to a queue or saving to a folder for examination.

    Args:
        queue (Queue, optional): Queue to send screenshots to for processing. Defaults to None.
        scanTime (float, optional): Time to wait between scans. Defaults to 0.25.
        save_folder (str, optional): Folder to save screenshots to. Defaults to "scan_input". Will create the directory if it doesn't exist.
        ui_matcher (UIElementMatcher, optional): UI element matcher to use. If None, a new one will be created.

    Returns:
        int: The number of items scanned
        None: If an error occurs

    Raises:
        ValueError: If neither a queue nor save_folder is provided
    """
    if save_folder and not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Create UI matcher if not provided
    if ui_matcher is None:
        ui_matcher = UIElementMatcher(screenWidth, screenHeight)

    # Get the UI elements from the predefined dictionary
    inventory_end_scrollbar = UI_ELEMENTS["inventory_end_scrollbar"]
    no_inventory_item_icon = UI_ELEMENTS["no_inventory_item_icon"]

    startPosition = (0.13 * screenWidth, 0.27 * screenHeight)  # start top left
    distanceBetweenColumns = 0.075 * screenWidth
    distanceBetweenRows = 0.165 * screenHeight
    columnNumber = 8  # vertical columns in the backpack
    rowNumber = 5  # rows per page

    pyautogui.moveTo(startPosition)

    curRowStart = startPosition
    scanNumber = 1

    while True:  # Scroll through pages until we hit the end
        # Scan current row
        for col in range(columnNumber):
            currentPos = (
                curRowStart[0] + (col * distanceBetweenColumns),
                curRowStart[1],
            )
            pyautogui.moveTo(currentPos)
            pyautogui.click()
            pyautogui.sleep(scanTime)

            # Take screenshot of the WEngine item
            if save_folder:
                getWEngine(
                    queue, os.path.join(save_folder, f"wengine_{scanNumber}.png")
                )
            else:
                getWEngine(f"TestImages/temp_{scanNumber}.png")
                os.remove(f"TestImages/temp_{scanNumber}.png")

            scanNumber += 1

        # Check if we've reached the end of the inventory
        try:
            # Create a full-screen search element to look for the end scrollbar
            end_scrollbar_element = UIElement(
                name=inventory_end_scrollbar.name,
                template_path=inventory_end_scrollbar.template_path,
                confidence=inventory_end_scrollbar.confidence,
            )

            # Check if end of inventory is visible
            endOfInventory = ui_matcher.locate_element(end_scrollbar_element)
            if endOfInventory:
                break
            else:  # If we don't find the end of inventory, continue (previously locateOnScreen would raise an image not found error)
                pass
        except Exception as e:
            print(f"Error checking for end of inventory: {e}")
            pass

        # Scroll down for next row
        pyautogui.scroll(-1)
        pyautogui.sleep(scanTime)

    # Scan remaining rows on the final page
    for row in range(1, rowNumber - 1):
        curRowStart = (
            startPosition[0],
            startPosition[1] + (row) * distanceBetweenRows,
        )

        # For each column in the row
        for col in range(columnNumber):
            currentPos = (
                curRowStart[0] + (col * distanceBetweenColumns),
                curRowStart[1],
            )

            # Check for empty slot
            try:
                next_slot_region = (
                    int(currentPos[0] - 0.08 * screenWidth),
                    int(currentPos[1] - 0.08 * screenHeight),
                    int(0.16 * screenWidth),
                    int(0.16 * screenHeight),
                )
                region_screenshot = pyautogui.screenshot(region=next_slot_region)
                ui_matcherExisting = ExistingScreenshotMatcher(
                    screenshot=region_screenshot,
                    screen_width=screenWidth,
                    screen_height=screenHeight,
                )
                emptySlot = ui_matcherExisting.locate_element_in_screenshot(
                    no_inventory_item_icon
                )

                # Check if empty slot is found
                if emptySlot:
                    return (
                        scanNumber - 1
                    )  # Exit  if we find an empty slot since we've reached the end of the inventory
                else:  # If we don't find an empty slot, continue (previously locateOnScreen would raise an image not found error)
                    pass
            except Exception as e:
                print(f"Error checking for empty slot: {e}")
                pass

            # Take screenshot if not empty
            pyautogui.moveTo(currentPos)
            pyautogui.click()
            pyautogui.sleep(scanTime)

            if save_folder:
                getWEngine(
                    queue, os.path.join(save_folder, f"wengine_{scanNumber}.png")
                )
            else:
                getWEngine(f"TestImages/temp_{scanNumber}.png")
                with open(f"TestImages/temp_{scanNumber}.png", "rb") as f:
                    queue.put((scanNumber, f.read()))
                os.remove(f"TestImages/temp_{scanNumber}.png")

            scanNumber += 1

    return scanNumber - 1  # Return total number of items scanned


### End of WEngine specific functions ###


### Character Scanning Functions ###
def navigate_character_details(target: str = "Base Stats"):
    """
    Navigate to a specific section of the character details page.

    Args:
        target (str): The section to navigate to.
                     Valid options: 'Base Stats', 'Skills', 'Equipment', 'Cinema'
    """
    if target not in ["Base Stats", "Skills", "Equipment", "Cinema"]:
        raise ValueError(
            "Invalid target. Must be one of: 'Base Stats', 'Skills', 'Equipment', 'Cinema'"
        )

    targetPos = None
    if target == "Base Stats":
        targetPos = (0.6 * screenWidth, 0.925 * screenHeight)
    elif target == "Skills":
        targetPos = (0.725 * screenWidth, 0.925 * screenHeight)
    elif target == "Equipment":
        targetPos = (0.87 * screenWidth, 0.925 * screenHeight)
    elif target == "Cinema":
        targetPos = (0.085 * screenWidth, 0.875 * screenHeight)

    pyautogui.moveTo(targetPos)
    pyautogui.click()


def scanDiskDriveCharacter(
    paritionNumber: int,
    queue: Queue,
    discScanTime: float,
    outputFolder: str = "scan_input",
    characterNumber: int = 0,
):
    """
    Scan the disk drive for the given partition number, and save the screenshot to a file

    Args:
        paritionNumber (int): The partition number to scan
        queue (Queue): The queue to put the image path in
        discScanTime (float): The time to wait for the disk drive to load
        outputFolder (str, optional): The folder to save the screenshot in, defaults to "scan_input"
        characterNumber (int, optional): The character number to save the screenshot as, defaults to 0

    Returns:
        cv2.Mat: The screenshot of the disk drive
    """
    # get a screenshot of the disk drive after waiting for it to load, save it to a file
    pyautogui.sleep(discScanTime)
    screenshot = pyautogui.screenshot(
        region=(
            int(0.31 * screenWidth),  # left
            int(0.1 * screenHeight),  # top
            int(0.2 * screenWidth),  # width
            int(0.55 * screenHeight),  # height
        )
    )
    # save with partition number and scan number
    save_path = f"./{outputFolder}/character_{characterNumber}_partition_{paritionNumber}_disk_scan.png"
    screenshot.save(save_path)
    # put the image path in the queue
    if queue:
        queue.put(save_path)
    return screenshot


def is_character_owned(
    ui_matcher: UIElementMatcher = None,
    scanTime: float = 0.25,
    pageLoadTime: float = 0.5,
) -> bool:
    """
    Check if the current character is owned by looking for the preview mode popup.
    Run only after the wish reel icon is clicked.

    Args:
        ui_matcher (UIElementMatcher, optional): UI element matcher instance to use, defaults to None and will create one
        scanTime (float, optional): Time to wait after clicking the wish reel icon, defaults to 0.25
        pageLoadTime (float, optional): Time to wait after pressing ESC, defaults to 0.5

    Returns:
        bool: True if character is owned, False if not owned

    Used In:
        get_character_snapshots()
    """

    # click the wish reel icon to display the promotion preview popup
    wishReelIconPosition = (0.92 * screenWidth, 0.2 * screenHeight)
    popExitPosition = (0.805 * screenWidth, 0.2 * screenHeight)
    pyautogui.moveTo(wishReelIconPosition)
    pyautogui.click()
    time.sleep(scanTime)

    # Create matcher if not provided
    if ui_matcher is None:
        screen_width, screen_height = pyautogui.size()
        ui_matcher = UIElementMatcher(screen_width, screen_height)

    try:
        # Check if the character not owned element is visible
        is_found = (
            ui_matcher.locate_element(UI_ELEMENTS["character_not_owned"]) is not None
        )

        # If we found the element, character is not owned
        time.sleep(
            pageLoadTime / 2
        )  # there's a delay before the close button becomes active after opening the popup
        pyautogui.moveTo(popExitPosition)
        pyautogui.click()
        time.sleep(pageLoadTime)
        print("Agent is owned: ", not is_found)
        return not is_found
    except Exception as e:
        # Handle any unexpected errors
        print(f"Error checking if agent is owned: {e}")
        pyautogui.moveTo(popExitPosition)
        pyautogui.click()
        time.sleep(pageLoadTime)
        return False


def get_character_disks_equipped(
    screenshot: PIL.Image.Image,
    target_folder: str = "Target_Images",
) -> list[bool]:
    """
    Get the disks equipped of the current character from an image of the equipment screen
    Note: This function doesn't take a pased in ui_matcher because it creates its own per screenshot

    Args:
        screenshot (PIL.Image.Image): The screenshot of the equipment screen to check from pyautogui.screenshot()
        target_folder (str, optional): The folder containing the reference target images, defaults to "Target_Images"

    Returns:
        list[bool]: A list of size 6 (which disks are equipped, each is true if equipped)

    Usage:
        Used in get_character_equipment_status() to determine what disks are available to scan
    """

    # create the matcher for our screenshot
    ui_matcher = ExistingScreenshotMatcher(screenshot, screenWidth, screenHeight)
    disk_targets = [
        UIElement(
            name=f"disk_{i}_empty",
            template_path=f"./{target_folder}/zzz-character-equipment-no-disk-{i}-1440p.png",
            confidence=0.9,
        )
        for i in range(1, 7)
    ]

    # For each disk_target, check if it matches in the screenshot
    disks_equipped = []
    for element in disk_targets:
        try:
            # Check if the empty disk marker is found
            location = ui_matcher.locate_element_in_screenshot(element)
            # If the empty disk template is found, the disk is NOT equipped
            if location is not None:
                disks_equipped.append(False)
            else:
                disks_equipped.append(True)
        except Exception as e:
            print(
                f"Warning: Error processing disk template {element.template_path}: {e}"
            )
            disks_equipped.append(
                False
            )  # Assume unequipped if template processing fails

    return disks_equipped


def is_character_wengine_equipped(
    waitTime: float = 0.5,
) -> bool:
    """
    Check if the character has a wengine equipped by clicking the wengine position and checking if the remove button is visible

    Args:
        waitTime (float, optional): The time to wait for the wengine to load, defaults to 0.5
    Returns:
        bool: True if the wengine is equipped, False otherwise

    Used In:
        get_character_equipment_status()
    """
    # Create UI matcher with current screen dimensions
    ui_matcher = UIElementMatcher(screenWidth, screenHeight)

    # Use the pre-defined wengine_remove_button element
    remove_button_element = UI_ELEMENTS["wengine_remove_button"]

    # Define the wengine position to click
    wengine_position = (0.725 * screenWidth, 0.5 * screenHeight)

    # Click on the wengine position
    pyautogui.moveTo(wengine_position)
    pyautogui.click()
    time.sleep(waitTime)
    # if we can see the remove button, than a wengine is equipped to be removed in the first place
    try:
        # Use the UI element matcher to find the remove button
        location = ui_matcher.locate_element(remove_button_element)
        is_equipped = location is not None
    except Exception as e:
        print(f"Error locating wengine remove button: {e}")
        is_equipped = False
    finally:
        # Always press Escape to close any open dialogs
        keyboard.press("esc")
        time.sleep(waitTime)

    return is_equipped


def get_character_equipment_status(
    waitTime: float = 0.5,
) -> dict:
    """
    Get the equipment status of the current character - do they have all disks equipped, is the wengine equipped, etc.
    Triggered when we enter the character's equipment screen

    Args:
        waitTime (float, optional): The time to wait for the wengine to load, defaults to 0.5

    Returns:
        dict: A dictionary containing the equipment status of the current character in the form:
        {
            "all_disks_equipped": bool,
            "wengine_equipped": bool,
            "disks_equipped": list[bool] of size 6 (which disks are equipped, each is true if equipped)
        }

    Usage:
        Used in get_character_snapshots() to determine what disks to scan and if the wengine needs to be scanned (aka if its equipped, we scan it)
    """
    disk_wheel_region = (
        int(0.5 * screenWidth),  # left
        int(0.15 * screenHeight),  # top
        int(0.45 * screenWidth),  # width
        int(0.7 * screenHeight),  # height
    )

    screenshot = pyautogui.screenshot(region=disk_wheel_region)
    disks_equipped = get_character_disks_equipped(screenshot)
    all_disks_equipped = all(disks_equipped)
    wengine_equipped = is_character_wengine_equipped(waitTime=waitTime)
    return {
        "all_disks_equipped": all_disks_equipped,
        "wengine_equipped": wengine_equipped,
        "disks_equipped": disks_equipped,
    }


# function to get the various screenshots for a character for later processing
def get_character_snapshots(
    agent_num: int,
    queue: Queue = None,
    ui_matcher: UIElementMatcher = None,
    output_folder: str = "scan_input",
    pageLoadTime: float = 2,
    scanTime: float = 0.25,
    getEquipment: bool = True,
):
    """
    Get the various screenshots for a character for later processing

    Args:
        agent_num (int): The number of the character to get the snapshots for
        queue (Queue, optional): The queue to put the image paths and status updates into for the image scanner process, REQUIRED if we want to scan the disks
        ui_matcher (UIElementMatcher, optional): The UI element matcher to use, defaults to None and will create one
        output_folder (str, optional): The folder to save the screenshots in, defaults to "scan_input"
        pageLoadTime (float, optional): The time to wait for the page to load, defaults to 2
        scanTime (float, optional): The time to wait for the disk drive to load, defaults to 0.25
        getEquipment (bool, optional): Whether to get the equipment status of the character, defaults to True
    """
    # create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    exitButtonPosition = (0.06 * screenWidth, 0.05 * screenHeight)

    if ui_matcher is None:
        screen_width, screen_height = pyautogui.size()
        ui_matcher = UIElementMatcher(screen_width, screen_height)

    if not is_character_owned(
        ui_matcher=ui_matcher, scanTime=scanTime, pageLoadTime=pageLoadTime
    ):
        return True
    time.sleep(pageLoadTime)

    name_region = (
        int(0.54 * screenWidth),
        int(0.255 * screenHeight),
        int(0.24 * screenWidth),
        int(0.08 * screenHeight),
    )

    level_region = (
        int(0.54 * screenWidth),
        int(0.4 * screenHeight),
        int(0.18 * screenWidth),
        int(0.08 * screenHeight),
    )

    skill_region = (
        int(0.375 * screenWidth),
        int(0.145 * screenHeight),
        int(0.1 * screenWidth),
        int(0.06 * screenHeight),
    )

    weapon_region = (
        int(0.31 * screenWidth),  # left
        int(0.1 * screenHeight),  # top
        int(0.2 * screenWidth),  # width
        int(0.2 * screenHeight),  # height
    )

    # take a snapshot of the character name
    screenshot = pyautogui.screenshot(
        region=name_region,
    )
    screenshot.save(f"./{output_folder}/agent_{agent_num}_name.png")
    if queue:
        queue.put(f"./{output_folder}/agent_{agent_num}_name.png")

    # character level and maxlevel snapshot
    screenshot = pyautogui.screenshot(region=level_region)
    screenshot.save(f"./{output_folder}/agent_{agent_num}_level.png")
    if queue:
        queue.put(f"./{output_folder}/agent_{agent_num}_level.png")

    # handle skills
    navigate_character_details("Skills")
    skill_start_pos = (0.53 * screenWidth, 0.65 * screenHeight)
    horz_skill_dist = 0.09 * screenWidth
    vert_dist_to_core_skill = 0.3 * screenHeight
    skill_names = [
        "basic_attack",
        "dodge",
        "assist",
        "special_attack",
        "chain_attack",
        "core",
    ]
    time.sleep(pageLoadTime)  # this takes a bit longer to load typically
    pyautogui.moveTo(skill_start_pos)
    pyautogui.click()
    time.sleep(scanTime)
    screenshot = pyautogui.screenshot(region=skill_region)
    screenshot.save(f"./{output_folder}/agent_{agent_num}_skill_{skill_names[0]}.png")
    if queue:
        queue.put(f"./{output_folder}/agent_{agent_num}_skill_{skill_names[0]}.png")
    time.sleep(scanTime)

    for i in range(4):
        pyautogui.moveRel(horz_skill_dist, 0)
        pyautogui.click()
        time.sleep(scanTime)
        screenshot = pyautogui.screenshot(region=skill_region)
        screenshot.save(
            f"./{output_folder}/agent_{agent_num}_skill_{skill_names[i+1]}.png"
        )
        if queue:
            queue.put(
                f"./{output_folder}/agent_{agent_num}_skill_{skill_names[i+1]}.png"
            )
    pyautogui.moveRel(0, -vert_dist_to_core_skill)
    pyautogui.click()
    time.sleep(scanTime)
    screenshot = pyautogui.screenshot(region=skill_region)
    screenshot.save(f"./{output_folder}/agent_{agent_num}_skill_{skill_names[5]}.png")
    if queue:
        queue.put(f"./{output_folder}/agent_{agent_num}_skill_{skill_names[5]}.png")
    pyautogui.moveTo(exitButtonPosition)
    pyautogui.click()
    time.sleep(scanTime)

    # grab the cinema screenshot
    navigate_character_details("Cinema")
    pyautogui.sleep(
        pageLoadTime
    )  # this specific screen has a rather slow transition animation
    screenshot = (
        pyautogui.screenshot()
    )  # we just need the whole screen, since we're looking for mindscape icons within most of it anyways
    screenshot.save(f"./{output_folder}/agent_{agent_num}_cinema.png")
    if queue:
        queue.put(f"./{output_folder}/agent_{agent_num}_cinema.png")
    pyautogui.moveTo(exitButtonPosition)
    pyautogui.click()
    time.sleep(scanTime)

    # Get a snapshot of all character equipment that is in use
    if getEquipment:
        navigate_character_details("Equipment")
        time.sleep(scanTime)

        # check what equipment is equipped
        equipment_status = get_character_equipment_status(scanTime * 2)
        time.sleep(scanTime)

        # Format the equipment status for the queue
        status_parts = [f"weapon_{equipment_status['wengine_equipped']}"]
        for i, disk_equipped in enumerate(equipment_status["disks_equipped"], 1):
            status_parts.append(f"disk{i}_{disk_equipped}")

        status_string = f"status: {', '.join(status_parts)}"

        # Send the status through the queue to the scanner
        if queue:
            queue.put(status_string)

        # Scan only equipped disks
        for disk_num, is_equipped in enumerate(equipment_status["disks_equipped"], 1):
            if is_equipped:
                selectParition(disk_num)
                scanDiskDriveCharacter(
                    disk_num, queue, scanTime, output_folder, agent_num
                )
                time.sleep(scanTime)

        pyautogui.moveTo(exitButtonPosition)
        pyautogui.click()
        time.sleep(scanTime)

        # Scan the weapon only if it's equipped
        if equipment_status["wengine_equipped"]:
            # Scan the agent's weapon
            weapon_position = (0.725 * screenWidth, 0.5 * screenHeight)
            pyautogui.moveTo(weapon_position)
            pyautogui.click()
            time.sleep(pageLoadTime)  # This takes a bit longer
            screenshot = pyautogui.screenshot(region=weapon_region)
            screenshot.save(f"./{output_folder}/agent_{agent_num}_weapon.png")
            if queue:
                queue.put(f"./{output_folder}/agent_{agent_num}_weapon.png")
            pyautogui.moveTo(exitButtonPosition)
            pyautogui.click()
            time.sleep(scanTime)


# intended to be a main function of sorts to be called in getImages.py for character image collection
def get_characters(
    pageLoadTime: float = 2,
    scanTime: float = 0.25,
    queue: Queue = None,
    ui_matcher: UIElementMatcher = None,
):
    """
    Get the character images for all characters in the character list

    Used In:
        getImages.py's getImages() function
    """
    num_characters = len(character_names)
    characters_in_final_row = 7
    startPosition = (0.57 * screenWidth, 0.045 * screenHeight)
    distance_between_characters = 0.0525 * screenWidth

    if ui_matcher is None:
        screen_width, screen_height = pyautogui.size()
        ui_matcher = UIElementMatcher(screen_width, screen_height)

    # click through the first row using offset selection
    cur_character_position = startPosition
    agents_scanned = 0
    end_of_owned_characters = False

    for i in range(characters_in_final_row):
        pyautogui.moveTo(cur_character_position)
        pyautogui.click()
        time.sleep(scanTime)
        navigate_character_details("Base Stats")
        time.sleep(scanTime)
        end_of_owned_characters = get_character_snapshots(
            agent_num=agents_scanned,
            queue=queue,
            pageLoadTime=pageLoadTime,
            scanTime=scanTime,
            ui_matcher=ui_matcher,
        )
        if end_of_owned_characters:
            break
        agents_scanned += 1
        # move to the next character position in the row
        cur_character_position = (
            cur_character_position[0] + distance_between_characters,
            cur_character_position[1],
        )

    # Save final position for scrolling through remaining characters
    final_position = (
        startPosition[0] + (characters_in_final_row - 1) * distance_between_characters,
        startPosition[1],
    )

    if not end_of_owned_characters:
        # click through all the scrollable characters (after the first row)
        for i in range(num_characters - characters_in_final_row):
            pyautogui.moveTo(final_position)
            pyautogui.scroll(-1)  # move to next character
            time.sleep(scanTime)
            pyautogui.click()
            time.sleep(scanTime)
            navigate_character_details("Base Stats")
            time.sleep(scanTime)
            end_of_owned_characters = get_character_snapshots(
                agent_num=agents_scanned,
                queue=queue,
                pageLoadTime=pageLoadTime,
                scanTime=scanTime,
                ui_matcher=ui_matcher,
            )
            if end_of_owned_characters:
                break
            agents_scanned += 1


### End of Character Scanning Functions ###


# the main function that will be called to get the images by the orchestrator
def getImages(
    queue: Queue,
    pageLoadTime,
    discScanTime,
    scantype,
    ui_matcher: UIElementMatcher = None,
):
    """
    Get the images for the specified type of scan

    Args:
        queue (Queue): Queue to send screenshots to for processing. Also used to signal the end and start of the image collection of each category & by error
        pageLoadTime (float): The time to wait for the page to load
        discScanTime (float): The time to wait between scans of the disk drives
        scantype (str): The type of scan to perform. Can be "all", "wengine", "character", "disk"
    """
    log_file_path = resource_path("scan_output/snapshotlog.txt")
    setup_logging(log_file_path)
    if ui_matcher is None:
        screen_width, screen_height = pyautogui.size()
        ui_matcher = UIElementMatcher(screen_width, screen_height)
    switchToZZZ()
    if scantype == "Disk":
        getToEquipmentScreen(queue, pageLoadTime, ui_matcher)
        queue.put("Disk")
        # go through the 6 partitions
        for i in range(1, 7):
            selectParition(i)
            scanPartition(i, queue, discScanTime)
    elif scantype == "WEngine":
        switchToWEngineBackpack(pageLoadTime)
        queue.put("WEngine")
        getWEngineTab(queue=queue, scanTime=discScanTime, ui_matcher=ui_matcher)
    elif scantype == "Character":
        getToEquipmentScreen(queue, pageLoadTime, ui_matcher)
        queue.put("Character")
        get_characters(pageLoadTime, discScanTime, queue, ui_matcher)
    elif scantype == "All":
        # get the disk data
        getToEquipmentScreen(queue, pageLoadTime, ui_matcher)
        queue.put("Disk")
        # go through the 6 partitions
        for i in range(1, 7):
            selectParition(i)
            scanPartition(i, queue, discScanTime)
        # get the wengine data
        queue.put("WEngine")
        switchToWEngineBackpackFromDisks(pageLoadTime)
        getWEngineTab(queue=queue, scanTime=discScanTime, ui_matcher=ui_matcher)
        # get the character data
        queue.put("Character")
        get_characters(pageLoadTime, discScanTime, queue, ui_matcher)
    # put a message in the queue to signal the end of the image collection
    queue.put("Done")


# a test function to run the getImages function
if __name__ == "__main__":

    # set the working directory to the directory of the script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create scan_output directory if it doesn't exist
    os.makedirs("scan_output", exist_ok=True)

    # remove the snapshotlog.txt file if it exists
    if os.path.exists("scan_output/snapshotlog.txt"):
        os.remove("scan_output/snapshotlog.txt")
    # now create it again as an empty file
    with open("scan_output/snapshotlog.txt", "w"):
        pass
    getImages(Queue(), 2, 0.25, "All")
