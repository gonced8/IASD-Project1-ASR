#!env/bin/python3.7

import sys

import search
from copy import deepcopy as copy_deepcopy


class ASARProblem(search.Problem):
    def __init__(self):
        super().__init__(None)
        self.A = self.C = self.P = self.L = []

    def load(self, f):
        self.A, self.C, self.P, self.L = read_input_from_file(f)

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once.

        Yields:
        (idx_airplane, leg, add_time)
        """
        # Iterate in adding to each airplane
        for idx, airplane_legs in enumerate(state.schedule):
            if not airplane_legs:
                # Iterate in adding each leg
                for next_leg in state.remaining:
                    # Compute new departure time at 2nd airport of leg
                    new_tod = leg_initial_time(self.A, next_leg)
                    ### function above not yet final
                    yield (idx, next_leg, new_tod)
            else:
                last_airport  = airplane_legs[-1]['arr']
                # See if plane can't leave the current airport
                if (state.tod[idx] > self.A[last_airport]['end']):
                    continue
                # See which legs can be added
                for next_leg in state.remaining:
                    if next_leg['dep'] != last_airport:
                        continue
                    new_tod = departure_time(next_leg, curr_time=state.tod[idx])
                    if new_departure == -1:
                        continue
                    yield (idx, next_leg, new_tod)

    def departure_time(self, leg, curr_time = 0):
        """
        Computes the time at which the airplane can start the next leg
        """
        dep_closing_time = airports[leg['dep']]['end']
        arr_opening_time = airports[leg['arr']]['start']
        arr_closing_time = airports[leg['arr']]['end']
        duration = leg['dl']

        if curr_time == 0:
            dep_time = airports[leg['dep']]['start']
        else:
            dep_time = curr_time

        # Minimum time before departing and starting a new flight
        delta_time = sum_time(duration, self.C[self.A[idx]['class']])

        earliest_arr_time = sum_time(dep_time, duration)
        earliest_dep_time = sum_time(arr_opening_time, duration, -1)

        if earliest_arr_time < arr_opening_time:
            if earliest_dep_time < dep_closing_time:
                return sum_time(earliest_dep_time, delta_time)
            else:
                return -1
        else:
            if earliest_arr_time < arr_closing_time:
                return sum_time(dep_time, delta_time)
            else:
                return -1

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        new_state = copy_deepcopy(state)

        idx_airplane = action[0]
        new_leg = action[1]
        new_tod = action[2]

        new_state.tod[idx_airplane] = new_tod
        new_state.schedule[idx_airplane].append(new_leg)
        new_state.remaining.remove(new_leg)

        return new_state


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
