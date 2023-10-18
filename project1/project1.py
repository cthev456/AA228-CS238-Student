import sys
import numpy as np
import networkx as nx
from scipy.special import loggamma

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

    def fit(self, variables: list[Variable], data: np.ndarray) -> nx.DiGraph:
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
    return np.dot(k, x - 1) + 1

def statistics(vars, G, D):
    n = D.shape[0]
    r = [vars[i].r for i in range(n)]
    q = [np.prod([r[j] for j in [v for v in G.neighbors(i)]]) for i in range(n)]
    M = [np.zeros((q[i], r[i])) for i in range(n)]
    
    for o in D.T:  # Transpose D for easier column-wise iteration
        for i in range(n):
            k = o[i]
            parents = [v for v in G.neighbors(i)]
            j = 1
            if parents:
                j = sub2ind([r[parent] for parent in parents], list(o[parents]))
            M[i][j - 1, k] += 1.0
    
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
            f.write("{}, {}\n".format(idx2names[edge[0]], idx2names[edge[1]]))


def compute(infile, outfile):
    # WRITE YOUR CODE HERE
    # FEEL FREE TO CHANGE ANYTHING ANYWHERE IN THE CODE
    # THIS INCLUDES CHANGING THE FUNCTION NAMES, MAKING THE CODE MODULAR, BASICALLY ANYTHING

    pass


def main():
    if len(sys.argv) != 3:
        raise Exception("usage: python project1.py <infile>.csv <outfile>.gph")

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    compute(inputfilename, outputfilename)


if __name__ == '__main__':
    main()
