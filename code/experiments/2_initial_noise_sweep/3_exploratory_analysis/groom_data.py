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
                akey = ['voxel_location', 'mm_location']
                for ak in akey:
                    tmp_dict[ak] = np.array(tmp_dict[ak])

        # For the 1-voxel experiment, JSON names will be in the form:
        #  sub-[]_ses-[]_dwi_eddy_1vox-********.[ext]
        one_file = op.basename(one_file)
        tmp_dict['filename'] = one_file
        tmp_dict['subses'] = "_".join(one_file.split('_')[:2])

        # If the file containes noise, grab the 8 character ID
        if "1vox" in one_file:
            tmp_dict['noise_id'] = one_file.split('-')[3][0:8]
        else:
            tmp_dict['noise_id'] = None

        list_of_dicts.append(tmp_dict)
        del tmp_dict

    ldf = pd.DataFrame(list_of_dicts)
    return ldf


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
    listdir = lambda pat: [op.join(pat, x) for x in os.listdir(pat)]

    # Grab and process the metadata
    json_files = listdir(results.json_dir)
    json_df = filelist2df(json_files)
    print('Noise Info footprint: {0} MB'.format(df_footprint_mb(json_df)))
    json_df.to_hdf(results.output_path, "metadata", mode='a')
    del json_df

    # Grab and process the graph data
    mat_files = listdir(results.graph_dir)
    mat_df = filelist2df(mat_files, mat=True)
    print('Graph footprint: {0} MB'.format(df_footprint_mb(mat_df)))
    mat_df.to_hdf(results.output_path, "graphs", mode="a")
    del mat_df


if __name__ == "__main__":
    main()
