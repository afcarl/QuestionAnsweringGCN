from experiment_construction.example_processor_construction.abstract_example_processor import AbstractExampleProcessor
import numpy as np


class PropagateScoresExampleProcessor(AbstractExampleProcessor):

    def process_example(self, example, mode="train"):
        scores = example["sentence_entity_map"][:, 3].astype(np.float32)
        if example["neighborhood"].centroids is None:
            centroids = [example["neighborhood"].to_index(c) for c in example["sentence_entity_map"][:, 2]]
            centroids = np.concatenate(centroids)
            example["neighborhood"].set_centroids(centroids)
        example["neighborhood"].propagate_scores(scores)

        return True