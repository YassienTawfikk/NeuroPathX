import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def get_data_generators(data_dir, batch_size=32, img_size=(299, 299), validation_split=0.2, seed=42):
    """
    Creates and returns train, validation, and test generators.
    Assumes data_dir contains subdirectories for classes.
    """
    
    # Train Data Generator with Augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        brightness_range=(0.8, 1.2),
        validation_split=validation_split
    )

    # Test Data Generator (Rescale only)
    test_datagen = ImageDataGenerator(rescale=1./255, validation_split=validation_split)

    # Train Generator
    train_gen = train_datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='training',
        seed=seed
    )

    # Validation Generator
    val_gen = test_datagen.flow_from_directory(
        data_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation',
        seed=seed
    )

    # For testing, strictly speaking we might want a separate directory or split,
    # but based on the notebook structure using split, we'll use val_gen as proxy for evaluation 
    # or the user can provide a separate test dir. 
    # For this implementation, we return train/val.
    
    return train_gen, val_gen
