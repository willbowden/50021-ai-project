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

## Our Results

### `bert-base-uncased`

Fine-tuning normal BERT on our data for 3 epochs with a learning rate of `2e-5` gave these results:

| Epoch | Validation Accuracy | Validation Loss   | Best |
| ----- | ------------------- | ----------------- | ---- |
| 1     | 0.9006838798522949  | 654.5871332064271 |      |
| 2     | 0.902708888053894   | 676.6227482389659 | *    |
| 3     | 0.9002257585525513  | 819.9385483749211 |      |

### `albert-base-v2`

| Epoch | Validation Accuracy | Validation Loss   | Best |
| ----- | ------------------- | ----------------- | ---- |
| 1     | 0.883808434009552   | 695.2815099170013 |      |
| 2     | 0.8934910297393799  | 705.5993305556476 | *    |
| 3     | 0.8923844695091248  | 720.7617895975709 |      |

### `distilbert-base-uncased`

| Epoch | Validation Accuracy | Validation Loss   | Best |
| ----- | ------------------- | ----------------- | ---- |
| 1     | 0.8978509902954102  | 667.3938904441893 |      |
| 2     | 0.9011375308036804  | 678.4093779828399 | *    |
| 3     | 0.8980391025543213  | 762.1903921728954 |      |