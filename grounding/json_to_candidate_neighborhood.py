import argparse
import json
import sys
from preprocessing.read_json_files import JsonReader
import numpy as np


class CandidateNeighborhoodGenerator:

    freebase_interface = None
    neighborhood_search_scope = None
    json_reader = None
    extra_literals = None

    def __init__(self, freebase_interface, json_reader, neighborhood_search_scope=1, extra_literals=False):
        self.freebase_interface = freebase_interface
        self.neighborhood_search_scope = neighborhood_search_scope
        self.json_reader = json_reader
        self.extra_literals = extra_literals

    def parse_file(self, filename):
        for sentence_entities in self.json_reader.parse_file(filename, output="entities"):
            neighborhood_hypergraph = self.freebase_interface.get_neighborhood_hypergraph(sentence_entities, hops=self.neighborhood_search_scope, extra_literals=self.extra_literals)
            yield neighborhood_hypergraph
