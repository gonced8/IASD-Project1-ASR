#!env/bin/python3.7

import sys

import search


class ASARProblem(search.Problem):
    def __init__(self):
        super().__init__(None)
        self.A = self.C = self.P = self.L = []

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

    return [tuple(l) for l in [A, C, P, L]]


def sumtime(t1, t2):
    # Receives two time strings and returns one string of the summed time
    sumtime = [int(t1[i:i+2]) + int(t2[i:i+2]) for i in range(0,len(t1),2)]
    if sumtime[1] >= 60: # More than 60 minutes
        sumtime[0] += 1
        sumtime[1] -= 60
    return "{:02d}{:02d}".format(sumtime[0], sumtime[1])
    # Returns string with added zeros if necessary, format hhmm

if __name__ == '__main__':
    filename = get_argv()

    p = ASARProblem()

    with open(filename, 'r') as f:
        p.load(f)

    print(p.A, '\n')
    print(p.C, '\n')
    print(p.P, '\n')
    print(p.L, '\n')

    print(sumtime("0630", "1230"))
