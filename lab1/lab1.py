import argparse
from collections import deque

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


def run_breadth_first_search():
    print('Running bfs:\n')
    states_visited = set()

    open_q = deque([Node(initial_state, 0, None)])
    while len(open_q) != 0:
        n = open_q.popleft()
        states_visited.add(n.state)
        if n.state in goal_states:
            print('States visited = ' + str(len(states_visited)))
            return get_path(n, None)
        for state in states[n.state]['transition']:
            state = state.split(',')
            open_q.append(Node(state[0], n.depth + 1, n))
    raise Exception('Solution was not found by breadth first search')


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


def run_a_star_search():
    print('Running astar:\n')
    states_visited = set()
    initial_node = Node(initial_state, 0, None)
    initial_node.cost = 0.0
    open_q = deque([initial_node])
    closed = set()
    while len(open_q) != 0:
        n = open_q.popleft()
        states_visited.add(n.state)
        if n.state in goal_states:
            print('States visited = {}'.format(str(len(states_visited))))
            return get_path(n, n.cost)
        closed.add(n)
        for state in states[n.state]['transition']:
            state = state.split(',')

            for existing in set(list(open_q) + list(closed)):
                if existing.state == state[0]:
                    if existing.cost < n.cost + float(state[1]):
                        continue
                    else:
                        if existing in open_q:
                            open_q.remove(existing)
                        if existing in closed:
                            closed.remove(existing)
                        break

            node = Node(state[0], n.depth + 1, n)
            node.cost = round(n.cost + float(state[1]), 6)
            node.function_cost = round(node.cost + float(states[node.state]['heuristic_value']), 6)
            open_q.append(node)
        open_q = deque(sorted(open_q, key=lambda node_sort: node_sort.function_cost))
    raise Exception('Solution was not found by A* search')


def is_heuristic_optimistic():
    global initial_state
    print('Checking if heuristic is optimistic.')
    optimistic = True
    for state in states:
        initial_state = state
        h_star = run_uniform_cost_search(output=False)
        if float(states[state]['heuristic_value']) > h_star:
            optimistic = False
            print('    [ERR] h({}) > h*: {} > {}'.format(state, states[state]['heuristic_value'], str(h_star)))
    return optimistic


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
    parser = argparse.ArgumentParser(description='Performs Breadth first search and Uniform cost search for given state'
                                                 ' space descriptor file and The A* algorithm'
                                                 ' for given heuristic descriptor, also, checks if heuristic'
                                                 ' is optimistic and consistent')
    parser.add_argument('-sd', '--state_space_descriptor', help='State space descriptor file')
    parser.add_argument('-hd', '--heuristic_descriptor', help='Heuristic descriptor file')
    parser.add_argument('-bfs', '--breadth_first_search', help='Perform breadth first search', action='store_true')
    parser.add_argument('-ucs', '--uniform_cost_search', help='Perform uniform cost search', action='store_true')
    parser.add_argument('-as', '--a_star', help='Perform A* search', action='store_true')
    parser.add_argument('-ho', '--heuristic_optimistic',
                        help='Check if given heuristic is optimistic', action='store_true')
    parser.add_argument('-hc', '--heuristic_consistent',
                        help='Check if given heuristic is consistent', action='store_true')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    if args.state_space_descriptor is None:
        raise ValueError('Specify state space descriptor file')

    read_state_space_descriptor(args.state_space_descriptor)

    print('Start state: {}'.format(initial_state))
    print('End state(s): {}'.format(str(goal_states)))
    print('State space size: {}'.format(len(states.keys())))

    number_of_transitions = 0
    for state in states:
        number_of_transitions += len(states[state]['transition'])

    print('Total transitions: {}\n'.format(number_of_transitions))

    if args.breadth_first_search:
        run_breadth_first_search()

    if args.uniform_cost_search:
        run_uniform_cost_search()

    if args.a_star:
        if args.heuristic_descriptor is None:
            raise ValueError('Specify heuristic descriptor file')
        read_heuristic_descriptor(args.heuristic_descriptor)
        run_a_star_search()

    if args.heuristic_optimistic:
        if args.heuristic_descriptor is None:
            raise ValueError('Specify heuristic descriptor file')
        read_heuristic_descriptor(args.heuristic_descriptor)
        optimistic = is_heuristic_optimistic()
        if not optimistic:
            print('Heuristic is not optimistic.\n')
        else:
            print('Heuristic is optimistic.\n')

    if args.heuristic_consistent:
        if args.heuristic_descriptor is None:
            raise ValueError('Specify heuristic descriptor file')
        read_heuristic_descriptor(args.heuristic_descriptor)
        consistent = is_heuristic_consistent()
        if not consistent:
            print('Heuristic is not consistent.\n')
        else:
            print('Heuristic is consistent.\n')


if __name__ == "__main__":
    main()
