import tkinter as tk
from tkinter import ttk
from typing import List, Tuple

class VisualPegSolitaire:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Peg Solitaire Solver")
        
        # Initializing the game state
        self.board = [
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 2, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 0, 0]
        ]
        self.moves = []  # Stores the sequence of moves for the solution
        self.directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        self.attempts = 0
        self.solving = False
        self.delay = 1500  # 1,5 second delay between moves
        self.current_move = 0
        self.total_solution_moves = 0
        self.solution_found = False

        # GUI elements
        self.setup_gui()

    def setup_gui(self):
        # Main frame
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0)
        
        # Canvas for the board
        self.canvas = tk.Canvas(frame, width=350, height=350, bg='white')
        self.canvas.grid(row=0, column=0, columnspan=2, pady=5)

        # Info label
        self.info_label = ttk.Label(frame, text="Ready to solve")
        self.info_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Solve", command=self.start_solving).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Show Solution", command=self.show_solution).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_game).grid(row=0, column=2, padx=5)

        # Draw board
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        size = 40
        offset = 35

        for r in range(7):
            for c in range(7):
                x = offset + c * size
                y = offset + r * size

                if self.board[r][c] != 0:
                    # Draw cell
                    self.canvas.create_rectangle(x, y, x+size, y+size, fill='tan')
                    
                    # Draw peg or hole
                    if self.board[r][c] == 1:  # Peg
                        self.canvas.create_oval(x+8, y+8, x+size-8, y+size-8, fill='brown')
                    else:  # Hole
                        self.canvas.create_oval(x+15, y+15, x+size-15, y+size-15, fill='black')

        # Update info label
        self.info_label.config(text=f"Pegs remaining: {self.count_pegs()} | Attempts: {self.attempts}")
        self.root.update()

    def count_pegs(self) -> int:
        return sum(row.count(1) for row in self.board)

    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < 7 and 0 <= col < 7 and self.board[row][col] != 0

    def get_valid_moves(self) -> List[Tuple[int, int, int, int]]:
        valid_moves = []
        for row in range(7):
            for col in range(7):
                if self.board[row][col] == 1:
                    for dx, dy in self.directions:
                        new_row, new_col = row + dx, col + dy
                        middle_row, middle_col = row + dx//2, col + dy//2
                        
                        if (self.is_valid_position(new_row, new_col) and 
                            self.is_valid_position(middle_row, middle_col) and
                            self.board[new_row][new_col] == 2 and
                            self.board[middle_row][middle_col] == 1):
                            valid_moves.append((row, col, new_row, new_col))
        return valid_moves

    def make_move(self, move: Tuple[int, int, int, int]):
        start_row, start_col, end_row, end_col = move
        middle_row, middle_col = (start_row + end_row)//2, (start_col + end_col)//2
        
        self.board[start_row][start_col] = 2
        self.board[middle_row][middle_col] = 2
        self.board[end_row][end_col] = 1
        self.moves.append(move)  # Add the move to the solution sequence
        self.current_move = len(self.moves)
        self.draw_board()

    def undo_move(self, move: Tuple[int, int, int, int]):
        start_row, start_col, end_row, end_col = move
        middle_row, middle_col = (start_row + end_row)//2, (start_col + end_col)//2
        
        self.board[start_row][start_col] = 1
        self.board[middle_row][middle_col] = 1
        self.board[end_row][end_col] = 2
        self.moves.pop()
        self.current_move = len(self.moves)
        self.draw_board()

    def solve(self) -> bool:
        if not self.solving:
            return False

        self.attempts += 1
        
        # Check if solved (1 peg in the middle)
        if self.count_pegs() == 1 and self.board[3][3] == 1:
            self.total_solution_moves = len(self.moves)
            self.solution_found = True
            return True
        
        valid_moves = self.get_valid_moves()
        for move in valid_moves:
            self.make_move(move)
            self.root.update()
            
            if self.solve():
                return True
                
            self.undo_move(move)
            self.root.update()
        
        return False

    def start_solving(self):
        self.solving = True
        self.solution_found = False
        self.info_label.config(text="Solving...")
        self.root.update()
        
        if self.solve():
            self.solution_moves = self.moves[:]  # Store solution moves separately for replay of the solution
            self.info_label.config(text=f"Solution found in {self.attempts} attempts! Click 'Show Solution' to view.")
        else:
            self.info_label.config(text="No solution found.")
        
        self.solving = False

    def show_solution(self):
        if not self.solution_found or not self.solution_moves:
            self.info_label.config(text="No solution to show.")
            return

        self.reset_game(update_gui=False)  # Reset without clearing moves
        self.moves = self.solution_moves[:]  # Restore moves for playback

        self.info_label.config(text="Showing solution...")
        self.root.update()

        def replay_step(index=0):
            if index < len(self.solution_moves):
                self.make_move(self.solution_moves[index])
                self.root.after(self.delay, lambda: replay_step(index + 1))
            else:
                self.info_label.config(text=f"Solution shown: {len(self.solution_moves)} moves")

        replay_step()  # Start replaying moves


    def reset_game(self, update_gui=True):
        self.board = [
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 2, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 0, 0]
        ]
        self.moves = []
        self.attempts = 0
        self.solving = False
        self.current_move = 0
        self.total_solution_moves = 0
        self.solution_found = False
        if update_gui:
            self.draw_board()
            self.info_label.config(text="Ready to solve")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = VisualPegSolitaire()
    game.run()