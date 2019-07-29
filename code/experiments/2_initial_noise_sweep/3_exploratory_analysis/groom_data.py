#!/usr/bin/env python

from argparse import ArgumentParser
import numpy as np
import pandas as pd
import os.path as op
import json
import os


def df_footprint_mb(df):
    return np.sum([_/1024.0/1024.0 for _ in df.memory_usage(deep=True).values])


def jsons2df(json_list):
    list_of_dicts = []
    for json_file in json_list:
        with open(op.join(json_file)) as fhandle:
            tmp_dict = json.load(fhandle)

        # For the 1-voxel experiment, JSON file names will be in the form:
        #  sub-*_ses-*_dwi_eddy_1vox-*********.json
        tmp_dict['filename'] = json_file
        tmp_dict['subses'] = "_".join(json_file.split('_')[:2])
        tmp_dict['noise_id'] = json_file.split('-')[-1].split('.')[0]

        list_of_dicts.append(tmp_dict)
        del tmp_dict

    ldf = pd.DataFrame(list_of_dicts)
    return ldf


def mats2df(mat_list):
    pass


def main(args=None):
    parser = ArgumentParser(__file__,
                            description="Re-formats JSON and matrix data from"
                                        "one-voxel + connectome generation for"
                                        "subsequent analysis.")
    parser.add_argument("json_dir",
                        help="")
    parser.add_argument("graph_dir",
                        help="")
    parser.add_argument("output_basename",
                        help="Path to the dataframes containing groomed data.")

    results = parser.parse_args() if args is None else parser.parse_args(args)

    # Define utility for listing directories
    listdir = lambda pat: [op.join(pat, x) for x in os.listdir(pat)]

    oname = results.output_basename + '_noise.h5'

    # Grab and process the metadata
    json_files = listdir(results.json_dir)
    json_df = jsons2df(json_files)
    print('Noise Info footprint: {0}'.format(df_footprint_mb(json_df)))
    json_df.to_hdf(oname, "metadata")
    del json_df

    # Grab and process the graph data
    mat_files = listdir(results.graph_dir)
    mat_df = mats2df(mat_files)
    print('Graph footprint: {0}'.format(df_footprint_mb(mat_df)))
    mat_df.to_hdf(oname, "graphs", mode="a")


if __name__ == "__main__":
    main()
