import os, cv2
from typing import Literal
from getImages import ScreenResolution
from ui_elements import ExistingScreenshotMatcher, UIElement


# given a path, preprocess the image for tesseract - for disk drive images
def preprocess_image(
    image_path,
    screen_width: int,
    screen_height: int,
    save_path=None,
    target_images_folder="./Target_Images",
):

    rarity_icon_threshold = 0.8
    agent_icon_threshold = 0.8
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply threshold
    threshold, binary_image = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Create a matcher directly with the binary image
    binary_image_bgr = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)
    ui_matcher = ExistingScreenshotMatcher(
        binary_image_bgr, screen_width, screen_height
    )

    # Define UI elements for ranks
    rank_elements = {
        "S": UIElement(
            name="rank_S",
            template_path=os.path.join(
                target_images_folder, "zzz-disk-drive-S-icon.png"
            ),
            confidence=rarity_icon_threshold,
        ),
        "A": UIElement(
            name="rank_A",
            template_path=os.path.join(
                target_images_folder, "zzz-disk-drive-A-icon.png"
            ),
            confidence=rarity_icon_threshold,
        ),
        "B": UIElement(
            name="rank_B",
            template_path=os.path.join(
                target_images_folder, "zzz-disk-drive-B-icon.png"
            ),
            confidence=rarity_icon_threshold,
        ),
    }

    # Find the best match among all ranks
    best_match = {"score": 0, "rank": None, "details": None}

    for rank, element in rank_elements.items():
        try:
            match_details = ui_matcher.locate_element_with_details(element)
            if match_details["score"] > best_match["score"]:
                best_match = {
                    "score": match_details["score"],
                    "rank": rank,
                    "details": match_details,
                }
        except Exception as e:
            print(f"Error matching {rank} icon: {e}")
            print(f"Template path: {element.template_path}")
            print(
                f"Binary image shape: {binary_image_bgr.shape}, type: {binary_image_bgr.dtype}"
            )
            # Try to load the template directly to check its format
            try:
                template = cv2.imread(element.template_path)
                print(f"Template shape: {template.shape}, type: {template.dtype}")
            except Exception as template_e:
                print(f"Error loading template: {template_e}")

    # Black out the rank icon if found
    if best_match["score"] > rarity_icon_threshold:
        loc = best_match["details"]["loc"]
        size = best_match["details"]["size"]
        binary_image[loc[1] : loc[1] + size[1], loc[0] : loc[0] + size[0]] = 0

    # remove agent icons
    # this should be done without recognition, as we don't know what the agent icons look like
    # the position of the agent icons can be done by enlarging the bounding box of the rarity icons
    # by a modifier, and then keeping the same y position but adjusting the x position so that the
    # edge of the bounding box hits the right side of the image

    agent_icon_size_modifier = 1.5
    agent_icon_y_offset = 0

    if (
        best_match["score"] > rarity_icon_threshold
    ):  # if we've found a good match and blacked it
        # Calculate the agent icon bounding box
        agent_icon_y = loc[1] + agent_icon_y_offset
        agent_icon_width = int(size[0] * agent_icon_size_modifier)
        agent_icon_height = int(size[1] * agent_icon_size_modifier)

        # now push the agent icon bounding box to the right edge of the image
        agent_icon_x = binary_image.shape[1] - agent_icon_width

        # Center vertically
        agent_icon_y = agent_icon_y - (agent_icon_height - size[1]) // 2

        # Black out the agent icon area
        binary_image[
            agent_icon_y : agent_icon_y + agent_icon_height,
            agent_icon_x : agent_icon_x + agent_icon_width,
        ] = 0

    # Save if requested
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image


# given a path, preprocess the image for tesseract - for WEngine images
def preprocess_wengine_image(
    image_path,
    save_path=None,
    target_images_folder="./Target_Images",
    resize=True,
    resize_width=400,
):
    upgrade_rank = 1  # default to 1
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aggressive threshold
    binary_image = cv2.threshold(
        gray,
        240,  # Fixed threshold value
        255,
        cv2.THRESH_BINARY,
    )[1]

    # black out the character / type section
    character_section_area = {
        "top": int(0.4 * image.shape[0]),
        "bottom": int(0.75 * image.shape[0]),
        "left": int(0.02 * image.shape[1]),
        "right": int(0.4 * image.shape[1]),
    }

    binary_image[
        character_section_area["top"] : character_section_area["bottom"],
        character_section_area["left"] : character_section_area["right"],
    ] = 0

    # black out the weapon section
    weapon_section_area = {
        "top": int(0.1 * image.shape[0]),
        "bottom": int(0.75 * image.shape[0]),
        "left": int(0.60 * image.shape[1]),
        "right": int(0.95 * image.shape[1]),
    }
    binary_image[
        weapon_section_area["top"] : weapon_section_area["bottom"],
        weapon_section_area["left"] : weapon_section_area["right"],
    ] = 0

    # black out the rarity section
    rarity_section_area = {
        "top": int(0.8 * image.shape[0]),
        "bottom": int(1 * image.shape[0]),
        "left": int(0.02 * image.shape[1]),
        "right": int(0.1 * image.shape[1]),
    }
    binary_image[
        rarity_section_area["top"] : rarity_section_area["bottom"],
        rarity_section_area["left"] : rarity_section_area["right"],
    ] = 0

    # downscale the image so that it is X pixels wide, and keep the aspect ratio
    # we do this to keep the font size in the ideal range for tessaract (20px high capitals)
    # calculate the scaling factor

    if resize:
        desired_width = resize_width
        scaling_factor = desired_width / binary_image.shape[1]
        desired_height = int(binary_image.shape[0] * scaling_factor)
        binary_image = cv2.resize(
            binary_image, (desired_width, desired_height), interpolation=cv2.INTER_AREA
        )

        # search for all instances of the upgrade star that indicates the upgrade level, note the number and black the space out
        upgrade_star_paths = [
            os.path.join(target_images_folder, "zzz-wengine-upgrade1.png"),  # 1
            os.path.join(target_images_folder, "zzz-wengine-upgrade2.png"),  # 2
            os.path.join(target_images_folder, "zzz-wengine-upgrade3.png"),  # 3
            os.path.join(target_images_folder, "zzz-wengine-upgrade4.png"),  # 4
            os.path.join(target_images_folder, "zzz-wengine-upgrade5.png"),  # 5
        ]

        # Try each upgrade template until we find a match
        upgrade_rank = 1  # default if no match found
        for rank, upgrade_path in enumerate(upgrade_star_paths, start=1):
            upgrade_template = cv2.imread(upgrade_path, cv2.IMREAD_GRAYSCALE)
            if upgrade_template is None:
                print(f"Warning: Could not load upgrade template {upgrade_path}")
                continue

            result = cv2.matchTemplate(
                binary_image, upgrade_template, cv2.TM_CCOEFF_NORMED
            )
            max_val = result.max()

            if max_val >= 0.9:  # If we found a good match
                upgrade_rank = rank
                h, w = upgrade_template.shape

                # Find the location of the match
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                top_left = max_loc

                # black out the matched area
                binary_image[
                    top_left[1] : top_left[1] + h,
                    top_left[0] : top_left[0] + w,
                ] = 0

                print(f"Found upgrade rank {upgrade_rank}")
                break  # Stop searching once we find a match

    # Save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image, upgrade_rank


### Character Preprocessing Functions ###
def preprocess_image_simple(image_path: str, save_path: str = None):
    """
    Preprocess the image minimally by converting to grayscale and thresholding

    Args:
        image_path (str): Path to the name image
        save_path (str, optional): Path to save the preprocessed image

    Returns:
        cv2.Mat: The preprocessed image

    Used In:
        process_name_image()
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aggressive threshold
    binary_image = cv2.threshold(
        gray,
        240,  # Fixed threshold value
        255,
        cv2.THRESH_BINARY,
    )[1]

    # NOTE: We aren't resizing the image here like in the other preprocess_images.py functions
    # This is because the font size already varies between characters, and I don't want to have to set a resize width per character

    # Save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image


def preprocess_level_image(image_path: str, save_path: str = None):
    """
    Preprocess the level image to get the agent level

    Args:
        image_path (str): Path to the level image
        save_path (str, optional): Path to save the preprocessed image

    Returns:
        cv2.Mat: The preprocessed image

    Used In:
        process_level_image()
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    # part of the level text we later want to extract is black, so we need to grab the subsection
    height, width = image.shape[:2]
    subsection_height = int(0.6 * height)
    subsection_width = int(0.29 * width)
    y_start = int(0.2 * height)
    x_start = int(0.45 * width)

    level_text_subsection = image[
        y_start : y_start + subsection_height,
        x_start : x_start + subsection_width,
    ]

    # white any black pixels in the subsection
    level_text_subsection[level_text_subsection == 0] = 255

    # resize the subsection to half size since the font size of the max level is larger
    new_height = subsection_height // 2
    new_width = subsection_width // 2
    resized_subsection = cv2.resize(level_text_subsection, (new_width, new_height))

    # calculate centering offsets
    y_offset = (subsection_height - new_height) // 2
    x_offset = (subsection_width - new_width) // 2

    # black out the original subsection area
    image[
        y_start : y_start + subsection_height,
        x_start : x_start + subsection_width,
    ] = 0

    # paste the resized subsection in the center of the blacked out area
    image[
        y_start + y_offset : y_start + y_offset + new_height,
        x_start + x_offset : x_start + x_offset + new_width,
    ] = resized_subsection

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aggressive threshold
    binary_image = cv2.threshold(
        gray,
        240,  # Fixed threshold value
        255,
        cv2.THRESH_BINARY,
    )[1]

    # black the rightmost 20% of the image (Where the >> level up icon or MAX text is)
    height, width = binary_image.shape[:2]
    binary_image[:, int(0.8 * width) :] = 0

    # NOTE: We aren't resizing the image here like in the other preprocess_images.py functions
    # This is because the font size already varies between characters, and I don't want to have to set a resize width per character

    # Save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image


def preprocess_skill_image(
    image_path: str, save_path: str = None, coreSkill: bool = False
):
    """
    Preprocess the skill image to get the skill level in white, and everything else in black

    Args:
        image_path (str): Path to the skill image
        save_path (str, optional): Path to save the preprocessed image
        coreSkill (bool, optional): Whether the skill is a core skill (so we can remove the play button)

    Returns:
        cv2.Mat: The preprocessed image
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None

    # black out the rightmost 30% of the image if it is a core skill
    if coreSkill:
        height, width = image.shape[:2]
        image[:, int(0.7 * width) :] = 0  # Set rightmost 30% to black
        blacked_out_image = image
    else:
        blacked_out_image = image

    # Convert the image to grayscale
    gray = cv2.cvtColor(blacked_out_image, cv2.COLOR_BGR2GRAY)

    # Aggressive threshold
    binary_image = cv2.threshold(
        gray,
        240,  # Fixed threshold value
        255,
        cv2.THRESH_BINARY,
    )[1]

    # save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image


def preprocess_character_weapon_image(
    image_path: str,
    screen_width: int,
    screen_height: int,
    save_path: str = None,
    target_folder: str = "./Target_Images",
    icon_padding_percentage: int = 5,
    resize_for_upgrade_scan: bool = True,
    resize_width: int = 384,
):
    """
    Preprocess the character weapon image to get a black and white image of the all sections of interest (name, level)
    we need to get a full scan of the character weapon (that way we can assign the correct weapon to the character)

    Args:
        image_path (str): Path to the character weapon image
        screen_width (int): Current screen width
        screen_height (int): Current screen height
        save_path (str, optional): Path to save the preprocessed image
        target_folder (str, optional): Path to the target folder
        icon_padding_percentage (int, optional): Percentage of image height to add to padding around icons to black out
        resize_for_upgrade_scan (bool, optional): Whether to resize the image for upgrade scan template matching
        resize_width (int, optional): Width to resize to for upgrade scan template matching

    Returns:
        tuple of:
            cv2.Mat: The preprocessed image
            int: weapon upgrade level (1 if not found)

    Used In:
        process_character_weapon_image()
    """

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return None, 1

    # Create the UI element matcher with the loaded image
    ui_matcher = ExistingScreenshotMatcher(image, screen_width, screen_height)

    # Create a UIElement for the weapon level image
    weapon_lvl_element = UIElement(
        name="weapon_level_icon",
        template_path=f"{target_folder}/zzz-character-weapon-lvl-1440p.png",
        confidence=0.7,  # Slightly lower confidence for flexibility
    )

    # Use the matcher to find the weapon level icon
    try:
        match_details = ui_matcher.locate_element_with_details(weapon_lvl_element)

        if not match_details["found"]:
            print("Warning: Weapon level icon not found with high confidence")

        # Get match location and size
        max_loc = match_details["loc"]
        template_width, template_height = match_details["size"]

    except Exception as e:
        print(f"Error matching weapon level icon: {e}")
        return None, 1

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aggressive threshold
    binary_image = cv2.threshold(
        gray,
        240,  # Fixed threshold value
        255,
        cv2.THRESH_BINARY,
    )[1]

    # Define the y-range to black out around the template match
    icon_padding = int(
        icon_padding_percentage / 100 * binary_image.shape[0]
    )  # 5% of image height
    icon_y_start = max(0, max_loc[1] - icon_padding)
    icon_y_end = min(binary_image.shape[0], max_loc[1] + template_height + icon_padding)

    binary_image[icon_y_start:icon_y_end, : max_loc[0]] = (
        0  # Black out left side of template to remove the rank icon
    )

    right_cutoff = int(0.8 * binary_image.shape[1])  # Rightmost 20% of image width
    binary_image[icon_y_start:icon_y_end, right_cutoff:] = (
        0  # Black out right side to remove the character icon
    )

    # Scan for weapon upgrade level
    upgrade_rank = 1  # default if no match found

    # Make a copy of the original grayscale image for upgrade level detection
    upgrade_scan_image = gray.copy()

    # Resize the image for template matching if needed
    if resize_for_upgrade_scan:
        original_height, original_width = upgrade_scan_image.shape
        scaling_factor = resize_width / original_width
        resized_height = int(original_height * scaling_factor)
        upgrade_scan_image = cv2.resize(
            upgrade_scan_image,
            (resize_width, resized_height),
            interpolation=cv2.INTER_AREA,
        )

    # Try to find the upgrade level stars
    upgrade_star_paths = [
        os.path.join(target_folder, "zzz-wengine-character-upgrade1.png"),  # 1
        os.path.join(target_folder, "zzz-wengine-character-upgrade2.png"),  # 2
        os.path.join(target_folder, "zzz-wengine-character-upgrade3.png"),  # 3
        os.path.join(target_folder, "zzz-wengine-character-upgrade4.png"),  # 4
        os.path.join(target_folder, "zzz-wengine-character-upgrade5.png"),  # 5
    ]

    # Try each upgrade template until we find a match
    for rank, upgrade_path in enumerate(upgrade_star_paths, start=1):
        # Load the upgrade template
        upgrade_template = cv2.imread(upgrade_path, cv2.IMREAD_GRAYSCALE)
        if upgrade_template is None:
            print(f"Warning: Could not load upgrade template {upgrade_path}")
            continue

        # Perform template matching
        result = cv2.matchTemplate(
            upgrade_scan_image, upgrade_template, cv2.TM_CCOEFF_NORMED
        )
        max_val = result.max()

        if (
            max_val >= 0.85
        ):  # If we found a good match (slightly lower threshold for flexibility)
            upgrade_rank = rank
            break  # Stop searching once we find a match

    # Save the image if a save_path is provided
    if save_path:
        cv2.imwrite(save_path, binary_image)
        print(f"Preprocessed image saved to {save_path}")

    return binary_image, upgrade_rank


### End of Character Preprocessing Functions ###

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # test the function
    image_path = "./TestImages/test_character_weapon_img.png"
    save_path = "./TestImages/test_character_weapon_img_processed.png"
    # import pyautogui

    # screen_width, screen_height = pyautogui.size()
    # processed_image = preprocess_image(
    #     image_path,
    #     screen_width,
    #     screen_height,
    #     save_path=save_path,
    #     target_images_folder="./Target_Images",
    # )
    # processed_character_weapon_image = preprocess_character_weapon_image(
    #     image_path,
    #     screen_width,
    #     screen_height,
    #     save_path,
    #     target_folder="./Target_Images",
    # )
