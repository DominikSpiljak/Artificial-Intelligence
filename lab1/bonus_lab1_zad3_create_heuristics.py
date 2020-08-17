import argparse
import math

def get_states():
    states = []
    with open('3x3_misplaced_heuristic.txt', 'r', encoding="utf8") as inp:
        for line in inp:
            line = line.strip()
            if line.startswith('#'):
                continue
            else:
                line = line.split(': ')
                states.append(line[0])
    return states

def create_manhattan_distance_heuristic(states):
    goal_state = ['123', '456', '78x']
    manhattan_heuristic = {}
    for state in states:
        manhattan_distance = 0
        state_matrix = state.split('_')
        for row in state_matrix:
            for column in row:
                if column == 'x':
                    continue
                else:
                    expected_row = (int(column) - 1) // 3
                    expected_column = goal_state[expected_row].index(column)
                    manhattan_distance += abs(expected_row - state_matrix.index(row)) + abs(expected_column - row.index(column))
        manhattan_heuristic[state] = manhattan_distance
    return manhattan_heuristic

def create_euclidian_distance_heuristic(states):
    goal_state = ['123', '456', '78x']
    euclidian_heuristic = {}
    for state in states:
        euclidian_distance = 0.0
        state_matrix = state.split('_')
        for row in state_matrix:
            for column in row:
                if column == 'x':
                    continue
                else:
                    expected_row = (int(column) - 1) // 3
                    expected_column = goal_state[expected_row].index(column)
                    euclidian_distance += math.sqrt((expected_row - state_matrix.index(row))**2 + (expected_column - row.index(column))**2)
        euclidian_heuristic[state] = euclidian_distance
    return euclidian_heuristic
    

def main():
    states = get_states()
    manhattan_heuristic = create_manhattan_distance_heuristic(states)
    with open('3x3_manhattan_heuristic.txt', 'w') as out:
        for state in manhattan_heuristic:
            out.write('{}: {}\n'.format(state, manhattan_heuristic[state]))
    euclidian_heuristic = create_euclidian_distance_heuristic(states)
    with open('3x3_euclidian_heuristic.txt', 'w') as out:
        for state in euclidian_heuristic:
            out.write('{}: {}\n'.format(state, round(euclidian_heuristic[state], 6)))

if __name__=="__main__":
    main()
