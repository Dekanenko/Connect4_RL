import streamlit as st
import requests
import os

# --- Configuration ---
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000/api")

# --- UI Helper Functions ---
def render_board_and_buttons(board: list[list[int]], game_state: dict):
    """
    Renders the Connect4 board and the action buttons in a single, aligned grid.
    This solves the alignment issue.
    """
    colors = {0: "⚪", 1: "🔴", 2: "🟡"}
    
    # Render the board rows directly without reversing
    for r, row_data in enumerate(board):
        cols = st.columns(7)
        for i, cell in enumerate(row_data):
            with cols[i]:
                st.markdown(
                    f"<div class='board-cell'>{colors[cell]}</div>",
                    unsafe_allow_html=True,
                )
    
    st.write("---") # Visual separator

    # Render action buttons below the board
    # Check if it's the human's turn and the game is not over
    is_human_turn = (
        not game_state.get("game_over")
        and game_state.get("current_player") == game_state.get("human_player")
    )

    cols = st.columns(7)
    for i, col in enumerate(cols):
        with col:
            # A column is valid if the top cell (board[0]) is empty (0)
            is_valid_move = board[0][i] == 0
            # Use the on_click callback pattern for robust state updates
            col.button(
                "↓", 
                key=f"move_col_{i}", 
                disabled=not is_valid_move or not is_human_turn,
                on_click=make_move,
                args=(i,), # Pass the column index to the callback
                use_container_width=True
            )

def render_game_info(game_state: dict):
    """Displays the current game status, player color, and AI first-move toast."""
    # Handle AI first move toast
    if st.session_state.get("ai_made_first_move"):
        st.toast("The AI was chosen to go first! 🤖")
        st.session_state.ai_made_first_move = False

    # Display game over status
    if game_state.get("game_over"):
        winner = game_state.get("winner")
        human_player = game_state.get("human_player")
        if winner == 3:
            st.success("The game is a draw! 🤝")
        elif winner == human_player:
            st.balloons()
            st.success("Congratulations! You won! 🎉")
        else:
            st.error("The AI won. Better luck next time! 🤖")
    # Display in-progress status
    else:
        current_player = game_state.get("current_player")
        human_player = game_state.get("human_player")
        if current_player == human_player:
            st.info("Your turn. Please make a move.")
        else:
            st.warning("AI is thinking...")

        # Display player color info below the status message
        human_player_id = game_state.get("human_player")
        if human_player_id:
            colors = {1: "Red (🔴)", 2: "Yellow (🟡)"}
            st.markdown(f"**You are playing as {colors.get(human_player_id, 'Unknown')}**")


# --- API Communication & State Management ---
def init_game():
    """Initializes a new game, clearing any previous state."""
    # Clear session state to ensure a fresh start
    for key in st.session_state.keys():
        del st.session_state[key]
        
    try:
        response = requests.post(f"{BACKEND_URL}/game/init")
        response.raise_for_status()
        game_state = response.json()
        st.session_state.game_state = game_state

        # Check if the board is not empty, which implies AI moved first
        board = game_state.get("board", [])
        if any(sum(row) > 0 for row in board):
            st.session_state.ai_made_first_move = True

    except requests.exceptions.RequestException as e:
        st.session_state.error = f"Error connecting to the backend: {e}"

def make_move(column: int):
    """Sends the player's move to the backend and updates the session state."""
    if "game_state" not in st.session_state:
        st.session_state.error = "Game not initialized."
        return
    
    session_id = st.session_state.game_state.get("session_id")
    if not session_id:
        st.session_state.error = "Session ID is missing."
        return

    payload = {"session_id": session_id, "column": column}
    
    try:
        response = requests.post(f"{BACKEND_URL}/game/move", json=payload)
        response.raise_for_status()
        st.session_state.game_state = response.json()
    except requests.exceptions.RequestException as e:
        st.session_state.error = f"Error making move: {e}"

# --- Main Application Layout ---
st.set_page_config(page_title="Connect4 AI", layout="centered")

st.title("Play Connect4 Against an AI")

# --- Responsive CSS ---
st.markdown("""
<style>
.board-cell {
    font-size: 2rem;
    text-align: center;
    line-height: 3rem; /* Increased from 2rem for more vertical space */
}
@media (max-width: 600px) {
    .board-cell {
        font-size: 1.5rem;
        line-height: 2.25rem; /* Increased proportionally */
    }
}
</style>
""", unsafe_allow_html=True)

# Sidebar for game controls
with st.sidebar:
    st.header("Game Controls")
    # Use on_click for the New Game button as well for consistency
    st.button("New Game", on_click=init_game)

# Initialize the game on the very first run
if "game_state" not in st.session_state:
    init_game()

# Display error messages if any exist
if "error" in st.session_state and st.session_state.error:
    st.error(st.session_state.error)
    # Clear the error after displaying it
    st.session_state.error = None

# Main game area - only render if the game state is valid
if "game_state" in st.session_state and st.session_state.game_state:
    game_state = st.session_state.game_state
    
    render_game_info(game_state)
    st.write("---")
    render_board_and_buttons(game_state["board"], game_state)
else:
    st.warning("Waiting for the backend to initialize the game...")
    if st.button("Retry Connection"):
        init_game()
