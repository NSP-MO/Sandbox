import pyautogui
import time
import base64
import os
import json
import pygetwindow as gw # Added for window selection
# For Google Gemini API (install google-generativeai)
import google.generativeai as genai

# --- Configuration ---
SCREENSHOT_INTERVAL = 7  # seconds
# GAME_WINDOW_REGION will be set by select_window()

# --- AI Configuration (Choose ONE and configure) ---
GEMINI_API_KEY = "AIzaSyB09PBV7PEYIJ7sYnxvnJB3rq5RmM1G6xY"  # Replace with your actual key

# --- Helper Functions ---

def select_game_window():
    """Lists available windows and lets the user select one for capturing."""
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
            else: # User typed a title
                for w in visible_windows:
                    if w.title == choice:
                        selected_window = w
                        break
                if not selected_window:
                    print("Window title not found. Please enter a valid number or exact title.")
                    continue

            if selected_window:
                print(f"Selected window: '{selected_window.title}'")
                # Ensure the window is not minimized and has a valid size
                if selected_window.isMinimized:
                    print("Warning: The selected window is minimized. Attempting to restore.")
                    selected_window.restore()
                    time.sleep(0.5) # Give time for window to restore

                if selected_window.width <=0 or selected_window.height <=0:
                    print("Error: Selected window has invalid dimensions (width or height is zero or negative).")
                    print("Please ensure the window is visible and not fully minimized or in a problematic state.")
                    return None

                # Fetch fresh geometry after potential restore
                # On some systems, directly using selected_window.box or .left, .top etc might be sufficient
                # but fetching fresh can be more reliable.
                refreshed_window = gw.getWindowsWithTitle(selected_window.title)
                if refreshed_window:
                    selected_window = refreshed_window[0]
                    return (selected_window.left, selected_window.top, selected_window.width, selected_window.height)
                else:
                    print("Could not re-fetch window details. Using previous.")
                    return (selected_window.left, selected_window.top, selected_window.width, selected_window.height)

        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"An error occurred during window selection: {e}")
            return None

def take_screenshot(region=None, filename="screenshot.png"):
    """Takes a screenshot of the specified region or full screen."""
    try:
        if region and (region[2] <= 0 or region[3] <= 0): # width or height is 0 or negative
            print(f"Error: Invalid screenshot region: {region}. Width and height must be positive.")
            print("This might happen if the selected window is minimized or not properly focused.")
            active_window = gw.getActiveWindow()
            if active_window:
                print(f"Attempting to capture active window: {active_window.title}")
                region = (active_window.left, active_window.top, active_window.width, active_window.height)
                if region[2] <= 0 or region[3] <= 0:
                    print("Error: Active window also has invalid dimensions. Capturing full screen as fallback.")
                    region = None # Fallback to full screen
            else:
                print("Error: No active window found. Capturing full screen as fallback.")
                region = None # Fallback to full screen

        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(filename)
        print(f"Screenshot saved as {filename}")
        return filename
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

def encode_image_to_base64(image_path):
    """Encodes an image file to a base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def get_feedback_from_gemini(image_path, prompt_text):
    """Sends an image and a prompt to the Gemini API and returns the response."""
    if not GEMINI_API_KEY: # MODIFIED: Allow the specific key to be considered configured
        return "Error: Gemini API key not configured."
    if not os.path.exists(image_path):
        return "Error: Screenshot image not found."

    try:
        model_to_use = 'gemini-2.0-flash' # UPDATED model name
        # For some regions or projects, you might need 'gemini-1.0-pro-vision-latest'
        # or to use the Vertex AI SDK with a specific model endpoint.
        # If you get model errors, try checking the available models in your Google AI Studio.
        gemini_model = genai.GenerativeModel(model_to_use)

        print(f"Sending screenshot to Gemini for feedback...")
        image_data = encode_image_to_base64(image_path)
        if not image_data:
            return "Error: Could not encode image."

        image_parts = [
            {
                "mime_type": "image/png", # Make sure this matches your screenshot format
                "data": image_data
            }
        ]
        prompt_parts = [prompt_text, image_parts[0]] # Order can matter for some models/prompts
        
        # Adjust generation config if needed (e.g., for longer/shorter responses)
        # generation_config = genai.types.GenerationConfig(
        #     candidate_count=1,
        #     max_output_tokens=256, # Adjust as needed
        #     temperature=0.7 # Adjust for creativity vs. factuality
        # )
        # response = gemini_model.generate_content(prompt_parts, generation_config=generation_config)
        
        response = gemini_model.generate_content(prompt_parts)

        if response and response.candidates:
            if response.candidates[0].content and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text.strip()
            elif hasattr(response, 'text') and response.text: # Fallback for simpler text responses
                return response.text.strip()
            else:
                # print(f"Full Gemini Response: {response}") # For debugging
                return "Gemini response format not as expected or empty."
        elif response and hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            # This helps diagnose if content was blocked (safety reasons, etc.)
            return f"Gemini content generation blocked. Reason: {response.prompt_feedback.block_reason}"
        else:
            # print(f"Full Gemini Response (if any): {response}") # For debugging
            return "No valid response or candidates from Gemini."

    except Exception as e:
        # More detailed error logging
        # import traceback
        # print(traceback.format_exc())
        return f"Error interacting with Gemini API: {e}"


# --- Main Loop ---
def main():
    global GAME_WINDOW_REGION # To store the selected window region

    # Configure Gemini API at the start
    if GEMINI_API_KEY: # MODIFIED: Allow the specific key to be used for configuration
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            print("Gemini API configured.")
        except Exception as e:
            print(f"Error configuring Gemini API: {e}. Please check your API key and setup.")
            return # Exit if API cannot be configured
    else:
        print("Warning: GEMINI_API_KEY is not set. AI feedback will not be available.")


    GAME_WINDOW_REGION = select_game_window()
    if not GAME_WINDOW_REGION:
        print("No game window selected or error during selection. Exiting.")
        return
    
    print(f"Capturing region: {GAME_WINDOW_REGION}")
    print(f"Taking screenshots every {SCREENSHOT_INTERVAL} seconds.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # Activate the selected window before taking a screenshot (optional, but can help)
            try:
                windows = gw.getWindowsWithTitle(gw.getActiveWindow().title) # A bit of a hack to find it again
                # A more robust way would be to store the selected window object if possible
                # and check if it's still valid, then activate it.
                # For now, we rely on the region. If the window moved/resized, this won't adapt.
                # To make it adapt, you'd re-call select_game_window() or a function to update coordinates
                # based on the stored window title/ID if it still exists.
                pass # Not activating for now to keep it simpler, pyautogui usually gets it right with region
            except Exception as e:
                print(f"Could not ensure window focus: {e}")


            screenshot_file = take_screenshot(region=GAME_WINDOW_REGION)

            if screenshot_file:
                if GEMINI_API_KEY: # MODIFIED: Allow the specific key to trigger AI feedback
                    game_prompt = "Based on this game screenshot, Suggest a strategic move based on the current situation. tell me in short and clear way.\n\n" \
                    # Or: "What is the most immediate threat in this image?"
                    # Or: "Suggest a strategic move based on the current situation."

                    feedback = get_feedback_from_gemini(screenshot_file, game_prompt)

                    print("\n--- AI Feedback ---")
                    print(feedback)
                    print("-------------------\n")
                else:
                    print("AI Feedback skipped as API key is not configured.")

                try:
                    os.remove(screenshot_file)
                except Exception as e:
                    print(f"Could not remove screenshot file: {e}")
            else:
                print("Failed to take screenshot. Skipping this interval.")

            time.sleep(SCREENSHOT_INTERVAL)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred in main loop: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()