import os, re

# python script that controls the scanning of the disk drives
# logging to file is handled by the the imageScanner.py and getImages.py scripts themselves


def prepareForScan():

    # delete old .png images in the scan_input directory
    for file in os.listdir("scan_input"):
        if file.endswith(".png"):
            os.remove("scan_input/" + file)

    # delete old .json file in the scan_output directory
    if os.path.exists("scan_output/scan_data.json"):
        os.remove("scan_output/scan_data.json")

    # find any old log files in the scan_output directory
    old_log_files = []
    for file in os.listdir("scan_output"):
        if re.match(r"old_log_\d+.txt", file):
            old_log_files.append(file)

    # sort the old log files by the number suffix, smallest to largest (eg: old_log_1.txt, old_log_2.txt, etc)
    old_log_files.sort(key=lambda x: int(re.search(r"\d+", x).group()))

    # if we have 10 old log files, delete the oldest one
    if len(old_log_files) == 10:
        os.remove("scan_output/" + old_log_files[0])

    # rename the old log files to make room for the new log file
    for i in range(len(old_log_files)):
        os.rename(
            "scan_output/" + old_log_files[i],
            "scan_output/old_log_" + str(i + 1) + ".txt",
        )

    # rename the current log file to old_log_1.txt
    if os.path.exists("scan_output/log.txt"):
        os.rename("scan_output/log.txt", "scan_output/old_log_1.txt")


if __name__ == "__main__":
    # get current directory so we can return to it later
    current_directory = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    from getImages import getImages
    from imageScanner import imageScanner

    getImages()
    imageScanner()
    os.chdir(current_directory)
