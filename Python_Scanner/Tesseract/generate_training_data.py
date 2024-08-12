import math
import os, logging, sys
import easyocr, cv2
from PIL import Image

easyocr_reader = easyocr.Reader(["en"])


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


def scan_image(image_path):
    logging.debug(f"Scanning image at {image_path}")
    result = easyocr_reader.readtext(image_path, detail=1)
    logging.debug(f"Scanning result Done")
    return result


def draw_boxes(image_path, result):
    image = cv2.imread(image_path)
    for detection in result:
        top_left = tuple(detection[0][0])
        bottom_right = tuple(detection[0][2])
        text = detection[1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        image = cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 3)
        image = cv2.putText(
            image, text, top_left, font, 0.5, (255, 255, 255), 2, cv2.LINE_AA
        )
    return image


# used to make sure image slicing doesn't go out of bounds and slicing is done with integers
def clamp(value, min_value, max_value):
    if not isinstance(max_value, int):  # make sure max_value is an integer
        max_value = math.floor(max_value)
    rounded_value = math.ceil(value)
    return min(max(min_value, rounded_value), max_value)


def snip_boxes(image_path, result):
    logging.debug(f"Snipping boxes from {image_path}")
    image = cv2.imread(image_path)
    sub_images = []
    for detection in result:
        top_left = tuple(detection[0][0])
        bottom_right = tuple(detection[0][2])

        # Snip out the sub-image using the bounding box coordinates, round up to the nearest integer but don't go out of bounds
        top_left = (
            clamp(top_left[0], 0, image.shape[1]),
            clamp(top_left[1], 0, image.shape[0]),
        )
        bottom_right = (
            clamp(bottom_right[0], 0, image.shape[1]),
            clamp(bottom_right[1], 0, image.shape[0]),
        )
        sub_image = image[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]

        # Append the sub-image to the list
        sub_images.append(sub_image)

    return sub_images


# take a result and generate a ground truth list element for it for each bounding box (aka snipped image)
def generate_ground_truth(image_path, result):
    logging.debug(f"Generating ground truths for {image_path}")
    image_name = os.path.basename(image_path)
    image_name = os.path.splitext(image_name)[0]
    sub_image_truths = []
    # for each detection, append a ground truth element to the list of it's bounding box and text
    for detection in result:
        top_left = tuple(detection[0][0])
        bottom_right = tuple(detection[0][2])
        text = detection[1]
        sub_image_truths.append(
            {
                "image_name": image_name,
                "top_left": top_left,
                "bottom_right": bottom_right,
                "text": text,
            }
        )
    return sub_image_truths


# combine the scan_image and draw_boxes functions to scan an image and draw the bounding boxes on it
def annotate_image(image_path):
    result = scan_image(image_path)
    image = draw_boxes(image_path, result)
    return image


# combine the scan_image and snip_boxes functions to scan an image and snip out the bounding boxes
def snip_image(image_path):
    result = scan_image(image_path)
    sub_images = snip_boxes(image_path, result)
    return sub_images


def save_image(image, save_path):
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    image_pil.save(save_path)


def generate_line_images_and_ground_truths(image_path):
    result = scan_image(image_path)
    sub_images = snip_boxes(image_path, result)
    ground_truths = generate_ground_truth(image_path, result)
    return sub_images, ground_truths


# save snipped images and their ground truths
def save_generated(sub_images, ground_truths, png_dir, gt_dir):
    original_image_name = ground_truths[0]["image_name"]
    # for sub images, use the original image name and append the index of the sub image after a -
    # sub images go to the png_dir, and ground truths go to the gt_dir
    for i, sub_image in enumerate(sub_images):
        sub_image_name = f"{original_image_name}-{i}"
        save_image(sub_image, f"{png_dir}/{sub_image_name}.png")
        with open(f"{gt_dir}/{sub_image_name}.gt.txt", "w") as f:
            f.write(f"{ground_truths[i]['text']}")

    print("Done saving generated images and ground truths")


# create line images and groun truths and save them given a folder, using .pngs within the folder
# combines most of the other functions in this file to do so
# creates initial training data for tesseract based on a heavier model (in this case, easyocr) - still needs manual verification
def generate_easyocr_training_data(input_folder, sub_image_dir, gt_dir):
    png_files = [f for f in os.listdir(input_folder) if f.endswith(".png")]
    png_files.sort()
    for file in png_files:
        image_path = os.path.join(input_folder, file)
        sub_images, ground_truths = generate_line_images_and_ground_truths(image_path)
        save_generated(sub_images, ground_truths, sub_image_dir, gt_dir)


# create the sub_images and txt_truths directories if they don't exist
# Exists so that git cloned projects don't have to create these directories manually
def create_test_dirs():
    if not os.path.exists("./training_data/sub_images"):
        os.makedirs("./training_data/sub_images")
    if not os.path.exists("./training_data/txt_truths"):
        os.makedirs("./training_data/txt_truths")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # NOTE: The Error closing: Operation on closed image error seems to be caused by easyocr's reader closing the image redundantly - can be ignored
    setup_logging(resource_path("./training_data/training_data_generation.log"))
    create_test_dirs()
    generate_easyocr_training_data(
        "./input_images_preprocessed",
        "./training_data/sub_images",
        "./training_data/txt_truths",
    )
