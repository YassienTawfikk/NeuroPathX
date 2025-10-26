import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import io
from .config import MODEL_PATH, IMAGE_SIZE, CLASS_LABELS


class BrainTumorPredictor:
    """
    A class to handle loading the Xception model and predicting tumor types
    from MRI images, mirroring the preprocessing steps used in the training notebook.
    """

    def __init__(self):
        """Initializes the predictor by loading the pre-trained Keras model."""
        try:
            # Load the model from the path specified in config.py
            self.model = load_model(MODEL_PATH)
            print(f"✅ Brain Tumor Xception Model loaded successfully from: {MODEL_PATH}")

        except Exception as e:
            # Handle the case where the model file is not found or corrupted
            print(f"❌ Error loading model from {MODEL_PATH}. Ensure the file is present.")
            raise FileNotFoundError(f"Model file not found or load failed: {e}")

    def _preprocess_image(self, img_path_or_bytes):
        """
        Loads and preprocesses an image: resize, convert to array, and scale (0-1).
        This mirrors the ImageDataGenerator's preprocessing: (img / 255.0).
        """
        target_size = (IMAGE_SIZE, IMAGE_SIZE)

        if isinstance(img_path_or_bytes, (str, bytes)):
            # Handle both file paths (str) and image bytes/file-like objects (e.g., for Flask)
            if isinstance(img_path_or_bytes, bytes):
                img_path_or_bytes = io.BytesIO(img_path_or_bytes)

            img = image.load_img(img_path_or_bytes,
                                 target_size=target_size,
                                 color_mode='rgb')
        else:
            # Assume it's already a loaded image object or file-like object
            img = image.load_img(img_path_or_bytes,
                                 target_size=target_size,
                                 color_mode='rgb')

        # Convert the image to a numpy array
        img_array = image.img_to_array(img)

        # Rescale the pixels to the [0, 1] range
        img_array = img_array / 255.0

        # Add a batch dimension (1, 299, 299, 3)
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def predict(self, img_path_or_bytes):
        """
        Predicts the tumor class for a given image.

        Args:
            img_path_or_bytes (str or bytes): Path to the image file or raw image bytes.

        Returns:
            dict: The predicted class label and the confidence scores for all classes.
        """
        # Preprocess the image
        processed_img = self._preprocess_image(img_path_or_bytes)

        # Make the prediction
        predictions = self.model.predict(processed_img, verbose=0)[0]

        # Get the index of the highest probability
        predicted_index = np.argmax(predictions)

        # Get the class label
        predicted_label = CLASS_LABELS[predicted_index]

        # Format results (e.g., for JSON API response)
        result = {
            "prediction": predicted_label,
            "confidence": float(predictions[predicted_index]),
            "probabilities": {
                label: float(prob) for label, prob in zip(CLASS_LABELS, predictions)
            }
        }

        return result

# Optional: Initialize the model on import (good for API optimization)
# try:
#     CLASSIFIER = BrainTumorPredictor()
# except FileNotFoundError:
#     CLASSIFIER = None