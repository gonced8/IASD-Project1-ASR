#!env/bin/python3.7

import sys

import search


class ASARProblem(search.Problem):
    def __init__(self):
        search.Problem.__init__(self, None)

    def load(self, f):
        self.A, self.C, self.P, self.L = read_input_from_file(f)


def get_argv():
    if len(sys.argv)>1:
        filename = sys.argv[1]
    else:
        print(sys.argv[0]+" <input file>")
        sys.exit(-1)

    return filename


def read_input_from_file(f):
    A = []
    C = []
    P = []
    L = []

    for line in f.readlines():
        splitted = line.split()
        if not splitted:
            continue

        code = splitted[0]
        arg = splitted[1:]

        if code == 'A':
            d = dict(zip(["code", "start", "end"], arg))
            A.append(d)

        elif code == 'C':
            d = dict(zip(["class", "dr"], arg))
            C.append(d)

        elif code == 'P':
            d = dict(zip(["airplane", "class"], arg))
            P.append(d)

        elif code == 'L':
            d = dict(zip(["dep", "arr", "dl"], arg[:3]))
            d.update({ arg[i]: arg[i+1] for i in range(3, len(arg), 2) })
            L.append(d)

    return A, C, P, L


if __name__ == '__main__':
    filename = get_argv()

    p = ASARProblem()

    with open(filename, 'r') as f:
        p.load(f)

    print(p.A, '\n')
    print(p.C, '\n')
    print(p.P, '\n')
    print(p.L, '\n')
