from example_reader.graph_reader.graph import Graph
import numpy as np

class GraphConverter:

    hypergraph_interface = None

    def __init__(self, hypergraph_interface):
        self.hypergraph_interface = hypergraph_interface

    def get_neighborhood_graph(self, entities):
        hypergraph = self.hypergraph_interface.get_neighborhood_graph(entities)

        graph = Graph()
        graph.vertices = np.concatenate((hypergraph.entity_vertices, hypergraph.event_vertices))
        graph.edges = np.concatenate((hypergraph.entity_to_entity_edges,
                                      hypergraph.event_to_entity_edges,
                                     hypergraph.entity_to_event_edges))

        return graph