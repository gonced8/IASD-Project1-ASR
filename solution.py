#!env/bin/python3.7

from copy import deepcopy as copy_deepcopy
import os.path
from time import time

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
    remaining : list of dictionaries
        A list of the remaining legs, that is, legs not yet assigned
    g : float
        Value of the cost function
    h : float
        Value of the heuristic
    depth : int
        Depth of the state (0 is the initial empty state)

    Methods
    -------
    __lt__(self, other)
        Compares each state through their evaluation function values: f(n)=g(n)+h(n)
    """

    def __init__(self, nplanes=None, legs=None, g=0, h=0, depth=0):
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

        self.g = g
        self.h = h
        self.depth = depth

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
        Dictionary with available airports. The key is the airport code and the value is a dictionary with keys: start and end times
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
        Loads a problem from a (opened) file object f (the formatting is specified in the Mini-Project statement). Gets the max profit of each leg. Initializes the initial state of this problem
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

        Checks done before returning an action to decrease expanded nodes include:
            Added leg is compatible with airport opening/closing times
            Matching "current leg arrival" and "next leg departure" airports
            Plane can make any more trips (current airport is not closed)
            If added leg is the last of the airplane, must match with the first airport
            Before assigning a leg to "empty" airplane, there must be at least to legs left to close the loop

        Parameters
        ----------
        state : str
            State of node chosen for expansion

        Yields
        -------
        tuple
            A tuple containing the index of the airplane to which the leg will
            be added, the leg to be added and the new tod of the airplane
        """

        for idx, airplane_legs in enumerate(state.schedule):
            if not airplane_legs:
                # Only one leg left and empty airplane, don't add the leg
                if len(state.remaining) == 1:
                    continue
                # Airplane has not flown any legs
                for next_leg in state.remaining:
                    # Compute new departure time at 2nd airport of leg
                    dep_time = leg_initial_time(self.A, next_leg)
                    new_tod = self.nextleg_dep_time(next_leg, idx, dep_time)
                    if new_tod == -1:
                        continue
                    yield (idx, next_leg, new_tod)
            else:
                if not state.tod[idx]:
                    # Empty string, schedule for this airplane is full
                    continue
                for next_leg in state.remaining:
                    if next_leg['dep'] != airplane_legs[-1]['arr']:
                        continue
                    new_tod = self.nextleg_dep_time(next_leg, idx, state.tod[idx])
                    if new_tod == -1:
                        # Is not valid time-wise
                        continue
                    if new_tod > self.A[next_leg['arr']]['end']:
                        # Can't leave the last airport
                        if airplane_legs[0]['dep'] != next_leg['arr']:
                            # Beginning and final airports don't match, invalid node
                            continue
                        new_tod = ''
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
        new_state.depth += 1

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
        state1 via action, assuming cost c to get up to state1.
        
        Receives a = (index of airplane, leg, ...) e.g. (3, {'dep': 'LPPT', 'arr': ...}, ...)
        Goes to the list of airplanes in self and figures out the class of airplane
        With the class information goes to the leg to add and figures out the profit
        For clarity: self.P[a[0]] = {'airplane': 'CS-TUA', 'class': 'a320'}
        """
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
        """Loads a problem from a (opened) file object f (the formatting is specified in the Mini-Project statement). Gets the max profit of each leg. Initializes the initial state of this problem

        Parameters
        ----------
        f : file
        """

        self.A, self.C, self.P, self.L = read_input_from_file(f)
        self.L = get_maxprofits(self.L)
        self.initial = state(len(self.P), self.L)

    def save(self, f, s):
        """Saves a solution state s to a (opened) file object f (the formatting is specified in the Mini-Project statement).

        Parameters
        ----------
        f : file
        s : state object
        """

        if s is None:
            f.write("Infeasible"+'\n')

        elif self.goal_test(s):     # safety test to be sure it's a goal
            for i, plane_schedule in enumerate(s.schedule):
                if not plane_schedule:    # plane has no flights
                    continue
                line = self.formatted_schedule(i, plane_schedule)
                f.write(line+'\n')

            # Calculate profit
            profit = self.calculate_profit(s)
            f.write('P {0:.1f}\n'.format(profit))

        else:
            print("An error occured in this problem")

    def calculate_profit(self, s):
        """Calculates the profit of the provided state (which corresponds to the airplanes schedules)

        Loops through each schedule in the state s and sums the correspoing profit to a total profit
        
        Parameters
        ----------
        s : state object

        Returns
        -------
        profit : int
            sum of the profits of each schedules
        """

        profit = 0

        for i, plane_schedule in enumerate(s.schedule):
            plane_class = self.P[i]['class']

            for leg in plane_schedule:
                profit += leg[plane_class]

        return profit

    def formatted_schedule(self, i, schedule):
        """Makes a string which represents an airplane schedule, that will be written int the output file (with the formatting specified in the Mini-Project statement)
        
        Receives an index - i - which corresponds to the selected airplane and a list of legs - schedule - with the associated legs. Loops through each schedule and gets a formatted string accordingly to the requisites in the Mini-Project statement.

        Parameters
        ----------
        i : int
        schedule : list of dictionaries

        Returns
        -------
        line : string
            String that will be written in the output file. Represents a schedule
        """

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

    def nextleg_dep_time(self, leg, idx, dep_time):
        """
        Computes the time at which the airplane can start the next leg
        Returns -1 if the leg is incompatible with the opening/closing
        time of the airports
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

def read_input_from_file(f):
    """From an open file f, reads each line and processes it, creating the problem input variables.

    Parameters
    ----------
    f : file
        Opened input file (with the formatting given in the Mini-Project statement)

    Returns
    -------
    A : dictionary
        Dictionary with airports, where the keys are the airport codes. The value is a dictionary with keys: 'start' and 'end' times
    C : dictionary
        Dictionary with planes classes, where the keys are the aircraft classes and the values are the rotation times
    P : list of dictionaries
        List of dictionaries, where each dictionary is a plane. These dictionaries have as keys: airplane and class
    L : list of dictionaries
        List of dictionaries, where each dictionary is a leg. These dictionaries have as keys: dep, arr, dl, and the aircraft classes
    """

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
            d.update({ arg[i]: float(arg[i+1]) for i in range(3, len(arg), 2) })
            L.append(d)

    return A, C, P, L

def getleg(state, plane, leg):
    """Receives the plane index and the leg number and returns a list
    containing the departure and arrival airport code"""
    if plane > len(state.schedule) or leg > len(state.schedule[plane]):
        return [None, None]
    return [state.schedule[plane][leg]['dep'], state.schedule[plane][leg]['arr']]

def sum_time(t1, t2, sign=1):
    """Receives two time strings and returns one string of the summed time
    Returns string with added zeros if necessary, format hhmm
    """
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

def leg_initial_time(airports, leg):
    """With the given leg, returns the earliest time at which an airplane could depart

    It takes into account the opening and closing times of each airport

    Parameters
    ----------
    airports : dictionary
        Dictionary with available airports. The key is the airport code and the value is a dictionary with keys: start and end times
    leg : dictionary
        Leg which initial time will be computed

    Returns
    -------
    string
        Earliest time at which the aircraft can departure. Empty string '' in case of invalid leg
    """

    dep = airports[leg['dep']]
    arr = airports[leg['arr']]
    duration = leg['dl']
    
    earliest_arr_time = sum_time(dep['start'], duration)
    earliest_dep_time = sum_time(arr['start'], duration, -1)

    if earliest_arr_time < arr['start']:    # plane arrives before arrival airport is opened
        if earliest_dep_time < dep['end']:  # plane departs before departure airport closes
            return earliest_dep_time
    else:
        if earliest_arr_time < arr['end']:  # plane arrives before arrival airport closes
            return dep['start']
    return ''                               # invalid leg timing

def get_maxprofits(legs):
    """Loops through each leg and gets the maximum profit of that leg

    The max profit is added as key to the legs dictionary

    Parameters
    ----------
    legs : list of dictionaries
        List of dictionaries, where each dictionary represents a leg

    Returns
    -------
    legs : list of dictionaries
        Same list as input, but each leg now has a key named maxprofit with the corresponding max profit
    """

    if legs:
        classes = list(legs[0].keys())[3:]

        for leg in legs:
            profits = [leg[c] for c in classes]
            leg['maxprofit'] = max(profits)
        
    return legs

def get_out_filename(in_filename):
    """Receives a filename and returns the string "output/filename". Works in every operating system

    Parameters:
    -----------
    in_filename : string
        Filename to use

    Returns:
    --------
    out_filename : string
        Filename inside directory output
    """

    out_filename = os.path.basename(in_filename)
    out_filename = os.path.join('output', out_filename)
    return out_filename

def str2bool(string):
    """Converts a string to a boolean

    Parameters:
    -----------
    string : string
    """
    return string.lower() in ("yes", "y", "true", "t", "1")

def print_stats(args, start, end, p, sol):
    """Receives the program arguments and prints the specified statistics

    Parameters:
    -----------
    args : list of strings
        The first element of args corresponds to the input file name.
        The second element is a boolean to print the execution time.
        The third element is a boolean to print the number of generated nodes.
        The fourth element is a boolean to print the solution depth.
    """

    if len(args)>1 and str2bool(args[1]):
        print("Execution time in seconds:", end-start)

    if len(args)>2 and str2bool(args[2]):
        print("Number of generated nodes:", p.n_nodes)

    if len(args)>3 and str2bool(args[3]) and sol is not None:
        print("Solution depth:", sol.depth)

    return

def main(args):
    """ Main function
    
    Initializes the problem and solves it with A* search. Saves the result in a file inside output folder

    Parameters:
    -----------
    args : list of strings
        The first element of args corresponds to the input file name.
        The second element is a boolean to print the execution time.
        The third element is a boolean to print the number of generated nodes.
        The fourth element is a boolean to print the solution depth.
    """

    if(len(args)<1):
        print("No input filename was given. Returned")
        return

    # Measure starting time
    start = time()

    in_filename = args[0]

    p = ASARProblem()

    with open(in_filename, 'r') as f:
        p.load(f)

    sol = search.astar_search(p, p.heuristic)

    out_filename = get_out_filename(in_filename)
    with open(out_filename, 'w') as f:
        if sol is None:
            p.save(f, None)
        else:
            p.save(f, sol.state)

    # Measure ending time
    end = time()

    # Print statistics
    print_stats(args, start, end, p, sol)

if __name__ == '__main__':
    from sys import argv
    if len(argv)==1:
        print(argv[0]+" <input file>")
        print(argv[0]+" <input file> <bool time> <bool n_nodes> <bool depth>")
    else:
        main(argv[1:])
