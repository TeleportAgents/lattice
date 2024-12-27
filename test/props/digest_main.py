import argparse

from example_directory.example_script import analyze_text_reviews


def main(*args):
    def action():
        return sum(args)

    print(action())

    positive, negative = analyze_text_reviews(["first", "second"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "integers",
        metavar="N",
        type=int,
        nargs="+",
        help="an integer for the accumulator",
    )

    args = parser.parse_args()
    main(args.integers[0])
