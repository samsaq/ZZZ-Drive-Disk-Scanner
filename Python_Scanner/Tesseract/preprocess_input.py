import pytesseract, os, logging, sys, time
from tesseract_test import preprocess_image, resource_path, setup_logging

# simple script to use the preprocess_image function on all images in a folder

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    log_file_path = resource_path("./input_images_preprocessed/preprocess_input.log")
    setup_logging(log_file_path)
    input_folder = "./input_images"
    output_folder = "./input_images_preprocessed"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for file in os.listdir(input_folder):
        if file.endswith(".png"):
            logging.debug(f"Preprocessing image: {file}")
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file)
            preprocess_image(input_path, output_path)
    print("Done preprocessing images")
    logging.debug("Done preprocessing images")
    logging.shutdown()
