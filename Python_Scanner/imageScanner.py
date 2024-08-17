import re
import sys
from multiprocessing import Queue
import os
import json
import logging
import pytesseract
from strsimpy import Cosine  # used for string cosine similarity
from preprocess_images import preprocess_image
from validMetadata import (
    valid_set_names,
    valid_partition_1_main_stats,
    valid_partition_2_main_stats,
    valid_partition_3_main_stats,
    valid_partition_4_main_stats,
    valid_partition_5_main_stats,
    valid_partition_6_main_stats,
    valid_random_stats,
    percentage_main_stats,
    validate_disk_drive,
    get_expected_main_stat_value,
    get_expected_sub_stat_values,
    get_rarity_stats,
)

debug = False
os.chdir(os.path.dirname(os.path.abspath(__file__)))


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
    config = "--oem 1 -l eng"  # force NN+LSTM finetuned model
    try:
        text = pytesseract.image_to_string(image_path, config=config)
    except Exception as e:
        logging.error("Error while scanning image: " + str(e))
        print("Error while scanning image: " + str(e))
        return None
    split_text = text.split("\n")
    split_text = list(filter(None, split_text))
    return split_text


def extract_metadata(result_text, image_path):
    # grab the data we need from the input text
    set_name = result_text[find_index_in_list("Set", result_text) + 1]
    # get partition number via the image path (eg: Partition1Scan1.png would be 1)
    partition_number = re.search(r"Partition(\d+)Scan", image_path).group(1)
    # get the current and max levels of the drive, in the form of Lv. Current/Max
    drive_level = find_string_in_list(
        "/", result_text
    )  # might swap back to "Lv." if this is too permissive
    drive_max_level = drive_level.split("/")[1].strip()
    drive_current_level = re.sub("\D", "", drive_level.split("/")[0])
    # convert a current level of 00 to 0, etc
    if drive_current_level[0] == "0":
        drive_current_level = "0"
    drive_base_stat_combined = result_text[find_index_in_list("Base", result_text) + 1]

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
    # they are found in the text after the "Random Stats" line and before the "Set Effect" line
    # each name has its value right after it, so we can iterate through the text and add the values to the array
    random_stats = []
    already_used_indexes = []
    for i in range(
        find_index_in_list("Random", result_text) + 1,
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
                find_index_in_list("Random", result_text) + 1, len(result_text)
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
    stat, valid_stats
):  # find the closest stat in the input list to the input stat
    cosine = Cosine(2)
    closest_stat = None
    closest_stat_similarity = 0
    for valid_stat in valid_stats:
        similarity = cosine.similarity(stat, valid_stat)
        if similarity > closest_stat_similarity:
            closest_stat_similarity = similarity
            closest_stat = valid_stat

    # if the original stat had a plus modifier (eg: +1 at the end), add it and the following number to the corrected stat
    if "+" in stat:
        closest_stat += stat[stat.index("+") : stat.index("+") + 2]

    # if the closest and original stat are different, log it, use string comparison to check since similarity would also catch substat upgrades
    if closest_stat != stat:
        logging.warning(f"Corrected {stat} to {closest_stat}")

    return closest_stat


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
        for sub_stat_name, sub_stat_value in metadata["random_stats"]:
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
                if ("%" in sub_stat_value or "CRIT" in sub_stat_name) and not any(
                    keyword in sub_stat_name for keyword in ["PEN", "Anomaly"]
                ):
                    expected_sub_stat_value = str(expected_sub_stat_value) + "%"
                if sub_stat_value != expected_sub_stat_value:
                    logging.warning(
                        f"Corrected sub stat {sub_stat_name} value {sub_stat_value} to {expected_sub_stat_value}"
                    )
                    # update the sub stat value to the expected value
                    sub_stat_index = find_index_in_list(
                        old_sub_stat_name,
                        metadata["random_stats"],
                        corrected_sub_stats_ignore_list,
                    )
                    # add the index to the ignore list so we don't double correct it
                    corrected_sub_stats_ignore_list.append(sub_stat_index)
                    metadata["random_stats"][sub_stat_index] = (
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


# the main function that will be called to process the images in orchestrator.py
def imageScanner(queue: Queue):
    setup_logging()
    # scan through all images in the scan_input folder
    scan_data = []
    imagenum = 0
    consecutive_errors = 0
    logging.info("Ready to process disk drives")
    getImagesDone = False
    while not getImagesDone:
        while not queue.empty():
            image_path = queue.get()
            if image_path == "Done":
                getImagesDone = True
                break
            elif (
                image_path == "Error"
            ):  # if the getImages process has crashed, stop the program
                logging.critical(
                    "Failed to get to the equipment screen - try increasing the page load time"
                )
                sys.exit(1)
            logging.info(f"Processing disk drive # {imagenum}, at {image_path}")
            if debug:
                print(f"Processing {image_path}")
            try:
                processed_image = preprocess_image(
                    image_path, target_images_folder="./Target_Images"
                )
                result = scan_image(processed_image)
                result_metadata = extract_metadata(result, image_path)
            except Exception as e:
                logging.error(f"Error analyzing drive #{imagenum}, skipping it: {e}")
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
                scan_data.append(result_metadata)
            else:
                logging.error(
                    f"Disk drive #{imagenum} failed validation, skipping: {error_message}"
                )
            logging.info(f"Finished processing disk drive #{imagenum}")
            consecutive_errors = 0
            imagenum += 1
            if debug:  # log out the output
                for key, value in result_metadata.items():
                    print(f"{key}: {value}")
                print("--------------------------------------------------")

    # write the data to a JSON file for later use inside of the scan_output folder
    logging.info("Finished processing. Writing scan data to file")
    with open("scan_output/scan_data.json", "w") as f:
        json.dump(scan_data, f, indent=4)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # test the scanner on a single image
    save_path = resource_path("./scan_output/Partition3Scan4.png")
    image_path = resource_path("./scan_input/Partition3Scan4.png")
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
