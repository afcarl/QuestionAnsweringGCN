"""
Tensorflow vs. e.g. oracle, train or no, that kind of stuff

May want to refactor name
"""
from experiment_construction.learner_construction.dummy_learner import DummyLearner
from experiment_construction.learner_construction.tensorflow_learner import TensorflowModel
from experiment_construction.learner_construction.validation_set_evaluator import ValidationSetEvaluator


class LearnerFactory:

    def __init__(self, evaluator_factory):
        self.evaluator_factory = evaluator_factory

    def construct_learner(self, preprocessor, candidate_generator, candidate_selector, example_processor, settings):
        learner = self.get_base_learner(candidate_selector, settings)
        learner.set_preprocessor(preprocessor)
        learner.set_candidate_generator(candidate_generator)
        learner.set_candidate_selector(candidate_selector)
        learner.set_example_processor(example_processor)

        if "early_stopping" in settings["training"] or "epochs_between_tests" in settings["training"]:
            evaluator = self.evaluator_factory.construct_evaluator(settings, "valid_file")
            learner = ValidationSetEvaluator(learner, evaluator)

        for k, v in settings["training"].items():
            learner.update_setting(k, v)

        return learner

    def get_base_learner(self, candidate_selector, settings):
        if candidate_selector.is_tensorflow:
            return TensorflowModel()
        else:
            return DummyLearner(settings["dataset"]["valid_file"], settings["endpoint"]["prefix"])