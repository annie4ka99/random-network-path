from dataclasses import dataclass
from typing import Callable
from tqdm import tqdm
from itertools import count
import numpy as np

from utils.graph import Graph

INIT_ALPHA = 2.0
INIT_BETA = 1.0
INIT_MU = 0.0
INIT_NU = 1.0

@dataclass
class Params:
    alpha: float
    beta: float
    mu: float
    nu: float

    logsum: float
    n: int
    vals: list[float]

    mean: float
    var: float

class PathSolver:
    def __init__(self, graph: Graph, network_call: Callable[[list[int]], list[float]], 
                 init_alpha: float = INIT_ALPHA, init_beta: float = INIT_BETA, 
                 init_mu: float = INIT_MU, init_nu: float = INIT_NU, 
                 max_explore_steps=10000, last_stable_steps=500,
                 random_state: int=0) -> None:
        self.graph = graph

        self.init_alpha = init_alpha
        self.init_beta = init_beta
        self.init_mu = init_mu
        self.init_nu = init_nu

        self.init_edges_params()

        self.max_explore_steps = max_explore_steps
        self.last_stable_steps = last_stable_steps

        self.network_call = network_call
        self.rng = np.random.default_rng(random_state)
        

    def init_edges_params(self) -> None:
        def dfs(v):
            is_ok = False
            for u in edges[v]:
                if u == self.graph.F:
                    ok_nodes[u] = 1
                elif ok_nodes[u] == 0:
                    dfs(u)
                if ok_nodes[u] == 1:
                    is_ok = True
                    ok_edges[v][u] = True
            ok_nodes[v] = 1 if is_ok else -1
        
        edges = self.graph.edges
        
        ok_nodes = [0] * self.graph.n
        ok_edges = [[False for _ in range(self.graph.n)] for i in range(self.graph.n)]

        dfs(self.graph.S)

        new_edges = []
        for v in range(self.graph.n):
            new_edges.append(dict((u, self.get_init_params()) for u in edges[v] if ok_edges[v][u]))
        self.graph.edges = new_edges
    

    def get_init_params(self) -> Params:
        return Params(alpha=self.init_alpha, beta=self.init_beta, mu=self.init_mu, nu=self.init_nu, 
                      logsum = 0.0, n = 0, vals=[], 
                      mean=self.init_mu, var=self.init_beta/(self.init_alpha - 1))
    

    def update_edge_posterior(self, from_: int, to_: int, t: float) -> None:
        params = self.graph.edges[from_][to_]
        alpha, beta, mu, nu, logsum, n, vals = (params.alpha, params.beta, 
                                                params.mu, params.nu, 
                                                params.logsum, params.n, 
                                                params.vals)

        vals.append(np.log(t))     
        n += 1
        logsum += np.log(t)
        logmean = logsum / n
        ss = sum([(x - logmean) ** 2 for x in vals])

        alpha += 1 / 2
        beta = self.init_beta + ss / 2 + self.init_nu*n*((logmean-self.init_mu)**2)*0.5/(self.init_nu+n)
        mu = (self.init_nu*self.init_mu + n*logmean) / (self.init_nu+n)
        nu += 1

        self.graph.edges[from_][to_] = Params(alpha=alpha, beta=beta, mu=mu, nu=nu, n=n, logsum=logsum, vals=vals,
                                              mean=params.mean, var=params.var)


    def sample_path(self) -> list[int]:
        path = self.graph.shortest_path(lambda edge: np.exp(edge.mean + edge.var / 2))[1]
        return path


    def sample_edges_params(self) -> None:
        for v in range(self.graph.n):
            for u in self.graph.edges[v]:
                params = self.graph.edges[v][u]
                alpha, beta, mu, nu = (params.alpha, params.beta, 
                                       params.mu, params.nu)

                var = 1 / self.rng.gamma(alpha, 1/beta)
                m = self.rng.normal(mu, np.sqrt(var/nu))
                self.graph.edges[v][u].mean = m
                self.graph.edges[v][u].var = var


    
    def expected_shortest_path(self) -> tuple[float, list[int]]:
        return self.graph.shortest_path(lambda edge: np.exp(edge.mu + (edge.beta/(edge.alpha-1)) / 2))

    def solve_path(self, stop_after_expore = False):
        
        stable_steps  = 0
        prev_path = None
        stabled = False

        min_expected_time = None
        min_expected_path = None
        for step in tqdm(count(), total=self.max_explore_steps if stop_after_expore else None):
            if not stabled:
                path = self.sample_path()
                time = self.network_call(path)

                for i in range(1, len(path)):
                    self.update_edge_posterior(path[i-1], path[i], time[i-1])
                self.sample_edges_params()
                
                if prev_path == path:
                    stable_steps += 1
                else:
                    stable_steps = 0

                prev_path = path

                stabled = (step >= self.last_stable_steps and 
                           (step >= self.max_explore_steps or stable_steps >= self.last_stable_steps))
            else:
                if min_expected_time is None:
                    min_expected_time, min_expected_path = self.expected_shortest_path()
                
                if stop_after_expore:
                    print(f'stopping after {step} step')
                    break

                self.network_call(min_expected_path)
            
        return min_expected_time, min_expected_path
                
                

            

                      
                
