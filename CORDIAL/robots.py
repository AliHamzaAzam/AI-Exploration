#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

class Robot:
    def __init__(self, name, start_position, end_position):
        self.name = name
        self.start_position = self.current_position = start_position
        self.end_position = end_position
        self.is_goal_reachable = True

    def get_position(self):
        return self.current_position


def parse_position(position_str):
    return tuple(map(int, position_str.strip('() ').split(',')))


class RobotLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.robots = self.load_robots()

    def load_robots(self):
        robots = []
        with open(self.file_path, 'r') as file:
            for line in file:
                name, positions = line.split(':')
                name = name.split()[1]
                start_str, end_str = positions.strip().split('End')
                start_position = parse_position(start_str.replace('Start', '').strip())
                end_position = parse_position(end_str.strip())
                robots.append(Robot(name, start_position, end_position))
        return robots

    def get_robots(self):
        return self.robots

