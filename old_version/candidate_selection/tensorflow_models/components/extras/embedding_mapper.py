import tensorflow as tf

from candidate_selection.tensorflow_models.components.abstract_component import AbstractComponent


class EmbeddingMapper(AbstractComponent):

    variable_prefix = None
    variables = None

    def __init__(self, variables, variable_prefix=""):
        self.variables = variables
        self.variable_prefix = variable_prefix
        if self.variable_prefix != "":
            self.variable_prefix += "_"

    def get_map(self, direction="forward"):
        g_indices = self.variables.get_variable(self.variable_prefix + "to_indices" if direction == "forward" else "from_indices")
        s_indices = self.variables.get_variable(self.variable_prefix + "from_indices" if direction == "forward" else "to_indices")
        stg_values = tf.to_float(tf.ones_like(g_indices))

        g_size = self.variables.get_variable(self.variable_prefix + "to_size" if direction == "forward" else "from_size")
        s_size = self.variables.get_variable(self.variable_prefix + "from_size"  if direction == "forward" else "to_size")

        stg_indices = tf.to_int64(tf.transpose(tf.stack([g_indices, s_indices])))
        stg_shape = tf.to_int64([g_size, s_size])

        return tf.sparse_softmax(tf.SparseTensor(indices=stg_indices,
                                                       values=stg_values,
                                                       dense_shape=stg_shape))

    def apply_map(self, embedding, direction="forward"):
        return tf.sparse_tensor_dense_matmul(self.get_map(direction=direction), embedding)

    def prepare_tensorflow_variables(self, mode="train"):
        self.variables.add_variable(self.variable_prefix + "from_indices", tf.placeholder(tf.int32))
        self.variables.add_variable(self.variable_prefix + "to_indices", tf.placeholder(tf.int32))
        self.variables.add_variable(self.variable_prefix + "from_size", tf.placeholder(tf.int32))
        self.variables.add_variable(self.variable_prefix + "to_size", tf.placeholder(tf.int32))

    def handle_variable_assignment(self, from_indices, to_indices, from_size, to_size):
        self.variables.assign_variable(self.variable_prefix + "from_indices", from_indices)
        self.variables.assign_variable(self.variable_prefix + "to_indices", to_indices)
        self.variables.assign_variable(self.variable_prefix + "from_size", from_size)
        self.variables.assign_variable(self.variable_prefix + "to_size", to_size)
