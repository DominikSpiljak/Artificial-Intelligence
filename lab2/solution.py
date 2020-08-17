import sys

def parse_args():
    args = sys.argv
    arg_dict =  {
        'assignment_flag': args[1],
        'loc_file': args[2]
    }

    if 'verbose' in sys.argv:
        arg_dict['verbose'] = True
    else:
        arg_dict['verbose'] = False
    
    if len(args) == 5:
        arg_dict['user_commands_file'] = args[3]
    elif len(args) == 4 and arg_dict['verbose'] is not True:
        arg_dict['user_commands_file'] = args[3]
    else:
        arg_dict['user_commands_file'] = None
    return arg_dict

def parse_loc_file(loc_file):
    loc = []
    with open(loc_file, 'r') as inp:
        for line in inp:
            line = line.strip().lower()
            if line.startswith('#'):
                continue
            loc.append(tuple([part.strip() for part in line.split(' v ')]))
    return loc

def negate(clause):
    clause = [part for part in clause]
    for i in range(len(clause)):
        if '~' in clause[i]:
            clause[i] = clause[i].replace('~', '')
        else:
            clause[i] = '~{}'.format(clause[i])
    parts = []
    for part in clause:
        parts.append(part)
    return set(tuple([part]) for part in parts)


def run_deletion_simplification(loc):
    for_deleting = set()
    for clause1 in loc:
        for clause2 in loc:
            if clause1 != clause2 and (set(clause1).issuperset(set(clause2))) and len(clause2) > 0 and len(clause1) > 0:
                for_deleting.update([clause1])
    for clause in loc:
        for part in clause:
            if '~' in part:
                formated_part = part.replace('~', '')   
            else:
                formated_part = '~{}'.format(part)

            if formated_part in clause:
                for_deleting.update([clause])
    
    for clause in for_deleting:
        loc[loc.index(clause)] = ()
    return loc

def select_clauses(loc, sos):
    clauses = []
    for clause in loc:
        for part in clause:
            if '~' in part:
                formated_part = part.replace('~', '')   
            else:
                formated_part = '~{}'.format(part)
            for sos_part in sos:
                if formated_part in sos_part:
                        clauses.append([clause, sos_part])
                        break
    return clauses

def plResolve(clause1, clause2):
    new = []
    clause1 = list(clause1)
    clause2 = list(clause2)
    for clause1_part in clause1:
        if '~' in clause1_part:
            formated_clause1_part = clause1_part.replace('~', '')   
        else:
            formated_clause1_part = '~{}'.format(clause1_part)
        for clause2_part in clause2:
            if formated_clause1_part  ==  clause2_part:
                clause1.remove(clause1_part)
                clause2.remove(clause2_part)
                for element in clause1 + clause2:
                    new.append(element)
    return tuple(new)


def print_clauses(loc, iterator, index=None):
    for clause in loc:
        if index is None:
            if len(clause) == 0:
                print('{}. {}'.format(iterator, 'NIL'))
            else:
                print('{}. {}'.format(iterator, ' v '.join(clause)))
        else:
            if len(clause) == 0:
                print('{}. {} ({}, {})'.format(iterator, 'NIL', index[loc.index(clause)][0], index[loc.index(clause)][1]))
            else:
                print('{}. {} ({}, {})'.format(iterator, ' v '.join(clause), index[loc.index(clause)][0], index[loc.index(clause)][1]))

        iterator += 1

    return iterator

def resolution(loc, goal_clause, verbose, output=True):
    if verbose:
        iterator = 1
        iterator = print_clauses(loc, iterator)
        print('=============')
    loc.extend(negate(goal_clause))
    set_of_support = []
    set_of_support.extend(negate(goal_clause))
    loc = run_deletion_simplification(loc)
    set_of_support = run_deletion_simplification(set_of_support)
    new = []

    if verbose:
        iterator = print_clauses(set_of_support, iterator)
        print('=============')

    while True:

        indexes = []
        new = []
        for clause1, clause2 in select_clauses(loc.copy(), set_of_support.copy()):
            resolvents = plResolve(clause1, clause2)
            old_resolvents = resolvents
            resolvents = tuple(set(resolvents))
            resolvents = run_deletion_simplification([resolvents])[0]

            indexes.append([loc.index(clause1) + 1, loc.index(clause2) + 1])

            if len(resolvents) == 0 and old_resolvents == resolvents:
                if verbose:
                    print_clauses([resolvents], iterator, indexes)
                if verbose:
                    print('=============')
                if output:
                    print('{} is true'.format(' v '.join(goal_clause)))
                return None

            if resolvents not in new:
                new.append(resolvents)


        if set(new).issubset(set(loc)):
            if verbose:
                print('=============')
            if output:
                print('{} is unknown'.format(' v '.join(goal_clause)))
            return set_of_support
                

        for element in new:
            if element not in loc:
                loc.append(element)
        loc = run_deletion_simplification(loc)

        for element in new.copy():
            if element not in set_of_support:
                set_of_support.append(element)
            else:
                del indexes[new.index(element)]
                new.remove(element)
        
        if verbose:
            iterator = print_clauses(new, iterator, indexes)

        loc = run_deletion_simplification(loc)
        set_of_support = run_deletion_simplification(set_of_support)


def interactive(loc, verbose):
    if verbose:
        print('Testing cooking assistant with standard resolution')
        print('Constructed with kowledge:')
        for clause in loc:
            print('> {}'.format(' v '.join(clause)))

    while True:
        if verbose:
            print('>>> Please enter your query')
        inp = input('>>> ')
        if inp == 'exit':
            return
        run_cooking_algorithm(loc, inp, verbose)


def test(loc, commands_file, verbose):
    if verbose:
        print('Testing cooking assistant with standard resolution')
        print('Constructed with kowledge:')
        for clause in loc:
            print('> {}'.format(' v '.join(clause)))

    with open(commands_file, 'r') as inp:
        for line in inp:
            line = line.lower().strip()
            if verbose:
                print('New command {}'.format(line))
            run_cooking_algorithm(loc, line, verbose)


def run_cooking_algorithm(loc, inp, verbose):
    error_color = '\033[91m'
    end_color = '\033[0m'

    if inp[-1] == '?':
        inp = inp.replace('?', '')
        inp = inp.strip()
        resolution(loc.copy(), tuple(inp.split(' v ')), verbose)
    elif inp[-1] == '-':
        inp = inp.replace('-', '')
        inp = inp.strip()
        try:
            loc.remove(tuple(inp.split(' v ')))
            if verbose:
                print('Removed {}'.format(inp))
        except ValueError:
            print(f"{error_color}Error: That clause doesn't exist!{end_color}")
    elif inp[-1] == '+':
        inp = inp.replace('+', '')
        inp = inp.strip()
        loc.append(tuple(inp.split(' v ')))
        if verbose:
            print('Added {}'.format(inp))


def run_smart_cooking_algorithm(loc, inp, verbose, output=True):
    error_color = '\033[91m'
    end_color = '\033[0m'

    if inp[-1] == '?':
        inp = inp.replace('?', '')
        inp = inp.strip()
        set_of_support = resolution(loc.copy(), tuple(inp.split(' v ')), verbose, output)
        if set_of_support is not None:
            found = False
            if verbose:
                print('Candidate questions: ', str([' v '.join(list(negate(clause))[0]) for clause in set_of_support if len(clause) != 0 
                                                and clause != list(negate(clause))[0] != tuple(inp.split(' v '))]))
            if verbose:
                for clause in set_of_support:
                    if len(clause) != 0 and list(negate(clause))[0] != tuple(inp.split(' v ')):
                        found = True
                        print('>>>', ' v '.join(list(negate(clause))[0]), '?')
                        if verbose:
                            print('>>> [Y/N/?]')
                        answer = input('>>> ').lower()
                        print()
                        if answer == 'y':
                            loc.append(list(negate(clause))[0])
                        elif answer == '?':
                            continue
                        elif answer == 'n':
                            loc.append(clause)
                        else:
                            print(f"{error_color}Error: Unknown command!{end_color}")
                if found:
                    resolution(loc.copy(), tuple(inp.split(' v ')), verbose)
                else:
                    print('No changes can be made.')
            else:
                for clause in set_of_support:
                    if len(clause) != 0 and list(negate(clause))[0] != tuple(inp.split(' v ')):
                        found = True
                        print(' v '.join(list(negate(clause))[0]))

    elif inp[-1] == '-':
        inp = inp.replace('-', '')
        inp = inp.strip()
        try:
            loc.remove(tuple(inp.split(' v ')))
            if verbose:
                print('Removed {}'.format(inp))
        except ValueError:
            print(f"{error_color}Error: That clause doesn't exist!{end_color}")
    elif inp[-1] == '+':
        inp = inp.replace('+', '')
        inp = inp.strip()
        loc.append(tuple(inp.split(' v ')))
        if verbose:
            print('Added {}'.format(inp))


def smart_interactive(loc, verbose):
    if verbose:
        print('Testing smart cooking assistant with standard resolution')
        print('Constructed with kowledge:')
        for clause in loc:
            print('> {}'.format(' v '.join(clause)))

    while True:
        if verbose:
            print('>>> Please enter your query')
        inp = input('>>> ')
        if inp == 'exit':
            return
        run_smart_cooking_algorithm(loc, inp, verbose)

def smart_test(loc, commands_file, verbose):
    if verbose:
        print('Testing cooking assistant with standard resolution')
        print('Constructed with kowledge:')
        for clause in loc:
            print('> {}'.format(' v '.join(clause)))

    with open(commands_file, 'r') as inp:
        for line in inp:
            line = line.lower().strip()
            if verbose:
                print('New command {}'.format(line))
                run_smart_cooking_algorithm(loc, line, verbose)
            else:
                run_smart_cooking_algorithm(loc, line, verbose, False)

            

def main():
    #arg_dict: {'assignment_flag': '...', 'loc_file': '...', 'user_commands_file': '...', 'verbose': True/False}
    arg_dict = parse_args()
    
    if arg_dict['assignment_flag'] == 'resolution':
        loc = parse_loc_file(arg_dict['loc_file'])
        goal_clause = loc.pop(-1)
        resolution(loc, goal_clause, arg_dict['verbose'])
    
    elif arg_dict['assignment_flag'] == 'cooking_test':
        loc = parse_loc_file(arg_dict['loc_file'])
        test(loc, arg_dict['user_commands_file'], arg_dict['verbose'])

    elif arg_dict['assignment_flag'] ==  'cooking_interactive':
        loc = parse_loc_file(arg_dict['loc_file'])
        interactive(loc, arg_dict['verbose'])

    elif arg_dict['assignment_flag'] == 'smart_resolution_interactive':
        loc = parse_loc_file(arg_dict['loc_file'])
        smart_interactive(loc, arg_dict['verbose'])

    elif arg_dict['assignment_flag'] == 'smart_resolution_test':
        loc = parse_loc_file(arg_dict['loc_file'])
        smart_test(loc, arg_dict['user_commands_file'], arg_dict['verbose'])

    elif arg_dict['assignment_flag'] == 'autocnf':
        #TODO: write autocnf()
        pass

if __name__ == "__main__":
    main()