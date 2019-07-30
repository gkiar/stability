#!/usr/bin/env python

from argparse import ArgumentParser
import numpy as np
import pandas as pd
import os.path as op
import json
import os

import warnings
warnings.filterwarnings('ignore',
                        category=pd.io.pytables.PerformanceWarning)


def df_footprint_mb(df):
    return np.sum([_/1024.0/1024.0 for _ in df.memory_usage(deep=True).values])


def filelist2df(file_list, mat=False):
    list_of_dicts = []
    for one_file in file_list:

        if mat:  # For matrix formatted data...
            tmp_dict = {"graph": np.loadtxt(one_file)}
        else:  # For JSON formatted data...
            with open(one_file) as fhandle:
                tmp_dict = json.load(fhandle)
                akey = ['mm_location', 'voxel_location']
                for ak in akey:
                    tmp_dict[ak] = np.array(tmp_dict[ak])

                # Looking at the shame of 'voxel_location' to determine type
                if tmp_dict[ak].shape == (1, 4):
                    tmp_dict['noise_type'] = "single"
                elif tmp_dict[ak].shape == (1, 3):
                    tmp_dict['noise_type'] = "continuous"
                else:
                    tmp_dict['noise_type'] = "independent"

        # For the 1-voxel experiment, JSON names will be in the form:
        #  sub-[]_ses-[]_dwi_eddy_1vox-********.[ext]
        one_file = op.basename(one_file)
        tmp_dict['filename'] = one_file
        tmp_dict['subses'] = "_".join(one_file.split('_')[:2])
        tmp_dict['sub'] = tmp_dict['subses'].split('_')[0].split('-')[1]
        tmp_dict['ses'] = tmp_dict['subses'].split('_')[1].split('-')[1]

        # If the file containes noise, grab the 8 character ID
        if "1vox" in one_file:
            tmp_dict['noise_id'] = one_file.split('-')[3][0:8]
        else:
            tmp_dict['noise_id'] = None

        list_of_dicts.append(tmp_dict)
        del tmp_dict

    ldf = pd.DataFrame(list_of_dicts)
    return ldf


def computedistances(df_meta, df_graphs, verbose=False):
    # Define norms to be used
    # Frobenius Norm
    def fro(x, y):
        return np.linalg.norm(x - y, ord='fro')

    # Mean Squared Error
    def mse(x, y):
        return np.mean((x - y)**2)

    # Sum of Squared Differences
    def ssd(x, y):
        return np.sum((x - y)**2)

    norms = [fro, mse, ssd]

    # Grab the unique subses IDs and add columns for norms
    count_dict = df_meta.subses.value_counts().to_dict()
    subses = list(count_dict.keys())
    for norm in norms:
        df_meta.loc[:, norm.__name__] = None

    # For each subses ID...
    for ss in subses:
        if verbose:
            print("Subject-Session: {0}  ".format(ss), end='\t')
            print("Number of simulations: {0}".format(count_dict[ss]))

        # Grab the reference image (i.e. one without noise)
        df_graphs_ss = df_graphs.query('subses == {0}'.format(ss))
        ref = df_graphs_ss.loc[df_graphs_ss.noise_id.isnull()].iloc[0].graph

        # For each noise simulation...
        for _, graph in df_graphs_ss.iterrows():
            idx = df_meta.loc[df_meta.noise_id == graph.noise_id].index
            for norm in norms:
                df_meta.loc[idx, norm.__name__] = norm(ref, graph.graph)

    return df_meta


def main(args=None):
    parser = ArgumentParser(__file__,
                            description="Re-formats JSON and matrix data from"
                                        "one-voxel + connectome generation for"
                                        "subsequent analysis.")
    parser.add_argument("json_dir",
                        help="Directory containing a collection of JSON noise "
                             "files produced by gkiar/oneVoxel.")
    parser.add_argument("graph_dir",
                        help="Corresponding directory containing graphs with "
                             "or without noise injected and stored in the .mat"
                             " ASCII-encoded format.")
    parser.add_argument("output_path",
                        help="Path to the dataframes containing groomed data.")

    results = parser.parse_args() if args is None else parser.parse_args(args)

    # Define utility for listing directories
    def listdir(pat):
        return [op.join(pat, x) for x in os.listdir(pat)]

    # Grab and process the metadata
    json_files = listdir(results.json_dir)
    df_meta = filelist2df(json_files)
    print('Noise Info footprint: {0} MB'.format(df_footprint_mb(df_meta)))

    # Grab and process the graph data
    mat_files = listdir(results.graph_dir)
    df_mat = filelist2df(mat_files, mat=True)
    print('Graph footprint: {0} MB'.format(df_footprint_mb(df_mat)))

    df_meta = computedistances(df_meta, df_mat)

    df_meta.to_hdf(results.output_path, "metadata", mode='a')
    df_mat.to_hdf(results.output_path, "graphs", mode="a")


if __name__ == "__main__":
    main()
