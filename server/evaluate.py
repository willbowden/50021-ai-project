import torch.nn as nn
from torch.utils.data import DataLoader

from dataset import ModyDataset
from arguments import args
from classifier import Classifier


if __name__ == "__main__":

    # Initialize analyzer.
    classifier = Classifier(for_training=False, args=args)

    # Set citerion, which takes as input logits of positive class and computes binary cross-entropy.
    criterion = nn.BCEWithLogitsLoss()

    # Initialize validation set and loader.
    val_set = ModyDataset(
        maxlen=args.maxlen_val, tokenizer=classifier.tokenizer
    )
    val_loader = DataLoader(
        dataset=val_set, batch_size=args.batch_size, num_workers=args.num_threads
    )

    # Evaluate analyzer and get accuracy + loss.
    val_accuracy, val_loss = classifier.evaluate(
        val_loader=val_loader, criterion=criterion
    )

    # Display accuracy and loss.
    print(f"Validation Accuracy : {val_accuracy}, Validation Loss : {val_loss}")