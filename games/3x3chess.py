import pyautogui
import time
import os # For joining paths

# --- CONFIGURATION - USER MUST UPDATE THESE VALUES ---
# TODO: Define the path to the directory where your game image snippets are stored
IMAGE_ASSETS_DIR = "path/to/your/game_image_assets/" 

# TODO: Update with your actual image filenames
IMAGE_FILES = {
    "BS": os.path.join(IMAGE_ASSETS_DIR, "black_S.png"),
    "BM": os.path.join(IMAGE_ASSETS_DIR, "black_M.png"),
    "BB": os.path.join(IMAGE_ASSETS_DIR, "black_B.png"),
    "WS": os.path.join(IMAGE_ASSETS_DIR, "white_S.png"),
    "WM": os.path.join(IMAGE_ASSETS_DIR, "white_M.png"),
    "WB": os.path.join(IMAGE_ASSETS_DIR, "white_B.png"),
    "EMPTY": os.path.join(IMAGE_ASSETS_DIR, "empty_cell.png"), # Optional, can infer empty
}

# TODO: Screen coordinates of the top-left corner of the 3x3 game board
BOARD_SCREEN_TOP_LEFT_X = 500 
BOARD_SCREEN_TOP_LEFT_Y = 300

# TODO: Dimensions of a single cell on the game board
CELL_WIDTH = 100
CELL_HEIGHT = 100

# TODO: Screen coordinates for clicking UI elements to select Black's pieces
# These are (x, y) screen coordinates.
UI_SELECT_BLACK_PIECE = {
    "S": (BOARD_SCREEN_TOP_LEFT_X - 50, BOARD_SCREEN_TOP_LEFT_Y + CELL_HEIGHT * 0.5), # Example: Left of board
    "M": (BOARD_SCREEN_TOP_LEFT_X - 50, BOARD_SCREEN_TOP_LEFT_Y + CELL_HEIGHT * 1.5), # Example
    "B": (BOARD_SCREEN_TOP_LEFT_X - 50, BOARD_SCREEN_TOP_LEFT_Y + CELL_HEIGHT * 2.5), # Example
}
# Add UI_SELECT_WHITE_PIECE if the script needs to control White or if selection differs.

# Confidence level for image recognition (0.0 to 1.0)
IMAGE_RECOGNITION_CONFIDENCE = 0.8 
# --- END OF CONFIGURATION ---


PLAYER_BLACK = "Black"
PLAYER_WHITE = "White"
EMPTY_SQUARE = None

PIECE_SIZES_MAP = {"S": 1, "M": 2, "B": 3} # Internal mapping
PIECE_CHARS_MAP = {v: k for k, v in PIECE_SIZES_MAP.items()}

INITIAL_PIECES_PER_PLAYER = {"S": 3, "M": 3, "B": 3}


class EggyChessGUIGame:
    def __init__(self):
        self.board_state = [[EMPTY_SQUARE for _ in range(3)] for _ in range(3)]
        self.player_pieces_count = {
            PLAYER_BLACK: INITIAL_PIECES_PER_PLAYER.copy(),
            PLAYER_WHITE: INITIAL_PIECES_PER_PLAYER.copy(),
        }
        self.current_player = PLAYER_BLACK
        
        # Verify image assets exist (basic check)
        for key, path in IMAGE_FILES.items():
            if key != "EMPTY" and not os.path.exists(path): # EMPTY is optional
                print(f"Warning: Image file not found: {path}. GUI automation will likely fail.")
        for piece_type, coords in UI_SELECT_BLACK_PIECE.items():
             if not isinstance(coords, tuple) or len(coords) != 2:
                print(f"Warning: UI_SELECT_BLACK_PIECE for '{piece_type}' is not configured correctly.")


    def _get_cell_screen_region(self, row, col):
        """Calculates the screen region (left, top, width, height) for a given board cell."""
        left = BOARD_SCREEN_TOP_LEFT_X + col * CELL_WIDTH
        top = BOARD_SCREEN_TOP_LEFT_Y + row * CELL_HEIGHT
        return (left, top, CELL_WIDTH, CELL_HEIGHT)

    def _click_at(self, x, y, duration=0.1):
        pyautogui.moveTo(x, y, duration=0.1) # Move mouse smoothly
        pyautogui.click(x, y)
        time.sleep(0.5) # Give UI time to react

    def _identify_piece_in_region(self, region_tuple):
        """Identifies a piece in a given screen region.
           Returns (PLAYER, SIZE_CHAR) or EMPTY_SQUARE."""
        # TODO: This is a simplified version. You might need more robust image matching.
        # Consider trying to match largest pieces first if they visually obscure smaller ones.
        # Or, if pieces have unique colors per player, use that.
        
        # Check for Black pieces
        for size_char, size_val in PIECE_SIZES_MAP.items():
            img_key = f"B{size_char}"
            try:
                if pyautogui.locateOnScreen(IMAGE_FILES[img_key], region=region_tuple, confidence=IMAGE_RECOGNITION_CONFIDENCE):
                    return (PLAYER_BLACK, size_val)
            except Exception as e: # pyautogui.ImageNotFoundException or key error
                # print(f"Error checking for {img_key} in region {region_tuple}: {e}")
                pass # Image not found or file missing

        # Check for White pieces
        for size_char, size_val in PIECE_SIZES_MAP.items():
            img_key = f"W{size_char}"
            try:
                if pyautogui.locateOnScreen(IMAGE_FILES[img_key], region=region_tuple, confidence=IMAGE_RECOGNITION_CONFIDENCE):
                    return (PLAYER_WHITE, size_val)
            except Exception as e:
                # print(f"Error checking for {img_key} in region {region_tuple}: {e}")
                pass
        
        # Optional: Check for an explicit empty cell image
        # try:
        #     if IMAGE_FILES.get("EMPTY") and os.path.exists(IMAGE_FILES["EMPTY"]) and \
        #        pyautogui.locateOnScreen(IMAGE_FILES["EMPTY"], region=region_tuple, confidence=IMAGE_RECOGNITION_CONFIDENCE):
        #         return EMPTY_SQUARE
        # except Exception:
        #     pass
            
        return EMPTY_SQUARE # Assume empty if no piece is found

    def update_board_from_screen(self):
        """Scans the game board on screen and updates the internal board_state."""
        print("Scanning board from screen...")
        for r in range(3):
            for c in range(3):
                region = self._get_cell_screen_region(r, c)
                # pyautogui.screenshot(f"debug_cell_{r}_{c}.png", region=region) # For debugging
                piece_info = self._identify_piece_in_region(region)
                if piece_info != EMPTY_SQUARE:
                    player, size_val = piece_info
                    self.board_state[r][c] = (player, size_val) # Store size_val (integer)
                else:
                    self.board_state[r][c] = EMPTY_SQUARE
        self.display_board_console() # For debugging/logging

    def display_board_console(self):
        """Prints the internal board state to the console."""
        print("\nInternal Board State:")
        for r_idx, row_data in enumerate(self.board_state):
            display_row = []
            for c_idx, cell_data in enumerate(row_data):
                if cell_data == EMPTY_SQUARE:
                    display_row.append(" .  ")
                else:
                    player, size_val = cell_data
                    player_char = "B" if player == PLAYER_BLACK else "W"
                    piece_char = PIECE_CHARS_MAP[size_val]
                    display_row.append(f"{player_char}{piece_char} ")
            print(" | ".join(display_row))
            if r_idx < 2:
                print("-----------------")
        print("-" * 20)

    def select_game_piece_from_ui(self, player, piece_size_char):
        """Clicks the UI element to select the specified piece for the player."""
        # This assumes Black is the one being automated primarily.
        if player == PLAYER_BLACK:
            ui_map = UI_SELECT_BLACK_PIECE
        else:
            # TODO: Define UI_SELECT_WHITE_PIECE if needed, or raise error
            print(f"Error: UI piece selection not configured for {player}")
            return False

        coords = ui_map.get(piece_size_char.upper())
        if not coords:
            print(f"Error: UI coordinates for {player}'s {piece_size_char} piece not found.")
            return False
        
        if self.player_pieces_count[player][piece_size_char.upper()] <= 0:
            print(f"Internal count: Player {player} has no {piece_size_char.upper()} pieces left. Attempting click anyway.")
            # Game UI should prevent selection, this is a fallback.

        print(f"Attempting to select {player}'s {piece_size_char} piece from UI at {coords}...")
        self._click_at(coords[0], coords[1])
        # Assuming the game confirms selection visually or by mouse cursor change.
        return True


    def place_piece_on_gui(self, player, piece_size_char, row, col):
        """Selects a piece from UI and places it on the board GUI."""
        print(f"Attempting to place {player}'s {piece_size_char} at ({row},{col}) on GUI.")
        
        # 1. Select the piece from the game's UI
        if not self.select_game_piece_from_ui(player, piece_size_char):
            return False

        # 2. Calculate screen coordinates for the target cell
        cell_region = self._get_cell_screen_region(row, col)
        # Click in the center of the cell
        target_x = cell_region[0] + cell_region[2] // 2
        target_y = cell_region[1] + cell_region[3] // 2
        
        print(f"Clicking on board cell ({row},{col}) at screen coordinates ({target_x},{target_y}).")
        self._click_at(target_x, target_y)
        
        # 3. Update internal piece count (optimistic update)
        # A more robust system would confirm the move by re-scanning the board.
        current_piece_val_on_board = PIECE_SIZES_MAP.get(piece_size_char.upper())
        
        # Check if we are overwriting an existing piece
        # This logic is simplified; real "eating" implies the overwritten piece might return to opponent
        # or its size matters. The video implied pieces are simply overwritten if smaller.
        self.board_state[row][col] = (player, current_piece_val_on_board) # Update internal state
        self.player_pieces_count[player][piece_size_char.upper()] -= 1
        
        time.sleep(1) # Wait for game animation/update
        self.update_board_from_screen() # Re-sync with what's on screen
        return True

    def check_winner_from_internal_board(self):
        """Checks for a winner based on the internal board_state."""
        lines = []
        # Rows
        for r in range(3): lines.append([self.board_state[r][c] for c in range(3)])
        # Columns
        for c in range(3): lines.append([self.board_state[r][c] for r in range(3)])
        # Diagonals
        lines.append([self.board_state[i][i] for i in range(3)])
        lines.append([self.board_state[i][2 - i] for i in range(3)])

        for line in lines:
            if any(cell == EMPTY_SQUARE for cell in line): continue
            
            # All cells in line must be non-empty. Check if they belong to the same player.
            first_player_in_line = line[0][0] # (Player, Size)
            if all(cell[0] == first_player_in_line for cell in line):
                return first_player_in_line # Return the winning player
        return None

    def wait_for_opponent_move(self, player_to_wait_for):
        """Waits for the opponent to make a move by monitoring screen changes."""
        print(f"Waiting for {player_to_wait_for} to make a move...")
        initial_board_snapshot = [row[:] for row in self.board_state] # Deep copy
        
        # Count pieces for the player we are waiting for
        def count_player_pieces(board, player):
            count = 0
            for r in range(3):
                for c in range(3):
                    if board[r][c] != EMPTY_SQUARE and board[r][c][0] == player:
                        count +=1
            return count

        initial_opponent_piece_count = count_player_pieces(initial_board_snapshot, player_to_wait_for)

        max_wait_cycles = 60 # e.g., 30 seconds if 0.5s sleep
        for _ in range(max_wait_cycles):
            time.sleep(1) # Check every second
            self.update_board_from_screen()
            current_opponent_piece_count = count_player_pieces(self.board_state, player_to_wait_for)
            
            # A simple way to detect a move is if the opponent has more pieces or a piece changed
            # More robust: compare entire board states for expected player's piece appearing.
            if current_opponent_piece_count > initial_opponent_piece_count or \
               (current_opponent_piece_count == initial_opponent_piece_count and \
                self.board_state != initial_board_snapshot and \
                any(self.board_state[r][c] != EMPTY_SQUARE and self.board_state[r][c][0] == player_to_wait_for and \
                    (initial_board_snapshot[r][c] == EMPTY_SQUARE or initial_board_snapshot[r][c][0] != player_to_wait_for) \
                    for r in range(3) for c in range(3))
                ):
                print(f"{player_to_wait_for} seems to have moved.")
                # Find the move (simplified: find the new piece)
                for r in range(3):
                    for c in range(3):
                        if self.board_state[r][c] != initial_board_snapshot[r][c] and \
                           self.board_state[r][c] != EMPTY_SQUARE and \
                           self.board_state[r][c][0] == player_to_wait_for:
                            _, piece_val = self.board_state[r][c]
                            piece_char = PIECE_CHARS_MAP[piece_val]
                            print(f"Detected {player_to_wait_for} played {piece_char} at ({r},{c}).")
                            return (r, c, piece_char) # row, col, piece_size_char
                return True # Move detected, but exact spot not isolated by simple logic above
            print(".", end="", flush=True)
        print("\nTimed out waiting for opponent's move or move detection failed.")
        return None


    def play_strategic_game_gui(self):
        """Plays out the initial strategy using GUI automation."""
        print("Starting GUI automated game...")
        pyautogui.FAILSAFE = True # Move mouse to top-left corner to stop script

        # Ensure game window is active and focused (user might need to click it first)
        print("Please ensure the game window is active. Starting in 5 seconds...")
        time.sleep(5)

        # === Black's First Move (Medium at Center) ===
        self.current_player = PLAYER_BLACK
        print(f"\n--- {self.current_player}'s Turn (Strateg_y 1) ---")
        if self.player_pieces_count[PLAYER_BLACK]['M'] > 0:
            self.place_piece_on_gui(PLAYER_BLACK, 'M', 1, 1)
        else:
            print("Black has no Medium pieces for the first strategic move!")
            return

        winner = self.check_winner_from_internal_board()
        if winner:
            print(f"\n!!! {winner} wins! !!!")
            return

        # === Wait for White's Move ===
        self.current_player = PLAYER_WHITE
        print(f"\n--- Waiting for {self.current_player}'s Move ---")
        opponent_move_details = self.wait_for_opponent_move(PLAYER_WHITE)
        if not opponent_move_details :
            print("Could not detect White's move. Aborting.")
            return
        
        # opponent_move_details might be just True, or (r,c,char)
        # For strategy, we need to know where White played.
        # The self.board_state is already updated by wait_for_opponent_move
        # So, we need to find where White's piece is, that wasn't there before Black's M.
        # This needs a more robust "find last move" if opponent_move_details isn't specific.
        # For now, we'll assume self.board_state is current.
        
        # Scan again to be sure of white's move position
        self.update_board_from_screen() 
        # Find white's latest move (assuming only one new white piece)
        white_move_pos = None
        for r in range(3):
            for c in range(3):
                cell_content = self.board_state[r][c]
                # Check if it's a white piece and not the center (where black played M)
                if cell_content != EMPTY_SQUARE and cell_content[0] == PLAYER_WHITE and not (r==1 and c==1):
                    white_move_pos = (r, c)
                    _, white_piece_val = cell_content
                    print(f"Confirmed White ({PIECE_CHARS_MAP[white_piece_val]}) at ({r},{c})")
                    break
            if white_move_pos:
                break
        
        if not white_move_pos:
            print("Could not determine White's move position after waiting. Aborting.")
            return

        winner = self.check_winner_from_internal_board()
        if winner:
            print(f"\n!!! {winner} wins! !!!")
            return

        # === Black's Second Move (React to White) ===
        self.current_player = PLAYER_BLACK
        print(f"\n--- {self.current_player}'s Turn (Strategy 2) ---")
        
        wr, wc = white_move_pos
        black_played_response = False

        if self.player_pieces_count[PLAYER_BLACK]['B'] > 0: # Strategy often uses Big piece
            # Strategy from video:
            # Case 1: White plays on a side adjacent to Black's center Medium.
            # Sides are (0,1), (1,0), (1,2), (2,1)
            is_side_move = (wr == 1 and wc != 1) or (wc == 1 and wr != 1)
            if is_side_move:
                print(f"White played on a side at ({wr},{wc}). Black plays Big on top.")
                self.place_piece_on_gui(PLAYER_BLACK, 'B', wr, wc)
                black_played_response = True
            
            # Case 2: White plays in a corner.
            # Corners are (0,0), (0,2), (2,0), (2,2)
            is_corner_move = (wr % 2 == 0) and (wc % 2 == 0)
            if not black_played_response and is_corner_move:
                print(f"White played in a corner at ({wr},{wc}). Black plays Big 'beside'.")
                # Example: White at (0,0), Black M at (1,1). Video showed Black B at (0,1).
                # If white at (r_w, c_w) (a corner), black plays Big at:
                #   - If r_w is 0 (top row) or 2 (bottom row), play at (r_w, 1).
                #   - If c_w is 0 (left col) or 2 (right col), play at (1, c_w).
                # This tries to make a line with the center piece.
                target_br, target_bc = -1, -1
                if wr == 0 or wr == 2: # Top or bottom row corner
                    target_br, target_bc = wr, 1
                elif wc == 0 or wc == 2: # Left or right col corner (and not already covered)
                    target_br, target_bc = 1, wc
                
                if target_br != -1 and (self.board_state[target_br][target_bc] == EMPTY_SQUARE or \
                                       self.board_state[target_br][target_bc][0] == PLAYER_WHITE and \
                                       PIECE_SIZES_MAP['B'] > self.board_state[target_br][target_bc][1]):
                    self.place_piece_on_gui(PLAYER_BLACK, 'B', target_br, target_bc)
                    black_played_response = True
                else:
                    print("Strategic spot for 'beside' move is blocked or invalid. Black might need another strategy here.")
                    # TODO: Implement fallback or more advanced placement choice.
                    # For now, if the primary spot is taken, it might skip or need a smarter target.


            if not black_played_response:
                print("Black could not make a standard strategic response with Big piece. Consider alternative.")
        else:
            print("Black has no Big pieces for the second strategic move!")
            # TODO: Fallback strategy if 'B' is not available.

        winner = self.check_winner_from_internal_board()
        if winner:
            print(f"\n!!! {winner} wins! !!!")
        else:
            print("\nInitial strategic moves demonstrated via GUI.")
            print("Further game play requires more opponent move detection and strategic decisions.")


if __name__ == "__main__":
    # Make sure to configure IMAGE_ASSETS_DIR, coordinates, and image filenames above.
    
    # Basic test for image localization (run this part first with game open)
    # print("Testing image localization for Black Medium piece. Ensure it's visible on screen.")
    # print(f"Looking for: {IMAGE_FILES.get('BM', 'BM image not configured')}")
    # try:
    #     # You might need to define a specific region if your screen is large
    #     # or if multiple instances of the image could exist.
    #     location = pyautogui.locateCenterOnScreen(IMAGE_FILES['BM'], confidence=IMAGE_RECOGNITION_CONFIDENCE)
    #     if location:
    #         print(f"Test: Found Black Medium piece at screen coordinates: {location}")
    #         pyautogui.moveTo(location, duration=0.5) # Move mouse to it
    #     else:
    #         print("Test: Black Medium piece not found on screen. Check image and game.")
    # except KeyError:
    #      print("Test: IMAGE_FILES['BM'] not configured.")
    # except Exception as e: # Catches pyautogui.ImageNotFoundException too
    #     print(f"Test: Error during image localization: {e}")
    # time.sleep(3)


    game_automator = EggyChessGUIGame()
    try:
        game_automator.play_strategic_game_gui()
    except pyautogui.FailSafeException:
        print("\nFailsafe triggered (mouse moved to top-left corner). Script terminated.")
    except Exception as e:
        print(f"\nAn error occurred during GUI automation: {e}")
        import traceback
        traceback.print_exc()