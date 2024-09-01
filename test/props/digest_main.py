import argparse


def main(*args):
    print(sum(args))


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
