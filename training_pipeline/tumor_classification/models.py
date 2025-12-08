import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.applications import Xception
from tensorflow.keras.optimizers import Adamax
from tensorflow.keras.metrics import Precision, Recall

def get_model(input_shape=(299, 299, 3), num_classes=4, learning_rate=0.001):
    """
    Builds and compiles the Xception-based model for tumor classification.
    """
    # Load the Xception model, pre-trained on ImageNet
    base_model = Xception(
        include_top=False,
        weights='imagenet',
        input_shape=input_shape,
        pooling='max'
    )

    # Freeze the weights of the base model layers
    base_model.trainable = False

    # Build the Sequential model
    model = Sequential([
        base_model,
        Flatten(),
        Dropout(rate=0.3),
        Dense(128, activation='relu'),
        Dropout(rate=0.25),
        Dense(num_classes, activation='softmax')
    ])

    # Compile the model
    model.compile(
        optimizer=Adamax(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy', Precision(), Recall()]
    )
    
    return model
