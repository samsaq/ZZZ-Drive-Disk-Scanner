import logging, sys, cv2, os
from generate_synth_data import (
    generate_number,  # these three are passed into the generate_synthetic_data function to tell it what to generate
    generate_percentage,
    generate_set_name,
    generate_main_stat,
    generate_sub_stat,
    generate_lvl_string,
    generate_synthetic_data,
)
from generate_training_data import (
    create_data_dirs,
    generate_easyocr_training_data,
)

# import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocess_images import preprocess_image

# the overarching script that will convert the input images to training data
# incorporates the following scripts:
# 1. generate_training_data.py
# 2. generate_synth_data.py

# Uses the ratios defined below to generate synthetic data to augment the real training data
ratio_synth_to_real = 0.2  # 20% of the final training data is synthetic
ratio_synth_number = 0.1
ratio_synth_percentage = 0.1
ratio_synth_set_names = 0.2
ratio_synth_main_stats = 0.1
ratio_synth_sub_stats = 0.2
ratio_synth_lvl_strings = 0.3

# set these variables to determine input and output folders
input_images_folder = "./input_images"
preprocessed_images_folder = "./input_images_preprocessed"
output_line_images_folder = "./training_data/synth_sub_images"
output_gt_folder = "./training_data/synth_txt_truths"


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
    num_synth_main_stats = int(num_synth_data * ratio_synth_main_stats)
    num_synth_sub_stats = int(num_synth_data * ratio_synth_sub_stats)
    num_synth_lvl_strings = int(num_synth_data * ratio_synth_lvl_strings)

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
    generate_synthetic_data(
        num_synth_main_stats,
        output_line_images_folder,
        output_gt_folder,
        resource_path("./training_data/ZZZ-Font.ttf"),
        generate_main_stat,
    )
    generate_synthetic_data(
        num_synth_sub_stats,
        output_line_images_folder,
        output_gt_folder,
        resource_path("./training_data/ZZZ-Font.ttf"),
        generate_sub_stat,
    )
    generate_synthetic_data(
        num_synth_lvl_strings,
        output_line_images_folder,
        output_gt_folder,
        resource_path("./training_data/ZZZ-Font.ttf"),
        generate_lvl_string,
    )

    # preprocess the input images
    for file in os.listdir(input_images_folder):
        if file.endswith(".png"):
            logging.debug(f"Preprocessing image: {file}")
            input_path = os.path.join(input_images_folder, file)
            output_path = os.path.join(preprocessed_images_folder, file)
            preprocess_image(
                input_path, output_path, target_images_folder="../Target_Images"
            )

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
    # make sure all the synth ratios add up to 1
    print(
        "Synth Ratios Total: "
        + str(
            ratio_synth_number
            + ratio_synth_percentage
            + ratio_synth_set_names
            + ratio_synth_main_stats
            + ratio_synth_sub_stats
            + ratio_synth_lvl_strings
        )
    )
    assert (
        ratio_synth_number
        + ratio_synth_percentage
        + ratio_synth_set_names
        + ratio_synth_main_stats
        + ratio_synth_sub_stats
        + ratio_synth_lvl_strings
        == 1
    )
    # process_input()

    # generate the synthetic data based on the ratios
    num_generated = 2000
    # calc the numbers per type
    num_synth_number = int(num_generated * ratio_synth_number)
    num_synth_percentage = int(num_generated * ratio_synth_percentage)
    num_synth_set_names = int(num_generated * ratio_synth_set_names)
    num_synth_main_stats = int(num_generated * ratio_synth_main_stats)
    num_synth_sub_stats = int(num_generated * ratio_synth_sub_stats)
    num_synth_lvl_strings = int(num_generated * ratio_synth_lvl_strings)

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
    generate_synthetic_data(
        num_synth_main_stats,
        output_line_images_folder,
        output_gt_folder,
        resource_path("./training_data/ZZZ-Font.ttf"),
        generate_main_stat,
    )
    generate_synthetic_data(
        num_synth_sub_stats,
        output_line_images_folder,
        output_gt_folder,
        resource_path("./training_data/ZZZ-Font.ttf"),
        generate_sub_stat,
    )
    generate_synthetic_data(
        num_synth_lvl_strings,
        output_line_images_folder,
        output_gt_folder,
        resource_path("./training_data/ZZZ-Font.ttf"),
        generate_lvl_string,
    )
