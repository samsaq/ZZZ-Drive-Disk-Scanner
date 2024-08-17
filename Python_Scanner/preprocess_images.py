import os, cv2


# given a path, preprocess the image for tesseract
def preprocess_image(
    image_path, save_path=None, target_images_folder="../Target_Images"
):
    rarity_icon_threshold = 0.8
    agent_icon_threshold = 0.8
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # non-adaptive thresholding
    threshold, binary_image = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # clean up the image
    # remove rarity icons
    s_rank_icon = cv2.imread(
        os.path.join(target_images_folder, "zzz-disk-drive-S-icon.png"),
        cv2.IMREAD_GRAYSCALE,
    )
    a_rank_icon = cv2.imread(
        os.path.join(target_images_folder, "zzz-disk-drive-A-icon.png"),
        cv2.IMREAD_GRAYSCALE,
    )
    b_rank_icon = cv2.imread(
        os.path.join(target_images_folder, "zzz-disk-drive-B-icon.png"),
        cv2.IMREAD_GRAYSCALE,
    )

    # see if any of the rarity icons are in the image (there should only be one instance of one of them)
    try:
        s_rank_match = cv2.matchTemplate(
            binary_image, s_rank_icon, cv2.TM_CCOEFF_NORMED
        )
        a_rank_match = cv2.matchTemplate(
            binary_image, a_rank_icon, cv2.TM_CCOEFF_NORMED
        )
        b_rank_match = cv2.matchTemplate(
            binary_image, b_rank_icon, cv2.TM_CCOEFF_NORMED
        )
    except cv2.error:
        s_rank_match = None
        a_rank_match = None
        b_rank_match = None

    rank_match = None

    # if any of the icons are found, set their area black
    if (
        cv2.minMaxLoc(s_rank_match)[1] > rarity_icon_threshold
        and s_rank_match is not None
    ):
        binary_image[
            cv2.minMaxLoc(s_rank_match)[3][1] : cv2.minMaxLoc(s_rank_match)[3][1]
            + s_rank_icon.shape[0],
            cv2.minMaxLoc(s_rank_match)[3][0] : cv2.minMaxLoc(s_rank_match)[3][0]
            + s_rank_icon.shape[1],
        ] = 0
        rank_match = s_rank_match
    if (
        cv2.minMaxLoc(a_rank_match)[1] > rarity_icon_threshold
        and a_rank_match is not None
    ):
        binary_image[
            cv2.minMaxLoc(a_rank_match)[3][1] : cv2.minMaxLoc(a_rank_match)[3][1]
            + a_rank_icon.shape[0],
            cv2.minMaxLoc(a_rank_match)[3][0] : cv2.minMaxLoc(a_rank_match)[3][0]
            + a_rank_icon.shape[1],
        ] = 0
        rank_match = a_rank_match
    if (
        cv2.minMaxLoc(b_rank_match)[1] > rarity_icon_threshold
        and b_rank_match is not None
    ):
        binary_image[
            cv2.minMaxLoc(b_rank_match)[3][1] : cv2.minMaxLoc(b_rank_match)[3][1]
            + b_rank_icon.shape[0],
            cv2.minMaxLoc(b_rank_match)[3][0] : cv2.minMaxLoc(b_rank_match)[3][0]
            + b_rank_icon.shape[1],
        ] = 0
        rank_match = b_rank_match
    # remove agent icons
    # this should be done without recognition, as we don't know what the agent icons look like
    # the position of the agent icons can be done by enlarging the bounding box of the rarity icons
    # by a modifier, and then keeping the same y position but adjusting the x position so that the
    # edge of the bounding box hits the right side of the image

    agent_icon_size_modifier = 1.5
    agent_icon_y_offset = 0

    # calculate the agent icon bounding box
    if rank_match is not None:
        agent_icon_y = cv2.minMaxLoc(rank_match)[3][1] + agent_icon_y_offset
        agent_icon_width = int(s_rank_icon.shape[1] * agent_icon_size_modifier)
        agent_icon_height = int(s_rank_icon.shape[0] * agent_icon_size_modifier)

        # now push the agent icon bounding box to the right edge of the image
        agent_icon_x = binary_image.shape[1] - agent_icon_width

        # adjust the y offset so that the bounding box is centered on the same y position
        agent_icon_y = agent_icon_y - (agent_icon_height - s_rank_icon.shape[0]) // 2

        # set the agent icon bounding box to black
        binary_image[
            agent_icon_y : agent_icon_y + agent_icon_height,
            agent_icon_x : agent_icon_x + agent_icon_width,
        ] = 0

    # downscale the image so that it is 256 pixels wide, and keep the aspect ratio
    # we do this to keep the font size in the ideal range for tessaract (20px high capitals)
    # calculate the scaling factor
    desired_width = 384
    scaling_factor = desired_width / binary_image.shape[1]
    # calculate the new height
    desired_height = int(binary_image.shape[0] * scaling_factor)

    # resize the image
    binary_image = cv2.resize(
        binary_image, (desired_width, desired_height), interpolation=cv2.INTER_AREA
    )

    # Save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # test the function
    image_path = "./scan_input/Partition1Scan7.png"
    save_path = "./scan_output/preprocessed_image_test.png"
    processed_image = preprocess_image(
        image_path, save_path=save_path, target_images_folder="./Target_Images"
    )
