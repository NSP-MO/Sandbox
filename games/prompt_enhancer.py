import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import keyboard
import google.generativeai as genai
import threading
import os
import pyperclip
import pystray # For system tray
from PIL import Image, ImageDraw # For icon handling

# --- Configuration ---
HOTKEY = "ctrl+alt+c" # Global hotkey
APP_ICON_PATH = "app_icon.png" # Recommended: 32x32 or 64x64 PNG

# --- Hardcoded API Key (as per user request) ---
GOOGLE_API_KEY = "AIzaSyB09PBV7PEYIJ7sYnxvnJB3rq5RmM1G6xY"
gemini_model = None

# Model name configuration
MODEL_NAME_TO_USE = os.environ.get("GEMINI_MODEL_NAME", 'gemini-2.0-flash')

if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        print(f"Attempting to initialize Gemini model with '{MODEL_NAME_TO_USE}'.")
        gemini_model = genai.GenerativeModel(MODEL_NAME_TO_USE)
        print(f"Gemini model '{MODEL_NAME_TO_USE}' initialized successfully.")
    except Exception as e:
        print(f"Error configuring Gemini with model '{MODEL_NAME_TO_USE}': {e}")
        gemini_model = None
else:
    print("Warning: API Key not provided in script. Gemini functionality will be disabled.") # Should not happen with hardcoded key

# --- Global Variables ---
root = None # Tkinter main window
status_label = None
original_text_display = None
enhanced_text_display = None
tray_icon_instance = None # pystray.Icon instance

# --- Gemini Logic (remains the same) ---
def enhance_text_with_gemini(text_to_enhance):
    if not gemini_model:
        return "Error: Gemini model not initialized."
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
        print(f"Error during Gemini API call: {str(e)}")
        return f"Error: Could not enhance text. ({type(e).__name__}: {str(e)})"

# --- GUI Update Logic (remains the same) ---
def update_gui_with_enhancement(original_text, enhanced_text):
    global original_text_display, enhanced_text_display, status_label
    if not root: return # GUI might not be ready or already destroyed

    def _update():
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
            if status_label: status_label.config(text="Enhancement failed. Details above or in console.")
        else:
            try:
                pyperclip.copy(enhanced_text)
                if status_label: status_label.config(text=f"Enhanced text copied to clipboard! ({HOTKEY})")
            except pyperclip.PyperclipException as e:
                print(f"Error copying to clipboard: {e}")
                if status_label: status_label.config(text="Enhanced. Failed to copy to clipboard.")
                messagebox.showwarning("Clipboard Error", f"Could not copy: {e}", parent=root if root and root.winfo_exists() else None)
    
    if root and root.winfo_exists():
        root.after(0, _update)


# --- Clipboard Processing Logic (remains the same) ---
def process_clipboard_enhancement_request():
    global status_label, root
    if not gemini_model:
        if root and root.winfo_exists():
            messagebox.showerror("Gemini Not Ready", "Gemini model not initialized.", parent=root)
        else:
            print("Gemini model not initialized.")
        if status_label and root and root.winfo_exists(): status_label.config(text="Gemini not ready.", foreground="red")
        return

    try:
        clipboard_text = pyperclip.paste()
        if not clipboard_text or not clipboard_text.strip():
            if status_label and root and root.winfo_exists(): status_label.config(text="Clipboard empty.")
            if original_text_display and root and root.winfo_exists():
                original_text_display.config(state=tk.NORMAL); original_text_display.delete(1.0, tk.END)
                original_text_display.insert(tk.END, "-- Clipboard was empty --"); original_text_display.config(state=tk.DISABLED)
            if enhanced_text_display and root and root.winfo_exists():
                enhanced_text_display.config(state=tk.NORMAL); enhanced_text_display.delete(1.0, tk.END); enhanced_text_display.config(state=tk.DISABLED)
            return
    except pyperclip.PyperclipException as e:
        print(f"Error reading from clipboard: {e}")
        if status_label and root and root.winfo_exists(): status_label.config(text="Error reading clipboard.")
        if root and root.winfo_exists():
            messagebox.showerror("Clipboard Error", f"Could not read from clipboard: {e}", parent=root)
        return
    except Exception as e: # Catch any other unexpected error during paste
        print(f"Unexpected error reading from clipboard: {e}")
        if status_label and root and root.winfo_exists(): status_label.config(text="Unexpected clipboard error.")
        if root and root.winfo_exists():
            messagebox.showerror("Clipboard Error", f"Unexpected clipboard error: {e}", parent=root)
        return
    
    if status_label and root and root.winfo_exists(): status_label.config(text="Enhancing from clipboard...")
    if original_text_display and root and root.winfo_exists():
        original_text_display.config(state=tk.NORMAL); original_text_display.delete(1.0, tk.END)
        original_text_display.insert(tk.END, clipboard_text); original_text_display.config(state=tk.DISABLED)
    if enhanced_text_display and root and root.winfo_exists():
        enhanced_text_display.config(state=tk.NORMAL); enhanced_text_display.delete(1.0, tk.END); enhanced_text_display.config(state=tk.DISABLED)

    def threaded_call():
        enhanced_text_result = enhance_text_with_gemini(clipboard_text)
        if root: # Check if GUI is still intended to be used
             update_gui_with_enhancement(clipboard_text, enhanced_text_result) # Uses root.after
        else: # If GUI is gone, maybe just copy to clipboard
            if "Error:" not in enhanced_text_result:
                try: pyperclip.copy(enhanced_text_result); print("Enhanced text copied to clipboard (GUI closed).")
                except: print("Failed to copy to clipboard (GUI closed).")
    threading.Thread(target=threaded_call, daemon=True).start()

# --- Window Management Functions ---
def show_main_window():
    if root and root.winfo_exists():
        root.after(0, lambda: [root.deiconify(), root.lift(), root.focus_force()])

def hide_main_window():
    if root and root.winfo_exists():
        root.after(0, root.withdraw)

def toggle_window_visibility():
    if root and root.winfo_exists():
        if root.state() == 'withdrawn' or not root.winfo_viewable():
            show_main_window()
        else:
            hide_main_window()

# --- Tray Icon Action Callbacks ---
def on_show_hide_clicked():
    toggle_window_visibility()

def on_enhance_clipboard_clicked():
    process_clipboard_enhancement_request() # This function is already designed to be callable

def on_exit_clicked():
    global tray_icon_instance, root
    print("Exit sequence started from tray menu.")
    if tray_icon_instance:
        tray_icon_instance.stop() # Stops the pystray thread's blocking run()

    try:
        keyboard.unhook_all_hotkeys()
        print("Hotkeys unhooked.")
    except Exception as e_unhook:
        print(f"Could not unregister hotkeys during exit: {e_unhook}")

    if root and root.winfo_exists():
        # root.destroy() will implicitly call root.quit() and stop the mainloop
        root.after(0, root.destroy) # Schedule destroy for the main Tkinter thread
    elif root: # If root exists but window doesn't (already destroyed somehow)
        root.quit() # Try to quit mainloop if still running

# --- System Tray Setup ---
def run_pystray_icon():
    global tray_icon_instance
    
    try:
        # Try to load user-provided icon
        image = Image.open(APP_ICON_PATH)
        print(f"Loaded icon from '{APP_ICON_PATH}'.")
    except FileNotFoundError:
        print(f"'{APP_ICON_PATH}' not found. Creating a default icon.")
        # Create a simple default icon if app_icon.png is not found
        width, height = 64, 64
        color1, color2 = (230, 230, 230, 255), (100, 100, 250, 255) # Light grey, blue
        image = Image.new('RGBA', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.ellipse([(width*0.2, height*0.2), (width*0.8, height*0.8)], fill=color2)
        dc.text((width*0.35, height*0.4), "CE", fill=(255,255,255,255), font_size=int(height*0.3))

    except Exception as e:
        print(f"Error loading icon '{APP_ICON_PATH}': {e}. Icon might not display correctly.")
        # Fallback if any other error occurs during image load
        image = Image.new('RGB', (64, 64), color='red') # Simple fallback

    menu = pystray.Menu(
        pystray.MenuItem('Show/Hide App', on_show_hide_clicked, default=True), # Default action on left-click
        pystray.MenuItem('Enhance from Clipboard', on_enhance_clipboard_clicked),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Exit', on_exit_clicked)
    )
    
    tray_icon_instance = pystray.Icon("ClipboardEnhancer", image, f"Clipboard Enhancer ({MODEL_NAME_TO_USE})", menu)
    print("Starting system tray icon...")
    tray_icon_instance.run() # This blocks the current thread until icon.stop()
    print("System tray icon stopped.")


# --- GUI Setup (Modified for Tray) ---
def setup_gui():
    global root, status_label, original_text_display, enhanced_text_display

    root = tk.Tk()
    root.title(f"Clipboard Prompt Enhancer ({MODEL_NAME_TO_USE})")
    root.geometry("750x600")

    # Override the 'X' button to hide the window instead of closing
    root.protocol("WM_DELETE_WINDOW", hide_main_window)

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    instructions_text = (
        f"1. Highlight text & Copy (Ctrl+C).\n"
        f"2. Press global hotkey: {HOTKEY}\n"
        f"   (Or use tray menu 'Enhance from Clipboard')\n"
        f"3. Enhanced text is copied to clipboard & shown below.\n"
        f"App runs in system tray. Use tray icon to Show/Hide or Exit."
    )
    ttk.Label(main_frame, text=instructions_text, justify=tk.LEFT).pack(pady=(0,10), anchor='w')

    ttk.Label(main_frame, text="Original Text (from Clipboard):").pack(pady=(5,0), anchor='w')
    original_text_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=10, font=("Arial", 10), state=tk.DISABLED, relief=tk.SOLID, borderwidth=1)
    original_text_display.pack(fill=tk.BOTH, expand=True, pady=(0,5))

    ttk.Label(main_frame, text="Enhanced Text (copied to clipboard):").pack(pady=(5,0), anchor='w')
    enhanced_text_display = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=10, font=("Arial", 10), state=tk.DISABLED, background="#f0f0f0", relief=tk.SOLID, borderwidth=1)
    enhanced_text_display.pack(fill=tk.BOTH, expand=True, pady=(0,5))

    status_text_default = f"Tray Active. Hotkey: {HOTKEY}. Right-click tray for menu."
    current_status_text = status_text_default
    
    if not GOOGLE_API_KEY: # Should not be hit due to hardcoding
        current_status_text = "CRITICAL: API Key missing. Functionality disabled."
    elif not gemini_model:
        current_status_text = f"ERROR: Gemini ('{MODEL_NAME_TO_USE}') failed. Check key/model. Disabled."

    status_label = ttk.Label(main_frame, text=current_status_text)
    status_label.pack(pady=(10,0), anchor='w')
    if "ERROR:" in current_status_text.upper() or "CRITICAL:" in current_status_text.upper():
        status_label.config(foreground="red")
        if root and root.winfo_exists(): # Show initial critical error as messagebox if GUI is up
             messagebox.showwarning("Startup Issue", current_status_text, parent=root)


    # Attempt to bring window to front on Mac when shown initially, helps with focus.
    # This is less relevant now as it starts hidden, but good for 'show_window'.
    if os.name == 'posix' and 'darwin' in os.uname().sysname.lower():
        try:
            root.tk.call('::tk::unsupported::MacWindowStyle', 'style', root._w, 'metal', 'closable')
        except tk.TclError: pass
    
    return root

# --- Main Application ---
if __name__ == "__main__":
    # Initialize GUI, but don't show it initially
    gui_root = setup_gui()
    if gui_root:
        hide_main_window() # Start hidden in tray

    # Register global hotkey
    try:
        keyboard.add_hotkey(HOTKEY, process_clipboard_enhancement_request, suppress=False)
        print(f"Global hotkey '{HOTKEY}' registered.")
    except Exception as e:
        error_msg_hotkey = f"Failed to register global hotkey '{HOTKEY}'. Error: {e}"
        print(error_msg_hotkey)
        if gui_root and gui_root.winfo_exists():
            messagebox.showerror("Hotkey Error", f"{error_msg_hotkey}\nApp may not work as expected.", parent=gui_root)
        # Decide if app should exit if hotkey is critical. For now, it continues.

    # Start the system tray icon in a separate thread
    # daemon=True ensures this thread exits when the main program exits
    tray_thread = threading.Thread(target=run_pystray_icon, daemon=True)
    tray_thread.start()

    # Start Tkinter main loop (this is blocking)
    if gui_root:
        try:
            gui_root.mainloop()
        except KeyboardInterrupt:
            print("KeyboardInterrupt caught in mainloop. Exiting...")
            on_exit_clicked() # Graceful shutdown
        finally:
            print("Tkinter mainloop finished.")
    else:
        print("GUI Root not created. Application cannot start UI mainloop.")
        # If GUI failed, tray might still run if thread started.
        # Consider cleaner exit if GUI is essential