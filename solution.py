#!env/bin/python3.7

from copy import deepcopy as copy_deepcopy
import os.path

import search


class state:
    """A class used to represent the state of each node in this search problem

    ...

    Attributes
    ----------
    tod : list of strings
        A list of string, where each string represents the time of departure of the i-th plane
    schedule : list of lists of dictionaries
        A list of schedules per plane. The first index corresponds to the plane and the second to the leg, with is a dictionary
    remaining: list of dictionaries
        A list of the remaining legs, that is, legs not yet assigned

    Methods
    -------
    __lt__(self, other)
        Compares each state through their evaluation function values: f(n)=g(n)+h(n)
    """

    def __init__(self, nplanes=None, legs=None):
        """
        Parameters
        ----------
        nplanes : int, optional
            The number of planes (default is None)
        legs : list of dictionaries, optional
            A list with the existing legs (default is None)
        """

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
        """Compares each state through their evaluation function values: f(n)=g(n)+h(n)

        Returns
        -------
        bool
            True if the evaluation function of the state in the left is less than the one in the right, or False otherwise
        """
        
        return (self.g + self.h) < (other.g + other.h)


class ASARProblem(search.Problem):
    """A class used to represent the ASAR problem, derived from the abstract class search.Problem (https://github.com/aimacode/aima-python)

    ...

    Attributes
    ----------
    A : dictionary
        Dictionary with available airports. The key is the airport code and the value is a dictionary with keys: opening and closing times
    C : dictionary
        Dictionary where the keys are the airplanes classes and the values are their rotation times
    L : list of dictionaries
        List of dictionaries where each dictionary represents a leg. Each leg has as keys the departure and arrival airports and the available classes (which values correspond to the profits associated)
    P : list of dictionaries
        List of dictionaries where each dictionary represents an airplane. Each airplane has as keys its name and class
    n_nodes : int
        Number of generated nodes

    Methods
    -------
    actions(state)
        
    result(state, action)

    goal_test(state)

    path_cost(c, s1, a, s2)

    heuristic(n, state=None)

    load(f)
        Loads a problem from a (opened) file object f (the formatting is specified in the Mini-Project statement). Groups the max profit of each leg in a list. Initializes the initial state of this problem
    save(f)
        Saves a solution state s to a (opened) file object f (the formatting is specified in the Mini-Project statement).
    calculate_profit(s)
        Calculates the profit of the provided state (which corresponds to the airplanes schedules)
    departure_time(leg, idx, dep_time)

    formatted_schedule(i, schedule)
        Makes a string which represents an airplane schedule, that will be written int the output file (with the formatting specified in the Mini-Project statement)
    """

    def __init__(self):
        super().__init__(None)
        self.A = self.C = {}
        self.L = self.P = []
        self.n_nodes = 0

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
        return c + 1/a[1][self.P[a[0]]['class']]

    def heuristic(self, n, state=None):
        """Returns the heuristic of node n, which encapsulates a given state"""
        if n is None:
            curr_state = state
        else:
            curr_state = n.state

        heurfun = 0
        for leg in curr_state.remaining:
            heurfun += 1/leg['maxprofit']

        return heurfun

    def load(self, f):
        self.A, self.C, self.P, self.L = read_input_from_file(f)
        self.L = get_maxprofits(self.L)
        self.initial = state(len(self.P), self.L)

    def save(self, f, s):
        if s is None:
            f.write("Infeasible"+'\n')

        elif self.goal_test(s):
            for i, plane_schedule in enumerate(s.schedule):
                if not plane_schedule:
                    continue
                line = self.formatted_schedule(i, plane_schedule)
                f.write(line+'\n')

            # Calculate profit
            profit = self.calculate_profit(s)
            f.write('P {}\n'.format(profit))

    def calculate_profit(self, s):
        profit = 0

        for i, plane_schedule in enumerate(s.schedule):
            plane_class = self.P[i]['class']

            for leg in plane_schedule:
                profit += leg[plane_class]

        return profit

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

    def formatted_schedule(self, i, schedule):
        line = 'S '
        line += self.P[i]['airplane'] + ' '

        time = leg_initial_time(self.A, schedule[0])
        dr = self.C[self.P[i]['class']]

        for leg in schedule:
            line += time + ' '
            line += leg['dep'] + ' '
            line += leg['arr'] + ' '

            time = sum_time(time, leg['dl'])
            time = sum_time(time, dr)

        return line


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
            d.update({ arg[i]: int(arg[i+1]) for i in range(3, len(arg), 2) })
            L.append(d)

    return A, C, P, L

def getleg(state, plane, leg):
    """Receives the plane index and the leg number and returns a list
    containing the departure and arrival airport code"""
    if plane > len(state.schedule) or leg > len(state.schedule[plane]):
        return [None, None]
    return [state.schedule[plane][leg]['dep'], state.schedule[plane][leg]['arr']]

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

def get_maxprofits(legs):
    if legs:
        classes = list(legs[0].keys())[3:]

        for leg in legs:
            profits = [leg[c] for c in classes]
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

def get_out_filename(in_filename):
    out_filename = os.path.basename(in_filename)
    out_filename = os.path.join('output', out_filename)
    return out_filename


if __name__ == '__main__':
    in_filename = get_argv()

    p = ASARProblem()

    with open(in_filename, 'r') as f:
        p.load(f)

    sol = search.astar_search(p, p.heuristic)
    #sol = search.uniform_cost_search(p)

    print(p.n_nodes)

    out_filename = get_out_filename(in_filename)
    with open(out_filename, 'w') as f:
        if sol is None:
            p.save(f, None)
        else:
            p.save(f, sol.state)
