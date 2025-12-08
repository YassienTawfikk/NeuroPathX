import sys
import os

# Add root directory to path to allow importing tumor_classification
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tumor_classification import get_model, get_data_generators, Trainer
from tumor_classification.utils import parse_args

def main():
    args = parse_args()

    if args.command == "fit":
        print(f"Starting training with config: {vars(args)}")

        # Path to the dataset
        # Assuming data is in 'data/classification_samples' relative to project root
        data_dir = os.path.join(os.path.dirname(__file__), '../../data/classification_samples')
        
        if not os.path.exists(data_dir):
            print(f"Error: Data directory not found at {data_dir}")
            return

        # Initialize Data Generators
        train_gen, val_gen = get_data_generators(
            data_dir=data_dir,
            batch_size=args.data_batch_size,
            img_size=(299, 299) # Fixed for Xception
        )

        # Initialize Model
        model = get_model(
            num_classes=args.model_nb_classes
        )

        # Start Training
        config = {
            'max_epochs': args.trainer_max_epochs,
            'ckpt_path': args.ckpt_path
        }
        
        trainer = Trainer(model, train_gen, val_gen, config)
        history = trainer.fit()
        print("Training completed.")

if __name__ == "__main__":
    main()
