#!/bin/bash
#SBATCH --job-name=tumor_classification_train
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --mem=64G
#SBATCH --cpus-per-task=24
#SBATCH --gres=gpu:1

# Ensure logs and checkpoints directories exist
mkdir -p logs checkpoints

# Load python module if environment requires it
# module load python

# Navigate to project root (parent of run/)
cd ..

# Run training
# Note: Adjust max_epochs as needed.
python scripts/training.py fit \
  --data.ndim=3 \
  --model.ndim=3 \
  --model.nb_classes=4 \
  --data.batch_size=32 \
  --data.num_workers=12 \
  --trainer.max_epochs=1000 \
  --trainer.accelerator=gpu
