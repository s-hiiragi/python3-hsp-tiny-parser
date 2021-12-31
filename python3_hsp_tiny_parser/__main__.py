import sys
import argparse

from python3_hsp_tiny_parser.tokenizer import TokenizeError
from .parser import Parser, ParseError
import colorama
from colorama import Fore, Back, Style


def print_error(*args, **kwargs):
    if len(args) >= 1:
        exc_name = type(args[0]).__name__
        args = list(args)
        args[0] = Fore.RED + f'{exc_name}: ' + str(args[0]) + Style.RESET_ALL
    if 'file' not in kwargs:
        kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('srcfile')
    return parser.parse_args()


def main():
    colorama.init()

    args = get_args()

    parser = Parser()
    try:
        ast = parser.parse(args.srcfile)
    except TokenizeError as e:
        print_error(e)
    except ParseError as e:
        print_error(e)


main()
