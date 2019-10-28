#!env/bin/python3.7

import sys

import search


class ASARProblem(search.Problem):
    def __init__(self):
        super().__init__(None)
        self.A = self.C = self.P = self.L = []

    def load(self, f):
        self.A, self.C, self.P, self.L = read_input_from_file(f)

    def getleg(self, state, plane, leg):
        """Receives the plane index and the leg number and returns a list
        containing the departure and arrival airport code"""
        if plane > len(state.schedule) or leg > len(state.schedule[plane]):
            return [None, None]
        return [state.schedule[plane][leg]['dep'], state.schedule[plane][leg]['arr']]

    def goal_test(state):
        """Returns True if the state is a goal. False otherwise"""
        if not state.remaining:
            # There are no remaining legs to add
            # We can check the validity of our solution
            for plane in state.schedule:
                if plane[0]['dep'] != plane[-1]['arr']:
                    # Departure airport is not the same as the arrival
                    return False
            return True
        else:
            return False

    def path_cost(self, c, s1, a, s2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1."""
        # Receives a = (index of airplane, leg, ...) e.g. (3, {'dep': 'LPPT', 'arr': ...}, ...)
        # Goes to the list of airplanes in self and figures out the class of airplane
        # With the class information goes to the leg to add and figures out the profit
        # For clarity: self.P[a[0]] = {'airplane': 'CS-TUA', 'class': 'a320'}
        return c + 1/a[1][self.P[a[0]]['class']]

    def heuristic(self, n):
        """Returns the heuristic of node n, which encapsulates a given state"""
        heurfun = 0
        maxprofit = 0
        for leg in n.state.remaining:
            for class in list(self.C.keys()):
                if(leg[class] > maxprofit):
                    maxprofit = leg[class]
            heurfun += 1/maxprofit
            maxprofit = 0
        return heurfun




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
