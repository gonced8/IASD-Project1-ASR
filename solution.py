#!env/bin/python3.7

from copy import deepcopy as copy_deepcopy
import os.path

import search


class state:
    def __init__(self, nplanes=None, legs=None):
        if nplanes:
            self.tod = [None for i in range(nplanes)]
            self.schedule = [[] for i in range(nplanes)]
        else:
            self.tod = None
            self.schedule = None

        if legs:
            self.remaining = [leg for leg in legs]
        else:
            self.remaining = None

        self.g = 0
        self.h = 0

    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)


class ASARProblem(search.Problem):
    def __init__(self):
        super().__init__(None)
        self.A = self.C = self.P = self.L = []
        self.n_nodes = 0

    def load(self, f):
        self.A, self.C, self.P, self.L = read_input_from_file(f)
        self.L = get_maxprofits(self.L)
        self.bound = sum(self.L)
        self.initial = state(len(self.P), self.L)

    def save(self, f, s):
        if s is None:
            f.write("Infeasible"+'\n')

        elif self.goal_test(s):
            for i, plane_schedule in enumerate(s.schedule):
                if not plane_schedule:
                    continue
                line = formatted_schedule(self.A, self.C, self.P, i, plane_schedule)
                f.write(line+'\n')

            # Calculate profit
            profit = self.calculate_profit(s)
            f.write('P {}\n'.format(profit))

    def calculate_profit(self, s):
        profit = 0

        for i, plane_schedule in enumerate(s.schedule):
            plane_class = self.P[i]['class']

            for leg in plane_schedule:
                profit += int(leg[plane_class])

        return profit

    def getleg(self, state, plane, leg):
        """Receives the plane index and the leg number and returns a list
        containing the departure and arrival airport code"""
        if plane > len(state.schedule) or leg > len(state.schedule[plane]):
            return [None, None]
        return [state.schedule[plane][leg]['dep'], state.schedule[plane][leg]['arr']]

    def goal_test(self, state):
        """Returns True if the state is a goal. False otherwise"""
        if not state.remaining:
            # There are no remaining legs to add
            # We can check the validity of our solution
            for plane in state.schedule:
                if not plane:
                    continue
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
        return c + self.bound - int(a[1][self.P[a[0]]['class']])

    def heuristic(self, n, state=None):
        """Returns the heuristic of node n, which encapsulates a given state"""
        if n is None:
            curr_state = state
        else:
            curr_state = n.state

        heurfun = 0
        for leg in curr_state.remaining:
            heurfun += self.bound - leg['maxprofit']

        return heurfun

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
                    new_tod = self.departure_time(next_leg, idx, new_tod)
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
                    new_tod = self.departure_time(next_leg, idx, state.tod[idx])
                    if new_tod == -1:
                        continue
                    yield (idx, next_leg, new_tod)

    def departure_time(self, leg, idx, dep_time):
        """
        Computes the time at which the airplane can start the next leg
        """
        airports = self.A
        dep_closing_time = airports[leg['dep']]['end']
        arr_opening_time = airports[leg['arr']]['start']
        arr_closing_time = airports[leg['arr']]['end']
        duration = leg['dl']

        # Minimum time before departing and starting a new flight
        delta_time = sum_time(duration, self.C[self.P[idx]['class']])

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
        self.n_nodes += 1

        new_state = copy_deepcopy(state)

        idx_airplane = action[0]
        new_leg = action[1]
        new_tod = action[2]

        new_state.tod[idx_airplane] = new_tod
        new_state.schedule[idx_airplane].append(new_leg)
        new_state.remaining.remove(new_leg)
        new_state.g = self.path_cost(state.g, state, action, new_state)
        new_state.h = self.heuristic(None, new_state)

        return new_state


def get_maxprofits(legs):
    if legs:
        classes = list(legs[0].keys())[3:]

        for leg in legs:
            profits = [int(leg[c]) for c in classes]
            leg['maxprofit'] = max(profits)

    return legs


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
    out_filename = os.path.basename(in_filename)
    out_filename = os.path.join('output', out_filename)
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

    sol = search.astar_search(p, p.heuristic)
    #sol = search.uniform_cost_search(p)

    # print(p.n_nodes)

    out_filename = get_out_filename(in_filename)
    with open(out_filename, 'w') as f:
        if sol is None:
            p.save(f, None)
        else:
            p.save(f, sol.state)

    '''
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
    '''
