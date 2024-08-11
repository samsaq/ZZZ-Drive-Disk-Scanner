import sys
import os, re, time
from multiprocessing import Process, Queue, freeze_support

# python script that controls the scanning of the disk drives
# logging to file is handled by the the imageScanner.py and getImages.py scripts themselves


def prepareForScan():

    # create the scan_input directory if it doesn't exist
    if not os.path.exists("scan_input"):
        os.makedirs("scan_input")

    # create the scan_output directory if it doesn't exist
    if not os.path.exists("scan_output"):
        os.makedirs("scan_output")

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
    freeze_support()  # Needed to prevent infinite import loop on Windows when building the exe
    overallStartTime = time.time()

    # get current directory so we can return to it later
    current_directory = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    prepareForScan()

    from getImages import getImages
    from imageScanner import imageScanner

    # get  arguments from the command line when running the script
    # this will come in the form of: python orchestrator.py <PageLoadTime> <DiscScanTime>
    # if we don't have the correct number of arguments, we will keep the defaults

    pageLoadTime = 2
    discScanTime = 0.25

    if len(sys.argv) == 3:
        pageLoadTime = float(sys.argv[1])
        discScanTime = float(sys.argv[2])

    image_queue = Queue()
    GetImagesStartTime = time.time()
    GetImagesEndTime = 0
    imageScannerEndTime = 0
    imageScannerStartTime = time.time()
    GetImagesStopped = False
    imageScannerStopped = False
    get_images_process = Process(
        target=getImages, args=((image_queue), (pageLoadTime), (discScanTime))
    )
    image_scanner_process = Process(target=imageScanner, args=(image_queue,))

    get_images_process.start()
    image_scanner_process.start()

    # Monitor the processes - shutdown gracefully if one of them fails
    while True:
        get_images_process.join(timeout=0.1)
        image_scanner_process.join(timeout=0.1)

        if get_images_process.exitcode is not None:
            if get_images_process.exitcode == 1:
                print(
                    "getImages process exited with error code 1. Terminating imageScanner process."
                )
                image_scanner_process.terminate()
                break
            elif get_images_process.exitcode == 0 and not GetImagesStopped:
                print("getImages process completed successfully.")
                GetImagesEndTime = time.time()
                GetImagesStopped = True

        if image_scanner_process.exitcode is not None:
            if image_scanner_process.exitcode == 1:
                print(
                    "imageScanner process exited with error code 1. Terminating getImages process."
                )
                get_images_process.terminate()
                break
            elif image_scanner_process.exitcode == 0 and not imageScannerStopped:
                print("imageScanner process completed successfully.")
                imageScannerEndTime = time.time()
                imageScannerStopped = True

        if not get_images_process.is_alive() and not image_scanner_process.is_alive():
            break

    cleanupImages()

    os.chdir(current_directory)

    print("Get Images Time: ", GetImagesEndTime - GetImagesStartTime)
    print("Image Scanner Time: ", imageScannerEndTime - imageScannerStartTime)
    print("Overall Time: ", time.time() - overallStartTime)
