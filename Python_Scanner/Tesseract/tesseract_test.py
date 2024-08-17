# lets scan an image in Target_Images and see what we get using tessaract
import pytesseract, os, logging, sys, time


# import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocess_images import preprocess_image


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


# NOTE: you can also pass in cv2 image object instead of image path
def scan_image(image_path):
    config = "--oem 1 -l ZZZ --tessdata-dir ./models"  # testing model
    try:
        text = pytesseract.image_to_string(image_path, config=config)
    except Exception as e:
        logging.error("Error while scanning image: ", e)
        print("Error while scanning image: ", e)
        return None
    split_text = text.split("\n")
    split_text = list(filter(None, split_text))
    return split_text


def preprocess_and_scan_image(image_path):
    preprocessed_image = preprocess_image(image_path, save_path=processed_path)
    return scan_image(preprocessed_image)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    overallStartTime = time.time()
    log_file_path = resource_path("tesseract-test.log")
    setup_logging(log_file_path)
    image_path = resource_path("../scan_input/Partition1Scan9.png")
    processed_path = image_path.replace(".png", "_processed_test.png")
    processStartTime = time.time()
    processedImage = preprocess_image(
        image_path, target_images_folder="../Target_Images"
    )
    processEndTime = time.time()
    result = scan_image(processedImage)
    print("Result: ", result)
    overallEndTime = time.time()
    print("Processing time: ", processEndTime - processStartTime)
    print("Scan Time: ", overallEndTime - processEndTime)
    print("Overall time: ", overallEndTime - overallStartTime)
