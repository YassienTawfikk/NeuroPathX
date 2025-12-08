import tensorflow as tf
from .models import get_model

class Trainer:
    def __init__(self, model, train_gen, val_gen, config):
        self.model = model
        self.train_gen = train_gen
        self.val_gen = val_gen
        self.config = config

    def fit(self):
        """
        Runs the model training.
        """
        callbacks = [
            tf.keras.callbacks.ModelCheckpoint(
                filepath=self.config.get('ckpt_path', 'checkpoints/model.keras'),
                save_best_only=True,
                monitor='val_loss'
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            )
        ]

        history = self.model.fit(
            self.train_gen,
            validation_data=self.val_gen,
            epochs=self.config.get('max_epochs', 10),
            callbacks=callbacks,
            verbose=1
        )
        return history
