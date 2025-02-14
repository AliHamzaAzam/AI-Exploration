#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#
import robots
import agents

class Grid:
    def __init__(self, grid_file):
        self.N = None
        self.grid = []
        self.load_grid(grid_file)

    def load_grid(self, grid_file):
        with open(grid_file, 'r') as file:
            # Read the first line to get the size of the grid
            self.N = int(file.readline().strip())
            # Read the grid rows while preserving trailing spaces
            for i in range(self.N):
                row = file.readline().rstrip('\n')
                self.grid.append(row)

    def initialize_grid(self, agents, robots, time=0):
        # Agents are a dictionary of dictionaries with time as key and position as value
        for agent in agents:
            position = agents[agent][time]
            x, y = position
            self.grid[y] = self.grid[y][:x] + 'A' + self.grid[y][x+1:]
        for robot in robots:
            position = robot.get_position()
            x, y = position
            self.grid[y] = self.grid[y][:x] + 'R' + self.grid[y][x+1:]

    def update_grid(self, agents, robots, time):
        # Clear the grid of all agents and robots
        for i in range(self.N):
            for agent in agents:
                self.grid[i] = self.grid[i].replace('A', ' ')
            for robot in robots:
                self.grid[i] = self.grid[i].replace('R', ' ')
        # Place the agents and robots in their new positions
        self.initialize_grid(agents, robots, time)

    def is_static_obstacle(self, x, y):
        return self.grid[y][x] == 'X'

    def print_grid(self):
        for row in self.grid:
            print(row)

    def get_grid(self):
        return self.grid

    def set_grid(self, grid):
        self.grid = grid

    def get_size(self):
        return self.N


# temp main for testing
if __name__ == "__main__":
    grid_file = 'Data/data0.txt'
    grid = Grid(grid_file)
    agents_file = 'Data/Agent0.txt'
    agent_loader = agents.Agent(agents_file)
    agent_loader.initialize_agents()
    agents = agent_loader.get_agents()
    robot_file = 'Data/Robots0.txt'
    robot_loader = robots.RobotLoader(robot_file)
    robots = robot_loader.get_robots()
    grid.initialize_grid(agents.values(), robots)
    grid.print_grid()
