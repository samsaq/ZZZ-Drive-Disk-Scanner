import os, re, time
from multiprocessing import Process, Queue

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

    # Rename the old log files to make room for the new log file if there is a log.txt file
    if os.path.exists("scan_output/log.txt"):
        for i in reversed(range(len(old_log_files))):
            new_index = (
                i + 2
            )  # We add 2 because the existing files need to move up one position, starting from 1
            old_name = old_log_files[i]
            new_name = f"old_log_{new_index}.txt"
            os.rename(
                os.path.join("scan_output", old_name),
                os.path.join("scan_output", new_name),
            )

    # rename the current log file to old_log_1.txt
    if os.path.exists("scan_output/log.txt"):
        os.rename("scan_output/log.txt", "scan_output/old_log_1.txt")

    # refresh the old_log_files list with the new names so we can delete the oldest ones if needed
    old_log_files = []
    for file in os.listdir("scan_output"):
        if re.match(r"old_log_\d+.txt", file):
            old_log_files.append(file)

    old_log_files.sort(key=lambda x: int(re.search(r"\d+", x).group()))

    # if we have more than 10 old log files, delete the oldest ones until we have 10
    while len(old_log_files) > 10:
        os.remove("scan_output/" + old_log_files.pop(len(old_log_files) - 1))


def cleanupImages():
    # delete old .png images in the scan_input directory
    for file in os.listdir("scan_input"):
        if file.endswith(".png"):
            os.remove("scan_input/" + file)


if __name__ == "__main__":
    overallStartTime = time.time()

    # get current directory so we can return to it later
    current_directory = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    prepareForScan()
    from getImages import getImages
    from imageScanner import imageScanner

    image_queue = Queue()
    GetImagesStartTime = time.time()
    imageScannerStartTime = time.time()
    get_images_process = Process(target=getImages, args=(image_queue,))
    image_scanner_process = Process(target=imageScanner, args=(image_queue,))

    get_images_process.start()
    image_scanner_process.start()

    get_images_process.join()
    GetImagesEndTime = time.time()
    image_scanner_process.join()
    imageScannerEndTime = time.time()

    cleanupImages()

    os.chdir(current_directory)

    print("Get Images Time: ", GetImagesEndTime - GetImagesStartTime)
    print("Image Scanner Time: ", imageScannerEndTime - imageScannerStartTime)
    print("Overall Time: ", time.time() - overallStartTime)
