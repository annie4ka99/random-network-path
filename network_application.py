import argparse
from flask import Flask, request, jsonify
from network import EdgeParams, RandomNetwork
import os
import logging


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


def run_application(input_file, log_file="env.log", random_state = 0, 
                    host="0.0.0.0", port=8080):
    if not os.path.exists(input_file):
        raise OSError(f"input file: {input_file} doesn't exist")
    n, start_node, finish_node, edges_params = parse_input(input_file)

    logging.basicConfig(filename=log_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

    
    network = RandomNetwork(n, start_node, finish_node, edges_params, random_state)
    print('network built succefully!')

    app = Flask(__name__)
    
    @app.route("/send-signal", methods=['GET', 'POST'])
    def send_signal():
        path = request.args.getlist('node', type=int)
        app.logger.info(f"{path} requested")
        
        result = network(path)
        if result is None:
            app.logger.info("incorrect path!")
            return f"incorrect path", 400

        app.logger.info(f"path time:{result}, total time:{sum(result)}\n")

        return jsonify({"total": sum(result), "result": result})
    
    
    app.run(debug=True, host=host, port=port)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='path to file with network parameters')
    parser.add_argument('--log', type=str, default='env.log', help='path to environment logs')
    parser.add_argument('--seed', type=int, default=0, help='random state')
    parser.add_argument('--host', type=str, default="0.0.0.0", help='host to run application')
    parser.add_argument('--port', type=int, default=8080, help='port to run application')

    opt = parser.parse_args()
    run_application(opt.input, opt.log, opt.seed, opt.host, opt.port)