import tensorflow as tf

class TargetComparator:

    variable_prefix = None
    variables = None

    def __init__(self, variables, variable_prefix=""):
        self.variables = variables
        self.variable_prefix = variable_prefix
        if self.variable_prefix != "":
            self.variable_prefix += "_"

    def get_comparison_scores(self, all_target_embeddings, element_embeddings):
        target_embeddings = tf.nn.embedding_lookup(all_target_embeddings, self.variables.get_variable(self.variable_prefix + "target_indices"))
        comparison = tf.reduce_sum(target_embeddings * element_embeddings, axis=1)
        return comparison


    def prepare_tensorflow_variables(self, mode="train"):
        self.variables.add_variable(self.variable_prefix + "target_indices", tf.placeholder(tf.int32))

    def handle_variable_assignment(self, target_indices):
        self.variables.assign_variable(self.variable_prefix + "target_indices", target_indices)
