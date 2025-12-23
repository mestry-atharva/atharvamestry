import tkinter as tk
import math
from tkinter import messagebox

root = tk.Tk()
root.title("Circular Tic Tac Toe")
size = 600
center = size // 2
canvas = tk.Canvas(root, width=size, height=size, bg="white")
canvas.pack()

radii = [60, 110, 160, 210]
current_player = "blue"  # Players will be colored circles: blue and red
board = [[None]*8 for _ in range(4)]  # 4 rings, 8 slices each

def draw_board():
    canvas.delete("all")
    # Draw circles
    for r in radii:
        canvas.create_oval(center - r, center - r, center + r, center + r, width=2)
    # Draw dividing lines
    for i in range(8):
        angle = math.radians(i * 45)
        x = center + radii[-1] * math.cos(angle)
        y = center + radii[-1] * math.sin(angle)
        canvas.create_line(center, center, x, y, width=2)
    # Draw player moves
    for ring in range(4):
        inner_r = 0 if ring == 0 else radii[ring - 1]
        outer_r = radii[ring]
        for slice_num in range(8):
            if board[ring][slice_num] is not None:
                # Compute center angle of slice
                angle = math.radians((slice_num * 45) + 22.5)
                # Compute middle radius between inner and outer circle
                r_middle = (inner_r + outer_r) / 2
                x = center + r_middle * math.cos(angle)
                y = center + r_middle * math.sin(angle)
                # Draw a circle for player move
                color = board[ring][slice_num]
                canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill=color)

def check_win():
    # Win conditions for circular tic tac toe could be lines in rings, slices or diagonals.
    # Here we implement simple line checks on rings and slices for brevity.

    # Check rings (rows)
    for ring in range(4):
        for color in ["blue", "red"]:
            if all(board[ring][s] == color for s in range(8)):
                return color
    # Check slices (columns)
    for slice_num in range(8):
        for color in ["blue", "red"]:
            if all(board[r][slice_num] == color for r in range(4)):
                return color
    # Diagonal checks can be added similarly if needed.
    return None

def check_win():
    def check_consecutive(lst, color, length=4):
        count = 0
        for cell in lst:
            if cell == color:
                count += 1
                if count == length:
                    return True
            else:
                count = 0
        return False

    players = ["blue", "red"]

    for player in players:
        # Check rings for 4 in a row (including wrap-around on circle)
        for ring in range(4):
            row = board[ring]
            extended_row = row + row[:3]  # to handle wrap around circularly
            if check_consecutive(extended_row, player):
                return player

        # Check columns (slices) for 4 in a row
        for slice_num in range(8):
            col = [board[ring][slice_num] for ring in range(4)]
            if check_consecutive(col, player):
                return player

        # Check diagonals/spirals
        # there are 8 possible diagonal starts (one for each slice)
        for start_slice in range(8):
            diag1 = [board[i][(start_slice + i) % 8] for i in range(4)]
            diag2 = [board[i][(start_slice - i) % 8] for i in range(4)]
            if check_consecutive(diag1, player) or check_consecutive(diag2, player):
                return player

    return None


def click_event(event):
    global current_player
    dx = event.x - center
    dy = event.y - center
    dist = math.sqrt(dx**2 + dy**2)
    ring = None
    for i, r in enumerate(radii):
        if dist <= r:
            ring = i
            break
    if ring is None:
        return  # Click outside the board

    angle = math.atan2(dy, dx)
    if angle < 0:
        angle += 2 * math.pi
    slice_num = int(angle / (2 * math.pi / 8))

    if board[ring][slice_num] is None:
        board[ring][slice_num] = current_player
        winner = check_win()
        draw_board()
        if winner:
            messagebox.showinfo("Game Over", f"{winner.capitalize()} wins!")
            reset_game()
        else:
            # Switch player
            current_player = "red" if current_player == "blue" else "blue"

def reset_game():
    global board, current_player
    board = [[None]*8 for _ in range(4)]
    current_player = "blue"
    draw_board()

draw_board()
canvas.bind("<Button-1>", click_event)

root.mainloop()
