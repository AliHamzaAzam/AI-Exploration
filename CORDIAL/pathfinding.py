#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

import heapq
from collections import defaultdict
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
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)]  # Added wait (0,0)
        self.max_time = 1000
        self.current_time = 0
        self.robot_current_steps = {robot.name: None for robot in self.robots}  # {name: (position, time)}

    def is_collision(self, pos: Tuple[int, int], time: int, current_robot_name: str) -> bool:
        # Check grid boundaries
        if not (0 <= pos[1] < self.grid.get_size() and 0 <= pos[0] < self.grid.get_size()):
            return True

        # Check static obstacles (grid is accessed as [y][x])
        if self.grid.grid[pos[1]][pos[0]] == 'X':
            return True

        # Check dynamic agents
        for agent_id, schedule in self.agents.items():
            if schedule:
                last_time = max(schedule.keys())
                period = 2 * last_time
                if period == 0:
                    period = 1
                t_mod = time % period

                # Calculate effective time for ping-pong behavior
                if t_mod <= last_time:
                    effective_time = t_mod
                else:
                    effective_time = period - t_mod

                if effective_time in schedule and schedule[effective_time] == pos:
                    return True

        # Check other robots' next positions
        for robot in self.robots:
            if robot.name == current_robot_name:
                continue
            other_robot_step = self.robot_current_steps.get(robot.name)
            if other_robot_step and other_robot_step[1] == time and other_robot_step[0] == pos:
                return True

        return False

    def get_neighbors(self, node: Node, current_robot_name: str) -> List[Node]:
        neighbors = []
        x, y = node.position
        current_time = node.time

        for dx, dy in self.directions:
            new_x = x + dx
            new_y = y + dy
            new_time = current_time + 1

            # Check boundaries and collision for the NEXT STEP
            if not (0 <= new_x < self.grid.get_size() and 0 <= new_y < self.grid.get_size()):
                continue

            neighbor_pos = (new_x, new_y)
            if self.is_collision(neighbor_pos, new_time, current_robot_name):
                continue

            new_g = node.g + 1
            neighbor = Node(
                position=neighbor_pos,
                time=new_time,
                g=new_g,
                parent=node
            )
            neighbors.append(neighbor)

        return neighbors

    def heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1]) + abs((pos[0] - goal[0]) * (pos[1] - goal[1]) * 0.001)

    def plan_single_step(self, robot, current_time: int) -> Tuple[Tuple[int, int], int]:
        current_pos = robot.current_position or robot.start_position

        # Early return if already at goal.
        if current_pos == robot.end_position:
            return (current_pos, current_time)

        # Only do pathfinding for robots whose goal is reachable (default True)
        if not getattr(robot, "is_goal_reachable", True):
            return (current_pos, current_time)

        # Check if the goal state is a static obstacle.
        # Note: the grid is indexed as grid[y][x]
        if self.grid.grid[robot.end_position[1]][robot.end_position[0]] == 'X':
            # print(f"Robot {robot.name}: goal {robot.end_position} is a static obstacle! Marking goal as unreachable.")
            robot.is_goal_reachable = False
            return (current_pos, current_time)

        # # Debug print
        # print(f"\nPlanning for Robot {robot.name}:")
        # print(f"Current position: {current_pos}")
        # print(f"Goal position: {robot.end_position}")

        # Attempt to plan the next step using dynamic A*.
        path = self.dynamic_a_star(
            current_pos,
            robot.end_position,
            current_time,
            robot.name
        )

        if path:
            # print(f"Found path for Robot {robot.name}: {path}")
            if len(path) > 1:
                # print(f"Taking next step: {path[1]}")
                return path[1]
            else:
                # print(f"Path has only one step (current position)")
                return path[0]
        else:
            # print(f"No path found for Robot {robot.name}")
            return (current_pos, current_time)

    def dynamic_a_star(self, start: Tuple[int, int], goal: Tuple[int, int],
                       start_time: int, current_robot_name: str,
                       avoid_pos: Optional[Tuple[int, int]] = None,
                       max_depth: int = 100000,
                       heuristic_weight: float = 1.0,
                       stagnation_threshold: int = 1000) -> Optional[List[Tuple[Tuple[int, int], int]]]:
        # Check if the goal state is an obstacle.
        # Note: grid is indexed as grid[y][x]
        if self.grid.grid[goal[1]][goal[0]] == 'X':
            # print(f"Goal {goal} is an obstacle for robot {current_robot_name}. No path exists.")
            return None

        open_heap = []
        closed_set = set()
        node_dict = {}

        # Initialize start node
        start_node = Node(start, start_time)
        start_node.g = 0  # Cost from start
        start_node.h = self.heuristic(start, goal)
        start_node.f = start_node.g + heuristic_weight * start_node.h

        heapq.heappush(open_heap, start_node)
        node_dict[(start_node.position, start_node.time)] = start_node

        # Track best progress toward the goal
        best_node = start_node
        best_distance = self.heuristic(start, goal)
        last_improvement_iteration = 0
        iterations = 0

        while open_heap and iterations < max_depth:
            current = heapq.heappop(open_heap)
            
            # Track current distance
            current_distance = self.heuristic(current.position, goal)
            if current_distance < best_distance:
                best_distance = current_distance
                best_node = current
                last_improvement_iteration = iterations

            # Found the exact goal
            if current.position == goal:
                # print(f"Exact path found for robot {current_robot_name} after {iterations} iterations")
                path = []
                while current:
                    path.append((current.position, current.time))
                    current = current.parent
                return path[::-1]

            # Check stagnation: if no improvement for a while, break early and use best partial path
            if iterations - last_improvement_iteration > stagnation_threshold:
                # print(f"Stagnation reached for robot {current_robot_name} after {iterations} iterations")
                break

            # Skip if we've already processed this state
            if (current.position, current.time) in closed_set:
                iterations += 1
                continue

            closed_set.add((current.position, current.time))

            # Generate neighbors
            neighbors = self.get_neighbors(current, current_robot_name)
            if current.position == start and current.time == start_time and avoid_pos:
                neighbors = [n for n in neighbors if n.position != avoid_pos]

            for neighbor in neighbors:
                key = (neighbor.position, neighbor.time)
                if key in closed_set:
                    continue

                tentative_g = current.g + 1  # Movement cost of 1 per step

                existing = node_dict.get(key)
                if not existing or tentative_g < existing.g:
                    neighbor.g = tentative_g
                    neighbor.h = self.heuristic(neighbor.position, goal)
                    neighbor.f = neighbor.g + heuristic_weight * neighbor.h
                    neighbor.parent = current
                    node_dict[key] = neighbor
                    heapq.heappush(open_heap, neighbor)

            iterations += 1

        # Termination: no complete path found within max_depth or search stagnated.
        if best_node != start_node:
            # print(f"Partial path found for robot {current_robot_name} after {iterations} iterations")
            # print(f"Best distance to goal: {best_distance} (initial distance was {self.heuristic(start, goal)})")
            path = []
            current = best_node
            while current:
                path.append((current.position, current.time))
                current = current.parent
            return path[::-1]

        # # If no progress made at all
        # print(f"A* failed for robot {current_robot_name} after {iterations} iterations")
        # print(f"Start: {start}, Goal: {goal}")
        # print("No progress made towards the goal; open list empty or no improvement.")

        return None

    def execute_time_step(self):
        # Skip robots that are already at their goals
        active_robots = [robot for robot in self.robots 
                        if robot.current_position != robot.end_position]
        
        # print(f"\nTime step {self.current_time}")
        # print(f"Active robots: {[robot.name for robot in active_robots]}")
        
        if not active_robots:  # If all robots are at their goals
            return

        # Collect proposed steps only for active robots
        proposed_steps = {}
        for robot in active_robots:
            next_step = self.plan_single_step(robot, self.current_time)
            proposed_steps[robot.name] = next_step
            self.robot_current_steps[robot.name] = next_step
            # print(f"Proposed step for {robot.name}: {next_step}")

        # Detect and resolve collisions (only for active robots)
        position_counts = defaultdict(list)
        for name, (pos, _) in proposed_steps.items():
            position_counts[pos].append(name)

        collision_pairs = {robot for pos, robots in position_counts.items()
                           if len(robots) > 1 for robot in robots}
        
        # if collision_pairs:
        #     print(f"Detected collisions between robots: {collision_pairs}")

        # Resolve collisions with prioritization (only for active robots)
        for robot in sorted(active_robots, key=lambda r: self.heuristic(r.current_position, r.end_position)):
            if robot.name in collision_pairs:
                current_pos = robot.current_position
                conflicting_pos = proposed_steps[robot.name][0]
                # print(f"\nResolving collision for {robot.name}")
                # print(f"Current position: {current_pos}")
                # print(f"Conflicting position: {conflicting_pos}")

                alternative_path = self.dynamic_a_star(
                    current_pos,
                    robot.end_position,
                    self.current_time,
                    robot.name,
                    avoid_pos=conflicting_pos
                )

                if alternative_path:
                    # If a valid alternative path is found, if possible use the next step.
                    new_pos = alternative_path[1][0] if len(alternative_path) > 1 else alternative_path[0][0]
                    robot.current_position = new_pos
                    self.robot_current_steps[robot.name] = (new_pos, self.current_time + 1)
                    # print(f"Robot {robot.name} taking alternative path to {new_pos}")
                else:
                    # Fallback strategy: try direct neighbors, excluding the conflicting move.
                    neighbors = self.get_neighbors(Node(current_pos, self.current_time), robot.name)
                    valid_neighbors = [n for n in neighbors if n.position != conflicting_pos]
                    # print(f"Found {len(valid_neighbors)} valid neighboring positions")
                    if valid_neighbors:
                        valid_neighbors.sort(key=lambda n: n.f)
                        new_pos = valid_neighbors[0].position
                        robot.current_position = new_pos
                        self.robot_current_steps[robot.name] = (new_pos, self.current_time + 1)
                        # print(f"Fallback: Robot {robot.name} moved from {current_pos} to {new_pos}")
                    else:
                        # No move possible; the robot stays in place.
                        self.robot_current_steps[robot.name] = (current_pos, self.current_time + 1)
                        # print(f"Robot {robot.name} has no alternative move from {current_pos} (staying in place)")
            else:
                # No collision: update robot position using the proposed move.
                robot.current_position = proposed_steps[robot.name][0]

        self.current_time += 1

