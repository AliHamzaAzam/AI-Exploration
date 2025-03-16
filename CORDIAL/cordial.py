#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

import grid
import agents
import robots
from pathfinding import PathFinder
import time

def visualize_grid(grid_obj, agents_dict, robots_list, current_time):
    grid_obj.update_grid(agents_dict, robots_list, current_time)
    print('\033[H', end='')
    grid_obj.print_grid()
    print(f"Grid state at time step: {current_time}\n")
    time.sleep(0.5)

def main():
    visualization_enabled = False
    max_timestamps = 1000

    # Initialize components
    grid_obj = grid.Grid('Data/data0.txt')
    agents_dict = agents.Agent('Data/Agent0.txt').get_agents()
    robots_list = robots.RobotLoader('Data/Robots0.txt').get_robots()

    # Initialize the pathfinder
    pathfinder = PathFinder(grid_obj, robots_list, agents_dict)

    print('\033[2J', end='')    # Clear entire screen
    print('\033[?25l', end='')  # Hide cursor

    robot_paths = {robot.name: [robot.start_position] for robot in robots_list}
    robot_completion_time = {robot.name: None for robot in robots_list}

    if visualization_enabled:
        visualize_grid(grid_obj, agents_dict, robots_list, pathfinder.current_time)

    for step in range(max_timestamps):
        pathfinder.execute_time_step()
        all_reached = True

        for robot in robots_list:
            if not robot.is_goal_reachable:
                robot_paths[robot.name] = "Goal is unreachable"
                robot_completion_time[robot.name] = pathfinder.current_time
                continue

            if robot.current_position != robot_paths[robot.name][-1]:
                robot_paths[robot.name].append(robot.current_position)

            if robot.current_position == robot.end_position:
                if robot_completion_time[robot.name] is None:
                    robot_completion_time[robot.name] = pathfinder.current_time
            else:
                all_reached = False

        if visualization_enabled:
            visualize_grid(grid_obj, agents_dict, robots_list, pathfinder.current_time)

        if all_reached:
            print(f"All robots reached their goals in {step + 1} steps!")
            break

    # Print the final path and total time for each robot
    max_time = 0
    for robot in robots_list:
        path = robot_paths[robot.name]
        if path == "Goal is unreachable":
            print(f"Robot {robot.name} Path: Goal is unreachable")
        else:
            total_time = robot_completion_time[robot.name] or pathfinder.current_time
            print(f"Robot {robot.name} Path: {robot_paths[robot.name]}")
            print(f"Robot {robot.name} Total Time: {total_time}")
            if total_time > max_time:
                max_time = total_time

    print('\033[?25h', end='')


if __name__ == "__main__":
    main()
