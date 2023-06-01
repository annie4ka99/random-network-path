import argparse
import requests

from agent.path_solver import PathSolver
from utils.graph import Graph

def run_application(network_host, network_port, 
                    alpha, beta, nu, mu, 
                    max_explore_steps, last_stable_steps, stop_after_explore,
                    seed, log_file='logs/agent.log'):
    def path_request(path:list[int]) -> list[float]:
        url = f"http://{network_host}:{network_port}/send-signal"
        r = requests.post(url, json={"path": path})
        if r.ok:
            r = r.json()
            total_time_hist.append(r['total'])
            return r['result']
        raise RuntimeError(f"couldn't process request to {url}")
    
    url = f"http://{network_host}:{network_port}/get-graph"
    ans = requests.post(url)
    total_time_hist = []
    if ans.ok:
        graph = Graph(**ans.json()['graph'])
        for v in range(graph.n):
            graph.edges[v] = dict(((int(u_str), None) for u_str in graph.edges[v]))
        
        path_solver = PathSolver(graph, path_request, 
                                 alpha, beta, mu, nu, 
                                 max_explore_steps, last_stable_steps, 
                                 random_state=seed)
        path_solver.solve_path(stop_after_expore=stop_after_explore)
        with open(log_file, 'w') as f:
            for t in total_time_hist: f.write(f'{t}\n')
    else:
        raise RuntimeError(f"couldn't process request to {url}")
    
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--network-host', type=str, default="0.0.0.0", help='host to send path requests')
    parser.add_argument('--network-port', type=int, default=8080, help='port to send path requests')

    parser.add_argument('--alpha', type=float, default=2.0, help='alpha for prior on sigma ~ InvGa(alpha, beta)')
    parser.add_argument('--beta', type=float, default=1.0, help='beta for prior on sigma ~ InvGa(alpha, beta)')
    parser.add_argument('--mu', type=float, default=0.0, help='mu for prior on mean ~ Norm(mu, sigma/nu)')
    parser.add_argument('--nu', type=float, default=1.0, help='nu for prior on mean ~ Norm(mu, sigma/nu)')

    parser.add_argument('--max-explore-steps', type=int, default=10000, help='maximum steps to explore')
    parser.add_argument('--stable-steps', type=int, default=500, 
                        help='number of stable steps(when path is not changing) to stop exploring')
    parser.add_argument('--stop-after-explore', type=bool, default=True, help="if to stop agent after exploring")

    parser.add_argument('--seed', type=int, default=0, help='random state')
    parser.add_argument('--log', type=str, default='logs/agent.log', help='path to requested paths total time')

    opt = parser.parse_args()
    run_application(opt.network_host, opt.network_port, 
                    opt.alpha, opt.beta, opt.nu, opt.mu, 
                    opt.max_explore_steps, opt.stable_steps, opt.stop_after_explore,
                    opt.seed, opt.log)