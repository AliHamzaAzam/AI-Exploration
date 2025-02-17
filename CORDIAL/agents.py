#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/02/2025
#

import ast

class Agent:
    def __init__(self, agent_file):
        self.agent_file = agent_file
        self.agent_positions = self.load_agents()
        self.agent_current_positions = {agent_id: positions[0] for agent_id, positions in self.agent_positions.items()}

    def load_agents(self):
        agent_positions = {}
        with open(self.agent_file) as f:
            for line in f:
                agent_id = int(line.split(':')[0].strip().split()[1])
                agent_path = ast.literal_eval(line[line.find("[")+1:line.find("]")])
                agent_time = ast.literal_eval(line[line.find("at times") + 9:line.rfind("]")] + "]")

                agent_positions[agent_id] = {agent_time[i]: agent_path[i] for i in range(len(agent_path))}
        return agent_positions

    def get_agents(self):
        return self.agent_positions
