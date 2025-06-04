import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import keyboard
import google.generativeai as genai
import threading
import os
import pyperclip # For clipboard access

# --- Configuration ---
# Hotkey to trigger enhancement of clipboard text
HOTKEY = "ctrl+shift+h" # You can change this

# --- Setup Gemini ---
GOOGLE_API_KEY = "AIzaSyB09PBV7PEYIJ7sYnxvnJB3rq5RmM1G6xY"
gemini_model = None

# Allow user to specify model via environment variable, with a fallback to a known working model.
# To use 'gemini-2.0-flash', set environment variable: GEMINI_MODEL_NAME=gemini-2.0-flash
MODEL_NAME_TO_USE = os.environ.get("GEMINI_MODEL_NAME", 'gemini-2.0-flash')

if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print(f"Attempting to initialize Gemini model with '{MODEL_NAME_TO_USE}'.")
        # WARNING: If GEMINI_MODEL_NAME is set to a non-existent model (e.g., 'gemini-2.0-flash'),
        # this line will likely raise an error.
        gemini_model = genai.GenerativeModel(MODEL_NAME_TO_USE)
        print(f"Gemini model '{MODEL_NAME_TO_USE}' initialized successfully.")
    except Exception as e:
        print(f"Error configuring Gemini with model '{MODEL_NAME_TO_USE}': {e}")
        gemini_model = None # Ensure model is None if initialization fails
else:
    print("Warning: GEMINI_API_KEY environment variable not set. Gemini functionality will be disabled.")

# --- Global Variables for GUI Elements ---
root = None
status_label = None
original_text_display = None
enhanced_text_display = None

def enhance_text_with_gemini(text_to_enhance):
    """Sends text to Gemini for enhancement and returns the result."""
    if not gemini_model:
        return "Error: Gemini model not initialized (API key issue or model configuration error)."
    try:
        # This prompt is geared towards enhancing prompts.
        # You might want to change it if you're processing general text.
        prompt = (
            f"You are an expert prompt engineer. Enhance the following text to be a more effective, clear, "
            f"and concise prompt. Focus on improving its ability to elicit the desired output from an AI. "
            f"Return only the enhanced prompt text, without any preamble or explanation. "
            f"Return the enhanced prompt without any additional text or formatting."
            f"Original text: \"{text_to_enhance}\""
        )
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error during Gemini API call: {str(e)}")
        return f"Error: Could not enhance text. ({type(e).__name__}: {str(e)})"

def update_gui_with_enhancement(original_text, enhanced_text):
    """Updates the GUI with original and enhanced text, and copies enhanced to clipboard."""
    global original_text_display, enhanced_text_display, status_label
    
    if original_text_display:
        original_text_display.config(state=tk.NORMAL)
        original_text_display.delete(1.0, tk.END)
        original_text_display.insert(tk.END, original_text)
        original_text_display.config(state=tk.DISABLED)

    if enhanced_text_display:
        enhanced_text_display.config(state=tk.NORMAL)
        enhanced_text_display.delete(1.0, tk.END)
        enhanced_text_display.insert(tk.END, enhanced_text)
        enhanced_text_display.config(state=tk.DISABLED)

    if "Error:" in enhanced_text:
        if status_label:
            status_label.config(text=f"Enhancement failed. See details in display areas or console.")
    else:
        try:
            pyperclip.copy(enhanced_text)
            if status_label:
                status_label.config(text=f"Enhanced text copied to clipboard! Press {HOTKEY} for next.")
        except pyperclip.PyperclipException as e:
            print(f"Error copying to clipboard: {e}")
            if status_label:
                status_label.config(text="Enhanced text displayed. Failed to copy to clipboard.")
            messagebox.showwarning("Clipboard Error", f"Could not copy enhanced text to clipboard: {e}\nOn Linux, ensure xclip or xsel is installed.")


def process_clipboard_enhancement_request():
    """Handles hotkey: reads from clipboard, calls Gemini, updates GUI & clipboard."""
    global status_label, root, original_text_display, enhanced_text_display

    if not gemini_model:
        messagebox.showerror("Gemini Not Ready", "Gemini model is not initialized. Please check your GEMINI_API_KEY, ensure the model name is configured correctly (e.g., via GEMINI_MODEL_NAME environment variable), and restart.")
        if status_label:
            status_label.config(text="Gemini not ready (API key/model issue).", foreground="red")
        return

    try:
        clipboard_text = pyperclip.paste()
        if not clipboard_text or not clipboard_text.strip():
            if status_label: status_label.config(text="Clipboard is empty or contains only whitespace.")
            if original_text_display:
                original_text_display.config(state=tk.NORMAL); original_text_display.delete(1.0, tk.END);
                original_text_display.insert(tk.END, "-- Clipboard was empty --"); original_text_display.config(state=tk.DISABLED)
            if enhanced_text_display:
                enhanced_text_display.config(state=tk.NORMAL); enhanced_text_display.delete(1.0, tk.END); enhanced_text_display.config(state=tk.DISABLED)
            return
    except pyperclip.PyperclipException as e:
        print(f"Error reading from clipboard: {e}")
        if status_label: status_label.config(text="Error reading from clipboard. Is it accessible?")
        messagebox.showerror("Clipboard Error", f"Could not read from clipboard: {e}\nOn Linux, you might need to install xclip or xsel (e.g., sudo apt-get install xclip).")
        return
    except Exception as e:
        print(f"Unexpected error reading from clipboard: {e}")
        if status_label: status_label.config(text="Unexpected error reading from clipboard.")
        messagebox.showerror("Clipboard Error", f"An unexpected error occurred while reading from clipboard: {e}")
        return

    if status_label: status_label.config(text="Enhancing text from clipboard with Gemini...")
    
    # Display original text immediately
    if original_text_display:
        original_text_display.config(state=tk.NORMAL); original_text_display.delete(1.0, tk.END)
        original_text_display.insert(tk.END, clipboard_text); original_text_display.config(state=tk.DISABLED)
    if enhanced_text_display: # Clear previous enhanced text
        enhanced_text_display.config(state=tk.NORMAL); enhanced_text_display.delete(1.0, tk.END); enhanced_text_display.config(state=tk.DISABLED)

    def threaded_gemini_call_and_update():
        enhanced_text_result = enhance_text_with_gemini(clipboard_text)
        if root: # Check if GUI is still alive
             root.after(0, lambda: update_gui_with_enhancement(clipboard_text, enhanced_text_result))
        elif not root:
            print("GUI closed before enhancement could be applied.")

    threading.Thread(target=threaded_gemini_call_and_update, daemon=True).start()


def setup_gui():
    global root, status_label, original_text_display, enhanced_text_display

    root = tk.Tk()
    root.title(f"Clipboard Prompt Enhancer ({MODEL_NAME_TO_USE})")
    root.geometry("750x600")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    instructions = (
        f"1. Highlight text in any application (e.g., browser).\n"
        f"2. Copy the highlighted text to clipboard (e.g., Ctrl+C).\n"
        f"3. Press the global hotkey: {HOTKEY}\n"
        f"The enhanced text will appear below and be copied to your clipboard."
    )
    ttk.Label(main_frame, text=instructions, justify=tk.LEFT).pack(pady=(0,10), anchor='w')

    ttk.Label(main_frame, text="Original Text (from Clipboard):").pack(pady=(5,0), anchor='w')
    original_text_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=10, font=("Arial", 10), state=tk.DISABLED, relief=tk.SOLID, borderwidth=1)
    original_text_display.pack(fill=tk.BOTH, expand=True, pady=(0,5))

    ttk.Label(main_frame, text="Enhanced Text (copied to clipboard):").pack(pady=(5,0), anchor='w')
    enhanced_text_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=10, font=("Arial", 10), state=tk.DISABLED, background="#f0f0f0", relief=tk.SOLID, borderwidth=1)
    enhanced_text_display.pack(fill=tk.BOTH, expand=True, pady=(0,5))

    status_text_default = f"Waiting for hotkey ({HOTKEY})..."
    status_text = status_text_default
    
    if not GOOGLE_API_KEY:
        status_text = "CRITICAL: GEMINI_API_KEY env var not set. Functionality disabled."
    elif not gemini_model: # Check if model initialization failed
        status_text = f"ERROR: Gemini model ('{MODEL_NAME_TO_USE}') failed to initialize. Check API key/model name. Disabled."

    if not GOOGLE_API_KEY or not gemini_model:
        messagebox.showwarning("API Key/Model Initialization Issue",
                               f"Gemini functionality is likely disabled.\nReason: {status_text}\n"
                               f"Ensure GEMINI_API_KEY is set. If GEMINI_MODEL_NAME is set, ensure '{MODEL_NAME_TO_USE}' is a valid model name.\n"
                               "Restart the application after correcting.")

    status_label = ttk.Label(main_frame, text=status_text)
    status_label.pack(pady=(10,0), anchor='w')
    if "ERROR:" in status_text.upper() or "CRITICAL:" in status_text.upper():
        status_label.config(foreground="red")

    # Attempt to bring window to front on Mac when launched, helps with initial focus for some operations.
    if os.name == 'posix' and 'darwin' in os.uname().sysname.lower():
        try:
            root.tk.call('::tk::unsupported::MacWindowStyle', 'style', root._w, 'metal', 'closable')
            root.deiconify()
            root.lift()
            root.focus_force()
        except tk.TclError:
            pass # Ignore if the call fails (e.g. on non-Mac or older Tk)


    return root

def main():
    global root

    gui_root = setup_gui()
    root = gui_root # Assign to global root for thread access (already done in setup_gui)

    try:
        keyboard.add_hotkey(HOTKEY, process_clipboard_enhancement_request, suppress=False)
        print(f"Global hotkey '{HOTKEY}' registered. Copy text and press it to enhance.")
        if status_label and "ERROR:" not in status_label.cget("text").upper() and "CRITICAL:" not in status_label.cget("text").upper():
             # Only update status if no critical errors are already shown
            status_label.config(text=f"Hotkey '{HOTKEY}' active. Copy text, then press hotkey.")
    except Exception as e:
        error_msg_hotkey = f"Failed to register global hotkey '{HOTKEY}'. Error: {e}"
        print(error_msg_hotkey)
        if status_label:
            status_label.config(text=f"CRITICAL ERROR: Failed to register hotkey {HOTKEY}. Try running as admin/root?", foreground="red")
        messagebox.showerror("Hotkey Registration Error",
                             f"{error_msg_hotkey}\n\nThis might be due to system permissions (try running as administrator/root if on Windows, or check Wayland/X11 permissions on Linux) or another application using this hotkey.\nThe application will run, but the hotkey enhancement feature will not work.")

    def on_closing():
        print("Closing application...")
        try:
            keyboard.unhook_all_hotkeys() # More robust than removing a single one if multiples were added by mistake
            print(f"All hotkeys unregistered.")
        except Exception as e_unhook:
            print(f"Could not unregister hotkeys: {e_unhook}")
        if gui_root:
            gui_root.destroy()

    gui_root.protocol("WM_DELETE_WINDOW", on_closing)
    gui_root.mainloop()

if __name__ == "__main__":
    main()