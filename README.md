# 50.021 Artificial Intelligence - Group Project

## Getting Started

### Running a Server

To run the Flask server for sentiment classification using the Chrome extension, you'll need to have a [trained model](#training-a-model).
Once you have that, run the following command:

```bash
python ./server/main.py --model_name_or_path <PATH_TO_YOUR_MODEL>
```

### Training a Model

To train a model on the Mody dataset, run the following command:

```bash
python ./server/train.py --model_name_or_path <BASE_MODEL_NAME> --output_dir <YOUR_MODEL_NAME> 
```

> `<BASE_MODEL_NAME>` can be one of `bert-base-uncased, albert-base-v2, distilbert-base-uncased`

To see all available arguments, please see `./server/arguments.py`.

### Classifying Text

If you wish to classify a single piece of text for testing, run the following command:

```bash
python ./server/classify.py --model_name_or_path <MODEL> --text "<TEST_TEXT>"
```

### Evaluating a Model

If you wish to re-evaluate a model, run the following command:

```bash
python ./server/evaluate.py --model_name_or_path <MODEL>"
```