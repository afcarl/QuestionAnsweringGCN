import argparse
import json
import sys
from KnowledgeBaseInterface.FreebaseInterface import FreebaseInterface
import numpy as np


class CandidateNeighborhoodGenerator:

    freebase_interface = None
    neighborhood_search_scope = None
    max_candidates = None

    def __init__(self, freebase_interface, neighborhood_search_scope=1, max_candidates=10000):
        self.freebase_interface = freebase_interface
        self.neighborhood_search_scope = neighborhood_search_scope
        self.max_candidates = max_candidates

    def parse_json_line(self, json_line):
        freebase_entities = np.array([self.parse_json_entity(entity) for entity in json_line['entities']])
        candidates = self.freebase_interface.get_neighborhood([freebase_entities], edge_limit=self.max_candidates, hops=self.neighborhood_search_scope)
        return candidates

    def parse_json_entity(self, entity):
        freebase_id = entity["entity"]
        return freebase_id



def parse_from_file(filename):
    fb = FreebaseInterface()
    gen = CandidateNeighborhoodGenerator(fb)
    with open(filename) as data_file:
        for line in (data_file):
            json_line = json.loads(line)
            print(gen.parse_json_line(json_line))
            exit()


def parse_from_console():
    fb = FreebaseInterface()
    gen = CandidateNeighborhoodGenerator(fb)
    for line in sys.stdin:
        json_line = json.loads(line)
        print(gen.parse_json_line(json_line))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Yields candidate graphs to stdout.')
    parser.add_argument('--file', type=str, help='The location of the .json-file to be parsed')

    args = parser.parse_args()

    if args.file is not None:
        parse_from_file(args.file)
    else:
        parse_from_console()
