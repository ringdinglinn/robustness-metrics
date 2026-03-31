from metrics import border_breadth, metrics_basic, metrics_complex, sparsity, spectral
import networkx as nx

def main():
    G = nx.read_edgelist('test/test_graph.txt')

    results = {}
    results.update(metrics_basic.compute(G))
    results.update(metrics_complex.compute(G))
    results.update(spectral.compute(G))
    results.update(sparsity.compute(G))
    results.update(border_breadth.compute(G))

    print(results)

if __name__ == "__main__":
    main()