from evaluation.python_evaluator import Evaluator
from helpers.read_conll_files import ConllReader
from helpers.static import Static


class ValidationSetEvaluator:

    inner = None

    epochs_between_tests = None
    max_epochs = None
    early_stopping = None

    def __init__(self, inner, evaluator):
        self.inner = inner
        self.evaluator = evaluator

    def initialize(self):
        self.inner.initialize()

    def update_setting(self, setting_string, value):
        if setting_string == "max_epochs":
            self.max_epochs = int(value)
        elif setting_string == "epochs_between_tests":
            self.epochs_between_tests = int(value)
        elif setting_string == "early_stopping":
            self.early_stopping = True if value == "True" else False

        self.inner.update_setting(setting_string, value)

    def predict(self, iterator):
        return self.inner.predict(iterator)

    def train_and_validate(self, train_file_iterator, validation_file_iterator):
        epoch = 0
        best_performance = -1
        best_epoch = 0
        Static.logger.write("Beginning training with max_epochs="+str(self.max_epochs)+ (", not" if not self.early_stopping else ",") + " using early stopping.", area="training", subject="validation_messages")
        while epoch < self.max_epochs:
            self.inner.train(train_file_iterator, start_epoch=epoch, epochs=self.epochs_between_tests)
            epoch += self.epochs_between_tests

            prediction = self.inner.predict(validation_file_iterator)
            evaluation = self.evaluator.evaluate(prediction)
            performance = evaluation.macro_f1

            Static.logger.write(evaluation.summarize(), "training", "validation_loss")

            if performance > best_performance:
                best_performance = performance
                best_epoch = epoch
            elif self.early_stopping:
                Static.logger.write("Stopping early.", "training", "validation_messages")
                break

        Static.logger.write("Best epoch was "+str(best_epoch)+" with performance "+str(best_performance), "training", "validation_messages")
        return best_epoch, best_performance

