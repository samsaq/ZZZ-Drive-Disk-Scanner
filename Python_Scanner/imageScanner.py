import re
import sys
from multiprocessing import Queue
import os
import json
import logging
import pytesseract
import cv2
from strsimpy import Cosine  # used for string cosine similarity
from preprocess_images import (
    preprocess_image,
    preprocess_wengine_image,
    preprocess_image_simple,
    preprocess_level_image,
    preprocess_skill_image,
    preprocess_character_weapon_image,
)
from getImages import ScreenResolution
from validMetadata import (
    valid_set_names,
    valid_partition_1_main_stats,
    valid_partition_2_main_stats,
    valid_partition_3_main_stats,
    valid_partition_4_main_stats,
    valid_partition_5_main_stats,
    valid_partition_6_main_stats,
    valid_random_stats,
    valid_weapon_names,
    character_names,
    validate_disk_drive,
    get_expected_main_stat_value,
    get_expected_sub_stat_values,
    get_rarity_stats,
)

debug = False
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# set the path to the tesseract-ocr folder
tesseract_path = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tesseract-OCR")
    + "\\tesseract.exe"
)
pytesseract.pytesseract.tesseract_cmd = tesseract_path


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# function to setup logging so it doesn't auto-run when imported
def setup_logging():
    loglevel = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=loglevel,
        filename=resource_path("scan_output/log.txt"),
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,  # used to allow logging to work even when running in IDE
    )


# scan a list of strings to see if the input substring is in one of the strings in the list, return the whole string if found
def find_string_in_list(substring, string_list):
    for string in string_list:
        if substring in string:
            return string
    logging.error(f"Could not find {substring} in the list")
    return None


# same as above, but return the index of the string in the list instead of the string itself
def find_index_in_list(substring, string_list, ignore_list=[]):
    # the ignore list is a list of indexes that we should skip over when searching
    for i in range(len(string_list)):
        if i in ignore_list:
            continue
        if substring in string_list[i]:
            return i
    logging.error(f"Could not find {substring} in the list for index")
    return None


# we can infer the drive rarity from the max level, as 9 is B rank, 12 is A rank, and 15 is S rank
def drive_rarity_from_max_level(max_level):
    if max_level == 9:
        return "B"
    elif max_level == 12:
        return "A"
    elif max_level == 15:
        return "S"
    else:
        return None


# NOTE: you can also pass in a cv2 image object instead of image path
def scan_image(image_path):
    # default_config = "--oem 1 -l eng"
    # old_config = "--oem 1 -l ZZZ --tessdata-dir ./tessdata"
    config = "--oem 1 -l eng --psm 6"  # force NN+LSTM finetuned model
    try:
        text = pytesseract.image_to_string(image_path, config=config)
    except Exception as e:
        logging.error("Error while scanning image: " + str(e))
        print("Error while scanning image: " + str(e))
        return None
    split_text = text.split("\n")
    split_text = list(filter(None, split_text))
    return split_text


def extract_metadata(result_text, image_path, provided_partition_number: int = None):
    # grab the data we need from the input text
    set_name = result_text[find_index_in_list("Set", result_text) + 1]
    # get partition number via the image path (eg: Partition1Scan1.png would be 1)
    if provided_partition_number:
        partition_number = provided_partition_number
    else:
        partition_number = re.search(r"Partition(\d+)Scan", image_path).group(1)
    # get the current and max levels of the drive, in the form of Lv. Current/Max
    drive_level = find_string_in_list(
        "/", result_text
    )  # might swap back to "Lv." if this is too permissive
    # clean out any text other than numbers and slashes and trim the string
    drive_level = re.sub("[^0-9/]", "", drive_level).strip()
    drive_max_level = drive_level.split("/")[1].strip()
    drive_current_level = re.sub("\D", "", drive_level.split("/")[0])
    # convert a current level of 00 to 0, etc
    if drive_current_level[0] == "0":
        drive_current_level = "0"
    # base stat is found after the "Main Stat" line
    drive_base_stat_combined = result_text[find_index_in_list("Main", result_text) + 1]

    drive_base_stat = re.sub("[\d%]", "", drive_base_stat_combined).strip()

    # if there are no numbers in the base stat, don't try to grab it, we'll rely on correcting it later
    drive_base_stat_number_missing = False
    if not any(char.isdigit() for char in drive_base_stat_combined):
        drive_base_stat_number_missing = True

    # get the base stat name and number from the combined string
    # strip out any numbers or % signs from the string, what remains is the base stat name
    drive_base_stat_number = None
    if not drive_base_stat_number_missing:
        # get the number from the string, and if it had a %, include it, this is the base stat number
        drive_base_stat_number = re.search(
            r"\d+(\.\d+)?%?", drive_base_stat_combined
        ).group()

    # the random stats of the drive should be stored as a pair, with the stat name and its value
    # they are found in the text after the "Sub-Stats" line and before the "Set Effect" line
    # each name has its value right after it, so we can iterate through the text and add the values to the array
    random_stats = []
    already_used_indexes = []
    for i in range(
        find_index_in_list("Sub", result_text) + 1,
        find_index_in_list("Set", result_text),
    ):

        cur_random_stat_name = re.search(r"[a-zA-Z ]+\+?\d?", result_text[i])
        cur_random_stat_value = re.search(r"(?<!\+)\d+(\.\d+)?%?", result_text[i])

        # if both are found, group them and append them to the random stats array
        if cur_random_stat_name and cur_random_stat_value:
            cur_random_stat_name = cur_random_stat_name.group()
            cur_random_stat_value = cur_random_stat_value.group()
            random_stats.append((cur_random_stat_name, cur_random_stat_value))
        elif cur_random_stat_name:
            # if only the name is found, iterate down the list until we find the value
            # (search each line for a match until we find one or reach the end)
            cur_random_stat_name = cur_random_stat_name.group()
            for j in range(
                find_index_in_list("Sub", result_text) + 1, len(result_text)
            ):
                cur_random_stat_value = None
                if (
                    j not in already_used_indexes
                ):  # so we don't just grab the same substat value multiple times
                    cur_random_stat_value = re.search(
                        r"^\d+(\.\d+)?%?$", result_text[j]
                    )
                if cur_random_stat_value:
                    cur_random_stat_value = cur_random_stat_value.group()
                    already_used_indexes.append(j)
                    random_stats.append((cur_random_stat_name, cur_random_stat_value))
                    break
                # if we get to the end of the list and still haven't found a value,  mark the value as none and append it
                if j == len(result_text) - 1:
                    cur_random_stat_value = ""
                    random_stats.append((cur_random_stat_name, cur_random_stat_value))
                    logging.warning(
                        f"Could not find value for random stat {cur_random_stat_name}"
                    )
        else:
            logging.DEBUG(f"Could not find random stat name in:" + result_text[i])
    return {
        "set_name": set_name,
        "partition_number": partition_number,
        "drive_rarity": drive_rarity_from_max_level(int(drive_max_level)),
        "drive_current_level": drive_current_level,
        "drive_max_level": drive_max_level,
        "drive_base_stat": drive_base_stat,
        "drive_base_stat_number": drive_base_stat_number,
        "drive_base_stat_combined": drive_base_stat_combined,
        "random_stats": random_stats,
    }


def find_closest_stat(
    stat, valid_stats, plus_modifier=True
):  # find the closest stat in the input list to the input stat
    cosine = Cosine(2)
    closest_stat = None
    closest_stat_similarity = 0
    for valid_stat in valid_stats:
        similarity = cosine.similarity(stat, valid_stat)
        if similarity >= closest_stat_similarity:
            closest_stat_similarity = similarity
            closest_stat = valid_stat

    # if the original stat had a plus modifier (eg: +1 at the end), add it and the following number to the corrected stat
    if plus_modifier and "+" in stat:
        closest_stat += stat[stat.index("+") : stat.index("+") + 2]

    # if the closest and original stat are different, log it, use string comparison to check since similarity would also catch substat upgrades
    if closest_stat != stat:
        logging.warning(f"Corrected {stat} to {closest_stat}")

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


# a function that will correct metadata based off of cosine similarity to known correct metadata values
# eg: for the set name, we can compare the input set name to a list of known set names use the cosine similarity to find the closest match
def correct_metadata(metadata):
    # correct the set name
    set_name = metadata["set_name"]
    closest_set_name = find_closest_stat(set_name, valid_set_names)
    metadata["set_name"] = closest_set_name

    # based off of the partition number, we can correct the main (base) stat
    partition_number = metadata["partition_number"]
    if partition_number == "1":
        closest_stat = find_closest_stat(
            metadata["drive_base_stat"], valid_partition_1_main_stats
        )
        metadata["drive_base_stat"] = closest_stat
    elif partition_number == "2":
        closest_stat = find_closest_stat(
            metadata["drive_base_stat"], valid_partition_2_main_stats
        )
        metadata["drive_base_stat"] = closest_stat
    elif partition_number == "3":
        closest_stat = find_closest_stat(
            metadata["drive_base_stat"], valid_partition_3_main_stats
        )
        metadata["drive_base_stat"] = closest_stat
    elif partition_number == "4":
        closest_stat = find_closest_stat(
            metadata["drive_base_stat"], valid_partition_4_main_stats
        )
        metadata["drive_base_stat"] = closest_stat
    elif partition_number == "5":
        closest_stat = find_closest_stat(
            metadata["drive_base_stat"], valid_partition_5_main_stats
        )
        metadata["drive_base_stat"] = closest_stat
    elif partition_number == "6":
        closest_stat = find_closest_stat(
            metadata["drive_base_stat"], valid_partition_6_main_stats
        )
        metadata["drive_base_stat"] = closest_stat

    # correct the random stats, each stat is a pair of (stat_name, stat_value)
    # we'll be checking the stat_name against the valid_random_stats list
    for i in range(len(metadata["random_stats"])):
        stat_name = metadata["random_stats"][i][0]
        closest_stat = find_closest_stat(stat_name, valid_random_stats)
        metadata["random_stats"][i] = (closest_stat, metadata["random_stats"][i][1])

    # correct the main stat value
    main_stats_progression, sub_stats_progression = get_rarity_stats(
        metadata["drive_rarity"]
    )
    expected_main_stat_value = get_expected_main_stat_value(
        metadata["drive_base_stat"],
        main_stats_progression,
        metadata["drive_current_level"],
        metadata["drive_max_level"],
        metadata["partition_number"],
    )
    if metadata["drive_base_stat_number"] != str(expected_main_stat_value):
        logging.warning(
            f"Corrected base stat value {metadata['drive_base_stat_number']} to {expected_main_stat_value}"
        )
        metadata["drive_base_stat_number"] = str(expected_main_stat_value)

    # try to correct the random stats
    try:
        expected_sub_stat_values = get_expected_sub_stat_values(
            metadata["random_stats"],
            sub_stats_progression,
        )
        # if the expected sub stats are different from the input sub stats, correct it, and log it
        # expected sub stats are in a list of (stat_name, stat_value) tuples
        expected_sub_stats_names = [stat[0] for stat in expected_sub_stat_values]
        corrected_sub_stats_ignore_list = []

        # Keep track of which stats we've seen to handle duplicates
        for i, (sub_stat_name, sub_stat_value) in enumerate(metadata["random_stats"]):
            old_sub_stat_name = sub_stat_name
            if any(keyword in sub_stat_name for keyword in ["HP", "ATK", "DEF"]):
                if "%" in sub_stat_value:
                    if "+" in sub_stat_name:
                        # add the % before the + to the sub stat name
                        sub_stat_name = (
                            sub_stat_name.split("+")[0]
                            + "%"
                            + "+"
                            + sub_stat_name.split("+")[1]
                        )
                    else:
                        sub_stat_name += "%"

            # see if the sub stat is in the expected sub stats, and if it is, check if the value is correct
            # if it isn't, throw an error since it should be in the expected sub stats
            if sub_stat_name in expected_sub_stats_names:
                # find the expected value for the sub stat
                expected_sub_stat_value = find_string_in_list(
                    sub_stat_name, expected_sub_stat_values
                )[1]

                if sub_stat_value.replace("%", "") != expected_sub_stat_value.replace(
                    "%", ""
                ):
                    logging.warning(
                        f"Corrected sub stat {sub_stat_name} value {sub_stat_value} to {expected_sub_stat_value}"
                    )
                    # Update the stat at the current index
                    metadata["random_stats"][i] = (
                        old_sub_stat_name,
                        expected_sub_stat_value,
                    )

            else:
                raise ValueError(
                    f"Sub stat {sub_stat_name} not found in expected sub stats"
                )

    except Exception as e:
        print("Error while correcting sub stats, proceeding uncorrected: ", e)
        logging.WARNING(
            f"Error while correcting sub stats, proceeding uncorrected: {e}"
        )


### WEngine Specific Functions ###
def process_wengine_text(text, preprocess_rank=1):
    """
    Processes the text from a wengine screenshot to extract the name and level data

    Args:
        text (list): The text to process, expected to be the output of scan_image
        preprocess_rank (int): The rank of the wengine found by the preprocess_wengine_image function, defaults to 1 (lowest)

    Returns:
        dict: The name, curLevel, maxLevel
    """
    # connect all the text array members before the first "Lv." or "XX/XX" form number together as the name
    if not text:
        return None

    # Pattern for level (Lv.) and form number (XX/XX)
    level_pattern = re.compile(r"Lv\.", re.IGNORECASE)
    number_pattern = re.compile(r"\d+/\d+")

    name_parts = []
    remaining_parts = []

    for line in text:
        # If we find either pattern, stop adding to name
        if level_pattern.search(line) or number_pattern.search(line):
            remaining_parts.append(line)
            break
        name_parts.append(line)

    # Add any remaining lines to remaining_parts
    remaining_parts.extend(text[len(name_parts) + 1 :])

    # Join name parts with spaces
    name = " ".join(name_parts).strip()

    # from the remaining_parts, find the first line that contains "XX/XX"
    level_data_line = None
    for line in remaining_parts:
        if number_pattern.search(line):
            level_data_line = line
            break

    # split the level info, it comes is "curLevel/maxLevel"
    level_data = level_data_line.split("/")
    # remove anything that is not a number to clean up
    curLevel = re.sub(r"\D", "", level_data[0])
    maxLevel = re.sub(r"\D", "", level_data[1])

    return {
        "name": name,
        "curLevel": curLevel,
        "maxLevel": maxLevel,
        "upgrade_rank": preprocess_rank,
    }


def correct_wengine_data(data):
    """
    Corrects the wengine data as much as possible

    Args:
        data (dict): The wengine data to correct, expected to be the output of process_wengine_text

    Returns:
        dict: The corrected wengine data
    """
    maxLevel = int(data["maxLevel"])
    # maxlevel can only be 10, 20, 30, 40, 50, 60 - correct it to the nearest one
    if maxLevel not in [10, 20, 30, 40, 50, 60]:
        data["maxLevel"] = str(round(maxLevel / 10) * 10)

    # curlevel can only between maxlevel-10 and maxlevel
    curLevel = int(data["curLevel"])
    if curLevel < maxLevel - 10:
        curLevel = maxLevel - 10
    elif curLevel > maxLevel:
        curLevel = maxLevel
    data["curLevel"] = curLevel

    # make sure the upgrade rank is between 1 and 5, if it's not, set it to the nearest one
    if data["upgrade_rank"] not in [1, 2, 3, 4, 5]:
        data["upgrade_rank"] = round(data["upgrade_rank"])

    # correct the name
    data["name"] = find_closest_stat(
        data["name"], valid_weapon_names, plus_modifier=False
    )

    return data


### End of WEngine Specific Functions ###

### Character Specific Functions ###


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
        logging.error(f"Error: Scanned character disk is not valid: {error_message}")
        return {}


def process_character_weapon_image(
    resolution: ScreenResolution, image_path: str
) -> dict:
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
    processed_image, upgrade_rank = preprocess_character_weapon_image(
        image_path=image_path, resolution=resolution
    )
    text = scan_image(processed_image)
    weapon = process_wengine_text(text, preprocess_rank=upgrade_rank)
    weapon["name"] = find_closest_stat(
        weapon["name"], valid_weapon_names
    )  # correct the name to the known list of weapon names
    return weapon


def process_cinema_image(
    resolution: ScreenResolution,
    image_path: str,
    target_folder: str = "./Target_Images",
) -> str:
    """
    Process the cinema image to get the mindscape level

    Args:
        resolution (ScreenResolution): Current screen resolution
        image_path (str): Path to the cinema image
        target_folder (str, optional): Path to the target folder

    Returns:
        str: The mindscape level (0 for none, 1 to 6 for the number of mindscapes unlocked)
    """
    locked_image_suffix = (
        "-1440p" if resolution == ScreenResolution.RES_1440P else "-1080p"
    )

    # load the main image
    image = cv2.imread(image_path)
    if image is None:
        logging.error(f"Error: Could not load cinema image at {image_path}")
        return None

    # check if the image has locked mindscape icons
    lowest_locked_index = None
    for i in range(1, 6):
        current_image_path = (
            f"{target_folder}/zzz-mindscape-locked-{i}{locked_image_suffix}.png"
        )
        template = cv2.imread(current_image_path)
        if template is None:
            logging.error(
                f"Error: Could not load cinema mindscape locked template at {current_image_path}, skipping it"
            )
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
            logging.error(f"Error: Could not parse skill level from text: {text}")
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
    text = find_closest_stat(text, character_names, plus_modifier=False)
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
            logging.error(f"Error: Could not parse levels from text: {text[0]}")
            logging.warning("Assuming max leveled character (60/60)")
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


### End of Character Specific Functions ###


# the main function that will be called to process the images in orchestrator.py
def imageScanner(queue: Queue, resolution: ScreenResolution):
    setup_logging()
    # scan through all images in the scan_input folder
    current_scan_type = None
    disk_data = []
    wengine_data = []
    character_data = []
    diskNum = 0
    wengineNum = 0
    characterNum = 0
    consecutive_errors = 0
    logging.info("Ready to process disk drives")
    getImagesDone = False
    while not getImagesDone:
        while not queue.empty():
            image_path = queue.get()
            # Handle marker strings that indicate scan type
            if image_path in ["Disk", "WEngine", "Character"]:
                current_scan_type = image_path
                continue  # Skip to next item in queue
            elif image_path == "Done":
                getImagesDone = True
                break

            # Process images based on current scan type
            if current_scan_type == "Disk":
                if image_path == "Error - failed to get to the equipment screen":
                    logging.critical(
                        "Failed to get to the equipment screen - try increasing the page load time"
                    )
                    sys.exit(1)
                logging.info(f"Processing disk drive # {diskNum}, at {image_path}")
                if debug:
                    print(f"Processing {image_path}")
                try:
                    processed_image = preprocess_image(
                        image_path, target_images_folder="./Target_Images"
                    )
                    result = scan_image(processed_image)
                    result_metadata = extract_metadata(result, image_path)
                except Exception as e:
                    logging.error(f"Error analyzing drive #{diskNum}, skipping it: {e}")
                    consecutive_errors += 1
                    # if we have more than 10 consecutive errors, stop the program and log it - probably wrong timing settings
                    if consecutive_errors > 10:
                        logging.critical(
                            "Over 10 consecutive errors, stopping the program - try increasing the time between disc drive scans"
                        )
                        sys.exit(1)
                    continue
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
                    disk_data.append(result_metadata)
                else:
                    logging.error(
                        f"Disk drive #{diskNum} failed validation, skipping: {error_message}"
                    )
                logging.info(f"Finished processing disk drive #{diskNum}")
                consecutive_errors = 0
                diskNum += 1
                if debug:  # log out the output
                    for key, value in result_metadata.items():
                        print(f"{key}: {value}")
                    print("--------------------------------------------------")
            elif current_scan_type == "WEngine":
                logging.info(f"Processing wengine # {wengineNum}, at {image_path}")
                if debug:
                    print(f"Processing {image_path}")
                try:
                    processed_image, found_rank = preprocess_wengine_image(image_path)
                    result = scan_image(processed_image)
                    result_metadata = process_wengine_text(
                        result, preprocess_rank=found_rank
                    )
                    result_metadata = correct_wengine_data(result_metadata)
                    # no point in a validation step since we're correcting the data as much as possible already
                    # it'd just automatically pass with this level of correction
                    wengine_data.append(result_metadata)
                except Exception as e:
                    logging.error(
                        f"Error analyzing wengine #{wengineNum}, skipping it: {e}"
                    )
                    consecutive_errors += 1
                    # if we have more than 10 consecutive errors, stop the program and log it - probably wrong timing settings
                    if consecutive_errors > 10:
                        logging.critical(
                            "Over 10 consecutive errors, stopping the program - try increasing the time between wengine scans"
                        )
                        sys.exit(1)
                    continue
                logging.info(f"Finished processing wengine #{wengineNum}")
                consecutive_errors = 0
                wengineNum += 1
                if debug:  # log out the output
                    for key, value in result_metadata.items():
                        print(f"{key}: {value}")
                    print("--------------------------------------------------")
            elif current_scan_type == "Character":
                # Initialize equipment status if needed (only for new characters)
                if "name" in image_path:
                    # Starting a new character
                    cur_character_data = {}
                    cur_equipment_status = {
                        "weapon": False,
                        "anyDisks": False,
                        "disks_equipped": [False, False, False, False, False, False],
                    }
                    character_data_complete = False
                    has_basic_info = False
                    equipment_status_received = False
                    logging.info(
                        f"Processing for new character #{characterNum}, at {image_path}"
                    )

                    # Process name image
                    cur_character_data["name"] = process_name_image(image_path)

                # Then continue with the existing code paths for other image types
                elif "status" in image_path:
                    # Parse equipment status...
                    # Parse the equipmentstatus string that will be in the format
                    # "status: weapon_true, disk1_true, disk2_false, disk3_true, disk4_false, disk5_true, disk6_false"
                    equipment_status_received = True
                    # Parse the equipmentstatus string
                    status_string = image_path.split("status: ")[1]
                    status_parts = status_string.split(", ")

                    for part in status_parts:
                        if part.startswith("weapon_"):
                            # Parse weapon status
                            weapon_status = part.split("weapon_")[1].lower() == "true"
                            cur_equipment_status["weapon"] = weapon_status
                        elif part.startswith("disk"):
                            # Parse disk status - format is "disk1_true", "disk2_false", etc.
                            disk_num = int(part[4:5]) - 1  # Convert to 0-based index
                            disk_status = part.split("_")[1].lower() == "true"

                            # Update the corresponding disk status
                            if 0 <= disk_num < 6:  # Ensure valid disk number
                                cur_equipment_status["disks_equipped"][
                                    disk_num
                                ] = disk_status

                                # If any disk is equipped, set anyDisks to True
                                if disk_status:
                                    cur_equipment_status["anyDisks"] = True

                    # Now we have the complete equipment status in cur_equipment_status
                    # We can use this to decide which disk images to process and whether to handle the weapon

                    # Initialize empty disk slots in the character data structure
                    for disk_num, is_equipped in enumerate(
                        cur_equipment_status["disks_equipped"], 1
                    ):
                        if not is_equipped:
                            # Create empty disk data for unequipped slots
                            cur_character_data[f"disk_{disk_num}"] = {}

                    # Handle weapon status
                    if not cur_equipment_status["weapon"]:
                        # If weapon is not equipped, create empty weapon data
                        cur_character_data["weapon"] = {}

                    # Check if we already have all the basic character info
                    if has_basic_info:
                        # If we have both equipment status and basic info, and no equipment to scan
                        if (
                            not cur_equipment_status["weapon"]
                            and not cur_equipment_status["anyDisks"]
                        ):
                            # No equipment to scan, character data is complete
                            character_data.append(cur_character_data)
                            cur_character_data = {}
                            character_data_complete = True
                            logging.info(
                                f"Finished processing character #{characterNum}, at {image_path}"
                            )
                            characterNum += 1
                elif "level" in image_path:
                    curLevel, curMaxLevel = process_level_image(image_path)
                    cur_character_data["level"] = curLevel
                    cur_character_data["max_level"] = curMaxLevel
                elif "skill" in image_path:
                    cur_skill_name = image_path.split("_skill_")[1].split("_")[0]
                    isCoreSkill = cur_skill_name == "core"
                    cur_character_data[cur_skill_name + "_level"] = process_skill_image(
                        image_path, isCoreSkill
                    )
                elif "weapon" in image_path and not character_data_complete:
                    # Only process if we haven't already completed this character
                    if cur_equipment_status["weapon"]:
                        cur_character_data["weapon"] = process_character_weapon_image(
                            resolution=resolution, image_path=image_path
                        )
                    # Weapon is the last piece of data to be collected, so we can append the character data and reset the character data structure
                    character_data.append(cur_character_data)
                    cur_character_data = {}
                    character_data_complete = True
                    logging.info(
                        f"Finished processing character #{characterNum}, at {image_path}"
                    )
                    characterNum += 1
                elif "cinema" in image_path:
                    cur_character_data["mindscape_level"] = process_cinema_image(
                        resolution=resolution, image_path=image_path
                    )
                    has_basic_info = (
                        True  # cinema is the last piece of basic info collected
                    )

                    # Correct the skill levels for the character based on the mindscape level
                    # At mindscape level 3 and level 5, the skill levels (other than core) are increased
                    skill_names = [
                        "basic_attack",
                        "dodge",
                        "assist",
                        "special_attack",
                        "chain_attack",
                    ]

                    for skill_name in skill_names:
                        skill_key = f"{skill_name}_level"
                        if skill_key in cur_character_data:
                            current_level = int(cur_character_data[skill_key])
                            if int(cur_character_data["mindscape_level"]) >= 5:
                                cur_character_data[skill_key] = str(current_level + 4)
                            elif int(cur_character_data["mindscape_level"]) >= 3:
                                cur_character_data[skill_key] = str(current_level + 2)

                    # If we already received equipment status and there's no equipment to scan
                    if (
                        equipment_status_received
                        and not cur_equipment_status["weapon"]
                        and not cur_equipment_status["anyDisks"]
                    ):
                        # No equipment to scan, character data is complete
                        character_data.append(cur_character_data)
                        cur_character_data = {}
                        character_data_complete = True
                        logging.info(
                            f"Finished processing character #{characterNum}, who had no equipment to scan"
                        )
                        characterNum += 1

                elif "disk" in image_path and not character_data_complete:
                    # Only process if we haven't already completed this character
                    # grab the partition number from the image path
                    partition_number = image_path.split("_partition_")[1].split(
                        "_scan"
                    )[0]

                    # Only process if this disk should be equipped
                    disk_index = int(partition_number) - 1
                    if (
                        0 <= disk_index < 6
                        and cur_equipment_status["disks_equipped"][disk_index]
                    ):
                        cur_character_data[f"disk_{partition_number}"] = (
                            process_character_disk_image(
                                image_path=image_path, partition_number=partition_number
                            )
                        )

                    # Check if this was the last piece we were waiting for
                    equipped_disk_indices = [
                        i
                        for i, equipped in enumerate(
                            cur_equipment_status["disks_equipped"]
                        )
                        if equipped
                    ]
                    equipped_disk_keys = [
                        f"disk_{i+1}" for i in equipped_disk_indices
                    ]  # Convert to 1-based keys

                    # Check if all equipped disks have been processed (not just initialized)
                    all_equipped_disks_processed = True
                    for disk_key in equipped_disk_keys:
                        # If the disk is equipped, it should have more than just an empty dict
                        if (
                            disk_key not in cur_character_data
                            or not cur_character_data[disk_key]
                            or len(cur_character_data[disk_key]) <= 1
                        ):
                            all_equipped_disks_processed = False
                            break

                    # Check if weapon is processed if it's equipped
                    weapon_processed = (not cur_equipment_status["weapon"]) or (
                        "weapon" in cur_character_data
                        and cur_character_data["weapon"]
                        and len(cur_character_data["weapon"]) > 1
                    )

                    if all_equipped_disks_processed and weapon_processed:
                        # All equipped items have been fully processed
                        character_data.append(cur_character_data)
                        cur_character_data = {}
                        character_data_complete = True
                        logging.info(
                            f"Processing character #{characterNum}, at {image_path} finished"
                        )
                        characterNum += 1

    # write the data to a JSON file for later use inside of the scan_output folder
    logging.info("Finished processing. Writing scan data to file")
    output_data = {
        "disk_data": disk_data,
        "wengine_data": wengine_data,
        "character_data": character_data,
    }
    with open("scan_output/scan_data.json", "w") as f:
        json.dump(output_data, f, indent=4)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # test the scanner on a single image
    save_path = resource_path("./scan_output/Partition2Scan7.png")
    image_path = resource_path("./scan_input/Partition2Scan7.png")
    setup_logging()
    processed_image = preprocess_image(
        image_path, save_path=save_path, target_images_folder="./Target_Images"
    )
    result = scan_image(processed_image)
    result_metadata = extract_metadata(result, image_path)
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
        logging.info("Disk drive passed validation")
    else:
        logging.error(f"Disk drive failed validation: {error_message}")
