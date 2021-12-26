import argparse
from .parser import Parser


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('srcfile')
    return parser.parse_args()


def main():
    args = get_args()

    parser = Parser()
    ast = parser.parse(args.srcfile)


main()
