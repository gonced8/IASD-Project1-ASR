#!env/bin/python3.7

import sys

import search


class ASARProblem(search.Problem):
    pass


def get_argv():
    if len(sys.argv)>1:
        filename = sys.argv[1]
    else:
        print(sys.argv[0]+" <input file>")
        sys.exit(-1)

    return filename


def read_input(filename):
    with open(filename, 'r') as f:
        pass


if __name__ == '__main__':
    filename = get_argv()
    read_input()
    

