from experiment_construction.experiment_runner_construction.experiment_runner import ExperimentRunner


class ExperimentRunnerFactory:

    def construct_experiment_runner(next, preprocessors, learner, settings):
        experiment_runner = ExperimentRunner()
        experiment_runner.learner = learner
        experiment_runner.set_train_file(settings["dataset"]["train_file"])
        return experiment_runner