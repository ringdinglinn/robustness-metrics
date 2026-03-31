import math
import json
import networkx as nx
import torch
import numpy as np
import time
import heapq

# --- Utilities ----------------------------------------------------------------

MIN_PART_SIZE = 1

def is_balanced(a, b, is_a, r, n):
    m = 0.05

    if (is_a):
        a -= 1
        b += 1
    else:
        a += 1
        b -= 1
    s = min(a, b)

    max_m = round(n * m)
    s_r = round(min(n * r, n * (1 - r)))

    balance_ok = (abs(s_r - s) <= max_m)
    non_empty_ok = (a > 0) & (b > 0)

    return balance_ok & non_empty_ok

def update_gains(G, assignment, gains, vertex):
    gains[vertex] = 0
    for neighbor in G.neighbors(vertex):
        if (assignment[vertex] != assignment[neighbor]):
            gains[neighbor] += 1
            gains[vertex] += 1
        else:
            gains[neighbor] -= 1
            gains[vertex] += 1

def intialize_gains(G, assignment):
    n = assignment.shape[0]
    gains = np.zeros(n)
    n_cut_edges = 0
    for i in range(n):
        for neighbor in G.neighbors(i):
            if assignment[neighbor] != assignment[i]:
                gains[i] += 1
                n_cut_edges += 1
            else:
                gains[i] -= 1

    n_cut_edges //= 2
    order = np.argsort(-gains)
    return gains, order, n_cut_edges


# --- Algorithm ---------------------------------------------------------------

def initial_partition(n, r):
    perm = torch.randperm(n)
    r = min(1 - r, r)
    k = max(1, round(n * r))
    A_idx = perm[:k]
    assignment = np.ones(n)
    assignment[A_idx] = -1
    return assignment, k, n - k

def partition_pass(G, r):
    nodes = list(G.nodes())
    n = len(nodes)
    if n == 0:
        return None

    assignment, size_a, size_b = initial_partition(n, r)

    moveable = np.ones(n, dtype=bool)

    gains, order, n_cut_edges = intialize_gains(G, assignment)  

    while (moveable).any().item():
        idx = 0
        vertex = order[idx]

        while idx < len(gains) :
            vertex = order[idx]
            if ((not is_balanced(size_a, size_b, assignment[vertex]==-1, r, n) or not moveable[vertex])):
                idx += 1
            else:
                break

        gain = gains[vertex]

        # update stuff

        if assignment[vertex] == -1:
            size_a -= 1
            size_b += 1
        else:
            size_a += 1
            size_b -= 1

        assignment[vertex] *= -1
        n_cut_edges += gain
        moveable[vertex] = False

        update_gains(G, assignment, gains, vertex)
        order = np.argsort(-gains)

    return n_cut_edges, np.sum(assignment==-1), np.sum(assignment==1)

# --- Top-level helpers -------------------------------------------------------

def cheeger(c, a, b):
    return c / min(a, b)

def run_passes(G, r, n_passes):
    min_cheeger = math.inf
    updates = 0
    min_partition = None

    for i in range(n_passes):
        res = partition_pass(G, r)
        if res is None:
            print(f"pass {i}: no improving moves (empty or trivial partition).")
            continue
        c, a, b = res

        current = cheeger(c, a, b)
        if current < min_cheeger:
            min_cheeger = current
            updates += 1
            min_partition = (c, a, b)

        print(f"pass: {i}, updates: {updates}, cur_cheeger: {current:.6f}, a = {a}, b = {b}")

    return min_partition

# --- JSON encoder for torch types -------------------------------------------

class TorchJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if torch.is_tensor(obj):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return super().default(obj)

# --- main --------------------------------------------------------------------

def compute_r(G, r_s, passes):
    results_r = {}
    for r in r_s:
        start = time.time()
        res = run_passes(G, r, passes)
        elapsed = time.time() - start
        if res is None:
            results_r[str(r)] = None
        else:
            c, a, b = res
            results_r[str(r)] = {"cheeger": cheeger(c, a, b), "c": c, "a": a, "b": b}
        print(f"r={r}: {elapsed:.2f}s")

    return min([r["cheeger"] for r in results_r.values()])

def compute(G):
    r_s = [0.05, 0.15, 0.25, 0.35, 0.45]
    passes = 10
    return compute_r(G, r_s, passes)
