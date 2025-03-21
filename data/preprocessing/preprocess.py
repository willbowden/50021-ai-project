import pandas as pd


def preprocess_dataset_1():
    # Load dataset
    df = pd.read_csv(
        '../datasets/dataset_1.csv',
        names=[
            '',
            'count',
            'hate_speech',
            'offensive_language',
            'neither',
            'class',
            'tweet',
        ],
        index_col='',
        header=0,
    )

    # Remove irrelevant columns
    df = df.drop(
        ['count', 'hate_speech', 'offensive_language', 'neither'],
        axis='columns',
    )

    # Todo: Filter unwanted characters & words from tweet bodies.

    print(df.head)


def main():
    preprocess_dataset_1()


if __name__ == '__main__':
    main()
