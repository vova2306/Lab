    def create_sand_particles(self):
        self.particles = []
        
        # Create particles in the top chamber with more variety
        for _ in range(self.total_particles):
            x = random.uniform(self.top_chamber['x1'] + 15, self.top_chamber['x2'] - 15)
            y = random.uniform(self.top_chamber['y1'] + 15, self.top_chamber['y2'] - 15)
            
            # Create different shapes for particles with more variety
            shape_type = random.choice(['circle', 'square', 'diamond', 'star', 'triangle'])
            size = random.randint(2, 5)  # Smaller particles for more natural look
            
            particle = {
                'x': x,
                'y': y,
                'size': size,
                'shape': shape_type,
                'speed': random.uniform(1.0, 3.0),  # Faster speeds
                'in_top': True,
                'in_neck': False,
                'in_bottom': False,
                'color': self.get_sand_color_variation(),
                'rotation': random.uniform(0, 360)  # Add rotation for more visual interest
            }
            
            self.particles.append(particle)import tkinter as tk
import time
import random
import math
from tkinter import ttk
from threading import Thread

class SandClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Песочные часы")
        self.root.geometry("400x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#F0E6D2")  # Warm background color
        
        # Colors
        self.sand_color = "#F2D16B"
        self.glass_color = "#ADD8E6"
        self.frame_color = "#8B4513"
        
        # Animation state
        self.running = False
        self.total_time = 10  # Default time in seconds
        self.remaining_time = self.total_time
        self.total_particles = 800  # Increased for better visual
        self.particles = []
        self.start_time = 0
        
        # Create UI elements
        self.create_widgets()
        
        # Draw initial state
        self.draw_initial_state()

    def create_widgets(self):
        # Main frame with background
        main_frame = tk.Frame(self.root, bg="#F0E6D2")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = tk.Label(main_frame, text="Песочные часы", font=("Arial", 18, "bold"), 
                              bg="#F0E6D2", fg="#8B4513")
        title_label.pack(pady=10)
        
        # Frame for controls with better styling
        control_frame = tk.Frame(main_frame, bg="#F0E6D2", bd=2, relief=tk.GROOVE)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=15)
        
        # Time input with better styling
        time_label = tk.Label(control_frame, text="Время (сек):", font=("Arial", 10, "bold"),
                             bg="#F0E6D2", fg="#8B4513")
        time_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.time_var = tk.StringVar(value="10")
        time_entry = tk.Entry(control_frame, textvariable=self.time_var, width=10,
                            font=("Arial", 10), bd=2, relief=tk.SUNKEN)
        time_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Start button with better styling
        self.start_button = tk.Button(control_frame, text="Старт", command=self.start_animation,
                                    font=("Arial", 10, "bold"), bg="#8B4513", fg="white",
                                    activebackground="#A0522D", bd=2, width=8)
        self.start_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Reset button with better styling
        self.reset_button = tk.Button(control_frame, text="Сброс", command=self.reset_animation,
                                    font=("Arial", 10, "bold"), bg="#8B4513", fg="white",
                                    activebackground="#A0522D", bd=2, width=8)
        self.reset_button.grid(row=0, column=3, padx=10, pady=10)
        
        # Canvas for drawing with border
        canvas_frame = tk.Frame(main_frame, bd=2, relief=tk.RIDGE, bg="#D2B48C")
        canvas_frame.pack(side=tk.TOP, padx=20, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#FFFAF0", width=400, height=500, bd=0)
        self.canvas.pack(padx=5, pady=5)
        
        # Timer label with better styling
        self.timer_label = tk.Label(control_frame, text="Время: 10 сек", 
                                  font=("Arial", 12, "bold"), bg="#F0E6D2", fg="#8B4513")
        self.timer_label.grid(row=1, column=0, columnspan=4, pady=5)

    def draw_initial_state(self):
        self.canvas.delete("all")
        
        # Draw sand clock frame
        self.draw_hourglass_frame()
        
        # Create initial sand particles in top chamber
        self.create_sand_particles()
        
        # Draw all particles
        self.draw_particles()
        
    def draw_hourglass_frame(self):
        # Draw fancy hour glass shape
        width, height = 400, 500
        center_x = width // 2
        
        # Improve visual style with more elegant shape
        # Top chamber - more rounded
        self.top_chamber = {
            'x1': center_x - 80,
            'y1': 50,
            'x2': center_x + 80,
            'y2': 180
        }
        
        # Bottom chamber - more rounded
        self.bottom_chamber = {
            'x1': center_x - 80,
            'y1': 320,
            'x2': center_x + 80,
            'y2': 450
        }
        
        # Draw wooden frame with better wood texture
        frame_gradient = ["#8B4513", "#A0522D", "#8B4513", "#6B4226"]
        for i in range(4):
            offset = i * 5
            self.canvas.create_rectangle(
                center_x - 100 + offset, 30 + offset, 
                center_x + 100 - offset, 470 - offset, 
                fill=frame_gradient[i], outline="#5E2605", width=1
            )
        
        # Draw glass top chamber with transparency effect
        self.canvas.create_arc(
            self.top_chamber['x1'] - 20, self.top_chamber['y1'] - 10, 
            self.top_chamber['x1'] + 40, self.top_chamber['y1'] + 50, 
            start=90, extent=180, fill=self.glass_color, outline="#AACCE6"
        )
        self.canvas.create_arc(
            self.top_chamber['x2'] - 40, self.top_chamber['y1'] - 10, 
            self.top_chamber['x2'] + 20, self.top_chamber['y1'] + 50, 
            start=270, extent=180, fill=self.glass_color, outline="#AACCE6"
        )
        self.canvas.create_rectangle(
            self.top_chamber['x1'], self.top_chamber['y1'] + 20, 
            self.top_chamber['x2'], self.top_chamber['y2'], 
            fill=self.glass_color, outline="#AACCE6"
        )
        
        # Add glass reflection effect
        self.canvas.create_arc(
            self.top_chamber['x1'] + 10, self.top_chamber['y1'] + 5, 
            self.top_chamber['x2'] - 10, self.top_chamber['y1'] + 40, 
            start=0, extent=180, fill="", outline="white", width=1
        )
        
        # Draw glass bottom chamber with transparency effect
        self.canvas.create_arc(
            self.bottom_chamber['x1'] - 20, self.bottom_chamber['y2'] - 50, 
            self.bottom_chamber['x1'] + 40, self.bottom_chamber['y2'] + 10, 
            start=90, extent=180, fill=self.glass_color, outline="#AACCE6"
        )
        self.canvas.create_arc(
            self.bottom_chamber['x2'] - 40, self.bottom_chamber['y2'] - 50, 
            self.bottom_chamber['x2'] + 20, self.bottom_chamber['y2'] + 10, 
            start=270, extent=180, fill=self.glass_color, outline="#AACCE6"
        )
        self.canvas.create_rectangle(
            self.bottom_chamber['x1'], self.bottom_chamber['y1'], 
            self.bottom_chamber['x2'], self.bottom_chamber['y2'] - 20, 
            fill=self.glass_color, outline="#AACCE6"
        )
        
        # Add glass reflection effect
        self.canvas.create_arc(
            self.bottom_chamber['x1'] + 10, self.bottom_chamber['y2'] - 40, 
            self.bottom_chamber['x2'] - 10, self.bottom_chamber['y2'] - 5, 
            start=0, extent=180, fill="", outline="white", width=1
        )
        
        # Draw neck of hourglass with slightly curved shape
        neck_width = 20
        neck_center = (self.top_chamber['y2'] + self.bottom_chamber['y1']) / 2
        neck_height = self.bottom_chamber['y1'] - self.top_chamber['y2']
        
        # Curved neck
        self.canvas.create_polygon(
            center_x - neck_width//2, self.top_chamber['y2'],
            center_x + neck_width//2, self.top_chamber['y2'],
            center_x + neck_width//2 + 2, neck_center,
            center_x + neck_width//2, self.bottom_chamber['y1'],
            center_x - neck_width//2, self.bottom_chamber['y1'],
            center_x - neck_width//2 - 2, neck_center,
            fill=self.glass_color, outline="#AACCE6"
        )
        
        # Define the neck area
        self.neck = {
            'x1': center_x - neck_width//2,
            'y1': self.top_chamber['y2'],
            'x2': center_x + neck_width//2,
            'y2': self.bottom_chamber['y1']
        }
        
        # Draw decorative elements
        # Top cap with 3D effect
        for i in range(3):
            offset = i * 2
            self.canvas.create_rectangle(
                center_x - 90 + offset, 30 + offset, 
                center_x + 90 - offset, 50 - offset, 
                fill="#8B4513" if i == 0 else "#6B4226" if i == 2 else "#A0522D", 
                outline="#5E2605"
            )
        
        # Bottom cap with 3D effect
        for i in range(3):
            offset = i * 2
            self.canvas.create_rectangle(
                center_x - 90 + offset, 450 + offset, 
                center_x + 90 - offset, 470 - offset, 
                fill="#8B4513" if i == 0 else "#6B4226" if i == 2 else "#A0522D", 
                outline="#5E2605"
            )
                                    
        # Draw decorative lines - patterns in the wood
        for x in range(center_x - 85, center_x + 86, 10):
            self.canvas.create_line(x, 30, x + 5, 50, fill="#5E2605", width=1)
            self.canvas.create_line(x, 450, x + 5, 470, fill="#5E2605", width=1)
            
        # Add ornamental metal corners
        corner_size = 15
        metal_color = "#D4AF37"  # Gold color
        
        # Top left corner
        self.canvas.create_polygon(
            center_x - 100, 30,
            center_x - 100 + corner_size, 30,
            center_x - 100, 30 + corner_size,
            fill=metal_color, outline="black"
        )
        
        # Top right corner
        self.canvas.create_polygon(
            center_x + 100, 30,
            center_x + 100 - corner_size, 30,
            center_x + 100, 30 + corner_size,
            fill=metal_color, outline="black"
        )
        
        # Bottom left corner
        self.canvas.create_polygon(
            center_x - 100, 470,
            center_x - 100 + corner_size, 470,
            center_x - 100, 470 - corner_size,
            fill=metal_color, outline="black"
        )
        
        # Bottom right corner
        self.canvas.create_polygon(
            center_x + 100, 470,
            center_x + 100 - corner_size, 470,
            center_x + 100, 470 - corner_size,
            fill=metal_color, outline="black"
        )

    def create_sand_particles(self):
        self.particles = []
        
        # Create particles in the top chamber
        for _ in range(self.total_particles):
            x = random.uniform(self.top_chamber['x1'] + 10, self.top_chamber['x2'] - 10)
            y = random.uniform(self.top_chamber['y1'] + 10, self.top_chamber['y2'] - 10)
            
            # Create different shapes for particles
            shape_type = random.choice(['circle', 'square', 'diamond'])
            size = random.randint(3, 6)
            
            particle = {
                'x': x,
                'y': y,
                'size': size,
                'shape': shape_type,
                'speed': random.uniform(0.5, 2.0),
                'in_top': True,
                'in_neck': False,
                'in_bottom': False,
                'color': self.get_sand_color_variation()
            }
            
            self.particles.append(particle)
    
    def get_sand_color_variation(self):
        # Create better variations of the sand color
        sand_colors = [
            "#F2D16B",  # Basic sand
            "#E8C455",  # Darker sand
            "#F7DC6F",  # Lighter sand
            "#D4AC0D",  # Gold sand
            "#F5CBA7",  # Pink sand
            "#EDBB99"   # Orange-tinted sand
        ]
        return random.choice(sand_colors)
    
    def draw_particles(self):
        for particle in self.particles:
            if particle['in_top'] or particle['in_neck'] or particle['in_bottom']:
                self.draw_particle(particle)
    
    def draw_particle(self, particle):
        x, y = particle['x'], particle['y']
        size = particle['size']
        
        if particle['shape'] == 'circle':
            self.canvas.create_oval(
                x - size, y - size, 
                x + size, y + size, 
                fill=particle['color'], outline=""
            )
        elif particle['shape'] == 'square':
            self.canvas.create_rectangle(
                x - size, y - size, 
                x + size, y + size, 
                fill=particle['color'], outline=""
            )
        elif particle['shape'] == 'diamond':
            self.canvas.create_polygon(
                x, y - size,
                x + size, y,
                x, y + size,
                x - size, y,
                fill=particle['color'], outline=""
            )
        elif particle['shape'] == 'star':
            # Simple 4-point star
            points = []
            for i in range(8):
                angle = math.radians(i * 45 + particle['rotation'])
                r = size if i % 2 == 0 else size * 0.5
                points.extend([x + r * math.cos(angle), y + r * math.sin(angle)])
            self.canvas.create_polygon(points, fill=particle['color'], outline="")
        elif particle['shape'] == 'triangle':
            rotation = math.radians(particle['rotation'])
            points = []
            for i in range(3):
                angle = rotation + math.radians(i * 120)
                points.extend([x + size * math.cos(angle), y + size * math.sin(angle)])
            self.canvas.create_polygon(points, fill=particle['color'], outline="")
    
    def start_animation(self):
        try:
            self.total_time = int(self.time_var.get())
            if self.total_time <= 0:
                raise ValueError("Время должно быть положительным")
        except ValueError:
            self.timer_label.config(text="Введите корректное время")
            return
            
        self.remaining_time = self.total_time
        self.timer_label.config(text=f"Время: {self.remaining_time} сек")
        
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.reset_button.config(state=tk.DISABLED)
            self.start_time = time.time()
            
            # Visual effect when starting - shake the hourglass
            self.shake_hourglass()
            
            # Start animation in a separate thread
            Thread(target=self.animate_sand_clock, daemon=True).start()
    
    def shake_hourglass(self):
        # Simple shaking animation effect when starting
        original_x = self.canvas.winfo_x()
        shake_distance = 5
        shake_speed = 0.05
        
        for _ in range(3):  # Shake 3 times
            for dx in [shake_distance, -shake_distance, shake_distance, -shake_distance, 0]:
                self.canvas.place(x=original_x + dx)
                self.root.update()
                time.sleep(shake_speed)
    
    def animate_sand_clock(self):
        particles_per_second = self.total_particles / self.total_time
        
        while self.running and (self.remaining_time > 0 or any(p['in_top'] or p['in_neck'] for p in self.particles)):
            self.canvas.delete("all")
            
            # Calculate elapsed time
            elapsed = time.time() - self.start_time
            self.remaining_time = max(0, self.total_time - elapsed)
            
            # Update timer display
            self.root.after(0, lambda: self.timer_label.config(text=f"Time: {self.remaining_time:.1f}s"))
            
            # Make sure all particles fall even after time is up
            particles_fallen = min(self.total_particles, 
                                  int(elapsed * particles_per_second) if self.remaining_time > 0 
                                  else self.total_particles)
            
            # Draw the hourglass frame
            self.draw_hourglass_frame()
            
            # Move particles
            self.move_particles(particles_fallen)
            
            # Draw all particles
            self.draw_particles()
            
            # Refresh GUI
            self.root.update()
            time.sleep(0.03)  # Control animation speed
            
        # Animation complete
        self.running = False
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.reset_button.config(state=tk.NORMAL))
    
    def move_particles(self, particles_fallen):
        neck_center_x = (self.neck['x1'] + self.neck['x2']) / 2
        
        # Make sure ALL particles will eventually fall
        # Calculate how many particles should have fallen by now based on elapsed time
        particles_to_move = particles_fallen
        
        for i in range(len(self.particles)):
            particle = self.particles[i]
            
            # If particle is still in top but should fall
            if particle['in_top'] and i < particles_to_move:
                # Move toward the neck
                angle = math.atan2(self.neck['y1'] - particle['y'], 
                                  neck_center_x - particle['x'])
                
                # Increase speed to make falling more visible
                particle['x'] += math.cos(angle) * particle['speed'] * 2
                particle['y'] += math.sin(angle) * particle['speed'] * 2
                
                # Check if particle reached the neck
                if (abs(particle['x'] - neck_center_x) < 8 and 
                    particle['y'] > self.top_chamber['y2'] - 10):
                    particle['in_top'] = False
                    particle['in_neck'] = True
                    particle['x'] = neck_center_x + random.uniform(-2, 2)
            
            # If particle is in the neck
            elif particle['in_neck']:
                # Move down through the neck faster
                particle['y'] += particle['speed'] * 3
                
                # Check if particle reached the bottom chamber
                if particle['y'] >= self.bottom_chamber['y1']:
                    particle['in_neck'] = False
                    particle['in_bottom'] = True
                    # Spread out in the bottom chamber
                    spread = 40  # Fixed spread for better distribution
                    particle['x'] = neck_center_x + random.uniform(-spread, spread)
            
            # If particle is in the bottom chamber
            elif particle['in_bottom']:
                # Calculate the overall pile shape using a conical distribution
                # The higher the particle count in bottom, the higher the pile
                
                # Count particles in bottom chamber
                bottom_count = sum(1 for p in self.particles if p['in_bottom'])
                fill_ratio = bottom_count / self.total_particles
                
                # Calculate max pile height
                max_pile_height = (self.bottom_chamber['y2'] - self.bottom_chamber['y1']) * 0.95
                
                # Base height of the pile
                base_height = max_pile_height * fill_ratio
                
                # Center of bottom chamber
                center_x = (self.bottom_chamber['x1'] + self.bottom_chamber['x2']) / 2
                
                # Distance from center affects height (conical pile)
                dist_from_center = abs(particle['x'] - center_x)
                max_dist = (self.bottom_chamber['x2'] - self.bottom_chamber['x1']) / 2
                
                # Calculate target y position (higher in center, lower at edges)
                cone_factor = 1 - (dist_from_center / max_dist) * 0.8
                target_y = self.bottom_chamber['y2'] - (base_height * cone_factor)
                
                # Move particle towards its final resting position
                if particle['y'] < target_y:
                    particle['y'] += particle['speed'] * 2
                else:
                    # Slightly adjust to create natural pile
                    if random.random() < 0.1:  # Only sometimes
                        # Particles slide down the pile sides
                        direction = 1 if particle['x'] < center_x else -1
                        particle['x'] += direction * random.uniform(0, 0.5)
                        particle['y'] = min(particle['y'] + random.uniform(0, 0.5), self.bottom_chamber['y2'] - 5)
                
                # Keep particles within bounds
                particle['x'] = max(self.bottom_chamber['x1'] + 5, 
                                  min(particle['x'], self.bottom_chamber['x2'] - 5))
    
    def reset_animation(self):
        self.running = False
        self.remaining_time = self.total_time
        self.timer_label.config(text=f"Time: {self.remaining_time}s")
        self.draw_initial_state()
        self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = SandClockApp(root)
    root.mainloop()
