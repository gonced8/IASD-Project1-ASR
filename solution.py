#!env/bin/python3.7

import sys

import search


class state:
    def __init__(self, nplanes=None, legs=None):
        if nplanes:
            self.tod = [None] * nplanes
            self.schedule = [[]] * nplanes
        else:
            self.tod = None
            self.schedule = None

        if legs:
            self.remaining = [leg for leg in legs]
        else:
            self.remaining = None

    def initial_time(self):
        # FINISH THIS FUNCTION. THINK ABOUT DICTIONARIES WITH OBJECTS INSTEAD OF STRINGS
        leg = self.schedule[0]
        time = '0000'

        return time


class ASARProblem(search.Problem):
    def __init__(self):
        super().__init__(None)
        self.A = self.C = self.P = self.L = []

    def load(self, f):
        self.A, self.C, self.P, self.L = read_input_from_file(f)
        self.initial = state(len(self.P), self.L)


    def save(self, f, s):
        if self.goal_test(s):
            for i, schedule in enumerate(s.schedule):
                line = 'S '
                line += self.P[i]['airplane'] + ' '

                time = s.initial_time()
                dr = self.C[self.P[i]['class']]

                for leg in s:
                    line += time + ' '
                    line += leg['dep'] + ' '
                    line += leg['arr'] + ' '

                    time = sum_time(time, leg['dl'])
                    time = sum_time(time, dr)

                f.write(line+'\n')
        else:
            f.write("Infeasible.")


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


def sum_time(t1, t2):
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

    print(sum_time("0630", "1230"))

    print(p.initial.tod, '\n')
    print(p.initial.schedule, '\n')
    print(p.initial.remaining, '\n')
