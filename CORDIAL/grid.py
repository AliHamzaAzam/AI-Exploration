#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#
import robots


def load_grid(file):
    with open(file, 'r') as f:
        N = int(f.readline().strip())
        return [f.readline().rstrip('\n') for _ in range(N)]


class Grid:
    def __init__(self, file):
        self.grid = load_grid(file)
        self.N = len(self.grid)
        self.M = len(self.grid[0]) if self.grid else 0
        self.display_grid = [[' ' for _ in range(self.M)] for _ in range(self.N)]
        self._init_display_grid()

    def _init_display_grid(self):
        # Initialize display grid with walls
        for y in range(self.N):
            for x in range(self.M):
                if self.grid[y][x] == 'X':
                    self.display_grid[y][x] = 'X'
                else:
                    self.display_grid[y][x] = ' '

    def initialize_grid(self, agents, robots, time=0):
        self._place_entities(agents, '\033[32mA\033[0m', time)  # Green for Agents
        self._place_entities({robot: {0: robot.get_position()} for robot in robots}, 'R', time)

    def _place_entities(self, entities, symbol, time):
        for entity, schedule in entities.items():
            last_time = max(schedule.keys())
            period = 2 * last_time or 1
            t_mod = time % period
            effective_time = t_mod if t_mod <= last_time else period - t_mod
            x, y = schedule[effective_time]

            # Determine symbol color
            if isinstance(entity, robots.Robot):
                if entity.current_position == entity.end_position:
                    colored_symbol = '\033[33mG\033[0m'  # Gold for Goal
                else:
                    colored_symbol = '\033[34mR\033[0m'  # Blue for Robots
            elif symbol == 'A':
                colored_symbol = '\033[32mA\033[0m'  # Green for Agents
            else:
                colored_symbol = symbol

            # Only place if not hitting a wall
            if self.display_grid[y][x] != 'X':
                self.display_grid[y][x] = colored_symbol

    def update_grid(self, agents, robots, time):
        # Reset display grid to only walls
        self._init_display_grid()
        # Place entities on the display grid
        self.initialize_grid(agents, robots, time)

    def print_grid(self):
        # Print the display grid row by row
        for row in self.display_grid:
            print(''.join(row))

    def get_rows(self):
        return self.N

    def get_columns(self):
        return self.M

    def get_grid(self):
        return self.grid

    def is_obstacle(self, position):
        x, y = position
        return self.grid[y][x] == 'X'  # Assuming 'X' represents an obstacle