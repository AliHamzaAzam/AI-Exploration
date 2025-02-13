#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

class Robot:
    def __init__(self, name, start_position, end_position):
        self.name = name
        self.start_position = start_position
        self.current_position = start_position
        self.end_position = end_position

    def __repr__(self):
        return f"{self.name}: Start {self.start_position} End {self.end_position}"

    def get_position(self):
        return self.current_position

    def move(self, direction):
        x, y = self.current_position
        if direction == 'U':
            self.current_position = (x, y - 1)
        elif direction == 'D':
            self.current_position = (x, y + 1)
        elif direction == 'L':
            self.current_position = (x - 1, y)
        elif direction == 'R':
            self.current_position = (x + 1, y)

class RobotLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.robots = []
        self.load_robots()

    def load_robots(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                parts = line.split(':')
                name = parts[0].strip()
                positions = parts[1].strip().split('End')
                start_str = positions[0].replace('Start', '').strip()
                end_str = positions[1].strip()
                start_position = tuple(map(int, start_str.strip('()').split(',')))
                end_position = tuple(map(int, end_str.strip('()').split(',')))
                self.robots.append(Robot(name, start_position, end_position))

    def get_robots(self):
        return self.robots

# temp main for testing
if __name__ == "__main__":
    robot_file = 'Data/Robots0.txt'
    loader = RobotLoader(robot_file)
    robots = loader.get_robots()
    for robot in robots:
        print(robot)
