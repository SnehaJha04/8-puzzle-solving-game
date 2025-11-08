import tkinter as tk
from tkinter import messagebox
import random
import heapq
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
SIZE = 3  
TILE_SIZE = 150  
GOAL = tuple(range(1, SIZE*SIZE)) + (0,)  
def is_solvable(state):
    """Check solvability using inversion count"""
    arr = [x for x in state if x != 0]
    inv = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1
    return inv % 2 == 0
def manhattan(state):
    """Heuristic: Manhattan distance"""
    dist = 0
    for idx, val in enumerate(state):
        if val == 0:
            continue
        goal_r, goal_c = divmod(val-1, SIZE)
        r, c = divmod(idx, SIZE)
        dist += abs(r - goal_r) + abs(c - goal_c)
    return dist
def get_neighbors(state):
    """Generate possible moves from current state"""
    zero_idx = state.index(0)
    r, c = divmod(zero_idx, SIZE)
    moves = []
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE:
            new_idx = nr*SIZE + nc
            new_list = list(state)
            new_list[zero_idx], new_list[new_idx] = new_list[new_idx], new_list[zero_idx]
            moves.append(tuple(new_list))
    return moves
def a_star(start):
    """A* search to find shortest solution"""
    pq = []
    heapq.heappush(pq, (manhattan(start), 0, start, []))
    visited = set()
    while pq:
        f, g, state, path = heapq.heappop(pq)
        if state == GOAL:
            return path
        if state in visited:
            continue
        visited.add(state)
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                heapq.heappush(pq, (g+1+manhattan(neighbor), g+1, neighbor, path+[neighbor]))
    return None
class EightPuzzleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-Puzzle Game")
        self.resizable(False, False)
        self.state = GOAL
        self.move_count = 0
        self.tile_photoimages = {}
        ctrl = tk.Frame(self)
        ctrl.pack(pady=(10, 0))
        self.moves_label = tk.Label(ctrl, text="Moves: 0", font=("Arial", 14))
        self.moves_label.grid(row=0, column=0, padx=5)
        shuffle_btn = tk.Button(ctrl, text="Shuffle", command=self.shuffle_state)
        shuffle_btn.grid(row=0, column=1, padx=5)
        solve_btn = tk.Button(ctrl, text="Solve (A*)", command=self.solve_with_astar)
        solve_btn.grid(row=0, column=2, padx=5)
        self.puzzle_frame = tk.Frame(self)
        self.puzzle_frame.pack(padx=10, pady=10)
        self.tiles = []
        for r in range(SIZE):
            for c in range(SIZE):
                idx = r * SIZE + c
                btn = tk.Button(
                    self.puzzle_frame,
                    text="",
                    borderwidth=2,
                    relief="raised",
                    command=lambda i=idx: self.on_tile_click(i))
                btn.grid(row=r, column=c, padx=1, pady=1)
                self.tiles.append(btn)
        if PIL_AVAILABLE:
            self.prepare_tile_images()
        self.shuffle_state()
    def prepare_tile_images(self):
        """Split external image into tiles with numbers overlay"""
        try:
            full_img = Image.open("8-puzzle.jpg").resize((TILE_SIZE * SIZE, TILE_SIZE * SIZE))
        except Exception as e:
            print("Could not load 8-puzzle.jpg, using default colored tiles.", e)
            return
        font_size = int(TILE_SIZE * 0.2)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        idx = 0
        for r in range(SIZE):
            for c in range(SIZE):
                box = (c * TILE_SIZE, r * TILE_SIZE, (c+1) * TILE_SIZE, (r+1) * TILE_SIZE)
                piece = full_img.crop(box)
                if idx < SIZE*SIZE - 1:
                    draw = ImageDraw.Draw(piece)
                    text = str(idx+1)
                    bbox = draw.textbbox((0, 0), text, font=font)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    draw.rectangle([TILE_SIZE-tw-10, 5, TILE_SIZE-5, th+10], fill=(255,255,255,180))
                    draw.text((TILE_SIZE-tw-8, 5), text, fill="black", font=font)
                    self.tile_photoimages[idx+1] = ImageTk.PhotoImage(piece)
                else:
                    blank = Image.new("RGB", (TILE_SIZE, TILE_SIZE), (220, 220, 220))
                    self.tile_photoimages[0] = ImageTk.PhotoImage(blank)
                idx += 1
    def on_tile_click(self, idx):
        """Manual move if adjacent to blank"""
        zero_idx = self.state.index(0)
        if self.can_swap(idx, zero_idx):
            new_list = list(self.state)
            new_list[zero_idx], new_list[idx] = new_list[idx], new_list[zero_idx]
            self.state = tuple(new_list)
            self.move_count += 1
            self.update_ui()
            if self.state == GOAL:
                messagebox.showinfo("Solved!", f" You solved it in {self.move_count} moves!")
    def can_swap(self, i, zero_idx):
        r1, c1 = divmod(i, SIZE)
        r0, c0 = divmod(zero_idx, SIZE)
        return abs(r1 - r0) + abs(c1 - c0) == 1
    def update_ui(self):
        """Update puzzle tiles + move count"""
        for i, btn in enumerate(self.tiles):
            val = self.state[i]
            if PIL_AVAILABLE and val in self.tile_photoimages:
                img = self.tile_photoimages[val]
                btn.config(image=img, text="", bg="white")
                btn.image = img
            else:
                if val == 0:
                    btn.config(text="", bg="lightgrey", image="")
                else:
                    btn.config(text=str(val), font=("Arial", 24), bg="#8fbcd4", image="")
        self.moves_label.config(text=f"Moves: {self.move_count}")
    def shuffle_state(self):
        """Shuffle to random solvable state"""
        state = list(GOAL)
        random.shuffle(state)
        while not is_solvable(state) or tuple(state) == GOAL:
            random.shuffle(state)
        self.state = tuple(state)
        self.move_count = 0
        self.update_ui()
    def solve_with_astar(self):
        """Solve puzzle using A* and animate"""
        path = a_star(self.state)
        if not path:
            messagebox.showerror("Error", "No solution found!")
            return
        def animate(i=0):
            if i < len(path):
                self.state = path[i]
                self.update_ui()
                self.after(500, lambda: animate(i+1))
            else:
                messagebox.showinfo("Solved by A*", f"Solved in {len(path)} steps (optimal)!")
        animate()
def main():
    root = EightPuzzleGUI()
    root.mainloop()
if __name__ == "__main__":
    main()