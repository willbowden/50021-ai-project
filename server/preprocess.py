import pandas as pd
import re
import emoji
import json
import gensim.downloader as api
from gensim.models import KeyedVectors
import os
import nltk
from nltk.tokenize import word_tokenize
from itertools import product
from transformers import AutoModelForMaskedLM, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForMaskedLM.from_pretrained("bert-base-uncased")

nltk.download('punkt_tab')


def get_contractions_dict():
    with open("../datasets/OurData/contractions", "r") as infile:
        contractions = eval(infile.read())

    return contractions


def clean_text(text: str) -> str:
    # Remove hyperlinks
    text = re.sub(r"http[s]?://\S+", "", text)

    # Remove user mentions (e.g., @username)
    text = re.sub(r"@\w+", "", text)

    # Remove emojis
    text = emoji.replace_emoji(text, replace="")

    # Remove emoticons
    emoticon_pattern = r"[:;=8xX][\'\-]?[)DpP/\\oO0*]"
    text = re.sub(emoticon_pattern, "", text)

    # Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text).strip()

    # Replace hyphens within words with spaces (e.g., new-age -> new age)
    text = re.sub(r'([a-zA-Z])\-([a-zA-Z])', r'\1 \2', text)

    # Remove special characters
    text = re.sub(r'[_`\"\-;%()|+&=*%.,!?:#$@[\]/]', '', text)

    return text


def score_sentence(sentence):
    """Scores a sentence using BERT."""
    inputs = tokenizer(sentence, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    # Calculate the mean logit score as a proxy for sentence quality
    logits = outputs.logits[0]
    sentence_score = logits.mean().item()
    return sentence_score


def expand_contractions(text):
    """Expands contractions based on context, also removes unneeded characters
        We remove special characters after expansion as contractions like "couldn't" need the apostrophe to be expanded
    """
    words = text.split()
    contractions = get_contractions_dict()
    
    # Create a list of possible replacements for each word (allowing for double contractions)
    expanded_options = [contractions.get(word.lower(), [word]) for word in words]

    # Generate all possible sentence combinations, removing apostrophes
    candidate_sentences = [re.sub(r'[\']', '', " ".join(sentence)) for sentence in product(*expanded_options)]

    return candidate_sentences

def select_best_expansion(candidate_sentences):
    # Score each candidate sentence
    scored_sentences = [(sent, score_sentence(sent)) for sent in candidate_sentences]

    # Select the best scoring sentence
    best_sentence = max(scored_sentences, key=lambda x: x[1])[0]
    return best_sentence


def preprocess_sample(text: str) -> None:
    text = clean_text(text)
    sentences = expand_contractions(text)
    corrected = select_best_expansion(sentences)

    return corrected


def test_preprocessing():
    raw = pd.read_csv("../datasets/HSData/0_RawData/data_huang_devansh.csv", nrows=2)
    print(raw["Content"][1])
    print(preprocess_sample(raw["Content"][1]))


if __name__ == "__main__":
    test_preprocessing()
