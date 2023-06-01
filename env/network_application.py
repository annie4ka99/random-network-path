import argparse
from flask import Flask, request, jsonify
import os
import logging

from env.network import StohasticNetwork
from utils.input import parse_input


def setup_logger(name, log_file, formatter, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def run_application(input_file, log_file="logs/env.log", random_state = 0, 
                    host="0.0.0.0", port=8080):
    if not os.path.exists(input_file):
        raise OSError(f"input file: {input_file} doesn't exist")
    n, start_node, finish_node, edges_params = parse_input(input_file)
    
    with open(log_file, 'w'): pass

    logger = setup_logger('paths_logger', log_file, logging.Formatter('%(asctime)s %(message)s'))

    network = StohasticNetwork(n, start_node, finish_node, edges_params, random_state)

    app = Flask(__name__)
    app.logger.info('network built succefully!')

    @app.route("/get-graph", methods=['GET', 'POST'])
    def get_graph():
        return jsonify({"graph": network.get_graph()})
    
    @app.route("/send-signal", methods=['GET', 'POST'])
    def send_signal():
        path = request.json['path']
        app.logger.info(f"{path} requested")
        
        result = network(path)
        if result is None:
            app.logger.info("incorrect path!")
            return f"incorrect path", 400

        logger.info(f"requested path:{path} ; total time:{sum(result):.2f} ; time:{[round(t, 2) for t in result]}\n")

        return jsonify({"total": sum(result), "result": result})
    
    
    app.run(debug=True, host=host, port=port)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='input/input.txt', help='path to file with network parameters')
    parser.add_argument('--log', type=str, default='logs/env.log', help='path to environment logs')
    parser.add_argument('--seed', type=int, default=0, help='random state')
    parser.add_argument('--host', type=str, default="0.0.0.0", help='host to run application')
    parser.add_argument('--port', type=int, default=8080, help='port to run application')

    opt = parser.parse_args()
    run_application(opt.input, opt.log, opt.seed, opt.host, opt.port)