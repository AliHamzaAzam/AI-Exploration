#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

class Grid:
    def __init__(self, grid_file):
        self.N = None
        self.grid = []
        self.load_grid(grid_file)

    def load_grid(self, grid_file):
        with open(grid_file, 'r') as file:
            # Read the first line to get the size of the grid
            self.N = int(file.readline().strip())
            # Read the grid
            for i in range(self.N):
                row = file.readline().strip()
                self.grid.append(row)

    def print_grid(self):
        for row in self.grid:
            print(row)

    def get_grid(self):
        return self.grid

    def get_size(self):
        return self.N


