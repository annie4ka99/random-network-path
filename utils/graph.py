from dataclasses import dataclass
from typing import Any, Callable


class Graph:
    def __init__(self, nodes_num: int, start: int, finish: int, 
                 edges: list[dict[int, Any]]) -> None:
        self.n = nodes_num
        self.S = start
        self.F = finish
        self.edges = edges

    def shortest_path(self, get_val: Callable[[Any], float]) -> tuple[float, list[int]]:
        d  = [None for _ in range(self.n)]
        not_used = set(range(self.n))
        prev = [None for _ in range(self.n)]

        d[self.S] = 0
        for _ in range(self.n):
            v = None
            for u in not_used:
                if (v is None or (d[u] is not None and d[u] < d[v])):
                    v = u
            if v is None:
                break
            not_used.remove(v)
            for u in self.edges[v]:
                
                if d[u] is None or d[v] + get_val(self.edges[v][u]) < d[u]:
                    d[u] = d[v] + get_val(self.edges[v][u])
                    prev[u] = v

        path_nodes = []
        node = self.F
        while node != self.S:
            path_nodes.append(node)
            node = prev[node]
        path_nodes.append(self.S)
        return d[self.F], path_nodes[::-1]
