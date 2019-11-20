#!/usr/bin/env python

from argparse import ArgumentParser
from network import algorithms as nxa
from network import function as nxf
import networkx as nx
import pandas as pd
import os.path as op
import numpy as np
import os


def prep_graphs(graph_dir):
    graph_files = os.listdir(op.abspath(graph_dir))
    graph_list = []
    for graph in graph_files:
        tmp_adj = np.loadtxt(graph)
        graph_list += [nx.graph.Graph(tmp_adj, weighted=True, directed=False)]
        assert tmp_adj == nx.adj_matrix(graph_list[-1]).todense()
    return graph_files, graph_list


def compute_summaries(graphs):
    # Stats will be organized as follows:
    #        name    : lambda g: function(g, *args, **kwargs)
    stats = {"edgecount": nxf.number_of_edges,
             "globaleffic": nxa.global_efficiency,
             "diameter": nxa.diameter,
             "degree": nxf.degree,
             "assort": nxa.assortativity.degree_assortativity_coefficient,
             "avplength": nxa.average_shortest_path_length,
             "weight": lambda g: nxf.get_edge_attributes(g, 'weight').values(),
             "ccoeff": lambda g: nxa.clustering(g, weight='weight').values(),
             "betweenness": lambda g: nxa.betweenness_centrality(g, weight='weight').values(),
             "plength": lambda g: [_
                                   for t in nxa.shortest_path_length(g)
                                   for _ in t[1].values()
                                   if _ > 0]}

    # create dataframe with a column per stat
    # for each graph...
    # add a df row for each stat on that graph
    # add graph me
    # for stat in stats:

    pass


def save_stats(summaries):
    pass


def concat_summaries(summary_list):
    pass


def main():
    parser = ArgumentParser()
    parser.add_argument("graph_dir", action="store", type=str,
                        help="")
    results = parser.parse_args()

    if results.concat is not None:
        concat_summaries(results.concat)
        return 0

    graph_list = prep_graphs(results.graph_dir)
    summaries = compute_summaries(graph_list)
    save_stats(summaries)


if __name__ == "__main__":
    main()
