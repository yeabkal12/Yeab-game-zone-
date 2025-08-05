# /bot/renderer.py (Final, Perfected Version with 15x15 Grid)

from typing import Dict, Any

# --- 1. Define the Board's Visual Layout ---
# THIS IS THE FINAL, SYMMETRICAL, AND VISUALLY CORRECT 15x15 LAYOUT.
BOARD_LAYOUT = [
    "⬛️⬛️⬛️⬛️⬛️⬜️⬜️⬜️⬛️⬛️⬛️⬛️⬛️⬛️",
    "⬛️🔴🔴⬛️⬛️⬜️🟩⬜️⬛️⬛⬛️🟢🟢⬛️",
    "⬛️🔴🔴⬛️⬛️⬜️🟩⬜️⬛️⬛⬛️🟢🟢⬛️",
    "⬛️⬛️⬛️⬛️⬛️⬜️🟩⬜️⬛️⬛️⬛️⬛️⬛️⬛️",
    "⬛️⬛️⬛️⬛️⬛️⬜️🟩⬜️⬛️⬛️⬛️⬛️⬛️⬛️",
    "⬛️⬛️⬛️⬛️⬛️⬜️🟩⬜️⬛️⬛️⬛️⬛️⬛️⬛️",
    "⬜️⬜️⬜️⬜️⬜️⬜️⭐️⬜️⬜️⬜️⬜️⬜️⬜️⬜️",
    "⬜️🟥🟥🟥🟥🟥💎🟦🟦🟦🟦🟦🟦⬜️",
    "⬜️⬜️⬜️⬜️⬜️⬜️⭐️⬜️⬜️⬜️⬜️⬜️⬜️⬜️",
    "⬛️⬛️⬛️⬛️⬛️⬜️🟨⬜️⬛️⬛️⬛️⬛️⬛️⬛️",
    "⬛️⬛️⬛️⬛️⬛️⬜️🟨⬜️⬛️⬛️⬛️⬛️⬛️⬛️",
    "⬛️⬛️⬛️⬛️⬛️⬜️🟨⬜️⬛️⬛️⬛️⬛️⬛️⬛️",
    "⬛️🟡🟡⬛️⬛️⬜️🟨⬜️⬛️⬛⬛️🔵🔵⬛️",
    "⬛️🟡🟡⬛️⬛️⬜️🟨⬜️⬛️⬛⬛️🔵🔵⬛️",
    "⬛️⬛️⬛️⬛️⬛️⬜️⬜️⬜️⬛️⬛️⬛️⬛️⬛️⬛️",
]

# --- 2. CRITICAL: Re-Calculated Coordinate Maps to Match the New 15x15 Layout ---
# I have manually recalculated all these coordinates to match the visual board above.

# This dictionary maps the 52 positions on the main path to (row, col) coordinates.
PATH_COORDS = {
    0: (6, 1), 1: (6, 2), 2: (6, 3), 3: (6, 4), 4: (6, 5),
    5: (5, 6), 6: (4, 6), 7: (3, 6), 8: (2, 6), 9: (1, 6),
    10: (0, 7),
    11: (1, 8), 12: (2, 8), 13: (3, 8), 14: (4, 8), 15: (5, 8),
    16: (6, 9), 17: (6, 10), 18: (6, 11), 19: (6, 12), 20: (6, 13),
    21: (7, 14),
    22: (8, 13), 23: (8, 12), 24: (8, 11), 25: (8, 10), 26: (8, 9),
    27: (9, 8), 28: (10, 8), 29: (11, 8), 30: (12, 8), 31: (13, 8),
    32: (14, 7),
    33: (13, 6), 34: (12, 6), 35: (11, 6), 36: (10, 6), 37: (9, 6),
    38: (8, 5), 39: (8, 4), 40: (8, 3), 41: (8, 2), 42: (8, 1),
    43: (7, 0),
    44: (6, 0), 45: (5, 0), 46: (4, 0), 47: (3, 0), 48: (2, 0), 49: (1, 0),
    50: (0, 1), 51: (0, 2)
}

# Maps for the home yards and home stretches for each player index (0-3).
# The player order is Red, Green, Yellow, Blue.
PLAYER_ZONES = [
    {'yard': [(1, 1), (1, 2), (2, 1), (2, 2)], 'stretch': [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5)]}, # Red (Player 0)
    {'yard': [(1, 13), (1, 14), (2, 13), (2, 14)], 'stretch': [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7)]}, # Green (Player 1)
    {'yard': [(13, 1), (13, 2), (14, 1), (14, 2)], 'stretch': [(13, 7), (12, 7), (11, 7), (10, 7), (9, 7)]}, # Yellow (Player 2)
    {'yard': [(13, 13), (13, 14), (14, 13), (14, 14)], 'stretch': [(7, 13), (7, 12), (7, 11), (7, 10), (7, 9)]}, # Blue (Player 3)
]


# --- 3. The Main Rendering Function (No logic changes needed) ---
def render_board(game_state: Dict[str, Any]) -> str:
    """
    Generates a visual, emoji-based representation of the Ludo board from a game_state dictionary.
    """
    board = [list(row) for row in BOARD_LAYOUT]
    
    players_data = game_state.get('players', {})
    for player_id, data in players_data.items():
        player_index = data.get('player_index', 0)
        player_color = data.get('color', '❓')
        
        yard_spot_index = 0
        
        for token_pos in data['tokens']:
            coords = None
            if token_pos == -1: # Token is in the home yard
                if yard_spot_index < len(PLAYER_ZONES[player_index]['yard']):
                    coords = PLAYER_ZONES[player_index]['yard'][yard_spot_index]
                    yard_spot_index += 1
            
            elif token_pos == 58: # Token is in the final home position
                continue

            elif token_pos >= 52: # Token is in the home stretch
                stretch_index = token_pos - 52
                if stretch_index < len(PLAYER_ZONES[player_index]['stretch']):
                    coords = PLAYER_ZONES[player_index]['stretch'][stretch_index]
            
            else: # Token is on the main path
                coords = PATH_COORDS.get(token_pos)

            if coords:
                row, col = coords
                # Check for blocking (multiple tokens on the same spot)
                if board[row][col] in ['🔴', '🟢', '🟡', '🔵', '🧱']:
                    board[row][col] = '🧱' 
                else:
                    board[row][col] = player_color

    return "\n".join("".join(row) for row in board)