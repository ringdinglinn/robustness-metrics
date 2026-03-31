import networkx as nx
import numpy as np

def degree_std(G):
    degrees = [d for _, d in G.degree()]
    return np.std(degrees)

def degree_entropy(G):
    degrees = [d for _, d in G.degree()]
    _, counts = np.unique(degrees, return_counts=True)
    probs = counts / counts.sum()
    entropy = -np.sum(probs * np.log2(probs))
    return entropy

def calculate_metrics(G):
    metrics = {}
    metrics['|V|'] = G.number_of_nodes()
    metrics['|E|'] = G.number_of_edges()
    metrics['avg_degree'] = 2 * G.number_of_edges() / G.number_of_nodes()
    metrics['nr_connected_components'] = nx.number_connected_components(G)
    metrics['degree_std'] = degree_std(G)
    metrics['degree_entropy'] = degree_entropy(G)
    metrics['assortativity'] = nx.degree_assortativity_coefficient(G)

    return metrics

def compute(G):
    return calculate_metrics(G)