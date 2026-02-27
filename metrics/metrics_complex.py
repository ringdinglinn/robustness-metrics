import networkx as nx
from metrics.network_partition import calculate_cheeger_costant

def calculate_metrics(G, graph_name):
    metrics = {}
    metrics['transitivity']         = nx.transitivity(G)
    print(f"{graph_name}, transitivity: {metrics['transitivity']}")
    metrics['average_clustering']   = nx.average_clustering(G)
    print(f"{graph_name}, average_clustering: {metrics['average_clustering']}")
    metrics['cheeger constant'], _  = calculate_cheeger_costant(G, 0.45, 3)
    print(f"{graph_name}, cheeger: {metrics['cheeger constant']}")

    return metrics

def compute(G):
    metrics = calculate_metrics(G)
    return metrics
