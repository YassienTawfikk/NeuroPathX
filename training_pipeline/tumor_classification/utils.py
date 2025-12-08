import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Tumor Classification CLI")
    parser.add_argument("command", choices=["fit"], help="Command to run (e.g., fit)")
    
    # Data args
    parser.add_argument("--data.ndim", type=int, default=3, dest="data_ndim")
    parser.add_argument("--data.batch_size", type=int, default=32, dest="data_batch_size")
    parser.add_argument("--data.num_workers", type=int, default=4, dest="data_num_workers")
    
    # Model args
    parser.add_argument("--model.ndim", type=int, default=3, dest="model_ndim")
    parser.add_argument("--model.nb_classes", type=int, default=4, dest="model_nb_classes")
    
    # Trainer args
    parser.add_argument("--trainer.max_epochs", type=int, default=10, dest="trainer_max_epochs")
    parser.add_argument("--trainer.accelerator", type=str, default="gpu", dest="trainer_accelerator")
    parser.add_argument("--ckpt_path", type=str, default="checkpoints/last.keras", dest="ckpt_path")

    # Allow partial parsing to ignore unknown args if needed, but strict is safer for now.
    return parser.parse_args()
