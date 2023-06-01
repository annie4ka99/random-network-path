from dataclasses import dataclass


@dataclass
class EdgeParams:
    from_: int
    to_: int
    mu: int
    sigma: int


def parse_input(input_file):
    try:
        with open(input_file, 'r') as f:
            n, m = map(int, f.readline().strip().split())
            start_node, finish_node = map(int, f.readline().strip().split())
            edges_params = []
            for _ in range(m):
                from_, to_, mu, sigma = f.readline().split()
                edges_params.append(EdgeParams(int(from_), int(to_), float(mu), float(sigma)))
            return n, start_node, finish_node, edges_params
    except:
        raise IOError('Incorrect input file format')


