import argparse
from collections import deque
import random
import time
import numpy as np

initial_state: str
goal_states: list
states = {}


class Node:
    state: str
    depth: int
    cost: float
    function_cost: float
    parent = None

    def __init__(self, state, depth, parent):
        self.state = state
        self.depth = depth
        self.parent = parent

    def get_parent(self):
        return self.parent


def read_state_space_descriptor(descriptor_file):
    global initial_state, goal_states, states
    i = 0
    with open(descriptor_file, 'r', encoding="utf8") as inp:
        for line in inp:
            line = line.strip()
            if line.startswith('#'):
                continue
            if i == 0:
                initial_state = line
            elif i == 1:
                goal_states = line.split(' ')
            else:
                transition = line.split(' ')
                states[transition[0][0:-1]] = {'transition': transition[1:]}
            i += 1


def read_heuristic_descriptor(heuristic_descriptor):
    global states
    with open(heuristic_descriptor, 'r', encoding="utf8") as inp:
        for line in inp:
            line = line.strip()
            if line.startswith('#'):
                continue
            else:
                line = line.split(': ')
                states[line[0]]['heuristic_value'] = line[1]


def get_path(n, cost, output=True):
    path = []
    while n:
        path.append(n.state)
        if 'h_star' not in states[n.state]:
            states[n.state]['h_star'] = cost - n.cost
        n = n.parent
    path.reverse()
    if output:
        if cost is not None:
            print('Found path of length {} with total cost {}:'.format(len(path), cost))
        else:
            print('Found path of length {}'.format(len(path)))
        print(' => \n'.join(path))
        print('\n')
    return cost


def run_uniform_cost_search(output=True):
    if output:
        print('Running ucs:\n')
    states_visited = set()
    initial_node = Node(initial_state, 0, None)
    initial_node.cost = 0.0
    open_q = deque([initial_node])
    while len(open_q) != 0:
        n = open_q.popleft()
        states_visited.add(n.state)

        if n.state in goal_states:
            if output:
                print('States visited = {}'.format(str(len(states_visited))))
            return get_path(n, n.cost, output)

        for state in states[n.state]['transition']:
            state = state.split(',')
            node = Node(state[0], n.depth + 1, n)
            node.cost = n.cost + float(state[1])
            open_q.append(node)
        open_q = deque(sorted(open_q, key=lambda node_sort: node_sort.cost))
    raise Exception('Solution was not found by uniform cost search')

def is_heuristic_optimistic_old():
    global initial_state
    print('Checking if heuristic is optimistic.')
    optimistic = True
    number_of_method_calls = 0
    for state in states:
        initial_state = state
        h_star = run_uniform_cost_search(output=False)
        number_of_method_calls += 1
        if float(states[state]['heuristic_value']) > h_star:
            optimistic = False
            print('    [ERR] h({}) > h*: {} > {}'.format(state, states[state]['heuristic_value'], str(h_star)))
    print('Called method for searching path {} times.'.format(str(number_of_method_calls)))
    if not optimistic:
        print('Heuristic is not optimistic.\n')
    else:
        print('Heuristic is optimistic.\n')
    return number_of_method_calls

def is_heuristic_optimistic_new():
    global initial_state
    print('Checking if heuristic is optimistic.')
    if is_heuristic_consistent():
        print('Heuristic is optimistic.\n')
        return 0
    optimistic = True
    number_of_method_calls = 0
    for state in states:
        initial_state = state
        if 'h_star' in states[state]:
            h_star = states[state]['h_star']
        else:
            h_star = run_uniform_cost_search(output=False)
            number_of_method_calls += 1
        if float(states[state]['heuristic_value']) > h_star:
            optimistic = False
            print('    [ERR] h({}) > h*: {} > {}'.format(state, states[state]['heuristic_value'], str(h_star)))
            print('Heuristic is not optimistic.\n')
            return number_of_method_calls

    print('Called method for searching path {} times.'.format(str(number_of_method_calls)))
    print('Heuristic is optimistic.\n')
    return number_of_method_calls

def is_heuristic_consistent():
    print('Checking if heuristic is consistent.')
    consistent = True
    for state1 in states:
        for transition in states[state1]['transition']:
            state2 = transition.split(',')[0]
            cost = float(transition.split(',')[1])
            if round(float(states[state1]['heuristic_value']), 6) > round(float(states[state2]['heuristic_value']) + cost, 6):
                consistent = False
                print('    [ERR] h({}) > h({}) + c: {} > {} + {}'.format(state1, state2,
                                                                        states[state1]['heuristic_value'],
                                                                        states[state2]['heuristic_value'], cost))
    return consistent


def parse_args():
    parser = argparse.ArgumentParser(description='Compare 2 solutions for is_heuristic_optimistic implementation')
    parser.add_argument('-sd', '--state_space_descriptor', help='State space descriptor file')
    parser.add_argument('-hd', '--heuristic_descriptor', help='Heuristic descriptor file')
    parser.add_argument('-on', '--only_new', help='Do only new method, in case the old one takes longer than 5 mins', action='store_true')
    args = parser.parse_args()
    return args


def main():
    global initial_state, states, goal_states
    args = parse_args()

    if args.state_space_descriptor is None:
        raise ValueError('Specify state space descriptor file')
    if args.heuristic_descriptor is None:
        raise ValueError('Specify heuristic descriptor file')

    read_state_space_descriptor(args.state_space_descriptor)
    read_heuristic_descriptor(args.heuristic_descriptor)

    print('Start state: {}'.format(initial_state))
    print('End state(s): {}'.format(str(goal_states)))
    print('State space size: {}'.format(len(states.keys())))

    number_of_transitions = 0
    for state in states:
        number_of_transitions += len(states[state]['transition'])

    print('Total transitions: {}\n'.format(number_of_transitions))

    time_taken = []
    methods_called = []

    if args.only_new:
        for i in range(10):
            print('--- initial state: {} ---'.format(initial_state))
            print('Execution time for is_heuristic_optimistic_new')
            start = time.time()
            method_calls_new = is_heuristic_optimistic_new()
            end = time.time()
            new_time = end - start
            print('Wall time: {}\n'.format(str(new_time)))

            method_calls_old = len(states.keys())
            old_time = 5 * 60

            print('New method is faster by: ' +  str(5 * 60 - new_time) + ' seconds\n')
            time_taken.append(old_time - new_time)
            print('New method has called method for finding path: ' +  str(method_calls_old - method_calls_new) + ' times less\n')
            methods_called.append(method_calls_old - method_calls_new)

            states = {}
            read_state_space_descriptor(args.state_space_descriptor)
            read_heuristic_descriptor(args.heuristic_descriptor)
            initial_state = random.choice(list(states.keys()))

    else:
        for i in range(10):
            states = {}
            read_state_space_descriptor(args.state_space_descriptor)
            read_heuristic_descriptor(args.heuristic_descriptor)

            print('--- initial state: {} ---'.format(initial_state))
            print('Execution time for is_heuristic_optimistic_old')
            start = time.time()
            method_calls_old = is_heuristic_optimistic_old()
            end = time.time()
            old_time = end - start
            print('Wall time: {}\n'.format(str(old_time)))

            states = {}
            read_state_space_descriptor(args.state_space_descriptor)
            read_heuristic_descriptor(args.heuristic_descriptor)

            print('Execution time for is_heuristic_optimistic_new')
            start = time.time()
            method_calls_new = is_heuristic_optimistic_new()
            end = time.time()
            new_time = end - start
            print('Wall time: {}\n'.format(str(new_time)))

            print('New method is faster by: ' +  str(old_time - new_time) + ' seconds\n')
            time_taken.append(old_time - new_time)
            print('New method has called method for finding path: ' +  str(method_calls_old - method_calls_new) + ' times less\n')
            methods_called.append(method_calls_old - method_calls_new)

            initial_state = random.choice(list(states.keys()))

    print('--- RESULTS ---')
    print('Mean time new method took less:', np.mean(time_taken))
    print('Standard Deviation of time new method took less:', np.std(time_taken))
    print('Mean number of path finding method calls for new method - path finding method calls for old method:', np.mean(methods_called))
    print('Standard Deviation of path finding method calls for new method - path finding method calls for old method:', np.std(methods_called))


if __name__ == "__main__":
    main()
