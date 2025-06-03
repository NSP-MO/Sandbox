import pyperclip
import time
import threading
from pynput import keyboard
from pynput.keyboard import Key, Controller as KeyboardController
import google.generativeai as genai
import os
import sys

# --- Configuration ---
API_KEY = "AIzaSyB09PBV7PEYIJ7sYnxvnJB3rq5RmM1G6xY" # User's provided key
if not API_KEY:
    print("DEBUG: GEMINI_API_KEY environment variable not set or API_KEY variable is empty.")
    API_KEY = input("Please enter your Gemini API Key: ")

if not API_KEY:
    print("ERROR: No API Key provided. Exiting.")
    sys.exit()

try:
    genai.configure(api_key=API_KEY)
    print("DEBUG: Gemini API Key configured.")
except Exception as e:
    print(f"ERROR: Failed to configure Gemini API: {e}")
    sys.exit()

model = genai.GenerativeModel('gemini-1.5-flash-latest')
print("DEBUG: Gemini model loaded.")

# --- Hotkey Definitions ---
MODIFIER_CTRL_KEYS = {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}
MODIFIER_SHIFT_KEYS = {keyboard.Key.shift_l, keyboard.Key.shift_r}
EXPECTED_CTRL_SHIFT_Q_KEYCODE = keyboard.KeyCode.from_char('\x11')

active_modifiers_pressed = set()
hotkey_action_in_progress = False

keyboard_controller = KeyboardController()

def enhance_text_with_gemini(text_to_enhance):
    global hotkey_action_in_progress # Ensure this is managed correctly
    print(f"DEBUG: enhance_text_with_gemini called with text: '{text_to_enhance[:50]}...'")
    if not text_to_enhance or not text_to_enhance.strip():
        print("DEBUG: No text to enhance.")
        # hotkey_action_in_progress should be reset by the caller or at the end of the action sequence
        return None 
    try:
        prompt = f"You are an AI prompt enhancer. Your task is to refine the user's input to make it clearer, more detailed, and more effective for an AI assistant. Return only the enhanced prompt itself, without any conversational filler, preamble, or explanation like 'Here's the enhanced prompt:'.\n\nOriginal prompt: \"{text_to_enhance}\""
        print(f"DEBUG: Sending prompt to Gemini: \"{prompt[:100]}...\"")
        response = model.generate_content(prompt)
        
        if response and response.text:
            enhanced = response.text.strip()
            print(f"DEBUG: Gemini response received: '{enhanced[:100]}...'")
            return enhanced
        else:
            print(f"DEBUG: Gemini response was empty or invalid. Response: {response}")
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                print(f"DEBUG: Prompt Feedback: {response.prompt_feedback}")
            return None
    except Exception as e:
        print(f"ERROR: Exception during Gemini API call: {e}")
        if hasattr(e, 'response') and e.response and hasattr(e.response, 'text'):
            print(f"ERROR DETAILS: {e.response.text}")
        return None
    # hotkey_action_in_progress will be reset in paste_enhanced_text or on_hotkey_actions error paths

def get_highlighted_text():
    print("DEBUG: get_highlighted_text called.")
    original_clipboard_content = pyperclip.paste()
    print(f"DEBUG: Original clipboard content: '{original_clipboard_content[:50]}...'")
    pyperclip.copy("") # Clear clipboard

    print("DEBUG: Simulating Ctrl+C.")
    with keyboard_controller.pressed(Key.ctrl):
        keyboard_controller.press('c')
        keyboard_controller.release('c')
    time.sleep(0.25)

    highlighted_text = pyperclip.paste()
    print(f"DEBUG: Text copied from clipboard: '{highlighted_text[:50]}...'")

    if not highlighted_text:
        print("DEBUG: No new text copied. Restoring original clipboard.")
        pyperclip.copy(original_clipboard_content)
        return None
    return highlighted_text

def paste_enhanced_text(enhanced_text):
    # This function is the end of a successful path, so reset hotkey_action_in_progress here
    global hotkey_action_in_progress
    print(f"DEBUG: paste_enhanced_text called with text: '{enhanced_text[:50]}...'")
    if enhanced_text:
        pyperclip.copy(enhanced_text)
        print("INFO: Enhanced text copied to clipboard. Attempting to paste...")
        time.sleep(0.1)

        print("DEBUG: Simulating Ctrl+V.")
        with keyboard_controller.pressed(Key.ctrl):
            keyboard_controller.press('v')
            keyboard_controller.release('v')
        print("INFO: Attempted to paste enhanced text. If it didn't appear, try manually pasting (Ctrl+V).")
    else:
        print("DEBUG: No enhanced text to paste.")
    hotkey_action_in_progress = False # Reset here

def on_hotkey_actions():
    global hotkey_action_in_progress # Make sure it's globally recognized
    if hotkey_action_in_progress: # Check if already set by a previous call
        print("DEBUG: Hotkey action already in progress (on_hotkey_actions entry). Skipping.")
        return # Should not happen if on_press logic is correct, but as safeguard
    
    hotkey_action_in_progress = True # Set flag at the beginning of the action
    print("INFO: Hotkey activated! Processing...")
    
    try:
        highlighted_text = get_highlighted_text()

        if highlighted_text:
            enhanced_text = enhance_text_with_gemini(highlighted_text)
            if enhanced_text:
                paste_enhanced_text(enhanced_text) # This will reset hotkey_action_in_progress
                return # Successful completion
            else:
                print("INFO: Failed to enhance text or text was empty.")
        else:
            print("INFO: Could not retrieve highlighted text.")
    except Exception as e:
        print(f"ERROR in on_hotkey_actions: {e}")
    finally:
        # Ensure the flag is reset if any path above didn't (e.g., an error before paste_enhanced_text)
        # or if paste_enhanced_text wasn't called due to no text.
        if highlighted_text and enhanced_text: # paste_enhanced_text would have reset it
            pass
        else: # Reset if not reset by paste_enhanced_text
            hotkey_action_in_progress = False
            print("DEBUG: hotkey_action_in_progress reset in on_hotkey_actions finally block.")


def on_press(key):
    try:
        print(f"DEBUG (Press): Key='{key}', Type='{type(key)}', VK='{getattr(key, "vk", "N/A")}', Current Modifiers='{active_modifiers_pressed}'")

        if key in MODIFIER_CTRL_KEYS or key in MODIFIER_SHIFT_KEYS:
            active_modifiers_pressed.add(key)
            print(f"DEBUG: Modifier '{key}' ADDED. Active Modifiers: '{active_modifiers_pressed}'")
            return True 

        ctrl_is_active = any(k_ctrl in active_modifiers_pressed for k_ctrl in MODIFIER_CTRL_KEYS)
        shift_is_active = any(k_shift in active_modifiers_pressed for k_shift in MODIFIER_SHIFT_KEYS)

        if ctrl_is_active and shift_is_active:
            if key == EXPECTED_CTRL_SHIFT_Q_KEYCODE:
                global hotkey_action_in_progress # Access global flag
                if hotkey_action_in_progress:
                    print("DEBUG: Hotkey combination detected, but action already in progress. Suppressing.")
                    return False # Suppress event, but don't start new thread

                print(f"SUCCESS: Hotkey (Ctrl+Shift + Q -> detected as \\x11) triggered with Key='{key}'!")
                print(f"DEBUG: Current active modifiers at trigger: {active_modifiers_pressed}")
                
                # Make the action thread NON-DAEMON
                action_thread = threading.Thread(target=on_hotkey_actions, daemon=False)
                action_thread.start()
                return False 
            else:
                print(f"DEBUG: Ctrl+Shift active, but Key='{key}' (VK='{getattr(key, "vk", "N/A")}') is not the expected trigger ('\\x11').")
        
        return True
    except Exception as e:
        print(f"ERROR in on_press callback: {e}")
        return True # Default to allowing propagation if our logic errors

def on_release(key):
    try:
        print(f"DEBUG (Release): Key='{key}', Type='{type(key)}', VK='{getattr(key, "vk", "N/A")}'")
        if key in active_modifiers_pressed:
            active_modifiers_pressed.discard(key)
            print(f"DEBUG: Modifier '{key}' REMOVED. Active Modifiers: '{active_modifiers_pressed}'")
    except Exception as e:
        print(f"ERROR in on_release callback: {e}")

def start_hotkey_listener():
    hotkey_display_string = f"Ctrl + Shift + Q"
    print(f"INFO: Hotkey listener started. Press {hotkey_display_string} to enhance highlighted text.")
    # ... (other info prints) ...
    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("DEBUG: keyboard.Listener object created.")
        listener.join() # This call blocks until the listener stops.
    print("DEBUG: keyboard.Listener finished or stopped.") # This will print if listener.join() unblocks

if __name__ == "__main__":
    print("DEBUG: Script starting...")
    if not API_KEY:
        print("CRITICAL ERROR: API Key is missing. Exiting.")
        sys.exit()

    try:
        start_hotkey_listener()
    except KeyboardInterrupt:
        print("INFO: Script interrupted by user (Ctrl+C).")
    except Exception as e:
        print(f"FATAL ERROR in main execution: {e}")
    finally:
        print("DEBUG: Script __main__ is finishing.")