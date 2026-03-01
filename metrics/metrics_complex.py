import networkx as nx
import metrics.network_partition as network_partition

def calculate_metrics(G):
    metrics = {}
    metrics['transitivity']         = nx.transitivity(G)
    metrics['average_clustering']   = nx.average_clustering(G)
    metrics['cheeger_constant']     = network_partition.compute(G)

    return metrics

def compute(G):
    metrics = calculate_metrics(G)
    return metrics
