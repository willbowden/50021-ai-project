import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import trange
from sklearn.model_selection import train_test_split
import pandas as pd

from dataset import ModyDataset
from arguments import args
from classifier import Classifier

if __name__ == "__main__":
    # Initialize classifier.
    classifier = Classifier(for_training=True, args=args)

    # Set citerion, which takes as input logits of positive class and computes binary cross-entropy.
    criterion = nn.BCEWithLogitsLoss()

    # Set optimizer to Adam.
    optimizer = optim.Adam(params=classifier.model.parameters(), lr=args.lr)

    # Load entire dataframe once
    full_df = pd.read_csv("./data/final_preprocessed_data_yidong_devansh.csv", names=["sentence", "label"])

    # Split into 80% train, 20% validation
    train_df, val_df = train_test_split(full_df, test_size=0.2, random_state=42, stratify=full_df["label"])

    # Create datasets using the split dataframes
    train_set = ModyDataset(maxlen=args.maxlen_train, tokenizer=classifier.tokenizer, dataframe=train_df)
    val_set = ModyDataset(maxlen=args.maxlen_val, tokenizer=classifier.tokenizer, dataframe=val_df)

    # Initialize validation set and loader.
    train_loader = DataLoader(
        dataset=train_set, batch_size=args.batch_size, num_workers=args.num_threads
    )
    val_loader = DataLoader(
        dataset=val_set, batch_size=args.batch_size, num_workers=args.num_threads
    )

    # Initialize best accuracy.
    best_accuracy = 0
    # Go through epochs.
    for epoch in trange(args.num_eps, desc="Epoch"):
        # Train classifier for one epoch.
        classifier.train(
            train_loader=train_loader, optimizer=optimizer, criterion=criterion
        )
        # Evaluate classifier; get validation loss and accuracy.
        val_accuracy, val_loss = classifier.evaluate(
            val_loader=val_loader, criterion=criterion
        )
        # Display validation accuracy and loss.
        print(
            f"Epoch {epoch} complete! Validation Accuracy : {val_accuracy}, Validation Loss : {val_loss}"
        )
        # Save classifier if validation accuracy imporoved.
        if val_accuracy > best_accuracy:
            print(
                f"Best validation accuracy improved from {best_accuracy} to {val_accuracy}, saving classifier..."
            )
            best_accuracy = val_accuracy
            classifier.save()