import numpy as np

from input_models.abstract_preprocessor import AbstractPreprocessor
from input_models.hypergraph.hypergraph_input_model import HypergraphInputModel


class HypergraphPreprocessor(AbstractPreprocessor):

    entity_indexer = None
    relation_indexer = None
    in_batch_indices = None
    in_batch_labels = None

    graph_counter = None

    def __init__(self, entity_indexer, relation_indexer, input_string, output_string, next_preprocessor, clean_dictionary=True):
        AbstractPreprocessor.__init__(self, next_preprocessor)
        self.entity_indexer = entity_indexer
        self.relation_indexer = relation_indexer
        self.in_batch_indices = {}
        self.in_batch_labels = {}
        self.graph_counter = 0

        self.input_string = input_string
        self.output_string = output_string
        self.clean_dictionary = clean_dictionary

    def process(self, batch_dictionary, mode="train"):
        #print("preprocessing...")
        if self.next_preprocessor is not None:
            self.next_preprocessor.process(batch_dictionary, mode=mode)

        hypergraph_batch = batch_dictionary[self.input_string]

        self.in_batch_indices = {}
        self.in_batch_labels = {}
        self.graph_counter = 0
        vertex_list_slices = np.empty((len(hypergraph_batch),2), dtype=np.int32)

        event_to_entity_edges = np.empty((0,2), dtype=np.int32)
        entity_to_event_edges = np.empty((0,2), dtype=np.int32)
        entity_to_entity_edges = np.empty((0,2), dtype=np.int32)
        event_to_entity_types = np.empty((0,), dtype=np.int32)
        entity_to_event_types = np.empty((0,), dtype=np.int32)
        entity_to_entity_types = np.empty((0,), dtype=np.int32)

        entity_map = np.empty(0, dtype=np.int32)
        entity_scores = np.empty(0, dtype=np.float32)
        event_scores = np.empty(0, dtype=np.float32)
        centroid_scores = np.empty(0, dtype=np.float32)

        event_start_index = 0
        entity_start_index = 0

        vertex_batch_map = [None] * len(hypergraph_batch)
        en_to_en_batch_map = [None] * len(hypergraph_batch)
        en_to_ev_batch_map = [None] * len(hypergraph_batch)
        ev_to_en_batch_map = [None] * len(hypergraph_batch)

        max_elements_in_en_to_ev_relation_bag = max([hypergraph.entity_to_event_relation_bags.shape[1] for hypergraph in hypergraph_batch])
        max_elements_in_ev_to_en_relation_bag = max([hypergraph.event_to_entity_relation_bags.shape[1] for hypergraph in hypergraph_batch])
        max_elements_in_en_to_en_relation_bag = max([hypergraph.entity_to_entity_relation_bags.shape[1] for hypergraph in hypergraph_batch])

        event_to_entity_bags = np.empty((0,max_elements_in_ev_to_en_relation_bag), dtype=np.int32)
        entity_to_event_bags = np.empty((0,max_elements_in_en_to_ev_relation_bag), dtype=np.int32)
        entity_to_entity_bags = np.empty((0,max_elements_in_en_to_en_relation_bag), dtype=np.int32)

        for i,hypergraph in enumerate(hypergraph_batch):
            #print("Element started")
            phg = self.preprocess_single_hypergraph(hypergraph, event_start_index, entity_start_index)
            vertex_list_slices[i][0] = phg[0]
            vertex_list_slices[i][1] = phg[1]

            event_start_index += phg[0]
            entity_start_index += phg[1]

            if phg[2].shape[0] > 0:
                event_to_entity_edges = np.concatenate((event_to_entity_edges, phg[2]))
                event_to_entity_types = np.concatenate((event_to_entity_types, phg[3]))
                padding_needed = max_elements_in_ev_to_en_relation_bag - hypergraph.event_to_entity_relation_bags.shape[1]
                padded_event_to_entity_bags = np.pad(hypergraph.event_to_entity_relation_bags, ((0,0), (0,padding_needed)), mode='constant')
                event_to_entity_bags = np.concatenate((event_to_entity_bags, padded_event_to_entity_bags))


            if phg[4].shape[0] > 0:
                entity_to_event_edges = np.concatenate((entity_to_event_edges, phg[4]))
                entity_to_event_types = np.concatenate((entity_to_event_types, phg[5]))
                padding_needed = max_elements_in_en_to_ev_relation_bag - hypergraph.entity_to_event_relation_bags.shape[1]
                padded_entity_to_event_bags = np.pad(hypergraph.entity_to_event_relation_bags, ((0,0), (0,padding_needed)), mode='constant')
                entity_to_event_bags = np.concatenate((entity_to_event_bags, padded_entity_to_event_bags))

            if phg[6].shape[0] > 0:
                entity_to_entity_edges = np.concatenate((entity_to_entity_edges, phg[6]))
                entity_to_entity_types = np.concatenate((entity_to_entity_types, phg[7]))
                padding_needed = max_elements_in_en_to_en_relation_bag - hypergraph.entity_to_entity_relation_bags.shape[1]
                padded_entity_to_entity_bags = np.pad(hypergraph.entity_to_entity_relation_bags, ((0,0), (0,padding_needed)), mode='constant')
                entity_to_entity_bags = np.concatenate((entity_to_entity_bags, padded_entity_to_entity_bags))

            entity_map = np.concatenate((entity_map, phg[8]))
            entity_scores = np.concatenate((entity_scores, hypergraph.vertex_scores))
            event_scores = np.concatenate((entity_scores, hypergraph.event_scores))
            centroid_scores = np.concatenate((centroid_scores, hypergraph.centroid_scores))

            vertex_batch_map[i] = np.ones(phg[1], dtype=np.int32)*i
            en_to_en_batch_map[i] = np.ones(phg[6].shape[0], dtype=np.int32)*i
            en_to_ev_batch_map[i] = np.ones(phg[4].shape[0], dtype=np.int32)*i
            ev_to_en_batch_map[i] = np.ones(phg[2].shape[0], dtype=np.int32)*i

        entity_vertex_slices = vertex_list_slices[:,1]
        #print("Getting vertex lookup matrix")
        entity_vertex_matrix = self.get_padded_vertex_lookup_matrix(entity_vertex_slices, hypergraph_batch)

        #print(entity_vertex_slices)
        #print(np.max(entity_map))

        n_entities = np.max(entity_vertex_matrix) if entity_vertex_matrix.shape[1] > 0 else 0
        n_events = np.sum(vertex_list_slices[:,0])

        input_model = HypergraphInputModel()
        input_model.entity_vertex_matrix = entity_vertex_matrix
        input_model.entity_vertex_slices = entity_vertex_slices
        input_model.entity_map = entity_map
        input_model.event_to_entity_edges = event_to_entity_edges
        input_model.event_to_entity_types = event_to_entity_types
        input_model.entity_to_event_edges = entity_to_event_edges
        input_model.entity_to_event_types = entity_to_event_types
        input_model.entity_to_entity_edges = entity_to_entity_edges
        input_model.entity_to_entity_types = entity_to_entity_types
        input_model.n_events = n_events
        input_model.n_entities = n_entities
        input_model.entity_scores = entity_scores
        input_model.event_scores = event_scores
        input_model.centroid_scores = centroid_scores

        input_model.entity_to_event_bags = entity_to_event_bags
        input_model.event_to_entity_bags = event_to_entity_bags
        input_model.entity_to_entity_bags = entity_to_entity_bags

        input_model.vertex_to_batch_map = np.concatenate(vertex_batch_map)
        input_model.en_to_ev_to_batch_map = np.concatenate(en_to_ev_batch_map)
        input_model.ev_to_en_to_batch_map = np.concatenate(ev_to_en_batch_map)
        input_model.en_to_en_to_batch_map = np.concatenate(en_to_en_batch_map)

        input_model.in_batch_indices = self.in_batch_indices

        batch_dictionary[self.output_string] = input_model

    def get_padded_vertex_lookup_matrix(self, entity_vertex_slices, hypergraph_batch):
        max_vertices = np.max(entity_vertex_slices)
        vertex_matrix = np.zeros((len(hypergraph_batch), max_vertices), dtype=np.int32)
        count = 0
        for i, n in enumerate(entity_vertex_slices):
            vertex_matrix[i][:n] = np.arange(n) + 1 + count
            count += n
        return vertex_matrix

    def retrieve_entity_indexes_in_batch(self, graph_index, entity_label):
        return self.in_batch_indices[graph_index][entity_label]

    def retrieve_entity_labels_in_batch(self, graph_index, entity_index):
        return self.in_batch_labels[graph_index][entity_index]

    def preprocess_single_hypergraph(self, hypergraph, event_start_index, entity_start_index):
        #print("Preprocessing hgraph")
        event_vertices = hypergraph.get_vertices(type="events")
        entity_vertices = hypergraph.get_vertices(type="entities") #, ignore_names=True)
        #print(event_vertices)
        #print(entity_vertices)

        vertex_map = entity_vertices
        #print(np.max(vertex_map))

        #print(self.graph_counter)
        #print(entity_vertices[:3])

        self.in_batch_labels[self.graph_counter] = {v:k for v, k in enumerate(entity_vertices)}
        self.in_batch_indices[self.graph_counter] = {k:v+entity_start_index for v, k in enumerate(entity_vertices)}

        n_event_vertices = event_vertices.shape[0]
        n_entity_vertices = entity_vertices.shape[0]

        event_to_entity_edges = hypergraph.get_edges(sources="events", targets="entities")
        event_to_entity_types = event_to_entity_edges[:,1]
        entity_to_event_edges = hypergraph.get_edges(sources="entities", targets="events")
        entity_to_event_types = entity_to_event_edges[:,1]
        entity_to_entity_edges = hypergraph.get_edges(sources="entities", targets="entities", ignore_names=True)
        entity_to_entity_types = entity_to_entity_edges[:,1]

        ev_to_en_2 = np.empty((event_to_entity_edges.shape[0], 2))
        ev_to_en_2[:,0] = event_to_entity_edges[:,0] + event_start_index
        ev_to_en_2[:,1] = event_to_entity_edges[:,2] + entity_start_index

        en_to_ev_2 = np.empty((entity_to_event_edges.shape[0], 2))
        en_to_ev_2[:,0] = entity_to_event_edges[:,0] + entity_start_index
        en_to_ev_2[:,1] = entity_to_event_edges[:,2] + event_start_index

        en_to_en_2 = np.empty((entity_to_entity_edges.shape[0], 2))
        en_to_en_2[:,0] = entity_to_entity_edges[:,0] + entity_start_index
        en_to_en_2[:,1] = entity_to_entity_edges[:,2] + entity_start_index

        self.graph_counter += 1

        return n_event_vertices, \
               n_entity_vertices, \
               ev_to_en_2, \
               event_to_entity_types, \
               en_to_ev_2, \
               entity_to_event_types, \
               en_to_en_2, \
               entity_to_entity_types, \
               vertex_map
