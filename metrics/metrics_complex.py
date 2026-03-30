import networkx as nx
import metrics.network_partition as network_partition

def calculate_metrics(G, r_s=None):
    metrics = {}
    metrics['transitivity']         = nx.transitivity(G)
    metrics['average_clustering']   = nx.average_clustering(G)
    if (r_s):
        metrics['cheeger_constant']     = network_partition.compute_r(G, r_s, 5)  
    else:
        metrics['cheeger_constant']     = network_partition.compute(G)  

    return metrics

def compute(G):
    metrics = calculate_metrics(G)
    return metrics
