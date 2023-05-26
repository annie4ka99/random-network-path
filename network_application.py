import argparse
from flask import Flask
from network import EdgeParams, RandomNetwork
import os

def parse_input(input_file):
    pass

def run_application(input_file, random_state):
    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='input.txt', help='path to file with network parameters')
    parser.add_argument('--seed', type=int, default=0, help='random state')

    opt = parser.parse_args()
    if not os.path.exists(opt.input):
        raise ValueError("input file doesn't exist")
    
    run_application(opt.input, opt.seed)