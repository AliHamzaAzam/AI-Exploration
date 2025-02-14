#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

import ast

class Agent:
    def __init__(self, agent_file):
        self.agent_file = agent_file
        self.num_agents = 0
        # Dictionary to hold each agent's positions with time as key
        self.agent_positions = {}
        self.load_agents()
        self.agent_current_positions = {}

    def load_agents(self):
        with open(self.agent_file) as f:
            lines = f.readlines()
            self.num_agents = len(lines)

            for line in lines:
                # Extract agent ID
                agent_id_str = line.split(':')[0].strip()
                agent_id = int(agent_id_str.split()[1])

                # Extract agent path
                agent_path_str = line[line.find("[")+1:line.find("]")]
                agent_path = ast.literal_eval(agent_path_str)

                # Extract agent times
                agent_time_str = line[line.find("at times") + 9:line.rfind("]")]
                agent_time = ast.literal_eval(agent_time_str + "]")

                # Initialize the agent's dictionary if not already present
                if agent_id not in self.agent_positions:
                    self.agent_positions[agent_id] = {}

                # Populate the agent's positions with time as key
                for i in range(len(agent_path)):
                    self.agent_positions[agent_id][agent_time[i]] = agent_path[i]

        # # Print agent positions for verification
        # for agent_id, positions in self.agent_positions.items():
        #     print(f"Agent {agent_id} positions:")
        #     for time, position in sorted(positions.items()):
        #         print(f"  Time {time}: Position {position}")

    def initialize_agents(self):
        for agent_id, positions in self.agent_positions.items():
            self.agent_current_positions[agent_id] = positions[0]

    def get_agents(self):
        return self.agent_positions

    def move_agent(self):
        # move all agents to next position
        for agent_id, positions in self.agent_positions.items():
            if positions:
                positions.pop(0)
                self.agent_current_positions[agent_id] = positions[0]


# temp main for testing
if __name__ == "__main__":
    agent = Agent("Data/Agent0.txt")

    # print(agent.get_agents())
    # print(agent.get_size())
    # print(agent.get_grid())
    # agent.print_grid()
    # agent.print_agents()