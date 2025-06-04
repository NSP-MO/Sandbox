import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import keyboard
import google.generativeai as genai
import threading
import os

# --- Configuration ---
HOTKEY = "ctrl+shift+h"

# --- Setup Gemini ---
# IMPORTANT: Your API key should be set as an environment variable 'GEMINI_API_KEY'
# DO NOT hardcode your API key directly in the script.
GOOGLE_API_KEY = "AIzaSyB09PBV7PEYIJ7sYnxvnJB3rq5RmM1G6xY"
gemini_model = None # Initialize to None

if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        # Changed to a more commonly available and recent model.
        # Other options: 'gemini-1.0-pro', 'gemini-1.5-pro-latest'
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        print("Gemini model initialized successfully with 'gemini-2.0-flash'.")
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        gemini_model = None # Ensure model is None if initialization fails
        # The GUI will show further warnings.
else:
    print("Warning: GEMINI_API_KEY environment variable not set. Gemini functionality will be disabled.")

# --- Global Variables for GUI Elements ---
text_widget = None
root = None
status_label = None

def enhance_text_with_gemini(text_to_enhance):
    """Sends text to Gemini for enhancement and returns the result."""
    if not gemini_model:
        return "Error: Gemini model not initialized (API key issue or model configuration error)."
    try:
        prompt = (
            f"You are an expert prompt engineer. Enhance the following text to be a more effective, clear, "
            f"and concise prompt. Focus on improving its ability to elicit the desired output from an AI. "
            f"Return only the enhanced prompt text, without any preamble or explanation. "
            f"Original text: \"{text_to_enhance}\""
        )
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error during Gemini API call: {str(e)}") # This will now show more specific errors if they occur
        return f"Error: Could not enhance text. ({type(e).__name__}: {str(e)})"

def update_text_widget_with_enhanced_text(original_selection_start, original_selection_end, enhanced_text):
    """Replaces the selected text in the widget with the enhanced text."""
    global text_widget, status_label
    if not text_widget:
        return

    try:
        text_widget.delete(original_selection_start, original_selection_end)
        text_widget.insert(original_selection_start, enhanced_text)
        
        text_widget.mark_set(tk.INSERT, f"{original_selection_start}+{len(enhanced_text)}c")
        text_widget.see(tk.INSERT)
        text_widget.focus_set()

        status_label.config(text=f"Text enhanced! Highlight text and press {HOTKEY}.")
    except tk.TclError as e:
        print(f"Tkinter error during text update: {e}")
        status_label.config(text="Error: Could not update text. Selection might have been lost.")
    except Exception as e:
        print(f"General error updating text widget: {e}")
        status_label.config(text=f"Error updating text: {str(e)}")

def process_enhancement_request():
    """Handles the hotkey press: gets selected text, calls Gemini, and updates GUI."""
    global text_widget, status_label, root

    if not text_widget:
        print("Text widget not initialized.")
        return

    if not gemini_model:
        messagebox.showerror("Gemini Not Ready", "Gemini model is not initialized. Please ensure your GEMINI_API_KEY is set correctly, the model name is valid, and restart.")
        if status_label:
            status_label.config(text="Gemini not ready (API key/model issue).", foreground="red")
        return

    try:
        selected_text_start = text_widget.index(tk.SEL_FIRST)
        selected_text_end = text_widget.index(tk.SEL_LAST)
        selected_text = text_widget.get(selected_text_start, selected_text_end)

        if not selected_text.strip():
            if status_label:
                status_label.config(text="No text selected or selection is empty.")
            return
    except tk.TclError:
        if status_label:
            status_label.config(text=f"No text selected. Highlight text and press {HOTKEY}.")
        return

    if status_label:
        status_label.config(text="Enhancing text with Gemini...")

    def threaded_gemini_call_and_update():
        enhanced_text = enhance_text_with_gemini(selected_text)
        if root and text_widget:
             root.after(0, lambda: update_text_widget_with_enhanced_text(selected_text_start, selected_text_end, enhanced_text))
        elif not root:
            print("GUI closed before enhancement could be applied.")

    threading.Thread(target=threaded_gemini_call_and_update, daemon=True).start()

def setup_gui():
    """Creates and sets up the main GUI window and widgets."""
    global text_widget, root, status_label

    root = tk.Tk()
    root.title("Gemini Prompt Enhancer")
    root.geometry("750x550")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Enter or paste your text below. Highlight a portion and press the hotkey to enhance it:").pack(pady=(0,5), anchor='w')

    text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, font=("Arial", 12), undo=True)
    text_widget.pack(fill=tk.BOTH, expand=True)
    text_widget.insert(tk.END, f"Welcome! This is a sample text.\n\nTry highlighting 'make this better' and pressing {HOTKEY}.\n\nOr, highlight this instruction: 'write a poem about a robot learning to dream'.")

    status_text = f"Hotkey: {HOTKEY}. Highlight text to enhance."
    if not GOOGLE_API_KEY:
        status_text = "Error: GEMINI_API_KEY not set. Functionality limited."
    elif not gemini_model: # Check if model initialization failed
        status_text = "Error: Gemini model failed to initialize. Check API key and model name. Functionality limited."

    if not GOOGLE_API_KEY or not gemini_model: # Show warning if either is an issue
        messagebox.showwarning("API Key/Initialization Issue",
                               "GEMINI_API_KEY environment variable might not be set, or the Gemini model failed to initialize.\n"
                               "Please check your API key, ensure the model name in the script is valid, and restart the application for full functionality.")


    status_label = ttk.Label(main_frame, text=status_text)
    status_label.pack(pady=(5,0), anchor='w')
    if "Error:" in status_text:
        status_label.config(foreground="red")

    text_widget.focus_set()
    return root

def main():
    """Main function to set up GUI and hotkeys."""
    global root

    gui_root = setup_gui()
    root = gui_root

    try:
        keyboard.add_hotkey(HOTKEY, process_enhancement_request, suppress=False)
        print(f"Hotkey '{HOTKEY}' registered successfully. Press it while text is selected in the application's text box.")
        if status_label and "Error:" not in status_label.cget("text"):
            status_label.config(text=f"Hotkey '{HOTKEY}' active. Highlight text and press it to enhance.")
    except Exception as e:
        error_msg = f"Failed to register hotkey '{HOTKEY}'. Error: {e}"
        print(error_msg)
        if status_label:
            status_label.config(text=f"CRITICAL ERROR: Failed to register hotkey {HOTKEY}. Try running as admin?", foreground="red")
        messagebox.showerror("Hotkey Registration Error",
                             f"{error_msg}\n\nThis might be due to system permissions "
                             f"(try running as administrator/root) or another application using this hotkey.\n"
                             "The application will run, but the hotkey enhancement feature will not work.")

    def on_closing():
        print("Closing application...")
        try:
            keyboard.remove_hotkey(HOTKEY)
            print(f"Hotkey '{HOTKEY}' unregistered.")
        except Exception:
            print(f"Could not unregister hotkey '{HOTKEY}' (it might not have been set).")
        if gui_root:
            gui_root.destroy()

    gui_root.protocol("WM_DELETE_WINDOW", on_closing)
    gui_root.mainloop()

if __name__ == "__main__":
    main()