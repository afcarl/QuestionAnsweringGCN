from example_batcher.batch import Batch


class ExampleBatcher:
    """
    Divides examples into batches for training
    """

    batch_size = None
    current_batch = None

    def __init__(self, batch_size):
        self.current_batch = Batch()
        self.batch_size = batch_size

    def put_example(self, example):
        self.current_batch.examples.append(example)

        if self.current_batch.count_examples() == self.batch_size:
            return self.get_batch()
        else:
            return None

    def get_batch(self):
        batch_to_return = self.current_batch
        self.current_batch = Batch()
        return batch_to_return
