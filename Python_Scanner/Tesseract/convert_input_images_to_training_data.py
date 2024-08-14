import logging, sys, cv2, os
from generate_synth_data import (
    generate_number,  # these three are passed into the generate_synthetic_data function to tell it what to generate
    generate_percentage,
    generate_set_name,
    generate_synthetic_data,
)
from generate_training_data import (
    create_data_dirs,
    generate_easyocr_training_data,
)

# the overarching script that will convert the input images to training data
# incorporates the following scripts:
# 1. generate_training_data.py
# 2. generate_synth_data.py

# Uses the ratios defined below to generate synthetic data to augment the real training data
ratio_synth_to_real = 0.2  # 20% of the final training data is synthetic
ratio_synth_number = 0.2  # 20% of the synth data is synthetic numbers
ratio_synth_percentage = 0.2  # 20% of the synth data is synthetic percentages
ratio_synth_set_names = 0.6  # 60% of the synth data is synthetic set names

# set these variables to determine input and output folders
input_images_folder = "./input_images"
preprocessed_images_folder = "./input_images_preprocessed"
output_line_images_folder = "./training_data/sub_images"
output_gt_folder = "./training_data/txt_truths"


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
def preprocess_image(image_path, save_path=None):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # non-adaptive thresholding
    threshold, binary_image = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image


def process_input():
    create_data_dirs()
    # check how many images are in the input folder
    num_images = len(
        [file for file in os.listdir(input_images_folder) if file.endswith(".png")]
    )

    # calculate how many synthetic pairs to generate
    num_synth_data = int(num_images * ratio_synth_to_real)
    num_synth_number = int(num_synth_data * ratio_synth_number)
    num_synth_percentage = int(num_synth_data * ratio_synth_percentage)
    num_synth_set_names = int(num_synth_data * ratio_synth_set_names)

    # generate the synthetic data
    generate_synthetic_data(
        num_synth_number,
        output_line_images_folder,
        output_gt_folder,
        resource_path("./training_data/ZZZ-Font.ttf"),
        generate_number,
    )
    generate_synthetic_data(
        num_synth_percentage,
        output_line_images_folder,
        output_gt_folder,
        resource_path("./training_data/ZZZ-Font.ttf"),
        generate_percentage,
    )
    generate_synthetic_data(
        num_synth_set_names,
        output_line_images_folder,
        output_gt_folder,
        resource_path("./training_data/ZZZ-Font.ttf"),
        generate_set_name,
    )

    # preprocess the input images
    for file in os.listdir(input_images_folder):
        if file.endswith(".png"):
            logging.debug(f"Preprocessing image: {file}")
            input_path = os.path.join(input_images_folder, file)
            output_path = os.path.join(preprocessed_images_folder, file)
            preprocess_image(input_path, output_path)

    # generate the training data
    generate_easyocr_training_data(
        preprocessed_images_folder, output_line_images_folder, output_gt_folder
    )
    print("Done converting input images to training data")
    print("Use the Data Verifier to manually review the generated training data")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    log_file_path = resource_path("convert_input_images_to_training_data.log")
    setup_logging(log_file_path)
    process_input()
