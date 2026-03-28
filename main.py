import cv2
import numpy as np
import pyautogui
import time
import uuid
import keyboard
from screeninfo import get_monitors

RESOLUTIONS = {
    "2K": {"MOUSE_SCROLL_LOCATION": (2491, 1300),
           "UNSEND_APPROVE_LOCATION": (1270, 647),
           "EMOJI_FILE": "emoji_2K.jpg",
           "MORE_BUTTON_IN_IMAGE_LOCATION": (13, 15),
           "UNSEND_BUTTON_RELATIVE_LOCATION": (-30, -30)},
    "4K": {"MOUSE_SCROLL_LOCATION": (3698, 1954),
           "UNSEND_APPROVE_LOCATION": (1911, 987),
           "EMOJI_FILE": "emoji_4K.png",
           "MORE_BUTTON_IN_IMAGE_LOCATION": (26, 19),
           "UNSEND_BUTTON_RELATIVE_LOCATION": (-164, -51),
           }
}


def get_resolution_label():
    try:
        monitors = get_monitors()

        if not monitors:
            return None

        primary = monitors[0]

        width = primary.width
        height = primary.height

        if width == 3840 and height == 2160:
            return "4K"

        if width == 2560 and height == 1440:
            return "2K"

        return None

    except Exception as e:
        print(f"Error detecting screen resolution: {e}")
        return None


def detect_more_button(screen_image, template_image, image_offsets):
    # Perform template matching
    result = cv2.matchTemplate(screen_image, template_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    threshold = 0.9  # Adjust the threshold as needed
    if max_val >= threshold:
        # max_loc = top left
        return max_loc[0] + image_offsets[0], max_loc[1] + image_offsets[1]
    else:
        return None


stop_flag = False


def stop():
    global stop_flag
    stop_flag = True
    print("Stop")


def main():
    print("Press ctrl+shift+x to cancel script execution, starting in 5 seconds...")
    keyboard.add_hotkey('ctrl+shift+x', stop)
    resolution_label = get_resolution_label()
    if not resolution_label:
        raise ValueError("Screen resolution not supported")
    resolutions_data = RESOLUTIONS[resolution_label]
    print(f"Resolution: {resolution_label}")

    # Load the template image
    template_image = cv2.imread(resolutions_data["EMOJI_FILE"], cv2.IMREAD_COLOR)

    non = 0
    time.sleep(5)
    global stop_flag
    clicks = 0
    while not stop_flag:
        non += 1  # increases by one when no message found
        pyautogui.moveTo(
            resolutions_data[
                "MOUSE_SCROLL_LOCATION"])  # This is where the mouse stays. instead of moving the mouse, the we simply scroll
        debugging_on = False
        screen_image = pyautogui.screenshot().convert('RGB')  # Convert to RGB format
        if debugging_on:
            filename = f"{uuid.uuid4()}.png"
            screen_image.save(filename)

        screen_np = np.array(screen_image)
        screen_cv = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)  # Convert to BGR format for OpenCV

        more_button_location = detect_more_button(screen_cv,
                                                  template_image, resolutions_data[
                                                      "MORE_BUTTON_IN_IMAGE_LOCATION"])
        if more_button_location:
            unsend_from_more_menu_location = (
                more_button_location[0] + resolutions_data["UNSEND_BUTTON_RELATIVE_LOCATION"][0],
                more_button_location[1] + resolutions_data["UNSEND_BUTTON_RELATIVE_LOCATION"][
                    1])  # The "Unsend" button

            # Click at the calculated location
            pyautogui.click(more_button_location)
            pyautogui.click(unsend_from_more_menu_location)

            # Depending on connection or browser speed, delays are necessary between button clicks, adjust them here
            time.sleep(0.5)
            # The confirmation for "Unsend" in the middle of the screen
            pyautogui.click(*resolutions_data["UNSEND_APPROVE_LOCATION"])
            time.sleep(1)
            clicks += 1
            non = 0  # non counter resets to 0, because message was found
            if clicks % 10 == 0:
                print(f"Clicks:{clicks}")
        else:
            pyautogui.scroll(20)

        # If no message is found for this many iterations, the program will quit
        if non == 10000:
            print("No messages found")
            break


if __name__ == "__main__":
    main()
