from indexing.abstract_index import AbstractIndex
import numpy as np


class LimitedFreebaseRelationIndex(AbstractIndex):

    additional_vector_count = 100
    cutoff = 20

    def __init__(self, index_cache_name, dimension):
        AbstractIndex.__init__(self, index_cache_name, dimension)
        self.index("<dummy_to_mention>")
        self.index("<dummy_to_word>")
        self.index("<word_to_word>")

        self.load_file()

    def get_file_string(self):
        return "data/webquestions/filtered_edge_count.txt"

    def load_file(self):
        file_string = self.get_file_string()

        for line in open(file_string, encoding="utf8"):
            parts = line.strip().split("\t")

            if int(parts[1]) > self.cutoff:
                self.index(parts[0])

        self.vector_count = (self.additional_vector_count + self.element_counter) * 2
        self.inverse_edge_delimiter = self.additional_vector_count + self.element_counter

        self.freeze()