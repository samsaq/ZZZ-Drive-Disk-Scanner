import re
from paddleocr import PaddleOCR, draw_ocr
import os

ocr = PaddleOCR(use_angle_cls=True, lang="en")  # loads the model into memory


# scan a list of strings to see if the input substring is in one of the strings in the list, return the whole string if found
def find_string_in_list(substring, string_list):
    for string in string_list:
        if substring in string:
            return string
    print(f"Could not find {substring} in the list")
    return None


# same as above, but return the index of the string in the list instead of the string itself
def find_index_in_list(substring, string_list):
    for i in range(len(string_list)):
        if substring in string_list[i]:
            return i
    print(f"Could not find {substring} in the list")
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
    set_name = result_text[result_text.index("Set Effect") + 1]
    # the number in the [] brackets is the drive_number (eg: [1] means slot 1), search through the text to find the drive_number
    drive_number = None
    for text in result_text:
        if "[" in text and "]" in text:
            # get the number between the brackets
            drive_number = text[text.index("[") + 1 : text.index("]")]
            break
    # get the current and max levels of the drive, in the form of Lv. Current/Max
    drive_level = find_string_in_list("Lv.", result_text)
    drive_max_level = drive_level.split("/")[1]
    drive_current_level = drive_level.split("/")[0].split(" ")[1]
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
        "drive_number": drive_number,
        "drive_rarity": drive_rarity_from_max_level(int(drive_max_level)),
        "drive_current_level": drive_current_level,
        "drive_max_level": drive_max_level,
        "drive_base_stat": drive_base_stat,
        "drive_base_stat_number": drive_base_stat_number,
        "random_stats": random_stats,
    }


def __main__():
    # scan through all images in the scan_input folder, print the result for each separately
    for image_path in os.listdir("scan_input"):
        # get the path to the image from here
        image_path = "scan_input/" + image_path
        result = result_text(scan_image(image_path))
        result_metadata = extract_metadata(result)
        for key, value in result_metadata.items():
            print(f"{key}: {value}")
        print("--------------------------------------------------")


if __name__ == "__main__":
    __main__()
