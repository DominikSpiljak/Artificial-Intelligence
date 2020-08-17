import math
import argparse

config: dict
feature_names: list

class ID3:

    class Node:
        def __init__(self, node_feature):
            self.node_feature = node_feature
            self.children = {}

        def add_child(self, transition, child_node):
            self.children[transition] = child_node

    class Leaf:
        def __init__(self, value):
            self.value = value
    
    def __init__(self, max_depth=-1):
        self.tree = None
        self.max_depth = max_depth

    def _get_info_gain(self, D, D1, y):
        info_gains = {}
        info_counts = {}
        info_entropies = {}
        start_set_counts = {}
        for sample in D1:
            if y[sample] not in start_set_counts:
                start_set_counts[y[sample]] = 1
            else:
                start_set_counts[y[sample]] += 1
            for i, feature in enumerate(D[sample]):
                if i not in info_counts:
                    info_counts[i] = {}
                if feature not in info_counts[i]:
                    info_counts[i][feature] = {}
                if y[sample] not in info_counts[i][feature]:
                    info_counts[i][feature][y[sample]] = 1
                else:
                    info_counts[i][feature][y[sample]] += 1
        start_set_entropy = sum([-start_set_counts[i]/len(D1) * math.log2(start_set_counts[i]/len(D1)) for i in start_set_counts.keys()])
        for index in info_counts:
            info_entropies[index] = {}
            for key in info_counts[index]:
                key_sum = sum(info_counts[index][key].values())
                info_entropies[index][key] = sum([-k/key_sum * math.log2(k/key_sum) for k in info_counts[index][key].values()])
        for index in info_entropies:
           info_gains[index] = start_set_entropy
           for key in info_entropies[index]:
               key_sum = sum(info_counts[index][key].values())
               info_gains[index] -= key_sum/len(D1) * info_entropies[index][key]
        return info_gains


    def _get_feature_values(self, X):
        feature_values = {}
        for sample in X:
            for i in range(len(sample)):
                if i not in feature_values:
                    feature_values[i] = set()
                feature_values[i].add(sample[i])
        return feature_values

    
    def _filter_by_target(self, D1, target, y):
        filtered = []
        for i in D1:
            if y[i] == target:
                filtered.append(i)
        return filtered

    def _filter_by_feature(self, D1, v, x, D):
        filtered = []
        for i in D1:
            if D[i][x] == v:
                filtered.append(i)
        return filtered

    def _max_count(self, y):
        count_dict = {}
        maxi = 0
        for entry in y:
            if entry not in count_dict:
                count_dict[entry] = 0
            count_dict[entry] += 1
            if count_dict[entry] > maxi:
                maxi = count_dict[entry]
                maxi_element = entry
            if maxi == count_dict[entry]:
                if maxi_element > entry:
                    maxi = count_dict[entry]
                    maxi_element = entry
        return maxi_element
                
    
    def _build_tree(self, D, D1, X, y, depth, print_list, parent_y, max_depth):
        if len(D1) == 0:
            value = self._max_count(parent_y)
            return self.Leaf(value)

        subset_y = [y[i] for i in D1]
        value =  self._max_count(subset_y)
        filtered_D1 = self._filter_by_target(D1, value, y)

        if depth == max_depth:
            max_depth_value = value
            return self.Leaf(max_depth_value)

        if len(X) == 0 or filtered_D1 == D1:
            return self.Leaf(value)

        d = self._get_info_gain(D, D1, y)
        for key in d.copy():
            if key not in X:
                d.pop(key)
        x = None
        maxi = -1
        for key in d:
            if d[key] > maxi:
                maxi = d[key]
                x = key
            if d[key] == maxi:
                if feature_names[x] > feature_names[key]:
                    maxi = d[key]
                    x = key 
        
        children = {}
        for v in X[x]:
            filtered_D1 = self._filter_by_feature(D1, v, x, D)
            child_features = X.copy()
            child_features.pop(x)   
            t = self._build_tree(D, filtered_D1, child_features, y, depth + 1, print_list, subset_y, max_depth)
            children[v] = t
        node = self.Node(x)
        print_list.append((depth, feature_names[x]))
        node.children = children
        return node
        

    def fit(self, X, y):
        D = X
        X = self._get_feature_values(X)
        D1 = list(range(len(D)))
        print_list = []
        self.tree = self._build_tree(D, D1, X, y, 0, print_list, y, self.max_depth)
        sorted_print_list = []
        for print_entry in sorted(print_list):
            sorted_print_list.append(':'.join([str(print_entry[0]), print_entry[1]]))
        print(', '.join(sorted_print_list))



    def predict(self, X):
        predictions = []
        for sample in X:
            current_node = self.tree
            while True:
                if isinstance(current_node, self.Leaf):
                    predictions.append(current_node.value)
                    break
                else:
                    feature = current_node.node_feature
                    current_node = current_node.children[sample[feature]]
                    continue
        return predictions


def parse_args():
    parser = argparse.ArgumentParser(description='AI lab 3')
    parser.add_argument('train_csv', help='.csv file containing train data')
    parser.add_argument('test_csv', help='.csv file containing test data')
    parser.add_argument('config_file', help='.cfg file containing configuration')
    args = parser.parse_args()
    return args
    
def read_csv(csv_file):
    global feature_names
    features = []
    target = []
    with open(csv_file, 'r') as csv:
        for i, line in enumerate(csv):
            line = line.strip().split(',')
            if i == 0:
                feature_names = line
            else:
                features.append(line[:-1])
                target.append(line[-1])
    return [features, target]

def read_cfg(config_file):
    config = {}
    with open(config_file, 'r') as cfg:
        for line in cfg:
            line = line.strip().split('=')
            config[line[0]] = line[1]
    return config


def main():
    global config
    args = parse_args()
    X_train, y_train = read_csv(args.train_csv)
    X_test, y_test = read_csv(args.test_csv)
    config = read_cfg(args.config_file)
    
    clf = ID3(max_depth = int(config['max_depth']))
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    print(' '.join(y_pred))
    
    confusion_matrix = {}
    for test in y_test:
        if test not in confusion_matrix:
            confusion_matrix[test] = {}
            for test1 in y_test:
                if test1 not in confusion_matrix[test]:
                    confusion_matrix[test][test1] = 0 
    
    correct = 0
    for i in range(len(y_test)):
        if y_pred[i] == y_test[i]:
            correct += 1
        confusion_matrix[y_test[i]][y_pred[i]] += 1

    accuracy = correct/len(y_test)

    print("%0.5f" % round(accuracy, 5))

    for i in sorted(confusion_matrix.keys()):
        for j in sorted(confusion_matrix[i].keys()):
            if j == sorted(confusion_matrix[i].keys())[-1]:
                print(confusion_matrix[i][j])
            else:
                print(confusion_matrix[i][j], end=' ')


if __name__ == "__main__":
    main()
