from arguments import args
from classifier import Classifier
from preprocessor import Preprocessor

if __name__ == "__main__":
    # Initialize classifier.
    classifier = Classifier(for_training=False, args=args)

    prep = Preprocessor()

    preprocessed_text = prep.preprocess_sample(args.text)

    result = classifier.classify_sentiment(preprocessed_text)

    if (result == 0):
        print(f"Model classified text as: 0: Normal")
    elif (result == 1):
        print(f"Model classified text as: 1: Offensive")

        

