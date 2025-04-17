from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument(
    "--maxlen_train",
    type=int,
    default=30,
    help="Maximum tokens in input during training.",
)
parser.add_argument(
    "--maxlen_val",
    type=int,
    default=50,
    help="Maximum tokens in input during evaluation.",
)
parser.add_argument(
    "--batch_size", type=int, default=32, help="Batch size."
)
parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate for Adam.")
parser.add_argument("--num_eps", type=int, default=2, help="Number of training epochs.")
parser.add_argument(
    "--num_threads",
    type=int,
    default=4,
    help="Number of threads for collecting the datasets.",
)
parser.add_argument(
    "--output_dir",
    type=str,
    default="my_model",
    help="Where to save the trained model.",
)
parser.add_argument(
    "--model_name_or_path",
    type=str,
    default=None,
    help="""Name of or path to the pretrained/trained model.""",
)

args = parser.parse_args()