#!/usr/bin/env python

from argparse import ArgumentParser
from glob import glob
import os.path as op
import pandas as pd
import numpy as np
import json
import os

import warnings
warnings.filterwarnings('ignore',
                        category=pd.io.pytables.PerformanceWarning)


def df_footprint_mb(df):
    return np.sum([_/1024.0/1024.0 for _ in df.memory_usage(deep=True).values])


def filelist2df(file_list):
    list_of_dicts = []
    for one_file in file_list:

        name_of_file = op.basename(one_file)
        name_of_sim = op.basename(op.dirname(one_file))
        name_of_setting = op.basename(op.dirname(op.dirname(one_file)))

        tmp_dict = {}
        if "ref" in name_of_setting:
            tmp_dict["noise_type"] = None
            tmp_dict["noise_precision"] = None
            tmp_dict["noise_backend"] = None
            tmp_dict["simulation_id"] = None
            tmp_dict["os"] = name_of_sim
        else:
            tmp_dict["noise_type"] = name_of_setting
            tmp_dict["noise_precision"] = 53
            tmp_dict["noise_backend"] = "quad"
            tmp_dict["simulation_id"] = int(name_of_sim.strip('sim-'))
            tmp_dict["os"] = "ubuntu"

        #  sub-[]_ses-[]_dwi_eddy_******.mat
        tmp_dict['filename'] = name_of_file
        tmp_dict['subses'] = "_".join(name_of_file.split('_')[:2])
        tmp_dict['sub'] = tmp_dict['subses'].split('_')[0].split('-')[1]
        tmp_dict['ses'] = tmp_dict['subses'].split('_')[1].split('-')[1]

        tmp_dict['graph'] = np.loadtxt(one_file)
        list_of_dicts.append(tmp_dict)
        del tmp_dict

    ldf = pd.DataFrame(list_of_dicts)
    return ldf


def computedistances(df_graphs, verbose=False):
    # Define norms to be used
    # Frobenius Norm
    def fro(x, y=None):
        if y is None: y = np.zeros_like(x)
        return np.linalg.norm(x - y, ord='fro')

    # Mean Squared Error
    def mse(x, y=None):
        if y is None: y = np.zeros_like(x)
        return np.mean((x - y)**2)

    # Sum of Squared Differences
    def ssd(x, y=None):
        if y is None: y = np.zeros_like(x)
        return np.sum((x - y)**2)

    norms = [fro, mse, ssd]

    # Grab the unique subses IDs and add columns for norms
    count_dict = df_graphs.subses.value_counts().to_dict()
    subses = list(count_dict.keys())
    for norm in norms:
        norm_col_name = norm.__name__ + " (self)"
        df_graphs.loc[:, norm_col_name] = None

        dist_col_name = norm.__name__ + " (ref)"
        df_graphs.loc[:, dist_col_name] = None

    # For each subses ID...
    for ss in subses:
        # Grab the reference image (i.e. one without noise)
        df_graphs_ss = df_graphs.query('subses == "{0}"'.format(ss))

        # Get down to two references, then pick the ubuntu one
        ref = df_graphs_ss.loc[df_graphs_ss.noise_type.isnull()]
        ref = ref.query("os == 'ubuntu'").iloc[0].graph

        # For each noise simulation...
        for idx, graph in df_graphs_ss.iterrows():
            df_graphs.loc[idx, norm_col_name] = norm(graph.graph)
            for norm in norms:
                df_graphs.loc[idx, dist_col_name] = norm(ref, graph.graph)

    return df_graphs


def main(args=None):
    parser = ArgumentParser(__file__,
                            description="Re-formats JSON and matrix data from"
                                        "one-voxel + connectome generation for"
                                        "subsequent analysis.")
    parser.add_argument("graph_dir",
                        help="Corresponding directory containing graphs with "
                             "or without noise injected and stored in the .mat"
                             " ASCII-encoded format. The directory structure "
                             "expected is: graph_dir/setting/sim-#/graphs.mat")
    parser.add_argument("output_path",
                        help="Path to the dataframes containing groomed data.")

    results = parser.parse_args() if args is None else parser.parse_args(args)

    # Grab and process the graph data
    mat_files = glob(op.join(results.graph_dir, '*', '*', '*.mat'))
    df_graphs = filelist2df(mat_files)
    df_graphs = computedistances(df_graphs)

    print('Graph footprint: {0} MB'.format(df_footprint_mb(df_graphs)))
    df_graphs.to_hdf(results.output_path, "graphs", mode="a")


if __name__ == "__main__":
    main()
