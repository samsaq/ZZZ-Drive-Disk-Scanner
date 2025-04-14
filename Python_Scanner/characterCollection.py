import os
import time
import re
import PIL
import cv2
import pyautogui
import pytesseract
import keyboard
from validMetadata import character_names, valid_weapon_names
from imageScanner import (
    extract_metadata,
    correct_metadata,
    process_wengine_text,
    validate_disk_drive,
)
from preprocess_images import preprocess_image
from multiprocessing import Queue
from strsimpy import Cosine
from getImages import selectParition
import numpy as np

# Seperate file to hold character collection functions for testing and creation before integration into getImages.py & imageScanner.py


class ScreenResolution:
    RES_1440P = (2560, 1440)
    RES_1080P = (1920, 1080)


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
    print("Switching to Zenless Zone Zero")
    ZZZWindow = pyautogui.getWindowsWithTitle("ZenlessZoneZero")[0]
    if ZZZWindow.isActive == False:
        pyautogui.press(
            "altleft"
        )  # Somehow this is needed to switch to the window, Why though?
        ZZZWindow.activate()
    print("Switched to Zenless Zone Zero")


def test_snapshot():
    screenshot = pyautogui.screenshot(
        "TestImages/testDisc.png",
        region=(
            int(0.31 * screenWidth),  # left
            int(0.1 * screenHeight),  # top
            int(0.2 * screenWidth),  # width
            int(0.6 * screenHeight),  # height
        ),
    )
    screenshot.save("TestImages/testDisc.png")


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
    save_path = (
        f"./{outputFolder}/agent_{characterNumber}_partition_{paritionNumber}_scan.png"
    )
    screenshot.save(save_path)
    # put the image path in the queue
    if queue:
        queue.put(save_path)
    return screenshot


def is_character_owned(
    target_folder: str = "Target_Images",
    resolution: ScreenResolution = screenResolution,
    pageLoadTime: float = 0.25,
) -> bool:
    """
    Check if the current character is owned by looking for the preview mode popup.

    Args:
        target_folder (str): Folder containing the reference images
        resolution (ScreenResolution): Current screen resolution

    Returns:
        bool: True if character is owned, False if not owned

    Used In:
        get_character_snapshots()
    """
    wishReelPreviewPath = None
    if resolution == ScreenResolution.RES_1440P:
        wishReelPreviewPath = f"./{target_folder}/zzz-character-not-owned-1440p.png"
    elif resolution == ScreenResolution.RES_1080P:
        wishReelPreviewPath = f"./{target_folder}/zzz-character-not-owned-1080p.png"

    try:
        pyautogui.locateOnScreen(
            wishReelPreviewPath,
            confidence=0.9,
            region=(
                int(0.25 * screenWidth),
                int(0.4 * screenHeight),
                int(0.5 * screenWidth),
                int(0.2 * screenHeight),
            ),
        )
        # If we get here, the image was found (character is not owned)
        keyboard.press("esc")
        time.sleep(pageLoadTime)
        print("Agent is not owned")
        return False
    except pyautogui.ImageNotFoundException:
        # Image not found means the agent is owned
        keyboard.press("esc")
        time.sleep(pageLoadTime)
        print("Agent is owned")
        return True
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Error checking if agent is owned: {e}")
        return False


def get_character_disks_equipped(
    screenshot: PIL.Image.Image,
    resolution: ScreenResolution,
    target_folder: str = "Target_Images",
):
    """
    Get the disks equipped of the current character from an image of the equipment screen

    Args:
        screenshot (PIL.Image.Image): The screenshot of the equipment screen to check from pyautogui.screenshot()
        resolution (ScreenResolution): The current screen resolution
        target_folder (str, optional): The folder containing the reference target images, defaults to "Target_Images"

    Returns:
        list[bool]: A list of size 6 (which disks are equipped, each is true if equipped)

    Usage:
        Used in get_character_equipment_status() to determine what disks are available to scan
    """
    resolution_suffix = (
        "-1440p" if resolution == ScreenResolution.RES_1440P else "-1080p"
    )
    disk_targets = [
        f"./{target_folder}/zzz-character-equipment-no-disk-{i}{resolution_suffix}.png"
        for i in range(1, 7)
    ]

    # Convert PIL Image to cv2 format
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # For each disk_target, check if it matches in the screenshot
    disks_equipped = []
    for disk_target in disk_targets:
        # Load the template image
        template = cv2.imread(disk_target)
        if template is None:
            print(f"Warning: Could not load disk template {disk_target}")
            disks_equipped.append(True)  # Assume equipped if template can't be loaded
            continue

        # Perform template matching
        result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
        max_val = result.max()

        # If we found a good match
        # then the disk is NOT equipped, so we negate the result
        disks_equipped.append(not (max_val >= 0.9))

    return disks_equipped


def get_character_equipment_status():
    """
    Get the equipment status of the current character - do they have all disks equipped, is the wengine equipped, etc.
    Triggered when we enter the character's equipment screen

    Args:
        None

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


# function to get the various screenshots for a character for later processing
def get_character_snapshots(
    agent_num: int,
    queue: Queue = None,
    target_folder: str = "Target_Images",
    output_folder: str = "scan_input",
    resolution: ScreenResolution = screenResolution,
    pageLoadTime: float = 0.25,
    getEquipment: bool = True,
):
    # create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    wishReelIconPosition = (0.92 * screenWidth, 0.2 * screenHeight)
    exitButtonPosition = (0.06 * screenWidth, 0.05 * screenHeight)
    pyautogui.moveTo(wishReelIconPosition)
    pyautogui.click()
    time.sleep(pageLoadTime)

    if not is_character_owned(target_folder, resolution, pageLoadTime):
        return

    name_region = (
        int(0.54 * screenWidth),
        int(0.255 * screenHeight),
        int(0.24 * screenWidth),
        int(0.08 * screenHeight),
    )

    level_region = (
        int(0.54 * screenWidth),
        int(0.4 * screenHeight),
        int(0.24 * screenWidth),
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
    time.sleep(pageLoadTime * 4)  # this takes a bit longer to load typically
    pyautogui.moveTo(skill_start_pos)
    pyautogui.click()
    time.sleep(pageLoadTime)
    screenshot = pyautogui.screenshot(region=skill_region)
    screenshot.save(f"./{output_folder}/agent_{agent_num}_skill_{skill_names[0]}.png")
    if queue:
        queue.put(f"./{output_folder}/agent_{agent_num}_skill_{skill_names[0]}.png")
    time.sleep(pageLoadTime)

    for i in range(4):
        pyautogui.moveRel(horz_skill_dist, 0)
        pyautogui.click()
        time.sleep(pageLoadTime)
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
    time.sleep(pageLoadTime)
    screenshot = pyautogui.screenshot(region=skill_region)
    screenshot.save(f"./{output_folder}/agent_{agent_num}_skill_{skill_names[5]}.png")
    if queue:
        queue.put(f"./{output_folder}/agent_{agent_num}_skill_{skill_names[5]}.png")
    pyautogui.moveTo(exitButtonPosition)
    pyautogui.click()
    time.sleep(pageLoadTime)

    # grab the cinema screenshot
    navigate_character_details("Cinema")
    pyautogui.sleep(
        pageLoadTime * 8
    )  # this specific screen has a rather slow transition animation
    screenshot = (
        pyautogui.screenshot()
    )  # we just need the whole screen, since we're looking for mindscape icons within most of it anyways
    screenshot.save(f"./{output_folder}/agent_{agent_num}_cinema.png")
    if queue:
        queue.put(f"./{output_folder}/agent_{agent_num}_cinema.png")
    pyautogui.moveTo(exitButtonPosition)
    pyautogui.click()
    time.sleep(pageLoadTime)

    # get a snapshot of each equipped disk
    if getEquipment:
        navigate_character_details("Equipment")
        time.sleep(pageLoadTime)
        selectParition(1)
        scanDiskDriveCharacter(1, queue, pageLoadTime, output_folder, agent_num)
        time.sleep(pageLoadTime)
        selectParition(2)
        scanDiskDriveCharacter(2, queue, pageLoadTime, output_folder, agent_num)
        time.sleep(pageLoadTime)
        selectParition(3)
        scanDiskDriveCharacter(3, queue, pageLoadTime, output_folder, agent_num)
        time.sleep(pageLoadTime)
        selectParition(4)
        scanDiskDriveCharacter(4, queue, pageLoadTime, output_folder, agent_num)
        time.sleep(pageLoadTime)
        selectParition(5)
        scanDiskDriveCharacter(5, queue, pageLoadTime, output_folder, agent_num)
        time.sleep(pageLoadTime)
        selectParition(6)
        scanDiskDriveCharacter(6, queue, pageLoadTime, output_folder, agent_num)
        time.sleep(pageLoadTime)
        pyautogui.moveTo(exitButtonPosition)
        pyautogui.click()
        time.sleep(pageLoadTime)
        # now to scan the agent's weapon
        weapon_position = (0.725 * screenWidth, 0.5 * screenHeight)
        pyautogui.moveTo(weapon_position)
        pyautogui.click()
        time.sleep(pageLoadTime * 4)  # this takes a bit longer
        screenshot = pyautogui.screenshot(region=weapon_region)
        screenshot.save(f"./{output_folder}/agent_{agent_num}_weapon.png")
        if queue:
            queue.put(f"./{output_folder}/agent_{agent_num}_weapon.png")
        pyautogui.moveTo(exitButtonPosition)
        pyautogui.click()
        time.sleep(pageLoadTime)


# intended to be a main function of sorts to be called in getImages.py for character image collection
def get_characters():
    """
    Get the character images for all characters in the character list

    Used In:
        getImages.py's getImages() function
    """
    num_characters = len(character_names)
    characters_in_final_row = 7
    startPosition = (0.57 * screenWidth, 0.045 * screenHeight)
    distance_between_characters = 0.0525 * screenWidth
    pyautogui.moveTo(startPosition)

    # click through all the scrollable characters
    agents_scanned = 0
    for i in range(num_characters - characters_in_final_row):
        pyautogui.click()
        get_character_snapshots(agents_scanned)
        agents_scanned += 1
        pyautogui.moveTo(startPosition)  # move back after character scan
        pyautogui.scroll(-1)

    # click through the final row
    cur_character_position = startPosition
    for i in range(characters_in_final_row):
        pyautogui.click()
        pyautogui.sleep(0.5)
        get_character_snapshots(agents_scanned)
        agents_scanned += 1
        # move to the next character, using absolute coordinates since we move the mouse in get_character_snapshots()
        cur_character_position = (
            cur_character_position[0] + distance_between_characters,
            cur_character_position[1],
        )
        # if at the end of the row, don't move the mouse since there are no more characters
        if i != characters_in_final_row - 1:
            pyautogui.moveTo(cur_character_position)


### Character Scanner Functions ###


def scan_image(image_path):
    # default_config = "--oem 1 -l eng"
    # old_config = "--oem 1 -l ZZZ --tessdata-dir ./tessdata"
    config = "--oem 1 -l eng --psm 6"  # force NN+LSTM finetuned model
    try:
        text = pytesseract.image_to_string(image_path, config=config)
    except Exception as e:
        print("Error while scanning image: " + str(e))
        return None
    split_text = text.split("\n")
    split_text = list(filter(None, split_text))
    return split_text


def find_closest_stat(
    stat, valid_stats
):  # find the closest stat in the input list to the input stat

    if stat == "":
        print("Error: Stat to correct is empty")
        return None
    cosine = Cosine(2)
    closest_stat = None
    closest_stat_similarity = 0
    for valid_stat in valid_stats:
        similarity = cosine.similarity(stat, valid_stat)
        if similarity >= closest_stat_similarity:
            closest_stat_similarity = similarity
            closest_stat = valid_stat

    # if the closest and original stat are different, log it, use string comparison to check since similarity would also catch substat upgrades
    if closest_stat != stat:
        print(f"Corrected {stat} to {closest_stat}")

    return closest_stat


def find_closest_number(value: str, valid_numbers: list[str]) -> str:
    """
    Find the closest number from a list of valid numbers

    Args:
        value (str): The number to check (as string)
        valid_numbers (list[str]): List of valid numbers (as strings)

    Returns:
        str: The closest valid number (as string)
    """
    try:
        num = int(value)
        valid_nums = [int(x) for x in valid_numbers]
        closest = min(valid_nums, key=lambda x: abs(x - num))

        if closest != num:
            print(f"Corrected {value} to {closest}")

        return str(closest)
    except ValueError:
        print(f"Error converting '{value}' to number, returning last valid number")
        return valid_numbers[-1]


def preprocess_image_simple(image_path: str, save_path: str = None):
    """
    Preprocess the image by converting to grayscale and thresholding simply

    Args:
        image_path (str): Path to the name image
        save_path (str, optional): Path to save the preprocessed image

    Returns:
        cv2.Mat: The preprocessed image

    Used In:
        process_name_image()
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aggressive threshold
    binary_image = cv2.threshold(
        gray,
        240,  # Fixed threshold value
        255,
        cv2.THRESH_BINARY,
    )[1]

    # NOTE: We aren't resizing the image here like in the other preprocess_images.py functions
    # This is because the font size already varies between characters, and I don't want to have to set a resize width per character

    # Save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image


def preprocess_level_image(image_path: str, save_path: str = None):
    """
    Preprocess the level image to get the agent level

    Args:
        image_path (str): Path to the level image
        save_path (str, optional): Path to save the preprocessed image

    Returns:
        cv2.Mat: The preprocessed image

    Used In:
        process_level_image()
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    # part of the level text we later want to extract is black, so we need to grab the subsection
    height, width = image.shape[:2]
    subsection_height = int(0.6 * height)  # 0.8 - 0.2 = 0.6
    subsection_width = int(0.325 * width)  # 1 - 0.675 = 0.325
    y_start = int(0.2 * height)
    x_start = int(0.675 * width)

    level_text_subsection = image[
        y_start : y_start + subsection_height,
        x_start : x_start + subsection_width,
    ]

    # white any black pixels in the subsection
    level_text_subsection[level_text_subsection == 0] = 255

    # resize the subsection to half size since the font size of the max level is larger
    new_height = subsection_height // 2
    new_width = subsection_width // 2
    resized_subsection = cv2.resize(level_text_subsection, (new_width, new_height))

    # calculate centering offsets
    y_offset = (subsection_height - new_height) // 2
    x_offset = (subsection_width - new_width) // 2

    # black out the original subsection area
    image[
        y_start : y_start + subsection_height,
        x_start : x_start + subsection_width,
    ] = 0

    # paste the resized subsection in the center of the blacked out area
    image[
        y_start + y_offset : y_start + y_offset + new_height,
        x_start + x_offset : x_start + x_offset + new_width,
    ] = resized_subsection

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aggressive threshold
    binary_image = cv2.threshold(
        gray,
        240,  # Fixed threshold value
        255,
        cv2.THRESH_BINARY,
    )[1]

    # NOTE: We aren't resizing the image here like in the other preprocess_images.py functions
    # This is because the font size already varies between characters, and I don't want to have to set a resize width per character

    # Save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image


def preprocess_skill_image(
    image_path: str, save_path: str = None, coreSkill: bool = False
):
    """
    Preprocess the skill image to get the skill level in white, and everything else in black

    Args:
        image_path (str): Path to the skill image
        save_path (str, optional): Path to save the preprocessed image
        coreSkill (bool, optional): Whether the skill is a core skill (so we can remove the play button)

    Returns:
        cv2.Mat: The preprocessed image
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    # black out the rightmost 30% of the image if it is a core skill
    if coreSkill:
        height, width = image.shape[:2]
        image[:, int(0.7 * width) :] = 0  # Set rightmost 30% to black
        blacked_out_image = image
    else:
        blacked_out_image = image

    # Convert the image to grayscale
    gray = cv2.cvtColor(blacked_out_image, cv2.COLOR_BGR2GRAY)

    # Aggressive threshold
    binary_image = cv2.threshold(
        gray,
        240,  # Fixed threshold value
        255,
        cv2.THRESH_BINARY,
    )[1]

    # save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image


def preprocess_character_weapon_image(
    image_path: str,
    save_path: str = None,
    target_folder: str = "./Target_Images",
    resolution: ScreenResolution = screenResolution,
    icon_padding_percentage: int = 5,
    resize_for_upgrade_scan: bool = True,
    resize_width: int = 384,
):
    """
    Preprocess the character weapon image to get a black and white image of the all sections of interest (name, level)
    we need to get a full scan of the character weapon (that way we can assign the correct weapon to the character)

    Args:
        image_path (str): Path to the character weapon image
        save_path (str, optional): Path to save the preprocessed image
        target_folder (str, optional): Path to the target folder
        resolution (ScreenResolution, optional): Current screen resolution
        icon_padding_percentage (int, optional): Percentage of image height to add to padding around icons to black out
        resize_for_upgrade_scan (bool, optional): Whether to resize the image for upgrade scan template matching
        resize_width (int, optional): Width to resize to for upgrade scan template matching

    Returns:
        tuple of:
            cv2.Mat: The preprocessed image
            int: weapon upgrade level (1 if not found)

    Used In:
        process_character_weapon_image()
    """

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None, 1

    weapon_lvl_image_suffix = (
        "-1440p" if resolution == ScreenResolution.RES_1440P else "-1080p"
    )
    weapon_lvl_image_path = (
        f"{target_folder}/zzz-character-weapon-lvl{weapon_lvl_image_suffix}.png"
    )
    # load the template image
    template = cv2.imread(weapon_lvl_image_path)
    if template is None:
        print(f"Error: Could not load template at {weapon_lvl_image_path}")
        return None, 1

    # perform template matching
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Get template dimensions to know where it ends
    template_height, template_width = template.shape[:2]

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aggressive threshold
    binary_image = cv2.threshold(
        gray,
        240,  # Fixed threshold value
        255,
        cv2.THRESH_BINARY,
    )[1]

    # Define the y-range to black out around the template match
    icon_padding = int(
        icon_padding_percentage / 100 * binary_image.shape[0]
    )  # 5% of image height
    icon_y_start = max(0, max_loc[1] - icon_padding)
    icon_y_end = min(binary_image.shape[0], max_loc[1] + template_height + icon_padding)

    binary_image[icon_y_start:icon_y_end, : max_loc[0]] = (
        0  # Black out left side of template to remove the rank icon
    )

    right_cutoff = int(0.8 * binary_image.shape[1])  # Rightmost 20% of image width
    binary_image[icon_y_start:icon_y_end, right_cutoff:] = (
        0  # Black out right side to remove the character icon
    )

    # Scan for weapon upgrade level
    upgrade_rank = 1  # default if no match found

    # Make a copy of the original grayscale image for upgrade level detection
    upgrade_scan_image = gray.copy()

    # Resize the image for template matching if needed
    if resize_for_upgrade_scan:
        original_height, original_width = upgrade_scan_image.shape
        scaling_factor = resize_width / original_width
        resized_height = int(original_height * scaling_factor)
        upgrade_scan_image = cv2.resize(
            upgrade_scan_image,
            (resize_width, resized_height),
            interpolation=cv2.INTER_AREA,
        )

    # Try to find the upgrade level stars
    upgrade_star_paths = [
        os.path.join(target_folder, "zzz-wengine-character-upgrade1.png"),  # 1
        os.path.join(target_folder, "zzz-wengine-character-upgrade2.png"),  # 2
        os.path.join(target_folder, "zzz-wengine-character-upgrade3.png"),  # 3
        os.path.join(target_folder, "zzz-wengine-character-upgrade4.png"),  # 4
        os.path.join(target_folder, "zzz-wengine-character-upgrade5.png"),  # 5
    ]

    # Try each upgrade template until we find a match
    for rank, upgrade_path in enumerate(upgrade_star_paths, start=1):
        # Load the upgrade template
        upgrade_template = cv2.imread(upgrade_path, cv2.IMREAD_GRAYSCALE)
        if upgrade_template is None:
            print(f"Warning: Could not load upgrade template {upgrade_path}")
            continue

        # Perform template matching
        result = cv2.matchTemplate(
            upgrade_scan_image, upgrade_template, cv2.TM_CCOEFF_NORMED
        )
        max_val = result.max()

        if (
            max_val >= 0.85
        ):  # If we found a good match (slightly lower threshold for flexibility)
            upgrade_rank = rank
            break  # Stop searching once we find a match

    # Save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image, upgrade_rank


def process_character_disk_image(image_path: str, partition_number: int) -> dict:
    """
    Process the character disk image to get the disk data for comparison with the current scan's data to assign the disk to a character later

    Args:
        image_path (str): Path to the character disk image
        partition_number (int): The partition number of the disk

    Returns:
        dict: The metadata of the disk or an empty dictionary if the disk is not valid
    """
    preprocess_image(
        image_path,
        target_images_folder="./Target_Images",
        save_path=image_path,
    )  # the regular preprocess_image function is used here as it is actually for disk images
    result = scan_image(image_path)
    result_metadata = extract_metadata(result, image_path, partition_number)
    correct_metadata(result_metadata)
    valid_disk_drive, error_message = validate_disk_drive(
        result_metadata["set_name"],
        result_metadata["drive_current_level"],
        result_metadata["drive_max_level"],
        result_metadata["partition_number"],
        result_metadata["drive_base_stat"],
        result_metadata["drive_base_stat_number"],
        result_metadata["random_stats"],
    )

    if valid_disk_drive:
        return result_metadata
    else:
        print(f"Error: Disk is not valid: {error_message}")
        return {}


def process_character_weapon_image(image_path: str) -> str:
    """
    Process the character weapon image to get the weapon name

    Args:
        image_path (str): Path to the character weapon image (not preprocessed)

    Returns:
        A weapon dictionary in format:
        {
            "name": str,
            "level": int,
            "max_level": int,
            "upgrade_rank": int,
        }
    """
    processed_image, upgrade_rank = preprocess_character_weapon_image(image_path)
    text = scan_image(processed_image)
    weapon = process_wengine_text(text, preprocess_rank=upgrade_rank)
    weapon["name"] = find_closest_stat(
        weapon["name"], valid_weapon_names
    )  # correct the name to the known list of weapon names
    return weapon


def process_cinema_image(
    image_path: str,
    target_folder: str = "./Target_Images",
    resolution: ScreenResolution = screenResolution,
) -> str:
    """
    Process the cinema image to get the mindscape level

    Args:
        image_path (str): Path to the cinema image
        target_folder (str, optional): Path to the target folder
        resolution (ScreenResolution, optional): Current screen resolution

    Returns:
        str: The mindscape level (0 for none, 1 to 6 for the number of mindscapes unlocked)
    """
    locked_image_suffix = (
        "-1440p" if resolution == ScreenResolution.RES_1440P else "-1080p"
    )

    # load the main image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    # check if the image has locked mindscape icons
    lowest_locked_index = None
    for i in range(1, 6):
        current_image_path = (
            f"{target_folder}/zzz-mindscape-locked-{i}{locked_image_suffix}.png"
        )
        template = cv2.imread(current_image_path)
        if template is None:
            print(f"Error: Could not load template at {current_image_path}")
            continue

        # Perform template matching
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # If we find a match with high confidence
        if max_val > 0.9:
            lowest_locked_index = i
            break

    # if we didn't find any locked images, then all are unlocked
    if lowest_locked_index is None:
        return "6"  # we are at all unlocked
    else:
        return str(lowest_locked_index - 1)


def process_skill_image(image_path: str, coreSkill: bool = False) -> str:
    """
    Process the skill image to get the skill level

    Args:
        image_path (str): Path to the skill image
        coreSkill (bool, optional): Whether the skill is a core skill (so we can remove the play button & handle the different level ranges)

    Returns:
        str: The skill level
    """
    processed_image = preprocess_skill_image(image_path=image_path, coreSkill=coreSkill)

    # scan the image
    text = scan_image(processed_image)
    text = " ".join(text)
    # grab exactly 2 digits from the text
    twoDigits = re.search(r"\d{2}", text)
    if twoDigits:
        text = twoDigits.group(0)
    else:
        # Fallback: try to get at least one digit (for low level skills)
        oneDigit = re.search(r"\d", text)
        if oneDigit:
            text = oneDigit.group(0)
        else:
            print(f"Could not parse skill level from text: {text}")
            return None

    # correction step: if not a core skill, it can be between 1 and 16, else 1 and 7
    # correct into the nearest valid level
    if not coreSkill:
        text = find_closest_number(
            text,
            [
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
            ],
        )
    else:
        text = find_closest_number(text, ["1", "2", "3", "4", "5", "6", "7"])
    return text


def process_name_image(image_path: str) -> str:
    """
    Process the name image to get the agent name

    Args:
        image_path (str): Path to the name image

    Returns:
        str: The agent name, corrected to the known list of agent names
    """
    processed_image = preprocess_image_simple(image_path)
    # concatenate the text from the image
    text = scan_image(processed_image)
    text = " ".join(text)
    # correct it to the known list of agent names
    text = find_closest_stat(text, character_names)
    return text


def process_level_image(image_path: str) -> tuple[str, str]:
    """
    Process the level image to get the agent level

    Args:
        image_path (str): Path to the level image

    Returns:
        str: The agent level
    """
    processed_image = preprocess_level_image(image_path)
    text = scan_image(processed_image)

    # if the text is only one string, we need to split it and grab the two level numbers from it
    if len(text) == 1:
        # Match two sequences of two digits
        match = re.search(r"(\d{2}).*?(\d{2})", text[0])
        if match:
            current_level = match.group(1)
            max_level = match.group(2)
        else:
            print(f"Could not parse levels from text: {text[0]}")
            print("Assuming max leveled character (60/60)")
            current_level = "60"
            max_level = "60"
    else:
        # if not, we can clean and grab the two numbers from the list
        # clean all members of non-digit characters
        text = [re.sub(r"\D", "", t) for t in text]
        # strip all of them
        text = [t.strip() for t in text]
        # remove any empty strings
        text = list(filter(None, text))
        current_level = text[0]
        max_level = text[1]

    # correction for the level text
    # the maxlevel is one of "10", "20", "30", "40", "50", "60"
    # the cur level must be equal to or less than the max level (up to 10 below)

    # correct the max level to the nearest valid level
    max_level = find_closest_number(max_level, ["10", "20", "30", "40", "50", "60"])

    # correct the current level
    # make sure the current level is less than or equal to the max level
    if int(current_level) > int(max_level):
        current_level = max_level

    # if it is more than 10 below the max level, set it to ten below the max level
    if int(current_level) < int(max_level) - 10:
        current_level = int(max_level) - 10

    return current_level, max_level


### End of Character Scanner Functions ###

if __name__ == "__main__":
    # set cwd to the script location
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # set the path to the tesseract-ocr folder
    tesseract_path = (
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tesseract-OCR")
        + "\\tesseract.exe"
    )
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    switchToZZZ()
    time.sleep(0.25)
    # wishReelIconPosition = (0.92 * screenWidth, 0.2 * screenHeight)
    # pyautogui.moveTo(wishReelIconPosition)
    # pyautogui.click()
    # time.sleep(0.25)
    # isCharacterOwned = is_character_owned(
    #     resolution=screenResolution,
    #     pageLoadTime=0.25,
    # )
    # print(isCharacterOwned)
    # navigate_character_details("Skills")
    # get_characters()
    # test_snapshot()
    # get_character_snapshots(0)
    # temp = pyautogui.screenshot(
    #     region=(
    #         int(0.5 * screenWidth),  # left
    #         int(0.15 * screenHeight),  # top
    #         int(0.45 * screenWidth),  # width
    #         int(0.7 * screenHeight),  # height
    #     ),
    # )
    # disks_status = get_character_disks_equipped(temp, screenResolution)
    # print(disks_status)
    # temp.save("./TestImages/test_character_equipment_screen.png")
    # img = preprocess_image_simple(
    #     "./TestImages/test_character_name_scan.png",
    #     save_path="./TestImages/test_character_name_scan_processed.png",
    # )
    # print(process_name_image("./TestImages/test_character_name_scan.png"))
    # print(process_skill_image("./TestImages/test.png", coreSkill=False))
    # print(process_skill_image("./TestImages/test1.png", coreSkill=True))
    # print(process_character_disk_image("./TestImages/testDisc.png", 1))
