import streamlit as st
import numpy as np
import time
from copy import deepcopy

# Initialize game state
if 'board' not in st.session_state:
    st.session_state.board = np.full((3, 3), ' ')
    st.session_state.current_player = 'X'
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.mode = "human_vs_ai"  # Default mode
    st.session_state.message = "X's turn"

# Minimax algorithm with Alpha-Beta pruning
def minimax(board, depth, is_maximizing, alpha=-float('inf'), beta=float('inf')):
    # Check terminal states
    winner = check_winner(board)
    if winner == 'O':
        return 10 - depth
    elif winner == 'X':
        return depth - 10
    elif is_board_full(board):
        return 0
    
    if is_maximizing:
        best_score = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'O'
                    score = minimax(board, depth + 1, False, alpha, beta)
                    board[i][j] = ' '
                    best_score = max(score, best_score)
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'
                    score = minimax(board, depth + 1, True, alpha, beta)
                    board[i][j] = ' '
                    best_score = min(score, best_score)
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
        return best_score

# Get AI move using Minimax
def get_ai_move(board):
    best_score = -float('inf')
    best_move = None
    
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                score = minimax(board, 0, False)
                board[i][j] = ' '
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    
    return best_move

# Check if board is full
def is_board_full(board):
    return ' ' not in board.flatten()

# Check for winner
def check_winner(board):
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] != ' ':
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != ' ':
            return board[0][col]
    
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]
    
    return None

# Reset game
def reset_game():
    st.session_state.board = np.full((3, 3), ' ')
    st.session_state.current_player = 'X'
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.message = "X's turn"

# Handle cell click
def handle_click(row, col):
    if st.session_state.game_over or st.session_state.board[row][col] != ' ':
        return
    
    # Human move
    st.session_state.board[row][col] = st.session_state.current_player
    st.session_state.winner = check_winner(st.session_state.board)
    
    if st.session_state.winner:
        st.session_state.game_over = True
        st.session_state.message = f"{st.session_state.winner} wins!"
    elif is_board_full(st.session_state.board):
        st.session_state.game_over = True
        st.session_state.message = "It's a tie!"
    else:
        st.session_state.current_player = 'O' if st.session_state.current_player == 'X' else 'X'
        st.session_state.message = f"{st.session_state.current_player}'s turn"
        
        # AI move in AI mode
        if st.session_state.mode == "human_vs_ai" and st.session_state.current_player == 'O' and not st.session_state.game_over:
            ai_row, ai_col = get_ai_move(st.session_state.board)
            st.session_state.board[ai_row][ai_col] = 'O'
            st.session_state.winner = check_winner(st.session_state.board)
            
            if st.session_state.winner:
                st.session_state.game_over = True
                st.session_state.message = f"{st.session_state.winner} wins!"
            elif is_board_full(st.session_state.board):
                st.session_state.game_over = True
                st.session_state.message = "It's a tie!"
            else:
                st.session_state.current_player = 'X'
                st.session_state.message = "X's turn"

# Get cell background color
def get_cell_bg_color(value, row, col):
    if st.session_state.winner:
        # Check if this cell is part of winning combination
        winner = st.session_state.winner
        board = st.session_state.board
        
        # Check row
        if board[row][0] == board[row][1] == board[row][2] == winner and value == winner:
            return "#90EE90"  # Light green for winning row
        
        # Check column
        if board[0][col] == board[1][col] == board[2][col] == winner and value == winner:
            return "#90EE90"  # Light green for winning column
        
        # Check diagonals
        if row == col and board[0][0] == board[1][1] == board[2][2] == winner and value == winner:
            return "#90EE90"  # Light green for diagonal
        if row + col == 2 and board[0][2] == board[1][1] == board[2][0] == winner and value == winner:
            return "#90EE90"  # Light green for anti-diagonal
    
    return "#FFFFFF"  # White for regular cells

# Streamlit UI
st.title("Tic-Tac-Toe AI")
st.write("Play against an unbeatable AI using Minimax algorithm!")

# Game mode selection
mode = st.radio("Select game mode:", 
                ["human_vs_ai", "human_vs_human"],
                format_func=lambda x: "Human vs AI" if x == "human_vs_ai" else "Human vs Human")

if mode != st.session_state.mode:
    st.session_state.mode = mode
    reset_game()

# Display game board
cols = st.columns(3)
for row in range(3):
    for col in range(3):
        with cols[col]:
            cell_value = st.session_state.board[row][col]
            bg_color = get_cell_bg_color(cell_value, row, col)
            
            # Add some animation with a button press effect
            if st.button(cell_value if cell_value != ' ' else ' ', 
                        key=f"cell_{row}_{col}",
                        on_click=handle_click, 
                        args=(row, col),
                        type="primary" if cell_value == 'X' else "secondary",
                        help=f"Row {row+1}, Column {col+1}"):
                pass
            
            # Custom CSS for coloring and animation
            st.markdown(f"""
                <style>
                    div[data-testid="stButton"] > button[kind="primary"] {{
                        background-color: #FF6B6B;
                        color: white;
                        font-size: 24px;
                        height: 80px;
                        width: 80px;
                        border: none;
                    }}
                    div[data-testid="stButton"] > button[kind="secondary"] {{
                        background-color: #4ECDC4;
                        color: white;
                        font-size: 24px;
                        height: 80px;
                        width: 80px;
                        border: none;
                    }}
                    div[data-testid="stButton"] > button:not([kind]) {{
                        background-color: {bg_color};
                        font-size: 24px;
                        height: 80px;
                        width: 80px;
                    }}
                </style>
            """, unsafe_allow_html=True)

# Game status and controls
st.write(st.session_state.message)

if st.button("Reset Game"):
    reset_game()

# Game instructions
st.markdown("""
### How to Play:
- **Human vs AI**: You play as X, the AI plays as O
- **Human vs Human**: Two players alternate turns
- Click any empty cell to make your move
- The first to get 3 in a row wins!
""")