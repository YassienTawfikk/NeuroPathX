import os

# --- Model Configuration ---
# The input size required by the Xception model (as used in the notebook)
IMAGE_SIZE = 299

# The filename of the trained model artifact
MODEL_FILENAME = "brain_tumor_xception_model.keras"

# Define the base directory for the package (current directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full path to the model file
MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)

# --- Classification Labels ---
# These class names must be in alphabetical order as they were derived from the
# Keras ImageDataGenerator's alphabetical indexing (glioma=0, meningioma=1, etc.)
CLASS_LABELS = ['glioma', 'meningioma', 'notumor', 'pituitary']
