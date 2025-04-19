#
# Created by Ali Hamza Azam (22I-2126 | CS-A) on 19/04/2025
#

import networkx as nx
import time
from typing import Any, Dict, List, Set, Tuple, Optional

# Read graph from file
def read_graph_from_file(filepath: str) -> nx.Graph:

    G = nx.Graph()
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.replace(',', ' ').split()
                u, v = parts[0], parts[1]
                w = float(parts[2]) if len(parts) > 2 else 1.0
                if G.has_edge(u, v):
                    G[u][v]['weight'] = min(G[u][v]['weight'], w)
                else:
                    G.add_edge(u, v, weight=w)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
    return G


def dfs_traverse(G: nx.Graph, start: Any, visited: Optional[Set[Any]] = None) -> Set[Any]:
    if visited is None:
        visited = set()
    visited.add(start)
    for nbr in G.neighbors(start):
        if nbr not in visited:
            dfs_traverse(G, nbr, visited)
    return visited


def bfs_traverse(G: nx.Graph, start: Any) -> Set[Any]:
    visited = {start}
    queue = [start]
    while queue:
        node = queue.pop(0)
        for nbr in G.neighbors(node):
            if nbr not in visited:
                visited.add(nbr)
                queue.append(nbr)
    return visited


def get_connected_components(G: nx.Graph) -> List[Set[Any]]:
    visited: Set[Any] = set()
    comps: List[Set[Any]] = []
    for node in G.nodes():
        if node not in visited:
            comp = dfs_traverse(G, node, visited=set())
            visited |= comp
            comps.append(comp)
    return comps


def find_cliques(G: nx.Graph, min_size: int = 3) -> List[List[Any]]:
    cliques: List[List[Any]] = []
    nodes = list(G.nodes())
    def bronk(R: Set[Any], P: Set[Any], X: Set[Any]):
        if not P and not X:
            if len(R) >= min_size:
                cliques.append(sorted(R))
            return
        pivot = max(P|X, key=lambda u: len(P & set(G.neighbors(u))), default=None)
        candidates = P - set(G.neighbors(pivot)) if pivot else P.copy()
        for v in list(candidates):
            nbrs = set(G.neighbors(v))
            bronk(R|{v}, P&nbrs, X&nbrs)
            P.remove(v)
            X.add(v)
    bronk(set(), set(nodes), set())
    cliques.sort(key=len, reverse=True)
    return cliques


def find_chains(G: nx.Graph, min_length: int = 3) -> List[List[Any]]:
    deg = dict(G.degree())
    chains: List[List[Any]] = []
    seen: Set[Tuple[Any,...]] = set()
    for comp in get_connected_components(G):
        endpoints = [n for n in comp if deg[n] != 2]
        for u in endpoints:
            for v in G.neighbors(u):
                path = [u, v]
                prev, curr = u, v
                while deg[curr] == 2:
                    nxt = next(n for n in G.neighbors(curr) if n != prev)
                    prev, curr = curr, nxt
                    path.append(curr)
                if curr != u and len(path) >= min_length:
                    key = tuple(path)
                    rev = tuple(reversed(path))
                    if key not in seen and rev not in seen:
                        chains.append(path)
                        seen.add(key); seen.add(rev)
    chains.sort(key=len, reverse=True)
    return chains


def find_stars(G: nx.Graph, min_size: int = 3) -> List[List[Any]]:
    stars: List[List[Any]] = []
    min_leaves = max(min_size - 1, 1)
    deg = dict(G.degree())
    for center in sorted(G.nodes(), key=lambda n: -deg[n]):
        if deg[center] < min_leaves:
            break
        leaves = [nbr for nbr in G.neighbors(center) if deg[nbr] == 1]
        if len(leaves) >= min_leaves:
            valid = all(not G.has_edge(a, b) for i,a in enumerate(leaves) for b in leaves[i+1:])
            if valid:
                stars.append([center] + leaves)
    stars.sort(key=len, reverse=True)
    return stars


def find_cycles(G: nx.Graph, min_length: int = 3) -> List[List[Any]]:
    visited: Set[Any] = set()
    parent: Dict[Any, Optional[Any]] = {}
    tree_edges: Set[frozenset] = set()
    back_edges: Set[frozenset] = set()
    def dfs(u: Any):
        visited.add(u)
        for v in G.neighbors(u):
            e = frozenset((u,v))
            if e in tree_edges or e in back_edges:
                continue
            if v not in visited:
                parent[v] = u; tree_edges.add(e); dfs(v)
            else:
                back_edges.add(e)
    for node in G.nodes():
        if node not in visited:
            parent[node] = None; dfs(node)
    cycles: List[List[Any]] = []
    for e in back_edges:
        u,v = tuple(e); pu,pv=[u],[v]
        while parent[pu[-1]] is not None: pu.append(parent[pu[-1]])
        while parent[pv[-1]] is not None: pv.append(parent[pv[-1]])
        lca = next(n for n in pv if n in set(pu))
        cycle = pu[:pu.index(lca)+1] + list(reversed(pv[:pv.index(lca)]))
        if len(cycle)>=min_length:
            m=min(cycle); i=cycle.index(m); norm=cycle[i:]+cycle[:i]
            if norm not in cycles: cycles.append(norm)
    cycles.sort(key=len, reverse=True)
    return cycles


def visualize_chain(chain: List[Any]) -> str:
    return " - ".join(map(str, chain))

def benchmark_traversals(filepaths: List[str], min_size: int = 3) -> None:
    print("Benchmarking DFS vs BFS traversal and subgraph counts:")
    for path in filepaths:
        G = read_graph_from_file(path)
        if G.number_of_nodes() == 0:
            print(f"  {path}: empty or missing.")
            continue
        start = next(iter(G.nodes()))
        # traversal timings
        t1 = time.time()
        dfs_traverse(G, start)
        d_time = time.time() - t1
        t2 = time.time()
        bfs_traverse(G, start)
        b_time = time.time() - t2
        # subgraph counts
        c_time = time.time(); cliques = find_cliques(G, min_size); c_count = len(cliques); c_time = time.time() - c_time
        ch_time = time.time(); chains = find_chains(G, min_size); ch_count = len(chains); ch_time = time.time() - ch_time
        s_time = time.time(); stars = find_stars(G, min_size); s_count = len(stars); s_time = time.time() - s_time
        cy_time = time.time(); cycles = find_cycles(G, min_size); cy_count = len(cycles); cy_time = time.time() - cy_time

        print(f"  {path}:")
        print(f"    DFS traversal: {d_time:.6f}s | BFS traversal: {b_time:.6f}s")
        print(f"    Cliques (≥{min_size}): {c_count} found in {c_time:.6f}s")
        print(f"    Chains (≥{min_size}): {ch_count} found in {ch_time:.6f}s")
        print(f"    Stars  (≥{min_size}): {s_count} found in {s_time:.6f}s")
        print(f"    Cycles (≥{min_size}): {cy_count} found in {cy_time:.6f}s")


if __name__ == '__main__':
    filepaths = ['Data1.txt', 'Data2.txt', 'Data3.txt']
    for path in filepaths:
        G = read_graph_from_file(path)
        print(f"Graph from {path}:")
        print(f"  Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
        print("-" * 40)
        # Cycles, Cliques, Chains, Stars
        cliques = find_cliques(G)
        chains = find_chains(G)
        stars = find_stars(G)
        cycles = find_cycles(G)
        # print count and visualization
        print(f"  Cliques: {len(cliques)} found")
        for i, clique in enumerate(cliques[:3]):
            print(f"    {i+1}: {clique}")
        print(f"  Chains: {len(chains)} found")
        for i, chain in enumerate(chains[:3]):
            print(f"    {i+1}: {visualize_chain(chain)}")
        print(f"  Stars: {len(stars)} found")
        for i, star in enumerate(stars[:3]):
            print(f"    {i+1}: {star}")
        print(f"  Cycles: {len(cycles)} found")
        for i, cycle in enumerate(cycles[:3]):
            print(f"    {i+1}: {cycle}")
        print("-" * 40)
        print()
    benchmark_traversals(filepaths)
