#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 13/03/2025
#

import random
import csv
import copy
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


class GraphColoring:
    def __init__(self, filename, beam_width=15, pre_defined_count=0, is_two_hop=False):
        self.graph = defaultdict(set)
        self.pre_assigned_colors = {}
        self.read_graph(filename)
        self.num_vertices = len(self.graph)
        self.beam_width = beam_width
        self.solution = None
        self.is_two_hop = is_two_hop
        if pre_defined_count > 0:
            self.set_random_pre_defined(pre_defined_count)

    def read_graph(self, filename):
        """Reads the graph from a CSV file, ignoring the heuristic values."""
        with open(filename, "r") as file:
            reader = csv.reader(file, delimiter=' ')
            next(reader)  # Skip the first line (header)
            for row in reader:
                u, v = int(row[0]), int(row[1])
                self.graph[u].add(v)
                self.graph[v].add(u)

    def set_random_pre_defined(self, pre_defined_count):
        """Assigns random colors to a subset of vertices."""
        vertices = list(self.graph.keys())
        random.shuffle(vertices)
        available_colors = list(range(1, max(len(self.graph[v]) for v in self.graph) + 1))
        # Assign colors to the first pre_defined_count vertices ensuring no conflicts
        for vertex in vertices[:pre_defined_count]:
            if vertex not in self.pre_assigned_colors:
                neighbor_colors = {self.pre_assigned_colors[n] for n in self.graph[vertex] if n in self.pre_assigned_colors}
                for color in available_colors:
                    if color not in neighbor_colors:
                        self.pre_assigned_colors[vertex] = color
                        break

        # Print the pre-assigned colors
        print("Pre-assigned colors:")
        for vertex, color in self.pre_assigned_colors.items():
            print(f"Vertex {vertex} assigned color {color}")


    def initialize_state(self):
        """Initializes a valid coloring while respecting pre-assigned colors."""
        state = {}
        available_colors = list(range(1, self.num_vertices + 1))

        # Assign pre-assigned colors first
        for vertex in self.graph:
            if vertex in self.pre_assigned_colors:
                state[vertex] = self.pre_assigned_colors[vertex]

        # Assign colors to the remaining vertices
        for vertex in sorted(self.graph, key=lambda v: len(self.graph[v]), reverse=True):
            if vertex not in state:
                neighbor_colors = {state[n] for n in self.graph[vertex] if n in state}
                for color in available_colors:
                    if color not in neighbor_colors:
                        state[vertex] = color
                        break
        return state

    def heuristic(self, state):
        direct_conflicts = 0
        two_hop_conflicts = 0
        penalty_factor = 5
        colors_used = set()

        for vertex, color in state.items():
            colors_used.add(color)
            for neighbor in self.graph[vertex]:
                if state[neighbor] == color:
                    direct_conflicts += 1  # Direct conflict

        if self.is_two_hop:
            for vertex in self.graph:
                for neighbor in self.graph[vertex]:
                    for next_vertex in self.graph[neighbor]:
                        if next_vertex != vertex and state[vertex] == state[next_vertex]:
                            two_hop_conflicts += 1  # Two-hop conflict

        color_counts = defaultdict(int)
        for color in state.values():
            color_counts[color] += 1
        color_imbalance = (max(color_counts.values()) - min(color_counts.values())) * 1
        return direct_conflicts + (penalty_factor * two_hop_conflicts) + len(colors_used) + color_imbalance

    def generate_successors(self, state):
        """Generates new valid colorings by changing colors of high-degree vertices first."""
        successors = []
        high_degree_vertices = sorted(self.graph, key=lambda v: len(self.graph[v]), reverse=True)

        for vertex in high_degree_vertices:
            if vertex in self.pre_assigned_colors:
                continue  # Cannot change pre-assigned colors

            current_color = state[vertex]
            neighbor_colors = {state[n] for n in self.graph[vertex]}
            next_neighbor_colors = {state[n] for n in self.graph[vertex] if n in state}
            available_colors = set(range(1, self.num_vertices + 1)) - neighbor_colors
            if self.is_two_hop:
                available_colors -= next_neighbor_colors

            for new_color in available_colors:
                if new_color != current_color:
                    new_state = copy.deepcopy(state)
                    new_state[vertex] = new_color
                    successors.append(new_state)
                    if len(successors) >= self.beam_width:
                        return successors
        return successors

    def local_beam_search(self):
        """Executes Local Beam Search to find an optimal graph coloring."""
        states = [self.initialize_state()]
        best_solution = states[0]
        best_score = self.heuristic(best_solution)

        while True:
            successors = []
            for state in states:
                successors.extend(self.generate_successors(state))

            if not successors:
                break  # No more improvements possible

            # Select the best beam_width states
            successors.sort(key=self.heuristic)
            states = successors[:self.beam_width]

            # Update the best solution found
            current_best_score = self.heuristic(states[0])
            if current_best_score < best_score:
                best_solution = states[0]
                best_score = current_best_score
            else:
                break  # No improvement

        self.solution = best_solution
        return best_solution

    def print_solution(self):
        """Displays the final solution."""
        print("Vertex  |  Color")
        print("-----------------")
        for vertex, color in sorted(self.solution.items()):
            print(f"{vertex:6}  |  {color}")

    def print_graph(self):
        """Displays the graph in adjacency list format."""
        for vertex, neighbors in self.graph.items():
            print(f"{vertex}: {neighbors}")

    def print_total_colors(self):
        """Displays the total number of colors used."""
        print(f"Total colors used: {len(set(self.solution.values()))}")
        color_counts = defaultdict(int)
        for color in self.solution.values():
            color_counts[color] += 1
        print("Color counts:")
        for color, count in color_counts.items():
            print(f"Color {color}: {count}")


    ###
    # The following methods are used for visualization and verification purposes.
    # They are not necessary for the core functionality of the algorithm.
    ###

    def draw_solution(self):
        """Visualizes the graph with nodes colored according to their assigned colors."""
        if not self.solution or not self.graph:
            print("No solution exists. Run local_beam_search first.")
            return
        graph = self.graph
        coloring = self.solution
        title = f"Graph Coloring Solution (Colors used: {len(set(self.solution.values()))})"
        G = nx.Graph()
        for vertex, neighbors in graph.items():
            G.add_node(vertex)
            for neighbor in neighbors:
                G.add_edge(vertex, neighbor)
        color_list = list(mcolors.TABLEAU_COLORS) + list(mcolors.CSS4_COLORS)
        color_map = {i + 1: color for i, color in enumerate(color_list)}
        pos = nx.spring_layout(G, seed=47)
        plt.figure(figsize=(10, 8))
        node_colors = [color_map[coloring[node]] for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7)
        labels = {node: f"{node} (C{coloring[node]})" for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
        unique_colors = sorted(set(coloring.values()))
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                      markerfacecolor=color_map[color], markersize=15,
                                      label=f'Color {color}') for color in unique_colors]
        plt.legend(handles=legend_elements, loc='upper right')
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.show()


    def is_valid_coloring(self):
        """Verifies that no two adjacent vertices have the same color."""
        if not self.solution:
            print("No solution exists. Run local_beam_search first.")
            return False

        for vertex, neighbors in self.graph.items():
            vertex_color = self.solution[vertex]
            for neighbor in neighbors:
                if self.solution[neighbor] == vertex_color:
                    print(f"Invalid coloring: Vertices {vertex} and {neighbor} both have color {vertex_color}")
                    return False

        print("The coloring is valid.")
        return True




### Main code to test the GraphColoring class ###
if __name__ == "__main__":
    filename = "data/hypercube_dataset.txt"
    gc = GraphColoring(filename, 100, 0, False)
    gc.print_graph()
    gc.local_beam_search()
    gc.print_solution()
    gc.print_total_colors()
    gc.is_valid_coloring()
    gc.draw_solution()