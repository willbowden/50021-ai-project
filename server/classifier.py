from model import Model

from tqdm import tqdm
import torch.nn as nn
import torch
from transformers import (
    AutoTokenizer,
    AutoConfig
)

def get_accuracy_from_logits(logits, labels):
    # Convert logits to probabilties
    probabilties = torch.sigmoid(logits.unsqueeze(-1))
    # Convert probabilities to predictions (1: positive, 0: negative)
    predictions = (probabilties > 0.5).long().squeeze()
    # Calculate qnd return accuracy
    return (predictions == labels).float().mean()

class Classifier:
    def __init__(self, for_training, args):    
        self.config = AutoConfig.from_pretrained(args.model_name_or_path)

        self.model = Model.from_pretrained(args.model_name_or_path)

        # Set up device as GPU if available, otherwise CPU.
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # Put model to device.
        self.model = self.model.to(self.device)

        # Set model to evaluation mode.
        self.model.eval()

        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)

        # Set output directory.
        self.output_dir = args.output_dir
    
    # Evaluates analyzer.
    def evaluate(self, val_loader, criterion):
        self.model.eval()

        batch_accuracy_summation, loss, num_batches = 0, 0, 0

        with torch.no_grad():
            # Go through validation set in batches.
            for input_ids, attention_mask, labels in tqdm(
                val_loader, desc="Evaluating"
            ):
                # Put input IDs, attention mask, and labels to device.
                input_ids, attention_mask, labels = (
                    input_ids.to(self.device),
                    attention_mask.to(self.device),
                    labels.to(self.device),
                )

                logits = self.model(input_ids=input_ids, attention_mask=attention_mask)

                batch_accuracy_summation += get_accuracy_from_logits(logits, labels)

                loss += criterion(logits.squeeze(-1), labels.float()).item()

                num_batches += 1
        # Calculate accuracy.
        accuracy = batch_accuracy_summation / num_batches

        return accuracy.item(), loss

    # Trains analyzer for one epoch.
    def train(self, train_loader, optimizer, criterion):
        self.model.train()

        for input_ids, attention_mask, labels in tqdm(
            iterable=train_loader, desc="Training"
        ):

            optimizer.zero_grad()

            input_ids, attention_mask, labels = (
                input_ids.to(self.device),
                attention_mask.to(self.device),
                labels.to(self.device),
            )

            logits = self.model(input_ids=input_ids, attention_mask=attention_mask)

            loss = criterion(input=logits.squeeze(-1), target=labels.float())

            loss.backward()

            optimizer.step()

    # Saves analyzer.
    def save(self):
        self.model.save_pretrained(save_directory=f"models/{self.output_dir}/")

        self.config.save_pretrained(save_directory=f"models/{self.output_dir}/")

        self.tokenizer.save_pretrained(save_directory=f"models/{self.output_dir}/")

    # Classifies sentiment as positve or negative.
    def classify_sentiment(self, text):
        # Don't track gradient.
        with torch.no_grad():
            tokens = ["[CLS]"] + self.tokenizer.tokenize(text) + ["[SEP]"]
            
            input_ids = (
                torch.tensor(self.tokenizer.convert_tokens_to_ids(tokens))
                .unsqueeze(0)
                .to(self.device)
            )

            attention_mask = (input_ids != 0).long()

            logit = self.model(
                input_ids=input_ids, attention_mask=attention_mask
            )
            
            positive_probability = torch.sigmoid(logit.unsqueeze(-1)).item()
            
            positive_percentage = positive_probability * 100
            
            is_positive = positive_probability > 0.5
            
            if is_positive:
                return "Positive", int(positive_percentage)
            else:
                return "Negative", int(100 - positive_percentage)