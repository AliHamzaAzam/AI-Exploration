#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

import heapq
from collections import defaultdict
from typing import List, Tuple, Optional


class Node:
    __slots__ = ['position', 'time', 'g', 'h', 'f', 'parent']

    def __init__(self, position: Tuple[int, int], time: int, g: float = 0, parent: 'Node' = None):
        self.position = position
        self.time = time
        self.g = g
        self.h = 0
        self.f = self.g + self.h
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f


class PathFinder:
    def __init__(self, grid, robots, agents):
        self.grid = grid
        self.robots = robots                                                    # List of Robot objects
        self.agents = agents                                                    # {agent_id: {time: position}}
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.current_time = 0
        self.robot_current_steps = {robot.name: None for robot in self.robots}  # {name: (position, time)}
        self.grid_rows = self.grid.get_rows()
        self.grid_cols = self.grid.get_columns()
        self.path_cache = {}

    def is_collision(self, pos: Tuple[int, int], time: int, current_robot_name: str) -> bool:
        # Boundary check
        if not (0 <= pos[0] < self.grid_cols and 0 <= pos[1] < self.grid_rows):
            return True

        # Check static obstacles (g is accessed as [y][x])
        if self.grid.grid[pos[1]][pos[0]] == 'X':
            return True

        # Dynamic agents check with period caching
        for agent_id, schedule in self.agents.items():
            if schedule:
                last_time = max(schedule.keys())
                period = 2 * last_time or 1
                t_mod = time % period
                effective_time = t_mod if t_mod <= last_time else period - t_mod

                if schedule.get(effective_time) == pos:
                    return True

        # Robot collision check
        for robot in self.robots:
            if robot.name != current_robot_name:
                other_robot_step = self.robot_current_steps.get(robot.name)
                if other_robot_step and other_robot_step[1] == time and other_robot_step[0] == pos:
                    return True

        return False

    def get_neighbors(self, node: Node, current_robot_name: str) -> List[Node]:
        neighbors = []
        x, y = node.position
        current_time = node.time
        g = node.g + 1

        for dx, dy in self.directions:
            new_pos = (x + dx, y + dy)
            new_time = current_time + 1

            if not self.is_collision(new_pos, new_time, current_robot_name):
                neighbors.append(Node(new_pos, new_time, g, node))

        return neighbors

    @staticmethod
    def heuristic(pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def plan_single_step(self, robot, current_time: int) -> Tuple[Tuple[int, int], int]:
        current_pos = robot.current_position or robot.start_position
        cache_key = (current_pos, robot.end_position)

        # Check cache first
        if cache_key in self.path_cache:
            cached_path = self.path_cache[cache_key]
            if cached_path and len(cached_path) > 1:
                return cached_path[1]

        if current_pos == robot.end_position or not getattr(robot, "is_goal_reachable", True):
            return current_pos, current_time

        # Cache end position check
        end_x, end_y = robot.end_position
        if self.grid.grid[end_y][end_x] == 'X':
            robot.is_goal_reachable = False
            return current_pos, current_time

        path = self.dynamic_a_star(current_pos, robot.end_position, current_time, robot.name)
        
        # Cache the result
        if path:
            self.path_cache[cache_key] = path
            if len(path) > 1:
                return path[1]
        return path[0] if path else (current_pos, current_time)

    def dynamic_a_star(self, start: Tuple[int, int], goal: Tuple[int, int],
                      start_time: int, current_robot_name: str,
                      avoid_pos: Optional[Tuple[int, int]] = None,
                      stagnation_threshold: int = 50) -> Optional[List[Tuple[Tuple[int, int], int]]]:
        if self.grid.grid[goal[1]][goal[0]] == 'X':
            return None

        open_heap = []
        closed_set = set()
        node_dict = {}

        start_node = Node(start, start_time)
        start_node.h = self.heuristic(start, goal)
        start_node.f = start_node.h

        heapq.heappush(open_heap, start_node)
        node_dict[(start, start_time)] = start_node

        best_node = start_node
        best_distance = self.heuristic(start, goal)
        last_improvement = iterations = 0

        while open_heap and iterations - last_improvement <= stagnation_threshold:
            current = heapq.heappop(open_heap)

            if current.position == goal:
                path = []
                while current:
                    path.append((current.position, current.time))
                    current = current.parent
                return path[::-1]

            key = (current.position, current.time)
            if key in closed_set:
                iterations += 1
                continue

            closed_set.add(key)

            current_distance = self.heuristic(current.position, goal)
            if current_distance < best_distance:
                best_distance = current_distance
                best_node = current
                last_improvement = iterations

            neighbors = self.get_neighbors(current, current_robot_name)
            if avoid_pos and current.position == start and current.time == start_time:
                neighbors = [n for n in neighbors if n.position != avoid_pos]

            for neighbor in neighbors:
                key = (neighbor.position, neighbor.time)
                if key in closed_set:
                    continue

                existing = node_dict.get(key)
                if not existing or neighbor.g < existing.g:
                    neighbor.h = self.heuristic(neighbor.position, goal)
                    neighbor.f = neighbor.g + neighbor.h + 0.001 * neighbor.time
                    node_dict[key] = neighbor
                    heapq.heappush(open_heap, neighbor)

            iterations += 1

        if best_node != start_node:
            path = []
            current = best_node
            while current:
                path.append((current.position, current.time))
                current = current.parent
            return path[::-1]
        return None

    def execute_time_step(self):
        active_robots = [robot for robot in self.robots
                        if robot.current_position != robot.end_position]

        if not active_robots:
            return

        proposed_steps = {}
        for robot in active_robots:
            next_step = self.plan_single_step(robot, self.current_time)
            proposed_steps[robot.name] = next_step
            self.robot_current_steps[robot.name] = next_step

        position_counts = defaultdict(list)
        for name, (pos, _) in proposed_steps.items():
            position_counts[pos].append(name)

        collision_pairs = {robot for pos, robots in position_counts.items()
                         if len(robots) > 1 for robot in robots}

        for robot in sorted(active_robots, key=lambda r: self.heuristic(r.current_position, r.end_position)):
            if robot.name in collision_pairs:
                current_pos = robot.current_position
                conflicting_pos = proposed_steps[robot.name][0]
                alternative_path = self.dynamic_a_star(
                    current_pos,
                    robot.end_position,
                    self.current_time,
                    robot.name,
                    avoid_pos=conflicting_pos
                )

                if alternative_path and len(alternative_path) > 1:
                    new_pos = alternative_path[1][0]
                    robot.current_position = new_pos
                    self.robot_current_steps[robot.name] = (new_pos, self.current_time + 1)
                else:
                    neighbors = self.get_neighbors(Node(current_pos, self.current_time), robot.name)
                    valid_neighbors = [n for n in neighbors if n.position != conflicting_pos]
                    if valid_neighbors:
                        valid_neighbors.sort(key=lambda n: n.f)
                        new_pos = valid_neighbors[0].position
                        robot.current_position = new_pos
                        self.robot_current_steps[robot.name] = (new_pos, self.current_time + 1)
                    else:
                        self.robot_current_steps[robot.name] = (current_pos, self.current_time + 1)
            else:
                robot.current_position = proposed_steps[robot.name][0]

        self.current_time += 1