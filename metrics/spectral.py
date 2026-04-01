import networkx as nx


def spectral_gap(e):
    return e[0] - e[1]

def spectral_radius(e):
    return e[0]

def compute(G):
    metrics = {}

    adj_spectrum = nx.adjacency_spectrum(G)

    metrics["spectral_radius"] = adj_spectrum[0]
    metrics["spectral_gap"] = adj_spectrum[0] - adj_spectrum[1]
    
    metrics["algebraic_connectivity"] = nx.algebraic_connectivity(G)

    return metrics