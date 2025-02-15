#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

import grid
import agents
import robots
from pathfinding import PathFinder

def main():
    # Configuration
    VISUALIZATION_ENABLED = True
    MAX_TIMESTEPS = 1000 # Reduced from 1000 for faster testing

    # Initialize components
    grid_file = 'Data/data4.txt'
    agents_file = 'Data/Agent4.txt'
    robot_file = 'Data/Robots4.txt'

    grid_obj = grid.Grid(grid_file)
    # print("Grid: " + grid_obj.get_grid()[94][28])
    agent_loader = agents.Agent(agents_file)
    agent_loader.initialize_agents()
    agents_dict = agent_loader.get_agents()
    robot_loader = robots.RobotLoader(robot_file)
    robots_list = robot_loader.get_robots()

    # Initialize the pathfinder
    pathfinder = PathFinder(grid_obj, robots_list, agents_dict)

    # Initialize tracking for robot paths and completion times.
    # For each robot, we start with its start position.
    robot_paths = {robot.name: [robot.start_position] for robot in robots_list}
    robot_completion_time = {robot.name: None for robot in robots_list}

    for step in range(MAX_TIMESTEPS):
        pathfinder.execute_time_step()

        # Update each robot's path with its new position.
        for robot in robots_list:
            if robot.is_goal_reachable:
                if robot.current_position != robot.end_position:
                    robot_paths[robot.name].append(robot.current_position)
                    # Record the time when the robot first reaches its goal.
                if robot.current_position == robot.end_position and robot_completion_time[robot.name] is None:
                    robot_completion_time[robot.name] = pathfinder.current_time - 1
            else:
                robot_paths[robot.name] = "Goal is unreachable"
                robot_completion_time[robot.name] = "Goal is unreachable"

        if VISUALIZATION_ENABLED:
            grid_obj.update_grid(agents_dict, robots_list, pathfinder.current_time)
            grid_obj.print_grid()
            print(f"Time step: {pathfinder.current_time}\n")

        # If all robots reached their goals, exit early.
        if all(robot.current_position == robot.end_position for robot in robots_list if robot.is_goal_reachable):
            print(f"All robots reached their goals in {step + 1} steps!")
            break
    else:
        print(f"Maximum time steps ({MAX_TIMESTEPS}) reached!")

    # Print the final path and total time for each robot in the desired format.
    for robot in robots_list:
        total_time = robot_completion_time[robot.name]
        if total_time is None:
            total_time = pathfinder.current_time  # In case a robot never reached its goal.
        print(f"Robot {robot.name} Path: {robot_paths[robot.name]}")
        print(f"Robot {robot.name} Total Time: {total_time}")

if __name__ == "__main__":
    main()









