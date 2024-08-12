# lets scan an image in Target_Images and see what we get using tessaract

import pytesseract, os, logging, sys, time


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
    sys.excepthook = exception_hook


def exception_hook(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit()


# given a path, preprocess the image for tesseract
def preprocess_image(image_path):
    print("Preprocessing image at ", image_path)
    # TODO: Implement image preprocessing (Binirization, Noise removal, etc.)
    # Text uses a specific color of white, so we can binarize the image to make it easier for tesseract to read


def scan_image(image_path):
    config = "--oem 3"  # testing different engines
    print("Scanning image at ", image_path)
    try:
        text = pytesseract.image_to_data(image_path, config=config)
    except Exception as e:
        logging.error("Error while scanning image: ", e)
        print("Error while scanning image: ", e)
        return None
    print("Scanned text: ", text)
    return text


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    log_file_path = resource_path("tesseract-test.log")
    setup_logging(log_file_path)
    result = None
    startTime = None
    endTime = None
    try:
        startTime = time.time()
        result = scan_image("./Target_Images/zzz-example-disc-drive.png")
        endTime = time.time()
    except Exception as e:
        logging.error("Error while scanning image: ", e)
        print("Error while scanning image: ", e)
    print("Done scanning image")
    logging.info("Done scanning image")
    logging.info("Scanned result: ")
    if startTime and endTime:
        logging.info("Time taken: " + str(endTime - startTime))
        print("Time taken: " + str(endTime - startTime))
    logging.info(str(result))
    logging.shutdown()
