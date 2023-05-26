from dataclasses import dataclass
import logging
from typing import Optional
import numpy as np

@dataclass
class EdgeParams:
    from_: int
    to_: int
    mu: int
    sigma: int


class RandomNetwork:
    def __init__(self, nodes_num:int, 
                 start_node:int, finish_node:int, 
                 edge_params:list[EdgeParams], 
                 log_path = "environment.log",
                 random_state=0):
        self.rng = np.random.default_rng(random_state)

        logging.basicConfig(filename=log_path,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
        self.logger = logging.getLogger('env logs')

        if not self.init_and_validate_graph(nodes_num, start_node, finish_node, edge_params):
            raise ValueError(f"couldn't build a network graph from specified parameters (see {log_path})")


    def __call__(self, path):
        self.logger.info(f"{path} requested")
        if not self.validate_path(path):
            raise ValueError(f"incorrect path: {path} (should exist and go from start to finish node)")
        
        return [self.rng.lognormal(*self.edges[i-1][i]) for i in range(1, len(path))]

    def validate_path(self, path):
        return (len(path) > 1 and 
                path[0] == self.S and path[-1] == self.F and
                all((self.is_node(path[i]) and (i == 0 or path[i] in self.edges[path[i-1]]) 
                     for i in range(len(path)))))


    def is_node(self, node):
        return node >= 0 and node < self.n

    def init_and_validate_graph(self, nodes_num: int, 
                                 start_node:int, finish_node:int, 
                                 edge_params:list[EdgeParams]) -> bool:
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
            self.logger.info(f"number of nodes should be positive")
            return False
        self.n = nodes_num

        if (not self.is_node(start_node) or not self.is_node(finish_node) or 
            not all((self.is_node(edge.from_) and self.is_node(edge.to_) for edge in edge_params))):
            self.logger.info(f"incorrect nodes in specified graph (should be between {0} and {self.n-1})")
            return False
        
        self.S = start_node
        self.F = finish_node

        edges = [dict() for _ in range(self.n)]
        
        for edge in edge_params:
            if edge.to_ in edges[edge.from_]:
                return "duplicated edges found"
            edges[edge.from_][edge.to_] = (edge.mu, edge.sigma)
        
        used = [-1] * self.n
        has_cycles = dfs(self.S)
        if has_cycles:
            self.logger.info(f"specified graph has a cycle")
            return False
        
        if not used[self.F]:
            self.logger.info(f"path from S to F doesn't exist in specified graph")
            return False
        
        self.edges = edges
        self.logger.info("graph instatinated succefully")
        return True
    
    def get_edges(self):
        return [list(node_edges.keys()) for node_edges in self.edges]
    
    def get_nodes(self):
        return self.n

    def get_start_node(self):
        return self.S
    
    def get_finish_node(self):
        return self.F