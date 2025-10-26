# --- Model Configuration ---

# Image size used during training (299x299 for Xception)
IMAGE_SIZE = 299

# Path to the saved model file
MODEL_FILENAME = "brain_tumor_xception_model.keras"
MODEL_PATH = MODEL_FILENAME  # Relative to the classify-model directory

# Class labels in the order determined by the Keras generator during training.
# The notebook output (Found X validated image filenames belonging to 4 classes) 
# implies the generator sorted them alphabetically.
CLASS_LABELS = ["glioma", "meningioma", "notumor", "pituitary"]
