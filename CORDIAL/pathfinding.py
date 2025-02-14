#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

import heapq
from typing import List, Tuple, Optional, Set, Dict
import agents
import robots
import grid


class Node:
    def __init__(self, position: Tuple[int, int], time: int, g: float = 0, parent: 'Node' = None):
        self.position = position
        self.time = time
        self.g = g  # Cost from start
        self.h = 0  # Heuristic to goal
        self.f = self.g + self.h  # Total cost
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.position == other.position and self.time == other.time

    def __hash__(self):
        return hash((self.position, self.time))


class PathFinder:
    def __init__(self, grid, robots, agents):
        self.grid = grid
        self.robots = robots  # List of Robot objects
        self.agents = agents  # {agent_id: {time: position}}
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Removed wait action
        self.max_time = 1000
        self.current_time = 0
        self.robot_paths: Dict[str, List[Tuple[Tuple[int, int], int]]] = {}
        self.replan_threshold = 3

    def is_collision(self, pos: Tuple[int, int], time: int) -> bool:
        # Check grid boundaries
        if not (0 <= pos[0] < self.grid.get_size() and 0 <= pos[1] < self.grid.get_size()):
            return True

        # Check static obstacles
        if self.grid.is_static_obstacle(pos[0], pos[1]):
            return True

        # Check dynamic agents (corrected)
        for agent_id, schedule in self.agents.items():
            if time in schedule and schedule[time] == pos:
                return True

        # Check other robots' paths (updated)
        for robot in self.robots:
            if robot.name in self.robot_paths:
                for path_pos, path_time in self.robot_paths[robot.name]:
                    if path_time == time and path_pos == pos:
                        return True

        return False

    def get_neighbors(self, node: Node) -> List[Node]:
        neighbors = []
        x, y = node.position
        current_time = node.time

        for dx, dy in self.directions:
            new_x = x + dx
            new_y = y + dy
            new_time = current_time + 1  # Time always advances

            # Skip invalid positions immediately
            if not (0 <= new_x < self.grid.get_size() and 0 <= new_y < self.grid.get_size()):
                continue

            # Calculate movement cost (uniform for grid)
            new_g = node.g + 1  # All moves cost 1

            # Create neighbor node
            neighbor = Node(
                position=(new_x, new_y),
                time=new_time,
                g=new_g,
                parent=node
            )

            if not self.is_collision(neighbor.position, neighbor.time):
                neighbors.append(neighbor)

        return neighbors

    def heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        # Manhattan distance for grid
        dy = abs(pos[0] - goal[0])
        dx = abs(pos[1] - goal[1])

        return dx + dy + abs((pos[0] - goal[0]) * (pos[1] - goal[1]) * 0.001)


    def dynamic_a_star(self, start: Tuple[int, int], goal: Tuple[int, int], start_time: int) -> Optional[
        List[Tuple[Tuple[int, int], int]]]:
        open_heap = []
        closed_set = set()

        start_node = Node(start, start_time)
        start_node.h = self.heuristic(start, goal)
        start_node.f = start_node.g + start_node.h

        heapq.heappush(open_heap, start_node)
        node_dict = {(start_node.position, start_node.time): start_node}

        while open_heap:
            current = heapq.heappop(open_heap)

            if current.position == goal:
                path = []
                while current:
                    path.append((current.position, current.time))
                    current = current.parent
                return path[::-1]

            if (current.position, current.time) in closed_set:
                continue
            closed_set.add((current.position, current.time))

            for neighbor in self.get_neighbors(current):
                key = (neighbor.position, neighbor.time)
                existing = node_dict.get(key)

                if existing:
                    if neighbor.g < existing.g:
                        existing.g = neighbor.g
                        existing.f = existing.g + existing.h
                        existing.parent = neighbor.parent
                        heapq.heapify(open_heap)
                else:
                    neighbor.h = self.heuristic(neighbor.position, goal)
                    neighbor.f = neighbor.g + neighbor.h
                    node_dict[key] = neighbor
                    heapq.heappush(open_heap, neighbor)

        return None

    def plan_all_paths(self) -> Dict[str, List[Tuple[Tuple[int, int], int]]]:
        """Plan initial paths for all robots."""
        self.robot_paths.clear()
        for robot in self.robots:
            path = self.dynamic_a_star(robot.start_position, robot.end_position, self.current_time)
            if path:
                self.robot_paths[robot.name] = path
                robot.set_preplanned_path(path)
            else:
                print(f"No path found for robot {robot.name}")
        return self.robot_paths


def visualize_path(grid, path: List[Tuple[Tuple[int, int], int]]) -> None:
    """Visualize the path on the grid."""
    if not path:
        return

    grid_size = len(grid.get_grid())
    for t, (pos, time) in enumerate(path):
        temp_grid = [row[:] for row in grid.get_grid()]
        temp_grid[pos[1]][pos[0]] = str(t)

        print(f"\nTime step {time}:")
        for row in temp_grid:
            print(" ".join(str(cell) for cell in row))

# temp main for testing
if __name__ == "__main__":
    # Initialize grid
    grid_file = 'Data/data0.txt'
    grid = grid.Grid(grid_file)
    # grid_to_set = [
    #     ' ' + ' ' + ' ' + ' ' + ' ',  # Row 0
    #     ' ' + 'X' + ' ' + ' ' + ' ',  # Row 1
    #     ' ' + ' ' + ' ' + 'X' + ' ',  # Row 2
    #     ' ' + ' ' + ' ' + ' ' + ' ',  # Row 3
    #     ' ' + ' ' + ' ' + ' ' + ' '  # Row 4
    # ]
    # grid = grid.Grid(grid_file)
    # grid.set_grid(grid_to_set)

    # Initialize agents and robots
    agents_file = 'Data/Agent0.txt'
    agent_loader = agents.Agent(agents_file)
    agent_loader.initialize_agents()
    agents = agent_loader.get_agents()

    robot_file = 'Data/Robots0.txt'
    robot_loader = robots.RobotLoader(robot_file)
    robots = robot_loader.get_robots()

    # Initialize pathfinder
    pathfinder = PathFinder(grid, robots, agents)

    # Plan initial paths for all robots
    print("\nInitial Path Planning:")
    print("----------------------")
    initial_paths = pathfinder.plan_all_paths()
    for robot_name, path in initial_paths.items():
        print(f"Initial path for {robot_name}: {path}")

    print("===================")

    # Final statistics
    print("\nFinal Statistics:")
    for robot in robots:
        path = pathfinder.robot_paths.get(robot.name, [])
        if path:
            path_length = len(path)
            final_position = path[-1][0] if path else None
            reached_goal = final_position == robot.end_position
            print(f"\nRobot {robot.name}:")
            print(f"Path Length: {path_length}")
            print(f"Final Position: {final_position}")
            print(f"Reached Goal: {reached_goal}")

    # Print paths taken by each robot and time taken as:
    # Robot 1 Path: [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
    # Robot 1 Total Time: 4
    for robot in robots:
        path = pathfinder.robot_paths.get(robot.name, [])
        path_length = len(path)
        # Robot 1 Path: [((0, 24), 0), ((1, 24), 1), ((1, 23), 2)] extract it to [(0, 24), (1, 24), (1, 23)]
        path = [pos for pos, time in path]
        print(f"\nRobot {robot.name} Path: {path}")
        print(f"Robot {robot.name} Total Time: {path_length}")