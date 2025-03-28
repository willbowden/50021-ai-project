import pandas as pd
import re
import emoji
import json
import gensim.downloader as api
import nltk
from nltk.tokenize import word_tokenize
from itertools import product

nltk.download('punkt_tab')


print("Loading Word2Vec model...")
w2v_model = api.load("word2vec-google-news-300")

# def compact_contractions():
#     """
#         Clean and combine the contractions datasets taken from the Mody paper
#     """

#     # Load contractions, and trim spaces from keys/values
#     with open("../datasets/HSData/1_ContractionProfanitiesEnglish/Contractions", "r") as infile:
#         contractions = eval(infile.read())

#         contractions = {
#             key.strip(): [each_val.strip() for each_val in val.split("/")] for key, val in contractions.items()
#         }

#     # Load double contractions, and trim spaces from keys/values and separate the double contractions into a list
#     with open("../datasets/HSData/1_ContractionProfanitiesEnglish/DoubleContractions", "r") as infile:
#         double_contractions = eval(infile.read())
#         double_contractions = {
#             key.strip(): [each_val.strip() for each_val in val.split("/")] for key, val in double_contractions.items()
#         }

#     # Save our processed dictionary
#     with open("../datasets/OurData/contractions", "w+") as outfile:
#         contractions.update(double_contractions)
#         outfile.write(contractions.__str__())


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

    return text


def expand_contractions(text: str) -> list:
    contractions = get_contractions_dict()

    words = text.split()

    # Create a list of possible replacements for each word (allowing for double contractions)
    expanded_options = [contractions.get(word.lower(), [word]) for word in words]

    # Generate all possible sentence combinations
    expanded_sentences = [" ".join(sentence) for sentence in product(*expanded_options)]

    return expanded_sentences

def correct_grammar(original_text: str, expanded_texts: list) -> str:
    original_tokens = word_tokenize(original_text.lower())

    best_text = original_text
    min_distance = float('inf')

    for expanded_text in expanded_texts:
        expanded_tokens = word_tokenize(expanded_text.lower())
        distance = w2v_model.wmdistance(original_tokens, expanded_tokens)

        if distance < min_distance:  # Choose the sentence with the lowest WMD
            min_distance = distance
            best_text = expanded_text

    return best_text


def preprocess_sample(text: str) -> None:
    text = clean_text(text)
    sentences = expand_contractions(text)

    corrected = correct_grammar(text, sentences)

    return corrected


def test_preprocessing():
    raw = pd.read_csv("../datasets/HSData/0_RawData/data_huang_devansh.csv", nrows=2)

    print(preprocess_sample("lol that was hilarious! https://google.com/"))
    # print(preprocess_sample(raw["Content"][0]))


if __name__ == "__main__":
    test_preprocessing()
