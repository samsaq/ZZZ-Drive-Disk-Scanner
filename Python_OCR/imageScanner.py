import re
from paddleocr import PaddleOCR, draw_ocr
import os
import json
import logging
import strsimpy  # used for string cosine similarity
from validMetadata import (
    valid_set_names,
    valid_partition_1_main_stats,
    valid_partition_2_main_stats,
    valid_partition_3_main_stats,
    valid_partition_4_main_stats,
    valid_partition_5_main_stats,
    valid_partition_6_main_stats,
    valid_random_stats,
)

debug = False
loglevel = logging.DEBUG if debug else logging.INFO
logging.basicConfig(
    level=loglevel,
    filename="scan_output/log.txt",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True,  # used to allow logging to work even when running in IDE
)


ocr = PaddleOCR(use_angle_cls=True, lang="en")  # loads the model into memory


# scan a list of strings to see if the input substring is in one of the strings in the list, return the whole string if found
def find_string_in_list(substring, string_list):
    for string in string_list:
        if substring in string:
            return string
    logging.error(f"Could not find {substring} in the list")
    return None


# same as above, but return the index of the string in the list instead of the string itself
def find_index_in_list(substring, string_list):
    for i in range(len(string_list)):
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


# scan an image from a given path, and return the result
def scan_image(image_path):
    result = ocr.ocr(image_path, cls=True)
    return result


def result_text(result):
    # clean the result to only include the text instead of with coordinates, weights, etc
    data = result[0]
    txts = [line[1][0] for line in data]
    return txts


def extract_metadata(result_text):
    # grab the data we need from the input text
    set_name = result_text[find_index_in_list("Set Effect", result_text) + 1]
    # the number in the [] brackets is the partition_number (eg: [1] means partition 1), search through the text to find the partition_number
    partition_number = None
    for text in result_text:
        if "[" in text and "]" in text:
            # get the number between the brackets
            partition_number = text[text.index("[") + 1 : text.index("]")]
            break
    # get the current and max levels of the drive, in the form of Lv. Current/Max
    drive_level = find_string_in_list("Lv.", result_text)
    drive_max_level = drive_level.split("/")[1].strip()
    drive_current_level = re.sub("\D", "", drive_level.split("/")[0])
    # convert a current level of 00 to 0, etc
    if drive_current_level[0] == "0":
        drive_current_level = "0"
    drive_base_stat = result_text[find_index_in_list("Base Stat", result_text) + 1]
    drive_base_stat_number = result_text[
        find_index_in_list("Base Stat", result_text) + 2
    ]
    # the random stats of the drive should be stored as a pair, with the stat name and its value
    # they are found in the text after the "Random Stats" line and before the "Set Effect" line
    # each name has its value right after it, so we can iterate through the text and add the values to the array
    random_stats = []
    cur_random_stat_name = None
    for i in range(
        find_index_in_list("Random Stats", result_text) + 1,
        find_index_in_list("Set Effect", result_text),
    ):
        # if numeric or ends in a %, it is a stat value, otherwise it is a stat name
        if result_text[i].isnumeric() or result_text[i].endswith("%"):
            random_stats.append((cur_random_stat_name, result_text[i]))
        else:
            cur_random_stat_name = result_text[i]

    return {
        "set_name": set_name,
        "partition_number": partition_number,
        "drive_rarity": drive_rarity_from_max_level(int(drive_max_level)),
        "drive_current_level": drive_current_level,
        "drive_max_level": drive_max_level,
        "drive_base_stat": drive_base_stat,
        "drive_base_stat_number": drive_base_stat_number,
        "random_stats": random_stats,
    }


def find_closest_stat(
    stat, valid_stats
):  # find the closest stat in the input list to the input stat
    cosine = strsimpy.Cosine(2)
    closest_stat = None
    closest_stat_similarity = 0
    for valid_stat in valid_stats:
        similarity = cosine.similarity(stat, valid_stat)
        if similarity > closest_stat_similarity:
            closest_stat_similarity = similarity
            closest_stat = valid_stat
    # if closest stat similarity is les than 1, then the stat was corrected, log it
    if closest_stat_similarity < 1:
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


def __main__():
    # scan through all images in the scan_input folder
    scan_data = []
    imagenum = 0
    logging.info("Starting to scan disk drives")
    for image_path in os.listdir("scan_input"):
        # get the path to the image from here
        image_path = "scan_input/" + image_path
        logging.info(f"Scanning disk drive # {imagenum}, at {image_path}")
        if debug:
            print(f"Scanning {image_path}")
        result = result_text(scan_image(image_path))
        result_metadata = extract_metadata(result)
        correct_metadata(result_metadata)
        scan_data.append(result_metadata)
        logging.info(f"Finished scanning disk drive #{imagenum}")
        imagenum += 1
        if debug:  # log out the output
            for key, value in result_metadata.items():
                print(f"{key}: {value}")
            print("--------------------------------------------------")

    # write the data to a JSON file for later use inside of the scan_output folder
    logging.info("Finished Scanning. Writing scan data to scan_output/scan_data.json")
    with open("scan_output/scan_data.json", "w") as f:
        json.dump(scan_data, f, indent=4)


if __name__ == "__main__":
    __main__()
