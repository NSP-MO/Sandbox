import pyautogui
import time
import base64
import os
import json
import pygetwindow as gw
import google.generativeai as genai

# --- Configuration ---
SCREENSHOT_INTERVAL = 5  # seconds

# --- AI Configuration ---
GEMINI_API_KEY = "AIzaSyB09PBV7PEYIJ7sYnxvnJB3rq5RmM1G6xY"  # Replace with your actual key

# --- Global Variables ---
GAME_WINDOW_REGION = None
GAME_WINDOW_TITLE = None # For re-activating the window

# --- Helper Functions ---

def select_game_window():
    """Lists available windows and lets the user select one for capturing. Sets GAME_WINDOW_TITLE."""
    global GAME_WINDOW_TITLE
    print("Fetching available windows...")
    windows = gw.getAllWindows()
    visible_windows = [w for w in windows if w.visible and w.title.strip() != ""]

    if not visible_windows:
        print("No visible windows found. Please make sure your game or application is running.")
        return None

    print("\nAvailable Windows:")
    for i, window in enumerate(visible_windows):
        print(f"{i + 1}: {window.title}")

    while True:
        try:
            choice = input("Enter the number of the window to capture (or type its exact title): ")
            selected_window = None
            if choice.isdigit():
                window_index = int(choice) - 1
                if 0 <= window_index < len(visible_windows):
                    selected_window = visible_windows[window_index]
            else:
                for w in visible_windows:
                    if w.title == choice:
                        selected_window = w
                        break
                if not selected_window:
                    print("Window title not found. Please enter a valid number or exact title.")
                    continue

            if selected_window:
                GAME_WINDOW_TITLE = selected_window.title
                print(f"Selected window: '{selected_window.title}'")
                print(f"DEBUG: Initial selected_window details: title='{selected_window.title}', left={selected_window.left}, top={selected_window.top}, width={selected_window.width}, height={selected_window.height}, right={selected_window.right}, bottom={selected_window.bottom}, box={selected_window.box}")

                if selected_window.isMinimized:
                    print("Warning: The selected window is minimized. Attempting to restore.")
                    selected_window.restore()
                    time.sleep(0.5) # Give time for window to restore

                if selected_window.width <= 0 or selected_window.height <= 0:
                    print(f"Error: Selected window '{selected_window.title}' has invalid dimensions after initial check/restore (width or height is zero or negative).")
                    print("Please ensure the window is visible and not fully minimized or in a problematic state.")
                    GAME_WINDOW_TITLE = None
                    return None

                refreshed_window_list = gw.getWindowsWithTitle(selected_window.title)
                if refreshed_window_list:
                    refreshed_window = refreshed_window_list[0]
                    print(f"DEBUG: Refreshed window details: title='{refreshed_window.title}', left={refreshed_window.left}, top={refreshed_window.top}, width={refreshed_window.width}, height={refreshed_window.height}, right={refreshed_window.right}, bottom={refreshed_window.bottom}, box={refreshed_window.box}")

                    if refreshed_window.isMinimized:
                        print(f"DEBUG: Refreshed window '{refreshed_window.title}' was minimized, restoring...")
                        refreshed_window.restore()
                        time.sleep(0.5)
                    if refreshed_window.width <=0 or refreshed_window.height <=0:
                         print(f"Error: Refreshed window '{refreshed_window.title}' has invalid dimensions after refresh/restore. Selection failed.")
                         GAME_WINDOW_TITLE = None
                         return None
                    GAME_WINDOW_TITLE = refreshed_window.title
                    return (refreshed_window.left, refreshed_window.top, refreshed_window.width, refreshed_window.height)
                else:
                    print(f"Warning: Could not re-fetch window details for '{selected_window.title}'. Using initially fetched details.")
                    if selected_window.width > 0 and selected_window.height > 0:
                        print(f"DEBUG: Falling back to initially selected window details: left={selected_window.left}, top={selected_window.top}, width={selected_window.width}, height={selected_window.height}")
                        return (selected_window.left, selected_window.top, selected_window.width, selected_window.height)
                    else:
                        print(f"Error: Fallback window details for '{selected_window.title}' also invalid. Selection failed.")
                        GAME_WINDOW_TITLE = None
                        return None

        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An error occurred during window selection: {e}")
            GAME_WINDOW_TITLE = None
            return None

def take_screenshot(region=None, filename="screenshot.png"):
    """
    Takes a screenshot of the specified region or full screen.
    Returns a tuple (filename, actual_region_captured) or (None, None) on failure.
    actual_region_captured is (left, top, width, height) relative to the screen.
    """
    actual_region_to_capture = region # The region we intend to capture

    try:
        # Validate and determine the actual region to capture
        if actual_region_to_capture:
            # Ensure dimensions are positive
            if actual_region_to_capture[2] <= 0 or actual_region_to_capture[3] <= 0:
                print(f"Warning: Invalid screenshot region passed (width/height non-positive): {actual_region_to_capture}.")
                active_window = gw.getActiveWindow()
                if active_window and active_window.width > 0 and active_window.height > 0:
                    print(f"Attempting to capture active window as fallback: '{active_window.title}'")
                    actual_region_to_capture = (active_window.left, active_window.top, active_window.width, active_window.height)
                    if actual_region_to_capture[2] <= 0 or actual_region_to_capture[3] <= 0: # Check again
                        print("Error: Active window also has invalid dimensions. Capturing full screen.")
                        screen_width, screen_height = pyautogui.size()
                        actual_region_to_capture = (0, 0, screen_width, screen_height)
                else:
                    print("Warning: No valid active window with positive dimensions found. Capturing full screen as fallback.")
                    screen_width, screen_height = pyautogui.size()
                    actual_region_to_capture = (0, 0, screen_width, screen_height)
        else: # No region was specified, so capture full screen
            print("DEBUG: No region specified by caller, capturing full screen.")
            screen_width, screen_height = pyautogui.size()
            actual_region_to_capture = (0, 0, screen_width, screen_height)

        # Final check, ensure all parts of the region are sensible before passing to pyautogui
        if not all(isinstance(val, (int, float)) for val in actual_region_to_capture[:4]) or \
           actual_region_to_capture[2] <= 0 or actual_region_to_capture[3] <= 0:
            print(f"Error: Screenshot region is still invalid {actual_region_to_capture} before pyautogui.screenshot. Capturing full screen.")
            screen_width, screen_height = pyautogui.size()
            actual_region_to_capture = (0, 0, screen_width, screen_height)

        # Pyautogui region parameter expects integers.
        # actual_region_to_capture might have floats if they came from pygetwindow.
        capture_params = {
            "region": (
                int(actual_region_to_capture[0]),
                int(actual_region_to_capture[1]),
                int(actual_region_to_capture[2]),
                int(actual_region_to_capture[3])
            )
        }

        print(f"DEBUG: pyautogui.screenshot called with region: {capture_params['region']}")
        screenshot = pyautogui.screenshot(**capture_params)
        screenshot.save(filename)
        # Return the region that was actually captured (matching capture_params['region'])
        print(f"Screenshot saved as {filename}, captured region: {capture_params['region']}")
        return filename, capture_params['region']

    except Exception as e:
        print(f"Error taking screenshot with intended region {region} (actual used: {actual_region_to_capture}): {e}")
        # Attempt full screen screenshot as a last resort if region failed
        try:
            print("Attempting full screen screenshot as fallback due to error.")
            screen_width, screen_height = pyautogui.size()
            fallback_region = (0, 0, screen_width, screen_height)
            screenshot = pyautogui.screenshot() # Full screen
            screenshot.save(filename)
            print(f"Full screenshot saved as {filename}, captured region: {fallback_region}")
            return filename, fallback_region
        except Exception as e_full:
            print(f"Error taking full screenshot: {e_full}")
            return None, None


def encode_image_to_base64(image_path):
    """Encodes an image file to a base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def get_feedback_from_gemini(image_path, prompt_text):
    """Sends an image and a prompt to the Gemini API and returns the response text."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        return "Error: Gemini API key not configured."
    if not os.path.exists(image_path):
        return "Error: Screenshot image not found."

    try:
        model_to_use = 'gemini-2.0-flash'
        gemini_model = genai.GenerativeModel(model_to_use)

        print(f"Sending screenshot to Gemini for feedback...")
        image_data = encode_image_to_base64(image_path)
        if not image_data:
            return "Error: Could not encode image."

        image_parts = [
            {
                "mime_type": "image/png",
                "data": image_data
            }
        ]
        prompt_parts = [prompt_text, image_parts[0]]

        response = gemini_model.generate_content(prompt_parts)

        if response and response.candidates:
            if response.candidates[0].content and response.candidates[0].content.parts:
                raw_text = response.candidates[0].content.parts[0].text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[len("```json"):]
                elif raw_text.startswith("```"):
                     raw_text = raw_text[len("```"):]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-len("```")]
                return raw_text.strip()
            elif hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                return "Gemini response format not as expected or empty."
        elif response and hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            return f"Gemini content generation blocked. Reason: {response.prompt_feedback.block_reason}"
        else:
            return "No valid response or candidates from Gemini."

    except Exception as e:
        return f"Error interacting with Gemini API: {e}"


# --- Main Loop ---
def main():
    global GAME_WINDOW_REGION, GAME_WINDOW_TITLE

    print(f"DEBUG: PyAutoGUI screen size: {pyautogui.size()}")
    try:
        active_win_autogui = pyautogui.getActiveWindow()
        if active_win_autogui:
            print(f"DEBUG: PyAutoGUI initial active window: title='{active_win_autogui.title}', left={active_win_autogui.left}, top={active_win_autogui.top}, width={active_win_autogui.width}, height={active_win_autogui.height}")
        else:
            print("DEBUG: PyAutoGUI initial active window: None")
    except Exception as e:
        print(f"DEBUG: Error getting PyAutoGUI active window info at start: {e}")


    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("Warning: GEMINI_API_KEY is not set. AI feedback will not be available.")
    else:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            print("Gemini API configured.")
        except Exception as e:
            print(f"Error configuring Gemini API: {e}. Please check your API key and setup.")
            return

    window_details_tuple = select_game_window()
    if not window_details_tuple:
        print("No game window selected or error during selection. Exiting.")
        return
    GAME_WINDOW_REGION = window_details_tuple # (left, top, width, height)

    print(f"Initial target window region: {GAME_WINDOW_REGION} for window '{GAME_WINDOW_TITLE}'")
    print(f"Taking screenshots every {SCREENSHOT_INTERVAL} seconds.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # This will be the region we request the screenshot for.
            # It's updated each loop to track the window.
            requested_screenshot_region = GAME_WINDOW_REGION

            if GAME_WINDOW_TITLE:
                try:
                    target_windows = gw.getWindowsWithTitle(GAME_WINDOW_TITLE)
                    if target_windows:
                        game_win_check = target_windows[0]
                        print(f"DEBUG: In loop, game_win_check ('{GAME_WINDOW_TITLE}') details: left={game_win_check.left}, top={game_win_check.top}, width={game_win_check.width}, height={game_win_check.height}")
                        if game_win_check.isMinimized:
                            print(f"Window '{GAME_WINDOW_TITLE}' was minimized. Restoring...")
                            game_win_check.restore()
                            time.sleep(0.5)

                        if game_win_check.width > 0 and game_win_check.height > 0:
                             # Update requested_screenshot_region for this iteration
                             requested_screenshot_region = (game_win_check.left, game_win_check.top, game_win_check.width, game_win_check.height)
                             GAME_WINDOW_REGION = requested_screenshot_region # Keep global updated
                             print(f"DEBUG: Updated requested_screenshot_region to: {requested_screenshot_region}")
                        else:
                             print(f"Window '{GAME_WINDOW_TITLE}' has invalid dimensions in loop ({game_win_check.width}x{game_win_check.height}). Last known good region: {requested_screenshot_region}. Screenshot might fallback.")
                             # We'll proceed with requested_screenshot_region (which might be outdated or lead to fallback in take_screenshot)
                    else:
                        print(f"Window '{GAME_WINDOW_TITLE}' not found in loop. Exiting.")
                        break
                except Exception as e_win_check:
                    print(f"Error checking/updating window status in loop: {e_win_check}. Using last known region: {requested_screenshot_region}")

            # `take_screenshot` will handle if requested_screenshot_region is invalid
            # and will return the region it *actually* captured.
            screenshot_capture_result = take_screenshot(region=requested_screenshot_region, filename="current_capture.png")

            if screenshot_capture_result and screenshot_capture_result[0] is not None:
                screenshot_file, actual_captured_region = screenshot_capture_result
                # actual_captured_region is (left, top, width, height) of the image sent to AI

                if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
                    game_prompt = (
                        "Analyze the provided game screenshot. Your task is to identify the best single mouse click action. "
                        "Respond ONLY with a JSON object. The JSON object must have three keys: "
                        "'action_type' (string: 'click' if a click is recommended, 'observe' otherwise), "
                        "'target_description' (string: a brief description of the item to click or the reason for observing), "
                        "and 'click_coordinates' (an array of two integers [x, y] representing the pixel coordinates *within the provided image* for the click. The top-left of the image is [0,0]. This should be null if 'action_type' is 'observe').\n"
                        "Example for click: {\"action_type\": \"click\", \"target_description\": \"Red health potion icon\", \"click_coordinates\": [150, 300]}\n"
                        "Example for observe: {\"action_type\": \"observe\", \"target_description\": \"Waiting for enemy to move closer\", \"click_coordinates\": null}\n"
                        "Focus on clear, actionable UI elements or game objects if recommending a click. Provide precise coordinates within the image."
                    )
                    feedback_text = get_feedback_from_gemini(screenshot_file, game_prompt)
                    print(f"\n--- AI Raw Feedback ---\n{feedback_text}\n-----------------------\n")

                    try:
                        ai_decision = json.loads(feedback_text)
                        action_type = ai_decision.get("action_type")
                        target_desc = ai_decision.get("target_description", "N/A")
                        click_coords_img = ai_decision.get("click_coordinates")

                        print(f"AI Decided Action: {action_type}, Target: '{target_desc}', Coords in Image: {click_coords_img}")

                        if action_type == "click" and isinstance(click_coords_img, list) and len(click_coords_img) == 2:
                            img_x, img_y = click_coords_img

                            if not (isinstance(img_x, (int, float)) and isinstance(img_y, (int, float))):
                                print(f"AI Error: Invalid coordinate types received from Gemini: {click_coords_img}")
                            else:
                                img_x = int(img_x) # Ensure integer for pixel math
                                img_y = int(img_y)

                                # USE actual_captured_region for calculations and validation
                                # These are screen coordinates for the top-left of the image AI saw, and its dimensions.
                                actual_img_left, actual_img_top, actual_img_width, actual_img_height = actual_captured_region

                                print(f"DEBUG: Validating Gemini coords ({img_x},{img_y}) against actual screenshot region dimensions ({actual_img_width}x{actual_img_height}) used for this iteration.")

                                if 0 <= img_x < actual_img_width and 0 <= img_y < actual_img_height:
                                    # Convert image-relative coords to screen-absolute coords
                                    screen_x = actual_img_left + img_x
                                    screen_y = actual_img_top + img_y

                                    print(f"DEBUG: Click Calculation: screen_x = {actual_img_left} (actual_img_left) + {img_x} (gemini_x) = {screen_x}")
                                    print(f"DEBUG: Click Calculation: screen_y = {actual_img_top} (actual_img_top) + {img_y} (gemini_y) = {screen_y}")

                                    # Window activation logic (remains largely the same)
                                    if GAME_WINDOW_TITLE:
                                        try:
                                            target_windows_for_activate = gw.getWindowsWithTitle(GAME_WINDOW_TITLE)
                                            if target_windows_for_activate:
                                                game_win_to_activate = target_windows_for_activate[0]
                                                if game_win_to_activate.isMinimized:
                                                    print(f"DEBUG: Window '{GAME_WINDOW_TITLE}' is minimized before click, restoring.")
                                                    game_win_to_activate.restore()
                                                    time.sleep(0.5)
                                                if not game_win_to_activate.isActive:
                                                    print(f"DEBUG: Activating window '{GAME_WINDOW_TITLE}' for click.")
                                                    game_win_to_activate.activate()
                                                    time.sleep(0.5) # Allow time for activation if needed
                                                print(f"DEBUG: Ensured window '{GAME_WINDOW_TITLE}' is (attempted) active for click.")
                                            else:
                                                print(f"Warning: Could not find window '{GAME_WINDOW_TITLE}' to activate for click. Click might be unreliable.")
                                        except Exception as e_activate:
                                            print(f"Error during window activation for click: {e_activate}")

                                    print(f"Attempting to click at screen coordinates: ({screen_x}, {screen_y}) for '{target_desc}'")
                                    pyautogui.click(screen_x, (screen_y))  # Adjusted for scaling
                                    target_x = screen_x * 2.5
                                    target_y = (screen_y + 10) * 1.25
                                    print(f"Clicked at ({target_x}, {target_y})")
                                    time.sleep(1)
                                else:
                                    print(f"AI Error: Click coordinates [{img_x}, {img_y}] are outside the actual screenshot bounds ({actual_img_width}x{actual_img_height}).")
                        elif action_type == "click":
                            print(f"AI suggested a click but coordinates were invalid or missing: {click_coords_img}")
                        else:
                            print(f"AI action '{action_type}' received. No click performed.")

                    except json.JSONDecodeError:
                        print(f"AI Error: Could not parse JSON response: '{feedback_text}'")
                    except Exception as e_parse:
                        print(f"Error processing AI feedback: {e_parse}")
                else:
                    print("AI Feedback skipped as API key is not configured or missing.")

                try:
                    if os.path.exists(screenshot_file): # Check if file exists before removing
                        os.remove(screenshot_file)
                        # print(f"Screenshot file '{screenshot_file}' removed.")
                except Exception as e:
                    print(f"Could not remove screenshot file '{screenshot_file}': {e}")
            else:
                print("Failed to take screenshot or get valid region. Skipping this interval.")

            time.sleep(SCREENSHOT_INTERVAL)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred in main loop: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("####################################################################")
        print("### PLEASE CONFIGURE YOUR GEMINI API KEY IN THE SCRIPT!          ###")
        print("### Replace 'YOUR_GEMINI_API_KEY' with your actual key.        ###")
        print("####################################################################")
    main()