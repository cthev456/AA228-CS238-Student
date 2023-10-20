import sys
import numpy as np
import networkx as nx
import random
import pandas as pd
from scipy.special import loggamma

class Variable():
    def __init__(self, variable, column):
        self.variable = variable
        self.r = len(np.unique(column))
    
class K2Search():
    """
    K2 search of the space of directed acyclic graphs using a specified variable ordering.
    This variable `ordering` imposes a topological ordering in the resulting graph.
    The `fit` function takes an ordered list variables `variables` and a data set `data`.
    The method starts with an empty graph and iteratively adds the next parent
    that maximally improves the Bayesian score.
    """
    def __init__(self, ordering: list[int]):
        self.ordering = ordering

    def fit(self, variables, data):
        graph = nx.DiGraph()
        graph.add_nodes_from(range(len(variables)))
        for k, i in enumerate(self.ordering[1:]):
            y = bayesian_score(variables, graph, data)
            while True:
                y_best, j_best = -np.inf, 0
                for j in self.ordering[:k]:
                    if not graph.has_edge(j, i):
                        graph.add_edge(j, i)
                        y_prime = bayesian_score(variables, graph, data)
                        if y_prime > y_best:
                            y_best, j_best = y_prime, j
                        graph.remove_edge(j, i)
                if y_best > y:
                    y = y_best
                    graph.add_edge(j_best, i)
                else:
                    break
        return graph
    
def sub2ind(siz, x):
    k = [1] + list(np.cumprod(siz[:-1]))
    x = [element - 1 for element in x]
    return np.dot(k, x)

def statistics(vars, G, D):
    n = len(vars)
    r = [vars[i].r for i in range(n)]
    q = np.array([int(np.prod([r[j] for j in G.predecessors(i)])) for i in range(n)])
    M = [np.zeros((q[i], r[i])) for i in range(n)]
    for o in D:  
        for i in range(n):
            k = o[i] - 1
            parents = [v for v in G.predecessors(i)]
            j = 1
            if parents:
                j = sub2ind([r[parent] for parent in parents], list(o[parents]-1))
            try:
                M[i][j - 1, k - 1] += 1.0
            except Exception as e:
                print(M, i, j, k, e)
                sys.exit(1)
    return M

def prior(variables, graph):
    """
    A function for generating a prior alpha_{ijk} where all entries are 1.
    The array of matrices that this function returns takes the same form
    as the counts generated by `statistics`.
    To determine the appropriate dimensions, the function takes as input the
    list of variables `variables` and structure `graph`.
    """
    n = len(variables)
    r = [var.r for var in variables]
    q = np.array([int(np.prod([r[j] for j in graph.predecessors(i)])) for i in range(n)])
    return [np.ones((q[i], r[i])) for i in range(n)]

def bayesian_score_component(M, alpha):
    # Note: The `loggamma` function is provided by `scipy.special`
    alpha_0 = np.sum(alpha, axis=1)
    p = np.sum(loggamma(alpha + M))
    p -= np.sum(loggamma(alpha))
    p += np.sum(loggamma(alpha_0))
    p -= np.sum(loggamma(alpha_0 + np.sum(M, axis=1)))
    return p

def bayesian_score(variables, graph, data):
    """
    An algorithm for computing the Bayesian score for a list of `variables` and a `graph` given `data`.
    This method uses a uniform prior alpha_{ijk} = 1 for all i, j, and k as generated by algorithm 4.2 (`prior`).
    Chapter 4 introduced the `statistics` and `prior` functions.

    Note: log(Γ(alpha)/Γ(alpha + m)) = log Γ(alpha) - log Γ(alpha + m), and log Γ(1) = 0.
    """
    n = len(variables)
    M = statistics(variables, graph, data)
    alpha = prior(variables, graph)
    return np.sum([bayesian_score_component(M[i], alpha[i]) for i in range(n)])

def write_gph(dag, idx2names, filename):
    with open(filename, 'w') as f:
        for edge in dag.edges():
            f.write("{}, {}\n".format(idx2names[edge[0]].variable, idx2names[edge[1]].variable))

# Define a function to read the CSV file and create Variable objects
def read_csv_and_create_variables(file_path):
    data = pd.read_csv(file_path)
    columns = data.columns
    variable_list = []

    for col_name in columns:
        variable = Variable(col_name, data[col_name])
        variable_list.append(variable)
    return variable_list

def compute(infile, outfile):
    # WRITE YOUR CODE HERE
    # FEEL FREE TO CHANGE ANYTHING ANYWHERE IN THE CODE
    # THIS INCLUDES CHANGING THE FUNCTION NAMES, MAKING THE CODE MODULAR, BASICALLY ANYTHING
    variables = read_csv_and_create_variables(infile)
    data = np.genfromtxt(infile, delimiter=',', dtype=None, encoding=None, skip_header=1)
    ordering = [i for i in range(len(variables))]
    random.shuffle(ordering)
    test_algo = K2Search(ordering)
    final_graph = test_algo.fit(variables, data)
    print(final_graph)
    final_score = bayesian_score(variables, final_graph, data)
    print(final_score)
    write_gph(final_graph, variables, outfile)

def main():
    if len(sys.argv) != 3:
        raise Exception("usage: python project1.py <infile>.csv <outfile>.gph")

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    compute(inputfilename, outputfilename)


if __name__ == '__main__':
    main()
