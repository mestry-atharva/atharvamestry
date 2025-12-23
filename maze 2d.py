import tkinter as tk
from tkinter import messagebox
import random
import time

class MazeGame:
    def __init__(self, master, width=25, height=25):
        self.master = master
        self.master.title("Cube Maze Game - Hard Mode")
        self.master.configure(bg='#0a0a2e')  # Darker background for difficulty
        
        # Maze dimensions (increased for difficulty)
        self.width = width
        self.height = height
        self.cell_size = 25  # Smaller cells for larger maze
        
        # Timer settings
        self.time_limit = 180  # 3 minutes in seconds
        self.start_time = time.time()
        self.game_active = True
        
        # Fog of war settings
        self.visibility_radius = 3  # How many cells around player are visible
        
        # Player direction (default: right)
        self.player_direction = "right"
        
        # Create main frame
        main_frame = tk.Frame(master, bg='#0a0a2e')
        main_frame.pack(padx=10, pady=10)
        
        # Timer display
        self.timer_label = tk.Label(
            main_frame,
            text="Time: 3:00",
            font=("Arial", 14, "bold"),
            bg='#0a0a2e',
            fg='#ff6b6b'
        )
        self.timer_label.pack(pady=5)
        
        # Create canvas with border
        canvas_frame = tk.Frame(main_frame, bg='#4a4a8a', relief=tk.RAISED, bd=3)
        canvas_frame.pack()
        
        self.canvas = tk.Canvas(
            canvas_frame, 
            width=self.width * self.cell_size, 
            height=self.height * self.cell_size,
            bg='#0a0a2e',
            highlightthickness=0
        )
        self.canvas.pack(padx=2, pady=2)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Cube Maze - HARD MODE", 
            font=("Arial", 18, "bold"),
            bg='#0a0a2e',
            fg='#ff6b6b'
        )
        title_label.pack(pady=5)
        
        # Initialize maze
        self.maze = [[1 for _ in range(width)] for _ in range(height)]
        self.generate_complex_maze()
        
        # Player position
        self.player_x = 1
        self.player_y = 1
        
        # Exit position (far from start)
        self.exit_x = width - 2
        self.exit_y = height - 2
        
        # Track visited cells for fog of war
        self.visited = [[False for _ in range(width)] for _ in range(height)]
        self.visited[self.player_y][self.player_x] = True
        
        # Draw maze
        self.draw_maze()
        
        # Bind keys
        self.master.bind("<Up>", self.move_up)
        self.master.bind("<Down>", self.move_down)
        self.master.bind("<Left>", self.move_left)
        self.master.bind("<Right>", self.move_right)
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Use arrow keys to navigate. Reach the red exit before time runs out!",
            bg='#0a0a2e',
            fg='#cccccc',
            font=("Arial", 10)
        )
        instructions.pack(pady=5)
        
        # Control buttons frame
        button_frame = tk.Frame(main_frame, bg='#0a0a2e')
        button_frame.pack(pady=5)
        
        # Reset button
        reset_button = tk.Button(
            button_frame,
            text="New Maze",
            command=self.reset_game,
            bg='#4a4a8a',
            fg='white',
            font=("Arial", 10, "bold"),
            width=10
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Hint button (reveals a small area)
        hint_button = tk.Button(
            button_frame,
            text="Hint (3)",
            command=self.use_hint,
            bg='#6a6a9a',
            fg='white',
            font=("Arial", 10, "bold"),
            width=10
        )
        hint_button.pack(side=tk.LEFT, padx=5)
        self.hint_count = 3
        self.hint_button = hint_button
        
        # Start timer
        self.update_timer()
    
    def generate_complex_maze(self):
        """Generate a more complex maze with more dead ends"""
        # Initialize all cells as walls
        self.maze = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        # Start from position (1, 1)
        stack = [(1, 1)]
        self.maze[1][1] = 0  # Mark as visited
        
        # Directions: up, right, down, left
        directions = [(-2, 0), (0, 2), (2, 0), (0, -2)]
        
        while stack:
            current = stack[-1]
            x, y = current
            
            # Find unvisited neighbors
            neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.height - 1 and 0 < ny < self.width - 1 and self.maze[nx][ny] == 1:
                    neighbors.append((nx, ny, dx, dy))
            
            if neighbors:
                # Prefer creating dead ends (bias towards cells with fewer neighbors)
                if random.random() < 0.3:  # 30% chance to create a dead end
                    # Choose neighbor that leads to fewer options
                    neighbors.sort(key=lambda n: self.count_potential_neighbors(n[0], n[1]))
                    nx, ny, dx, dy = neighbors[0]
                else:
                    # Choose random neighbor
                    nx, ny, dx, dy = random.choice(neighbors)
                
                # Remove wall between current and chosen neighbor
                self.maze[x + dx // 2][y + dy // 2] = 0
                self.maze[nx][ny] = 0
                
                # Add neighbor to stack
                stack.append((nx, ny))
            else:
                # Backtrack
                stack.pop()
        
        # Add some random walls to create more complexity
        for _ in range(self.width * self.height // 50):
            x = random.randrange(2, self.height - 2, 2)
            y = random.randrange(2, self.width - 2, 2)
            if self.maze[x][y] == 0 and self.count_adjacent_paths(x, y) > 2:
                self.maze[x][y] = 1
        
        # Ensure start and end are clear
        self.maze[1][1] = 0
        self.maze[self.height - 2][self.width - 2] = 0
        
        # Create a path from start to end (ensure it's solvable)
        self.ensure_solvable()
    
    def count_potential_neighbors(self, x, y):
        """Count potential neighbors for a cell (for maze complexity)"""
        count = 0
        directions = [(-2, 0), (0, 2), (2, 0), (0, -2)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < self.height - 1 and 0 < ny < self.width - 1 and self.maze[nx][ny] == 1:
                count += 1
        return count
    
    def count_adjacent_paths(self, x, y):
        """Count adjacent path cells"""
        count = 0
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.height and 0 <= ny < self.width and self.maze[nx][ny] == 0:
                count += 1
        return count
    
    def ensure_solvable(self):
        """Ensure there's at least one path from start to end"""
        # Simple pathfinding to check solvability
        visited = set()
        stack = [(1, 1)]
        visited.add((1, 1))
        
        while stack:
            x, y = stack.pop()
            if (x, y) == (self.height - 2, self.width - 2):
                return  # Solvable
            
            directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.height and 0 <= ny < self.width and 
                    self.maze[nx][ny] == 0 and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    stack.append((nx, ny))
        
        # If not solvable, create a direct path
        self.create_direct_path()
    
    def create_direct_path(self):
        """Create a direct path from start to end"""
        x, y = 1, 1
        while x < self.height - 2 or y < self.width - 2:
            if x < self.height - 2 and random.random() < 0.5:
                x += 1
            elif y < self.width - 2:
                y += 1
            else:
                x += 1
            self.maze[x][y] = 0
    
    def draw_maze(self):
        """Draw the maze with fog of war effect"""
        self.canvas.delete("all")
        
        # Draw maze cells with fog of war
        for i in range(self.height):
            for j in range(self.width):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Check if cell is visible
                distance = abs(i - self.player_y) + abs(j - self.player_x)
                is_visible = distance <= self.visibility_radius or self.visited[i][j]
                
                if is_visible:
                    if self.maze[i][j] == 1:  # Wall
                        self.canvas.create_rectangle(
                            x1, y1, x2, y2,
                            fill='#4a4a8a',  # Darker walls
                            outline='#3a3a7a'
                        )
                    else:  # Path
                        self.canvas.create_rectangle(
                            x1, y1, x2, y2,
                            fill='#1a1a3e',  # Dark paths
                            outline='#1a1a3e'
                        )
                else:
                    # Fog of war
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill='#0a0a2e',  # Black fog
                        outline='#0a0a2e'
                    )
        
        # Draw exit if visible
        exit_distance = abs(self.exit_y - self.player_y) + abs(self.exit_x - self.player_x)
        if exit_distance <= self.visibility_radius or self.visited[self.exit_y][self.exit_x]:
            x1 = self.exit_x * self.cell_size
            y1 = self.exit_y * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill='#ff0000',  # Red exit
                outline='#ff0000'
            )
        
        # Draw player
        self.draw_player()
    
    def draw_player(self):
        """Draw the player character based on direction"""
        # Calculate the position of the player
        x = self.player_x * self.cell_size
        y = self.player_y * self.cell_size
        
        # Scale factor for pixel art
        scale = self.cell_size / 16
        
        # Draw different character based on direction
        if self.player_direction == "up":
            self.draw_character_up(x, y, scale)
        elif self.player_direction == "down":
            self.draw_character_down(x, y, scale)
        elif self.player_direction == "left":
            self.draw_character_left(x, y, scale)
        else:  # right
            self.draw_character_right(x, y, scale)
    
    def draw_character_up(self, x, y, scale):
        """Draw character facing up"""
        # Head (white)
        self.canvas.create_rectangle(
            x + 5*scale, y + 2*scale, x + 11*scale, y + 8*scale,
            fill='white', outline='white', tags="player"
        )
        # Eyes (black)
        self.canvas.create_rectangle(
            x + 6*scale, y + 4*scale, x + 7*scale, y + 5*scale,
            fill='black', outline='black', tags="player"
        )
        self.canvas.create_rectangle(
            x + 9*scale, y + 4*scale, x + 10*scale, y + 5*scale,
            fill='black', outline='black', tags="player"
        )
        # Body (blue)
        self.canvas.create_rectangle(
            x + 5*scale, y + 8*scale, x + 11*scale, y + 14*scale,
            fill='#4169E1', outline='#4169E1', tags="player"
        )
        # Item/Arm (holding something up)
        self.canvas.create_rectangle(
            x + 11*scale, y + 6*scale, x + 13*scale, y + 7*scale,
            fill='#8B4513', outline='#8B4513', tags="player"
        )
    
    def draw_character_down(self, x, y, scale):
        """Draw character facing down"""
        # Head (white)
        self.canvas.create_rectangle(
            x + 5*scale, y + 2*scale, x + 11*scale, y + 8*scale,
            fill='white', outline='white', tags="player"
        )
        # Eyes (black)
        self.canvas.create_rectangle(
            x + 6*scale, y + 4*scale, x + 7*scale, y + 5*scale,
            fill='black', outline='black', tags="player"
        )
        self.canvas.create_rectangle(
            x + 9*scale, y + 4*scale, x + 10*scale, y + 5*scale,
            fill='black', outline='black', tags="player"
        )
        # Body (blue)
        self.canvas.create_rectangle(
            x + 5*scale, y + 8*scale, x + 11*scale, y + 14*scale,
            fill='#4169E1', outline='#4169E1', tags="player"
        )
        # Item/Arm (holding something down)
        self.canvas.create_rectangle(
            x + 11*scale, y + 12*scale, x + 13*scale, y + 13*scale,
            fill='#8B4513', outline='#8B4513', tags="player"
        )
    
    def draw_character_left(self, x, y, scale):
        """Draw character facing left"""
        # Head (white)
        self.canvas.create_rectangle(
            x + 4*scale, y + 3*scale, x + 10*scale, y + 9*scale,
            fill='white', outline='white', tags="player"
        )
        # Eyes (black)
        self.canvas.create_rectangle(
            x + 5*scale, y + 5*scale, x + 6*scale, y + 6*scale,
            fill='black', outline='black', tags="player"
        )
        self.canvas.create_rectangle(
            x + 5*scale, y + 7*scale, x + 6*scale, y + 8*scale,
            fill='black', outline='black', tags="player"
        )
        # Body (blue)
        self.canvas.create_rectangle(
            x + 4*scale, y + 9*scale, x + 10*scale, y + 15*scale,
            fill='#4169E1', outline='#4169E1', tags="player"
        )
        # Item/Arm (holding something left)
        self.canvas.create_rectangle(
            x + 2*scale, y + 10*scale, x + 4*scale, y + 11*scale,
            fill='#8B4513', outline='#8B4513', tags="player"
        )
    
    def draw_character_right(self, x, y, scale):
        """Draw character facing right"""
        # Head (white)
        self.canvas.create_rectangle(
            x + 6*scale, y + 3*scale, x + 12*scale, y + 9*scale,
            fill='white', outline='white', tags="player"
        )
        # Eyes (black)
        self.canvas.create_rectangle(
            x + 10*scale, y + 5*scale, x + 11*scale, y + 6*scale,
            fill='black', outline='black', tags="player"
        )
        self.canvas.create_rectangle(
            x + 10*scale, y + 7*scale, x + 11*scale, y + 8*scale,
            fill='black', outline='black', tags="player"
        )
        # Body (blue)
        self.canvas.create_rectangle(
            x + 6*scale, y + 9*scale, x + 12*scale, y + 15*scale,
            fill='#4169E1', outline='#4169E1', tags="player"
        )
        # Item/Arm (holding something right)
        self.canvas.create_rectangle(
            x + 12*scale, y + 10*scale, x + 14*scale, y + 11*scale,
            fill='#8B4513', outline='#8B4513', tags="player"
        )
    
    def move_player(self, dx, dy):
        """Move the player in the specified direction"""
        if not self.game_active:
            return
            
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        # Check if move is valid
        if 0 <= new_x < self.width and 0 <= new_y < self.height and self.maze[new_y][new_x] == 0:
            self.player_x = new_x
            self.player_y = new_y
            
            # Update visited cells
            self.visited[new_y][new_x] = True
            
            # Redraw maze with fog of war
            self.draw_maze()
            
            # Check if player reached the exit
            if self.player_x == self.exit_x and self.player_y == self.exit_y:
                self.win_game()
    
    def move_up(self, event):
        self.player_direction = "up"
        self.move_player(0, -1)
    
    def move_down(self, event):
        self.player_direction = "down"
        self.move_player(0, 1)
    
    def move_left(self, event):
        self.player_direction = "left"
        self.move_player(-1, 0)
    
    def move_right(self, event):
        self.player_direction = "right"
        self.move_player(1, 0)
    
    def use_hint(self):
        """Use a hint to reveal more of the maze"""
        if self.hint_count > 0 and self.game_active:
            self.hint_count -= 1
            self.hint_button.config(text=f"Hint ({self.hint_count})")
            
            # Temporarily increase visibility radius
            old_radius = self.visibility_radius
            self.visibility_radius = 8
            self.draw_maze()
            
            # Reset after 2 seconds
            self.master.after(2000, lambda: setattr(self, 'visibility_radius', old_radius) or self.draw_maze())
    
    def update_timer(self):
        """Update the countdown timer"""
        if self.game_active:
            elapsed = time.time() - self.start_time
            remaining = max(0, self.time_limit - elapsed)
            
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            
            # Change color based on time remaining
            if remaining < 30:
                color = '#ff0000'  # Red
            elif remaining < 60:
                color = '#ffaa00'  # Orange
            else:
                color = '#ff6b6b'  # Light red
            
            self.timer_label.config(text=f"Time: {minutes}:{seconds:02d}", fg=color)
            
            if remaining == 0:
                self.lose_game()
            else:
                self.master.after(1000, self.update_timer)
    
    def win_game(self):
        """Handle winning the game"""
        self.game_active = False
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        messagebox.showinfo("Congratulations!", f"You've solved the maze in {minutes}:{seconds:02d}!")
        self.reset_game()
    
    def lose_game(self):
        """Handle losing the game"""
        self.game_active = False
        messagebox.showwarning("Time's Up!", "You ran out of time! Try again.")
        self.reset_game()
    
    def reset_game(self):
        """Reset the game with a new maze"""
        self.game_active = True
        self.start_time = time.time()
        self.hint_count = 3
        self.hint_button.config(text=f"Hint ({self.hint_count})")
        
        # Reset visited
        self.visited = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        # Generate new maze
        self.generate_complex_maze()
        
        # Reset player position
        self.player_x = 1
        self.player_y = 1
        self.visited[self.player_y][self.player_x] = True
        
        # Draw maze
        self.draw_maze()
        
        # Restart timer
        self.update_timer()

# Create the main window
root = tk.Tk()
game = MazeGame(root, width=25, height=25)
root.mainloop()