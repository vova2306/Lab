import tkinter as tk
from tkinter import messagebox, ttk
import random

# ... (Constants and Helper Classes Ship, Board remain the same as your last provided version) ...
# --- Constants ---
GRID_SIZE = 10
CELL_SIZE = 30
CYRILLIC_COLS = ['А', 'Б', 'В', 'Г', 'Ґ', 'Д', 'Е', 'Є', 'Ж', 'З']
LABEL_OFFSET = 20

# Cell states
EMPTY = 0
SHIP = 1
HIT = 2
SUNK = 3
MISS = 4
FORBIDDEN = 5

SHIP_CONFIG = {4: 1, 3: 2, 2: 3, 1: 4}

# --- Helper Classes (Ship, Board - без змін, як у попередній версії) ---
class Ship:
    def __init__(self, size, coords, orientation):
        self.size = size
        self.coords = set(coords)
        self.hits = set()
        self.orientation = orientation
        self.sunk = False

    def add_hit(self, coord):
        if coord in self.coords:
            self.hits.add(coord)
            if len(self.hits) == self.size:
                self.sunk = True
            return True
        return False

    def is_sunk(self):
        return self.sunk

class Board:
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.grid = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.ship_cells_hit_count = 0

    def _is_valid(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def _get_ship_cells(self, r_start, c_start, ship_size, orientation):
        ship_cells = []
        if orientation == 'H':
            for i in range(ship_size):
                ship_cells.append((r_start, c_start + i))
        else: # 'V'
            for i in range(ship_size):
                ship_cells.append((r_start + i, c_start))
        return ship_cells

    def _get_ship_and_perimeter_cells(self, r_start, c_start, ship_size, orientation):
        ship_cells = self._get_ship_cells(r_start, c_start, ship_size, orientation)
        perimeter_cells = set()
        for r_ship, c_ship in ship_cells:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    pr, pc = r_ship + dr, c_ship + dc
                    if self._is_valid(pr, pc):
                        perimeter_cells.add((pr,pc))
        return ship_cells, perimeter_cells

    def can_place_ship(self, r_start, c_start, ship_size, orientation):
        if ship_size <= 0: return False
        ship_cells, _ = self._get_ship_and_perimeter_cells(r_start, c_start, ship_size, orientation)
        if not ship_cells: return False

        for r, c in ship_cells:
            if not self._is_valid(r, c) or self.grid[r][c] == FORBIDDEN or self.grid[r][c] == SHIP:
                return False
        for r_ship, c_ship in ship_cells:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
                    nr, nc = r_ship + dr, c_ship + dc
                    if self._is_valid(nr, nc) and self.grid[nr][nc] == SHIP:
                        return False
        return True

    def place_ship(self, r_start, c_start, ship_size, orientation):
        if not self.can_place_ship(r_start, c_start, ship_size, orientation):
            return None
        ship_coords, perimeter_coords = self._get_ship_and_perimeter_cells(r_start, c_start, ship_size, orientation)
        new_ship = Ship(ship_size, ship_coords, orientation)
        self.ships.append(new_ship)
        for r, c in ship_coords:
            self.grid[r][c] = SHIP
        for pr, pc in perimeter_coords:
            if (pr,pc) not in ship_coords and self.grid[pr][pc] == EMPTY:
                 self.grid[pr][pc] = FORBIDDEN
        return new_ship

    def receive_shot(self, r, c):
        if not self._is_valid(r, c): return "ERROR", None
        cell_state = self.grid[r][c]
        if cell_state == HIT or cell_state == SUNK or cell_state == MISS:
            return "ALREADY_SHOT", None
        if cell_state == EMPTY or cell_state == FORBIDDEN:
            self.grid[r][c] = MISS
            return "MISS", None
        if cell_state == SHIP:
            self.grid[r][c] = HIT
            # self.ship_cells_hit_count +=1 # This can be misleading if ships overlap or logic is off
            hit_ship_obj = None # Renamed for clarity
            for ship_obj in self.ships:
                if (r, c) in ship_obj.coords:
                    ship_obj.add_hit((r, c))
                    hit_ship_obj = ship_obj
                    break
            
            # Recalculate total hits for all_ships_sunk check
            current_total_hits_on_board = 0
            for s_obj in self.ships:
                current_total_hits_on_board += len(s_obj.hits)
            self.ship_cells_hit_count = current_total_hits_on_board


            if hit_ship_obj and hit_ship_obj.is_sunk():
                for sr, sc in hit_ship_obj.coords:
                    self.grid[sr][sc] = SUNK # Mark all parts as SUNK
                # Mark perimeter around the now fully SUNK ship
                sunk_ship_coords = list(hit_ship_obj.coords)
                all_perimeter_cells = set()
                for r_sunk, c_sunk in sunk_ship_coords:
                    for dr_sunk in [-1,0,1]:
                        for dc_sunk in [-1,0,1]:
                            if dr_sunk==0 and dc_sunk==0: continue # Skip the ship cell itself
                            nr,nc = r_sunk+dr_sunk,c_sunk+dc_sunk
                            if self._is_valid(nr,nc) and (self.grid[nr][nc]==EMPTY or self.grid[nr][nc]==FORBIDDEN):
                                all_perimeter_cells.add((nr,nc))
                for pr, pc in all_perimeter_cells:
                     self.grid[pr][pc] = MISS # Mark as MISS
                return "SUNK", hit_ship_obj
            return "HIT", hit_ship_obj # Return the ship object even on a non-sinking hit
        return "ERROR", None # Should not happen

    def all_ships_sunk(self):
        if not self.ships: return True # No ships to sink means all are "sunk" (edge case for empty board)
        # Check if all ships that are supposed to be on the board are sunk
        # This relies on SHIP_CONFIG defining the fleet.
        expected_total_ship_cells = sum(s * c for s, c in SHIP_CONFIG.items())
        
        # Count actual sunk cells that were part of ships
        actual_sunk_cells = 0
        for ship in self.ships:
            if ship.is_sunk():
                actual_sunk_cells += ship.size
        
        # A more robust check: are all ship objects marked as sunk?
        # And ensure the board was fully populated according to config.
        if len(self.ships) != sum(SHIP_CONFIG.values()):
            # This indicates an issue during setup, but for game end:
            # If fewer ships than expected, and all present are sunk, it might be a win.
            # However, standard rules require all configured ships to be sunk.
            # For now, let's stick to checking all *placed* ship objects.
            pass # Potentially log a warning here if ship count mismatch

        return all(s.is_sunk() for s in self.ships)


    def reset(self):
        self.grid = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.ships = []
        self.ship_cells_hit_count = 0

    def auto_place_ships(self, ship_config_dict):
        self.reset()
        sorted_ship_config = sorted(ship_config_dict.items(), key=lambda item: item[0], reverse=True)
        for size, count in sorted_ship_config:
            if size <= 0: continue
            for _ in range(count):
                placed = False
                attempts = 0
                while not placed and attempts < 500: # Increased attempts
                    attempts += 1
                    orient = random.choice(['H', 'V'])
                    if orient == 'H':
                        r = random.randint(0, self.size - 1)
                        c = random.randint(0, self.size - size)
                    else:
                        r = random.randint(0, self.size - size)
                        c = random.randint(0, self.size - 1)
                    if self.place_ship(r, c, size, orient):
                        placed = True
                if not placed:
                    # print(f"Warning: Could not place ship size {size}. Retrying all.")
                    return self.auto_place_ships(ship_config_dict)
        return True

    def get_ship_counts(self):
        counts = {size: 0 for size in SHIP_CONFIG.keys()}
        sunk_counts = {size: 0 for size in SHIP_CONFIG.keys()}
        for ship in self.ships:
            if ship.size in counts:
                counts[ship.size] +=1
                if ship.is_sunk():
                    sunk_counts[ship.size] +=1
        return counts, sunk_counts


class BattleshipGUI(tk.Tk):
    # ... ( __init__ and _setup_ui as in your last working version with grid labels and keybinds) ...
    def __init__(self):
        super().__init__()
        self.title("Морський бій (Battleship)")

        self.player_board = Board()
        self.computer_board = Board()

        self.ships_to_place_config_list = []
        self.current_ship_idx_to_place = 0
        self.current_ships_placed_for_type = 0
        self.current_placement_orientation = tk.StringVar(value='H')

        self.game_state = "PLACING_SHIPS"

        self.ai_shots_made = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.ai_target_mode = False
        self.ai_hit_coords = [] # Координати влучань по поточному кораблю

        self.player_ship_labels = {}
        self.computer_ship_labels = {}

        self.last_mouse_x = None
        self.last_mouse_y = None

        self._setup_ui()
        self.start_new_game_setup()

        self.bind('<KeyPress>', self.handle_global_keypress)


    def handle_global_keypress(self, event):
        if self.game_state == "PLACING_SHIPS":
            char_pressed = event.char.lower()
            orientation_to_set = None
            if char_pressed == 'h' or char_pressed == 'г': orientation_to_set = 'H'
            elif char_pressed == 'v' or char_pressed == 'в': orientation_to_set = 'V'
            if orientation_to_set: self.set_orientation_from_key(orientation_to_set)

    def set_orientation_from_key(self, orientation_char):
        if self.game_state == "PLACING_SHIPS":
            if orientation_char != self.current_placement_orientation.get():
                self.current_placement_orientation.set(orientation_char)
                self._update_placement_info()
                if self.last_mouse_x is not None and self.last_mouse_y is not None:
                    mock_event = tk.Event()
                    mock_event.x, mock_event.y, mock_event.widget = self.last_mouse_x, self.last_mouse_y, self.player_canvas
                    self.on_player_canvas_motion(mock_event)
    
    def _setup_ui(self): # Копіюю ваш останній робочий _setup_ui
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        canvas_width = GRID_SIZE * CELL_SIZE + 2 * LABEL_OFFSET
        canvas_height = GRID_SIZE * CELL_SIZE + 2 * LABEL_OFFSET

        player_area_frame = ttk.Frame(main_frame)
        player_area_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        player_frame_ui = ttk.LabelFrame(player_area_frame, text="Ваше поле (Your Board)") # Renamed to avoid conflict
        player_frame_ui.pack(pady=5)
        self.player_canvas = tk.Canvas(player_frame_ui, width=canvas_width, height=canvas_height, bg="white")
        self.player_canvas.pack()
        self.player_canvas.bind("<Button-1>", self.on_player_canvas_click)
        self.player_canvas.bind("<Motion>", self.on_player_canvas_motion)
        self.player_canvas.bind("<Leave>", self.on_player_canvas_leave)

        player_counters_frame = ttk.LabelFrame(player_area_frame, text="Ваші кораблі")
        player_counters_frame.pack(pady=5, fill=tk.X)
        for size in sorted(SHIP_CONFIG.keys(), reverse=True):
            count = SHIP_CONFIG[size]
            frame = ttk.Frame(player_counters_frame)
            frame.pack(fill=tk.X)
            ttk.Label(frame, text=f"{size}-палубні:").pack(side=tk.LEFT)
            self.player_ship_labels[size] = ttk.Label(frame, text=f"0/{count}")
            self.player_ship_labels[size].pack(side=tk.RIGHT)

        computer_area_frame = ttk.Frame(main_frame)
        computer_area_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        computer_frame_ui = ttk.LabelFrame(computer_area_frame, text="Поле комп'ютера (Computer's Board)") # Renamed
        computer_frame_ui.pack(pady=5)
        self.computer_canvas = tk.Canvas(computer_frame_ui, width=canvas_width, height=canvas_height, bg="lightgray")
        self.computer_canvas.pack()
        self.computer_canvas.bind("<Button-1>", self.on_computer_canvas_click)

        computer_counters_frame = ttk.LabelFrame(computer_area_frame, text="Кораблі комп'ютера")
        computer_counters_frame.pack(pady=5, fill=tk.X)
        for size in sorted(SHIP_CONFIG.keys(), reverse=True):
            count = SHIP_CONFIG[size]
            frame = ttk.Frame(computer_counters_frame)
            frame.pack(fill=tk.X)
            ttk.Label(frame, text=f"{size}-палубні:").pack(side=tk.LEFT)
            self.computer_ship_labels[size] = ttk.Label(frame, text=f"{count}/{count}")
            self.computer_ship_labels[size].pack(side=tk.RIGHT)

        status_controls_frame = ttk.Frame(main_frame)
        status_controls_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.EW)
        self.status_label = ttk.Label(status_controls_frame, text="Розмістіть свої кораблі.", font=("Arial", 12))
        self.status_label.pack(pady=5)
        controls_frame = ttk.Frame(status_controls_frame)
        controls_frame.pack()
        self.new_game_button = ttk.Button(controls_frame, text="Нова гра (New Game)", command=self.start_new_game_setup)
        self.new_game_button.pack(side=tk.LEFT, padx=5)
        self.random_place_button = ttk.Button(controls_frame, text="Розмістити випадково (Random Place)", command=self.player_auto_place_ships)
        self.random_place_button.pack(side=tk.LEFT, padx=5)
        self.placement_controls_frame = ttk.Frame(controls_frame) 
        ttk.Label(self.placement_controls_frame, text="Орієнтація:").pack(side=tk.LEFT)
        self.h_radio = ttk.Radiobutton(self.placement_controls_frame, text="Горизонтально", variable=self.current_placement_orientation, value='H', command=self._update_placement_info_and_preview_from_radio)
        self.h_radio.pack(side=tk.LEFT)
        self.v_radio = ttk.Radiobutton(self.placement_controls_frame, text="Вертикально", variable=self.current_placement_orientation, value='V', command=self._update_placement_info_and_preview_from_radio)
        self.v_radio.pack(side=tk.LEFT)
        self.ship_info_label = ttk.Label(self.placement_controls_frame, text="")
        self.ship_info_label.pack(side=tk.LEFT, padx=5)
    
    def _update_placement_info_and_preview_from_radio(self):
        self._update_placement_info()
        if self.last_mouse_x is not None and self.last_mouse_y is not None and self.game_state == "PLACING_SHIPS":
            mock_event = tk.Event()
            mock_event.x, mock_event.y, mock_event.widget = self.last_mouse_x, self.last_mouse_y, self.player_canvas
            self.on_player_canvas_motion(mock_event)

    def on_player_canvas_motion(self, event):
        # ... (as in your last working version)
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

        if self.game_state != "PLACING_SHIPS" or not self.ships_to_place_config_list or \
           self.current_ship_idx_to_place >= len(self.ships_to_place_config_list):
            self.player_canvas.delete("preview")
            return

        col = (event.x - LABEL_OFFSET) // CELL_SIZE
        row = (event.y - LABEL_OFFSET) // CELL_SIZE
        
        current_ship_size_to_place, _ = self.ships_to_place_config_list[self.current_ship_idx_to_place]
        if current_ship_size_to_place <= 0:
            self.player_canvas.delete("preview")
            return

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            orientation = self.current_placement_orientation.get()
            is_valid = self.player_board.can_place_ship(row, col, current_ship_size_to_place, orientation)
            self._draw_placement_preview(self.player_canvas, row, col, current_ship_size_to_place, orientation, is_valid)
        else:
            self.player_canvas.delete("preview")


    def on_player_canvas_leave(self, event=None):
        # ... (as in your last working version)
        self.player_canvas.delete("preview")
        self.last_mouse_x = None
        self.last_mouse_y = None


    def _draw_placement_preview(self, canvas, r_start, c_start, ship_size, orientation, is_valid_placement):
        # ... (as in your last working version)
        canvas.delete("preview")
        if ship_size <= 0: return

        ship_preview_cells = self.player_board._get_ship_cells(r_start, c_start, ship_size, orientation)
        fill_color = "green" if is_valid_placement else "red"
        
        for r, c in ship_preview_cells:
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                x1 = c * CELL_SIZE + LABEL_OFFSET
                y1 = r * CELL_SIZE + LABEL_OFFSET
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black", tags="preview", stipple="gray50")


    def _draw_grid(self, canvas, board, show_ships=True):
        # ... (as in your last working version with grid labels)
        canvas.delete("all") 
        for i in range(GRID_SIZE):
            canvas.create_text(LABEL_OFFSET + i * CELL_SIZE + CELL_SIZE / 2, LABEL_OFFSET / 2,
                               text=CYRILLIC_COLS[i], anchor=tk.CENTER, font=("Arial", 10))
            canvas.create_text(LABEL_OFFSET / 2, LABEL_OFFSET + i * CELL_SIZE + CELL_SIZE / 2,
                               text=str(i + 1), anchor=tk.CENTER, font=("Arial", 10))

        for r_idx in range(GRID_SIZE): # Renamed r to r_idx
            for c_idx in range(GRID_SIZE): # Renamed c to c_idx
                x1 = c_idx * CELL_SIZE + LABEL_OFFSET
                y1 = r_idx * CELL_SIZE + LABEL_OFFSET
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                fill_color = "white"
                cell_state = board.grid[r_idx][c_idx]

                if cell_state == SHIP and show_ships: fill_color = "darkgray"
                elif cell_state == HIT: fill_color = "orange"
                elif cell_state == SUNK: fill_color = "red"
                elif cell_state == MISS: fill_color = "lightblue"
                
                canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=fill_color, tags="grid_cells")
                
                if cell_state == HIT or cell_state == SUNK:
                    canvas.create_line(x1+5, y1+5, x2-5, y2-5, fill="black", width=2, tags="grid_cells")
                    canvas.create_line(x1+5, y2-5, x2-5, y1+5, fill="black", width=2, tags="grid_cells")
                elif cell_state == MISS:
                    canvas.create_oval(x1+CELL_SIZE//2-3, y1+CELL_SIZE//2-3,
                                       x1+CELL_SIZE//2+3, y1+CELL_SIZE//2+3, fill="darkblue", tags="grid_cells")

    def _update_ship_counters(self):
        # ... (as in your last working version)
        player_total_ships, player_sunk_ships = self.player_board.get_ship_counts()
        for size_key, initial_count in SHIP_CONFIG.items(): 
            placed_count = player_total_ships.get(size_key, 0)
            sunk_count = player_sunk_ships.get(size_key, 0)
            remaining_alive = placed_count - sunk_count
            if size_key in self.player_ship_labels:
                if self.game_state == "PLACING_SHIPS":
                    self.player_ship_labels[size_key].config(text=f"{placed_count}/{initial_count}")
                else:
                    actual_placed_for_size = sum(1 for ship in self.player_board.ships if ship.size == size_key)
                    self.player_ship_labels[size_key].config(text=f"{actual_placed_for_size - sunk_count}/{actual_placed_for_size if actual_placed_for_size > 0 else initial_count}")

        comp_total_ships, comp_sunk_ships = self.computer_board.get_ship_counts()
        for size_key, initial_count in SHIP_CONFIG.items(): 
            sunk_by_player = comp_sunk_ships.get(size_key, 0)
            remaining_to_sink = initial_count - sunk_by_player
            if size_key in self.computer_ship_labels:
                self.computer_ship_labels[size_key].config(text=f"{remaining_to_sink}/{initial_count}")


    def _update_placement_info(self):
        # ... (as in your last working version)
        if not self.ships_to_place_config_list:
             self.ships_to_place_config_list = sorted([item for item in SHIP_CONFIG.items() if item[0] > 0], key=lambda x: x[0], reverse=True)

        if self.current_ship_idx_to_place < len(self.ships_to_place_config_list):
            size_val, total_count_for_type = self.ships_to_place_config_list[self.current_ship_idx_to_place] # Renamed size
            if size_val <= 0:
                self.current_ship_idx_to_place += 1
                self._update_placement_info()
                return

            remaining_for_type = total_count_for_type - self.current_ships_placed_for_type
            self.ship_info_label.config(text=f"Розмістіть: {size_val}-палубний ({remaining_for_type} залишилось)")
            self.status_label.config(text=f"Розмістіть {size_val}-палубний корабель. Орієнтація: {'Горизонтально' if self.current_placement_orientation.get() == 'H' else 'Вертикально'}.")
            self.placement_controls_frame.pack(side=tk.LEFT, padx=10)
        else:
            self.ship_info_label.config(text="")
            self.placement_controls_frame.pack_forget()
            self.status_label.config(text="Всі кораблі розміщено. Натисніть на поле комп'ютера, щоб почати.")
            if self.game_state == "PLACING_SHIPS":
                 self.game_state = "PLAYER_TURN"
        self._update_ship_counters()


    def start_new_game_setup(self):
        # ... (as in your last working version, ensure self.focus_set() is present)
        self.player_board.reset()
        self.computer_board.reset()
        if not self.computer_board.auto_place_ships(SHIP_CONFIG):
            messagebox.showerror("Помилка", "Не вдалося розмістити кораблі комп'ютера. Спробуйте знову.")
            return

        self.ships_to_place_config_list = sorted([item for item in SHIP_CONFIG.items() if item[0] > 0], key=lambda x: x[0], reverse=True)
        self.current_ship_idx_to_place = 0
        self.current_ships_placed_for_type = 0
        self.current_placement_orientation.set('H')

        self.ai_shots_made = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.ai_target_mode = False
        self.ai_hit_coords = []
        self.last_mouse_x = None
        self.last_mouse_y = None

        self.game_state = "PLACING_SHIPS"
        self._update_placement_info()
        self._redraw_boards()
        self.random_place_button.config(state=tk.NORMAL)
        self.player_canvas.delete("preview")
        self.focus_set() # Важливо для обробки клавіш головним вікном


    def player_auto_place_ships(self):
        # ... (as in your last working version)
        if self.game_state != "PLACING_SHIPS": return
        if not self.player_board.auto_place_ships(SHIP_CONFIG):
            messagebox.showerror("Помилка", "Не вдалося розмістити ваші кораблі автоматично.")
            self.player_board.reset()
            self._update_ship_counters()
            self._redraw_boards()
            return

        self.current_ship_idx_to_place = len(self.ships_to_place_config_list)
        self._update_placement_info()
        self._redraw_boards()
        self.random_place_button.config(state=tk.DISABLED)
        self.player_canvas.delete("preview")


    def _redraw_boards(self):
        # ... (as in your last working version)
        self._draw_grid(self.player_canvas, self.player_board, show_ships=True)
        self._draw_grid(self.computer_canvas, self.computer_board, show_ships=False)


    def on_player_canvas_click(self, event):
        # ... (as in your last working version with LABEL_OFFSET)
        if self.game_state != "PLACING_SHIPS": return
        if not self.ships_to_place_config_list or self.current_ship_idx_to_place >= len(self.ships_to_place_config_list):
             self.status_label.config(text="Всі кораблі розміщено. Стріляйте по полю комп'ютера.")
             return

        col = (event.x - LABEL_OFFSET) // CELL_SIZE
        row = (event.y - LABEL_OFFSET) // CELL_SIZE

        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return

        current_size_val, total_count = self.ships_to_place_config_list[self.current_ship_idx_to_place] # Renamed
        if current_size_val <= 0:
            self.current_ship_idx_to_place +=1
            self._update_placement_info()
            return

        orientation = self.current_placement_orientation.get()

        if self.player_board.place_ship(row, col, current_size_val, orientation):
            self.current_ships_placed_for_type += 1
            if self.current_ships_placed_for_type >= total_count:
                self.current_ship_idx_to_place += 1
                self.current_ships_placed_for_type = 0
            self._update_placement_info()
            self._redraw_boards()
            if self.current_ship_idx_to_place < len(self.ships_to_place_config_list):
                 self.on_player_canvas_motion(event)
            else:
                 self.player_canvas.delete("preview")
        else:
            self.status_label.config(text="Неможливо розмістити тут! Спробуйте інше місце.")


    def on_computer_canvas_click(self, event):
        # ... (as in your last working version with LABEL_OFFSET)
        if self.game_state != "PLAYER_TURN":
            if self.game_state == "PLACING_SHIPS": self.status_label.config(text="Спочатку розмістіть всі свої кораблі!")
            elif self.game_state == "GAME_OVER": self.status_label.config(text="Гра завершена. Почніть нову гру.")
            else: self.status_label.config(text="Зараз хід комп'ютера.")
            return

        col = (event.x - LABEL_OFFSET) // CELL_SIZE
        row = (event.y - LABEL_OFFSET) // CELL_SIZE

        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return

        result, ship_obj = self.computer_board.receive_shot(row, col) # Renamed ship
        self._redraw_boards()
        self._update_ship_counters()

        if result == "ALREADY_SHOT": self.status_label.config(text="Ви вже стріляли сюди. Спробуйте ще раз.")
        elif result == "MISS":
            self.status_label.config(text=f"Гравець: Промах по ({CYRILLIC_COLS[col]}{row+1}). Хід комп'ютера.")
            self.game_state = "COMPUTER_TURN"
            self.after(500, self.computer_turn)
        elif result == "HIT": self.status_label.config(text=f"Гравець: Влучив ({CYRILLIC_COLS[col]}{row+1})! Ваш хід знову.")
        elif result == "SUNK":
            self.status_label.config(text=f"Гравець: Потопив {ship_obj.size}-палубний корабель! Ваш хід знову.")
            if self.computer_board.all_ships_sunk(): self.game_over("Гравець")
        else: self.status_label.config(text="Помилка пострілу.")


    def computer_turn(self):
        if self.game_state != "COMPUTER_TURN": return

        r_shot, c_shot = self._ai_choose_shot()
        if r_shot is None: # AI cannot make a move
            # This could happen if all cells are shot, or an AI logic error.
            # Check if player has actually won.
            if not self.player_board.all_ships_sunk():
                self.status_label.config(text="AI не може зробити хід. Можливо, помилка. Ваш хід.")
            else: # Player already won, but AI turn was somehow triggered.
                self.game_over("Комп'ютер") # Or should be Player? Check win condition logic.
                return
            self.game_state = "PLAYER_TURN"
            return

        # Mark shot BEFORE processing, important for AI's own logic if it gets immediate retry
        self.ai_shots_made[r_shot][c_shot] = True 
        
        result, sunk_ship_obj = self.player_board.receive_shot(r_shot, c_shot)
        self._redraw_boards() # Show the hit/miss on player's board
        self._update_ship_counters() # Update ship counts

        shot_coord_str = f"({CYRILLIC_COLS[c_shot]}{r_shot+1})"

        if result == "ALREADY_SHOT":
            # This should ideally not happen if ai_shots_made is tracked correctly.
            # If it does, AI might be stuck. Forcing a new hunt might be an option.
            self.status_label.config(text=f"Комп'ютер (AI): Повторний постріл {shot_coord_str} (помилка AI). Хід комп'ютера.")
            self.ai_target_mode = False # Reset target mode to force new hunt next time
            self.ai_hit_coords = []
            self.after(100, self.computer_turn) # Try again quickly
            return

        if result == "MISS":
            self.status_label.config(text=f"Комп'ютер: Промах по {shot_coord_str}. Ваш хід.")
            # If AI was in target mode and missed, it should re-evaluate.
            # If the miss was part of extending a line, ai_hit_coords might need adjustment
            # or target_mode reset if the line seems to end.
            # Current _ai_choose_shot handles this by falling back to hunt if _get_next_target_shot returns None.
            self.game_state = "PLAYER_TURN"
        elif result == "HIT":
            self.status_label.config(text=f"Комп'ютер: Влучив у ваш корабель {shot_coord_str}! Хід комп'ютера.")
            if not self.ai_target_mode: # First hit of a new target sequence
                self.ai_hit_coords = [] # Clear previous (if any, though should be cleared on SUNK)
            self.ai_hit_coords.append((r_shot, c_shot))
            self.ai_target_mode = True
            self.after(500, self.computer_turn) # AI gets another turn
        elif result == "SUNK":
            self.status_label.config(text=f"Комп'ютер: Потопив ваш {sunk_ship_obj.size}-палубний корабель {shot_coord_str}! Хід комп'ютера.")
            # ai_hit_coords now contains all hits of the sunk ship.
            # Mark area around sunk ship as known misses for AI
            for r_s, c_s in sunk_ship_obj.coords:
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        nr, nc = r_s+dr, c_s+dc
                        if self.player_board._is_valid(nr,nc) and \
                           self.player_board.grid[nr][nc] == MISS and \
                           not self.ai_shots_made[nr][nc]:
                            self.ai_shots_made[nr][nc] = True
            
            self.ai_target_mode = False # Reset target mode
            self.ai_hit_coords = []     # Clear hit coordinates for the sunk ship

            if self.player_board.all_ships_sunk():
                self.game_over("Комп'ютер")
            else:
                self.after(500, self.computer_turn) # AI gets another turn
        else: # ERROR
            self.status_label.config(text="Помилка пострілу комп'ютера.")
            self.game_state = "PLAYER_TURN" # Give turn back to player on error

    def _get_next_target_shot(self):
        if not self.ai_hit_coords:
            return None

        potential_targets = []
        
        # Try to extend the line from known hits
        if len(self.ai_hit_coords) >= 1:
            # Sort hits to find extremities
            sorted_hits_r = sorted(self.ai_hit_coords, key=lambda x: x[0])
            sorted_hits_c = sorted(self.ai_hit_coords, key=lambda x: x[1])

            min_r, max_r = sorted_hits_r[0][0], sorted_hits_r[-1][0]
            min_c, max_c = sorted_hits_c[0][1], sorted_hits_c[-1][1]

            is_likely_horizontal = (max_r - min_r == 0) and (max_c - min_c < 4) # Max ship length 4
            is_likely_vertical = (max_c - min_c == 0) and (max_r - min_r < 4)

            if is_likely_horizontal: # Prioritize extending horizontally
                r_fixed = self.ai_hit_coords[0][0] # All hits on this row
                # Try left of min_c and right of max_c
                if self.player_board._is_valid(r_fixed, min_c - 1) and not self.ai_shots_made[r_fixed][min_c - 1]:
                    potential_targets.append((r_fixed, min_c - 1))
                if self.player_board._is_valid(r_fixed, max_c + 1) and not self.ai_shots_made[r_fixed][max_c + 1]:
                    potential_targets.append((r_fixed, max_c + 1))
            
            if is_likely_vertical: # Prioritize extending vertically
                c_fixed = self.ai_hit_coords[0][1] # All hits on this col
                 # Try above min_r and below max_r
                if self.player_board._is_valid(min_r - 1, c_fixed) and not self.ai_shots_made[min_r - 1][c_fixed]:
                    potential_targets.append((min_r - 1, c_fixed))
                if self.player_board._is_valid(max_r + 1, c_fixed) and not self.ai_shots_made[max_r + 1][c_fixed]:
                    potential_targets.append((max_r + 1, c_fixed))
            
            # If no clear line or line ends are blocked, try neighbors of all hit cells
            if not potential_targets:
                for r_hit, c_hit in self.ai_hit_coords:
                    for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]: # N, S, E, W
                        nr, nc = r_hit + dr, c_hit + dc
                        if self.player_board._is_valid(nr, nc) and not self.ai_shots_made[nr][nc] and (nr,nc) not in self.ai_hit_coords:
                            if (nr,nc) not in potential_targets : potential_targets.append((nr,nc))
        
        if potential_targets:
            # print(f"AI Target Mode: Hits: {self.ai_hit_coords}, Potential Targets: {potential_targets}")
            return random.choice(potential_targets)
        
        # print(f"AI Target Mode: Hits: {self.ai_hit_coords}, NO VALID TARGETS FOUND.")
        return None # No valid target found

    def _ai_choose_shot(self):
        if self.ai_target_mode and self.ai_hit_coords:
            target_shot = self._get_next_target_shot()
            if target_shot:
                return target_shot
            else: # Could not find a good target to continue, revert to hunt
                # print("AI: Target mode failed to find next shot, reverting to hunt.")
                self.ai_target_mode = False
                self.ai_hit_coords = []

        # Hunt mode
        available_cells_priority = [] # Checkerboard
        available_cells_other = []
        for r_idx in range(GRID_SIZE):
            for c_idx in range(GRID_SIZE):
                if not self.ai_shots_made[r_idx][c_idx]:
                    if (r_idx + c_idx) % 2 == 0:
                        available_cells_priority.append((r_idx,c_idx))
                    else:
                        available_cells_other.append((r_idx,c_idx))
        
        if available_cells_priority:
            return random.choice(available_cells_priority)
        if available_cells_other:
            return random.choice(available_cells_other)
        
        # print("AI: No unshot cells left in hunt mode.")
        return (None, None) # No valid moves left


    def game_over(self, winner_name):
        self.game_state = "GAME_OVER"
        self.status_label.config(text=f"Гра завершена! Переможець: {winner_name}!")
        messagebox.showinfo("Гра завершена!", f"Переможець: {winner_name}!")
        self.random_place_button.config(state=tk.NORMAL)
        self.player_canvas.delete("preview")


if __name__ == "__main__":
    app = BattleshipGUI()
    app.mainloop()