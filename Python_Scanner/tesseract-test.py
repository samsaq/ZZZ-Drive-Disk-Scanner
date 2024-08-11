# lets scan an image in Target_Images and see what we get using tessaract

import pytesseract


def scan_image(image_path):
    print("Scanning image at ", image_path)
    text = pytesseract.image_to_data(image_path)
    print("Scanned text: ", text)


if __name__ == "__main__":
    scan_image("Target_Images/zzz-equipment-button.png")
