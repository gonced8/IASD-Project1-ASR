#!env/bin/python3.7

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


class ASARProblem(search.Problem):
    def __init__(self):
        super().__init__(None)
        self.A = self.C = self.P = self.L = []

    def load(self, f):
        self.A, self.C, self.P, self.L = read_input_from_file(f)
        self.initial = state(len(self.P), self.L)


    def goal_test(self, s):
        return True


    def save(self, f, s):
        if self.goal_test(s):
            for i, plane_schedule in enumerate(s.schedule):
                line = formatted_schedule(self.A, self.C, self.P, i, plane_schedule)
                f.write(line+'\n')

            # Calculate profit
        else:
            f.write("Infeasible.")


def get_argv():
    from sys import argv, exit

    if len(argv)>1:
        filename = argv[1]
    else:
        print(argv[0]+" <input file>")
        exit(-1)

    return filename


def read_input_from_file(f):
    A = {}
    C = {}
    P = []
    L = []

    for line in f.readlines():
        splitted = line.split()
        if not splitted:
            continue

        code = splitted[0]
        arg = splitted[1:]

        if code == 'A':
            d = {'start': arg[1], 'end': arg[2]}
            A[arg[0]] = d

        elif code == 'C':
            C[arg[0]] = arg[1]

        elif code == 'P':
            d = {"airplane": arg[0], "class": arg[1]}
            P.append(d)

        elif code == 'L':
            d = {"dep": arg[0], "arr": arg[1], "dl": arg[2]}
            d.update({ arg[i]: arg[i+1] for i in range(3, len(arg), 2) })
            L.append(d)

    return A, C, P, L


def sum_time(t1, t2, sign=1):
    # Receives two time strings and returns one string of the summed time
    if sign>0:
        sumtime = [int(t1[i:i+2]) + int(t2[i:i+2]) for i in range(0,len(t1),2)]
        if sumtime[1] >= 60: # More than 60 minutes
            sumtime[0] += 1
            sumtime[1] -= 60
    else:
        sumtime = [int(t1[i:i+2]) - int(t2[i:i+2]) for i in range(0,len(t1),2)]
        if sumtime[1] < 0: # More than 0 minutes
            sumtime[0] -= 1
            sumtime[1] += 60

    return "{:02d}{:02d}".format(sumtime[0], sumtime[1])
    # Returns string with added zeros if necessary, format hhmm


def leg_initial_time(airports, leg):
    dep_time = airports[leg['dep']]['start']
    arr_time = airports[leg['arr']]['start']
    duration = leg['dl']

    if sum_time(dep_time, duration) < arr_time:
        return sum_time(arr_time, duration, -1)
    else:
        return dep_time


def get_out_filename(in_filename):
    out_filename = in_filename.split('/')
    if len(out_filename)==1:
        sep = '\\'
        out_filename = in_filename.split('\\')
    else:
        sep = '/'

    out_filename[0] = 'output'

    out_filename = sep.join(out_filename)

    return out_filename


def formatted_schedule(A, C, P, i, schedule):
    line = 'S '
    line += P[i]['airplane'] + ' '

    time = leg_initial_time(A, schedule[0])
    dr = C[P[i]['class']]

    for leg in schedule:
        line += time + ' '
        line += leg['dep'] + ' '
        line += leg['arr'] + ' '

        time = sum_time(time, leg['dl'])
        time = sum_time(time, dr)

    return line


if __name__ == '__main__':
    in_filename = get_argv()

    p = ASARProblem()

    with open(in_filename, 'r') as f:
        p.load(f)

    print(p.A, '\n')
    print(p.C, '\n')
    print(p.P, '\n')
    print(p.L, '\n')

    print(sum_time("0630", "1230"))

    print(p.initial.tod, '\n')
    print(p.initial.schedule, '\n')
    print(p.initial.remaining, '\n')

    out_filename = get_out_filename(in_filename)
    test_state = state(2, None)
    test_state.schedule = [[p.L[0], p.L[1]], [p.L[2], p.L[3]]]
    with open(out_filename, 'w') as f:
        p.save(f, test_state)
