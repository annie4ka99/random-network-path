from dataclasses import dataclass
from typing import Any
import numpy as np

from utils.graph import Graph
from utils.input import EdgeParams


class StohasticNetwork:
    def __init__(self, nodes_num:int, 
                 start_node:int, finish_node:int, 
                 edge_params:list[EdgeParams],
                 random_state=0) -> None:
        self.rng = np.random.default_rng(random_state)

        self.init_and_validate_graph(nodes_num, start_node, finish_node, edge_params)     


    def __call__(self, path: list[int]) -> list[float]:
        if not self.validate_path(path):
            return None
        
        return [self.rng.lognormal(*self.graph.edges[path[i-1]][path[i]]) for i in range(1, len(path))]

    def validate_path(self, path: list[int]) -> bool:
        return (len(path) > 1 and 
                path[0] == self.graph.S and path[-1] == self.graph.F and
                all((path[i] >= 0 and path[i] < self.graph.n 
                     and (i == 0 or path[i] in self.graph.edges[path[i-1]]) for i in range(len(path)))))

    
    def init_and_validate_graph(self, nodes_num: int, 
                                 start_node:int, finish_node:int, 
                                 edge_params:list[EdgeParams]) -> None:
        def is_node(node):
            return node >= 0 and node < n
        
        def dfs(v):
            used[v] = 0
            has_cycles = False
            for u in edges[v]:
                if used[u] == 0 or (used[u] == -1 and dfs(u)):
                    has_cycles = True
                    break
            used[v] = 1
            return has_cycles
        
        if nodes_num <= 0:
            raise ValueError(f"number of nodes should be positive")
        n = nodes_num

        if (not is_node(start_node) or not is_node(finish_node) or 
            not all((is_node(edge.from_) and is_node(edge.to_) for edge in edge_params))):
            raise ValueError(f"incorrect nodes in specified graph (should be in [0,{n})")

        edges = [dict() for _ in range(n)]
        
        for edge in edge_params:
            if edge.to_ in edges[edge.from_]:
                return "duplicated edges found"
            edges[edge.from_][edge.to_] = (edge.mu, edge.sigma)
        
        used = [-1] * n
        has_cycles = dfs(start_node)
        
        if has_cycles:
            raise ValueError(f"specified graph has a cycle")
        
        if not used[finish_node]:
            raise ValueError(f"path from S to F doesn't exist in specified graph")
        
        self.graph = Graph(n, start_node, finish_node, edges)

    def get_shortest_path(self) -> tuple[float, list[int]]:
        return self.graph.shortest_path(lambda params: np.exp(params[0] + (params[1] ** 2)/2))
    
    def get_graph(self) -> dict[str, Any]:
        return dict(nodes_num = self.graph.n, 
                    start=self.graph.S, finish=self.graph.F, 
                    edges=[dict(((k, None) for k in node_edges.keys())) for node_edges in self.graph.edges])