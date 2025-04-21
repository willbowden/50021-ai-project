# 50.021 Artificial Intelligence - Group Project

## Description

This project is a text sentiment classification model, using fine trained BERT-based models. It is intended to be used to flag tweets as offensive, and can be used either directly with the Python code, or via the Chrome extension under the `client` folder. 

Thanks to Github file size limits, our locally-trained model and the training dataset cannot be included in this repository. You can find the dataset [here](https://data.mendeley.com/datasets/9sxpkmm8xn/1)
and use it to train your own model by saving it as `./server/data/final_preprocessed_data_yidong_devansh.csv`.

## Getting Started

### Running a Server

To run the Flask server for sentiment classification using the Chrome extension, you'll need to have a [trained model](#training-a-model).
Once you have that, run the following command from the `server` directory:

```bash
python main.py --model_name_or_path <PATH_TO_YOUR_MODEL>
```

### Training a Model

To train a model on the Mody dataset, run the following command from the `server` directory:

```bash
python train.py --model_name_or_path <BASE_MODEL_NAME> --output_dir <YOUR_MODEL_NAME> 
```

> `<BASE_MODEL_NAME>` can be one of `bert-base-uncased, albert-base-v2, distilbert-base-uncased`

To see all available arguments, please see `./server/arguments.py`.

### Classifying Text

If you wish to classify a single piece of text for testing, run the following command from the `server` directory:

```bash
python classify.py --model_name_or_path <MODEL> --text "<TEST_TEXT>"
```

### Evaluating a Model

If you wish to re-evaluate a model, run the following command from the `server` directory:

```bash
python evaluate.py --model_name_or_path <MODEL>"
```