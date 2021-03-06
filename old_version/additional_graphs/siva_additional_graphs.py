from model.hypergraph import Hypergraph
import numpy as np
import sys

from model.hypergraph_model import HypergraphModel


class Predicate:

    head = None
    params = []

    def __str__(self):
        return self.head + "(" + ", ".join(self.params) + ")"

class SivaAdditionalGraphs:

    def to_predicate(self, string):
        if string.endswith(")"):
            string = string[:-1]

        br = string.index("(")

        predicate = Predicate()
        predicate.head = string[:br]
        predicate.params = [p.strip() for p in string[br+1:].split(", ")]

        return predicate

    def produce_additional_graphs(self):
        #print("starting...")
        target_sentence = next(sys.stdin)
        #for line, mapping in zip(sys.stdin, self.json_iterator_for_mapping):
        for line in sys.stdin:
            graph_string = next(sys.stdin)
            hypergraphs = []
            #print("reading siva graphs")
            while not " [main] DEBUG: " in graph_string and not graph_string.strip() == "END":
                s_index = graph_string.index("[")
                graph_string = graph_string[s_index+1:-2]

                if len(graph_string) == 0:
                    graph_string = next(sys.stdin)
                    continue

                graph_parts = graph_string.split("), ")
                graph_preds = [self.to_predicate(gp) for gp in graph_parts]
                
                hypergraph = HypergraphModel()
                for graph_pred in graph_preds:
                    for v in np.unique(graph_pred.params):
                        hypergraph.add_vertices(np.array([v]), type="events" if v[-1] == "e" else "entities")
                        hypergraph.populate_discovered(type="entities")
                        hypergraph.populate_discovered(type="events")

                    if len(graph_pred.params) == 1:
                        hypergraph.add_vertices(np.array([graph_pred.head]), type="entities")
                        hypergraph.populate_discovered(type="entities")
                        hypergraph.append_edges(np.array([[graph_pred.head, graph_pred.head, graph_pred.params[0]]]),
                                             sources="entities",
                                             targets="events" if graph_pred.params[0][-1] == "e" else "entities")
                    elif len(graph_pred.params) != 2:
                        print("HOLY FUCKING SHIT")
                        print(str(graph_pred))
                        exit()
                    else:
                        if not (graph_pred.params[0][-1] == "e" and graph_pred.params[1][-1] == "e"):
                            hypergraph.append_edges(np.array([[graph_pred.params[0], graph_pred.head, graph_pred.params[1]]]),
                                                 sources="events" if graph_pred.params[0][-1] == "e" else "entities",
                                                 targets="events" if graph_pred.params[1][-1] == "e" else "entities")

                graph_string = next(sys.stdin)
                hypergraphs.append(hypergraph)

            # TODO: Chooses last hypergraph completely randomly
            done = False
            chosen_hypergraph = None
            for hypergraph in hypergraphs:
                for vertex in hypergraph.get_vertices(type="entities"):
                    if "-blank-" in vertex:
                        chosen_hypergraph = hypergraph
                        target_entity = vertex
                        done = True
                        break
                if done:
                    break

            print(target_sentence)

            if chosen_hypergraph is None:
                yield None
                continue

            mapping = {}
            for vertex in chosen_hypergraph.get_vertices(type="entities"):
                # Ensure the vertex is an entitity and not the literal "m." (occurs once in training data)
                if ":m." in vertex and not vertex.endswith("m."):
                    mapping[vertex] = "http://rdf.freebase.com/ns/" + vertex[vertex.index(":m.")+1:]
                elif "-blank-" in vertex:
                    target_entity = vertex

            print(chosen_hypergraph.get_vertices(type="entities"))
            target_sentence = graph_string
            #print("yield")

            yield chosen_hypergraph, mapping, target_entity
