import numpy as np

from example_reader.graph_reader.database_interface.data_interface.FreebaseInterface import FreebaseInterface
from model_tester.evaluator.evaluation import Evaluation


class RelationPredictionFreebaseEntityEvaluator:

    evaluation = None

    def __init__(self, relation_index):
        self.relation_index = relation_index
        self.freebase_interface = FreebaseInterface()

    def begin_evaluation(self, steps=[0.5]):
        self.evaluations = [(step, Evaluation(default_method="micro")) for step in steps]

    def add_prediction(self, example):
        for step, evaluation in self.evaluations:
            self.add_predictions_to_step(example, step, evaluation)

    def add_predictions_to_step(self, example, step, evaluation):
        true_labels = example.get_gold_relation_vector()
        predicted_labels = example.prediction

        target = np.argmax(true_labels)
        pred_target = np.argmax(predicted_labels)

        print(example)
        print([gp.relation_mention for gp in example.gold_paths])
        print(self.relation_index.from_index(target))
        print(predicted_labels[target])
        print(self.relation_index.from_index(pred_target))
        print(predicted_labels[pred_target])

        pred_edge = self.relation_index.from_index(pred_target)

        for c in example.mentions:
            centroid = c.entity_label
            edge_parts = pred_edge.split("|")

            first_edge = edge_parts[0].strip()

            forward = True

            if first_edge.endswith(".1"):
                first_edge = first_edge[:-2]
            elif first_edge.endswith(".2"):
                first_edge = first_edge[:-2]
                forward = False
            elif first_edge.endswith(".inverse"):
                forward = False

            retrieved = self.freebase_interface.get_entities([centroid], first_edge, forward)
            print(retrieved)
            names = self.freebase_interface.get_names(retrieved)
            print(names)
            exit()

        print(pred_edge)

        target_edges = ["http://rdf.freebase.com/ns/" + gp.relation_mention + " | http://rdf.freebase.com/ns/" + gp.relation_gold for gp in example.gold_paths]

        if pred_edge not in target_edges:
            evaluation.total_false_positives += 1

        for target_edge in target_edges:
            if target_edge == pred_edge:
                evaluation.total_true_positives += 1
            else:
                evaluation.total_false_negatives += 1

        evaluation.n_samples += 1

    def compute_final_scores(self, evaluation):
        if np.sum(evaluation.total_true_positives) + np.sum(evaluation.total_false_positives) == 0:
            evaluation.micro_precision = 1.0
        else:
            evaluation.micro_precision = evaluation.total_true_positives / (
                evaluation.total_true_positives + evaluation.total_false_positives)

        evaluation.micro_recall = evaluation.total_true_positives / (
            evaluation.total_true_positives + evaluation.total_false_negatives)

        if evaluation.micro_precision + evaluation.micro_recall > 0:
            evaluation.micro_f1 = 2 * (evaluation.micro_precision * evaluation.micro_recall) / (
                evaluation.micro_precision + evaluation.micro_recall)
        else:
            evaluation.micro_f1 = 0.0

    def final_scores(self):
        for step, evaluation in self.evaluations:
            self.compute_final_scores(evaluation)

        return self.evaluations