import math
import os
import sys
import pyautogui
import logging
from keyboard import press
from multiprocessing import Queue


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


def switchToZZZ():
    logging.info("Switching to ZenlessZoneZero")
    ZZZWindow = pyautogui.getWindowsWithTitle("ZenlessZoneZero")[0]
    if ZZZWindow.isActive == False:
        pyautogui.press(
            "altleft"
        )  # Somehow this is needed to switch to the window, Why though?
        ZZZWindow.activate()
    logging.info("Switched to ZenlessZoneZero")


def getToEquipmentScreen(queue: Queue, pageLoadTime):
    logging.info("Getting to the equipment screen")
    # press c to get to the character screen
    press("c")
    logging.info("Pressed c for character screen")
    # wait for the character screen to load
    pyautogui.sleep(pageLoadTime)
    # adjust the target based on devMode
    target = "./Target_Images/zzz-equipment-button.png"
    # press the equipment button to get to the equipment screen
    try:
        equipmentButton = pyautogui.locateOnScreen(target, confidence=0.8)
    except Exception as e:
        logging.error(f"Error locating equipment button:  + {e}")
        logging.error(f"Current directory: {os.getcwd()}")
    logging.info("Located equipment button: " + str(equipmentButton))
    if equipmentButton == None:
        logging.error("Equipment button not found")
        print("Equipment button not found")
        queue.put("Error")  # cause the process to end early
        sys.exit(1)
    pyautogui.click(equipmentButton)
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
    columnNumber = 4  # in 1440p, we have 4 columns
    rowNumber = 5  # in 1440p, we have 5 rows
    endOfDiskDrives = scanForEndOfDiskDrives(distanceBetwenRows)

    pyautogui.moveTo(startPosition)

    # loop through this row of disk drives
    # if the end of the disk drives is visible, we'll need to figure out which of the 4 columns is the last one
    # and only continue down the row until we reach the last column with a disk drive

    curRowStart = startPosition
    scanNumber = 1
    while not endOfDiskDrives:  # scan until the last row is visible on the screen
        scanNumber = scanRow(
            columnNumber,
            curRowStart,
            distanceBetwenColumns,
            partitionNumber,
            queue,
            discScanTime,
            scanNumber,
        )
        pyautogui.scroll(-1)
        endOfDiskDrives = scanForEndOfDiskDrives(distanceBetwenRows)

    scanNumber = scanRow(  # scan the top row of the final page of disk drives
        columnNumber,
        curRowStart,
        distanceBetwenColumns,
        partitionNumber,
        queue,
        discScanTime,
        scanNumber,
    )
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
    pyautogui.click()
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
    pyautogui.click()
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


def scanForEndOfDiskDrives(distanceBetwenRows, rowNumber=None):

    if rowNumber == None:
        try:
            target = "./Target_Images/zzz-no-disk-drive-icon.png"
            endOfDiskDrivesIcon = pyautogui.locateOnScreen(
                target,
                confidence=0.8,
            )
        except:
            endOfDiskDrivesIcon = False

        try:
            target = "./Target_Images/zzz-no-disk-drive-scrollbar.png"
            endOfDiskDrivesScrollbar = pyautogui.locateOnScreen(
                target,
                confidence=0.95,
            )
        except:
            endOfDiskDrivesScrollbar = False
        # return false if both the icon and the scrollbar are not visible
        if endOfDiskDrivesIcon == False and endOfDiskDrivesScrollbar == False:
            return False
        # else, return the one that is not false
        if endOfDiskDrivesIcon != False:
            return endOfDiskDrivesIcon
        return endOfDiskDrivesScrollbar

    rowModifier = 0.1 + (distanceBetwenRows * (rowNumber - 1))

    # check if the end of the disk drives is visible
    endOfDiskDrives = False
    try:
        target = "./Target_Images/zzz-no-disk-drive-icon.png"
        endOfDiskDrives = pyautogui.locateOnScreen(
            target,
            confidence=0.8,
            region=(
                int(0.04 * screenWidth),  # left
                int(rowModifier * screenHeight),  # top
                int(0.275 * screenWidth),  # width
                int(0.125 * screenHeight),  # height
            ),
        )
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


# the main function that will be called to get the images by the orchestrator
def getImages(queue: Queue, pageLoadTime, discScanTime):
    log_file_path = resource_path("scan_output/templog.txt")
    setup_logging(log_file_path)
    switchToZZZ()
    getToEquipmentScreen(queue, pageLoadTime)
    # go through the 6 partitions
    for i in range(1, 7):
        selectParition(i)
        scanPartition(i, queue, discScanTime)
    # put a message in the queue to signal the end of the image collection
    queue.put("Done")


# a test function to run the getImages function
if __name__ == "__main__":
    getImages(Queue(), 2, 0.25)
